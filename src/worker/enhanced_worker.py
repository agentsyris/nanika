import redis
import json
from typing import Dict, Any
import asyncio
from search_service import WebSearchService
from llm_service import OllamaService

class EnhancedWorker:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.search_service = WebSearchService()
        self.llm_service = OllamaService()
        
    async def process_task(self, task: Dict[str, Any]):
        """Process tasks with real data retrieval"""
        task_type = task.get('type')
        
        if task_type == 'company_research':
            return await self.research_company(task)
        elif task_type == 'market_analysis':
            return await self.analyze_market(task)
        elif task_type == 'lead_generation':
            return await self.generate_leads(task)
            
    async def research_company(self, task: Dict) -> Dict:
        """Research a company with real data"""
        company_name = task.get('company_name')
        
        # Step 1: Get real search results
        search_results = await self.search_service.search_companies(company_name)
        
        # Step 2: Search LinkedIn specifically
        linkedin_results = await self.search_service.search_linkedin_companies(company_name)
        
        # Step 3: Use LLM to analyze and structure the real data
        analysis_prompt = f"""
        Analyze the following real search data about {company_name}:
        
        Search Results:
        {json.dumps(search_results, indent=2)}
        
        LinkedIn Results:
        {json.dumps(linkedin_results, indent=2)}
        
        Provide a structured analysis with:
        1. Company Overview (from actual data only)
        2. Key Personnel (if found)
        3. Recent News/Updates
        4. Business Focus Areas
        5. Potential Opportunities for Art Consulting
        
        Only use information directly from the search results. Do not invent any details.
        """
        
        analysis = await self.llm_service.generate(
            prompt=analysis_prompt,
            model="llama3.1:70b"
        )
        
        return {
            'company_name': company_name,
            'raw_data': {
                'search_results': search_results,
                'linkedin_results': linkedin_results
            },
            'analysis': analysis,
            'sources': search_results.get('sources', []),
            'timestamp': search_results.get('timestamp')
        }
    
    async def generate_leads(self, task: Dict) -> Dict:
        """Generate real leads based on search criteria"""
        criteria = task.get('criteria', {})
        industry = criteria.get('industry', 'technology')
        location = criteria.get('location', 'San Francisco')
        
        # Search for real companies
        search_query = f"{industry} companies {location} office expansion new headquarters"
        results = await self.search_service.search_companies(search_query, location)
        
        # Process into leads
        leads = []
        for company in results.get('companies', []):
            lead = {
                'company': company.get('title'),
                'snippet': company.get('snippet'),
                'url': company.get('link'),
                'domain': company.get('domain'),
                'relevance_score': self._calculate_relevance(company, criteria)
            }
            leads.append(lead)
            
        # Sort by relevance
        leads.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            'leads': leads[:10],  # Top 10 leads
            'search_criteria': criteria,
            'total_found': len(leads),
            'sources': results.get('sources', [])
        }
    
    def _calculate_relevance(self, company: Dict, criteria: Dict) -> float:
        """Calculate relevance score based on criteria"""
        score = 0.5  # Base score
        
        keywords = criteria.get('keywords', [])
        snippet = company.get('snippet', '').lower()
        
        for keyword in keywords:
            if keyword.lower() in snippet:
                score += 0.1
                
        # Boost for specific indicators
        if any(term in snippet for term in ['expansion', 'new office', 'headquarters', 'moving']):
            score += 0.2
            
        return min(score, 1.0)
