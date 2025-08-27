import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import time

class CalmOpsPriority(Enum):
    """Aligned with your top 10 priorities for CalmOps"""
    VALIDATION = "workflow challenges creative teams marketing operations"
    SCALING_PAIN = "growing fast hiring scaling challenges coordination"
    WORKFLOW_CHAOS = "project delays missed deadlines rework"
    TOOL_SPRAWL = "too many tools software consolidation"
    REMOTE_COORDINATION = "remote team collaboration hybrid work"
    CREATIVE_BOTTLENECK = "creative process bottleneck approval delays"
    OPERATIONAL_MATURITY = "Series A Series B operational efficiency"

class CalmOpsSearchService:
    def __init__(self):
        self.api_key = os.getenv('8c05dfce5bdd4f7a982c7c4604208a44e2502179Y')
        self.base_url = "https://google.serper.dev/search"
        
        # Target markets - avoiding SF
        self.target_markets = {
            'new_york': {
                'query_suffix': 'New York NYC Manhattan Brooklyn',
                'companies_size': '50-200 employees',
                'sectors': ['media', 'fashion', 'fintech', 'adtech', 'ecommerce']
            },
            'new_jersey': {
                'query_suffix': 'New Jersey Newark Jersey City Hoboken Princeton',
                'companies_size': '50-200 employees',  
                'sectors': ['pharma', 'biotech', 'financial services', 'logistics']
            },
            'south_florida': {
                'query_suffix': 'Miami Fort Lauderdale Boca Raton West Palm Beach',
                'companies_size': '50-200 employees',
                'sectors': ['hospitality', 'real estate tech', 'healthtech', 'fintech']
            },
            'los_angeles': {
                'query_suffix': 'Los Angeles LA Santa Monica Venice Culver City',
                'companies_size': '50-200 employees',
                'sectors': ['entertainment', 'gaming', 'fashion', 'DTC brands', 'content']
            }
        }
        
    def validate_problem_search(self, market: str = 'all', week_number: int = 1) -> Dict:
        """
        Week 1 Priority: Find 10 target prospects with visible workflow challenges
        """
        results = {
            'priority': 'VALIDATE_PROBLEM',
            'week': week_number,
            'prospects': [],
            'decision_makers': []
        }
        
        # Determine which markets to search
        if market == 'all':
            markets_to_search = list(self.target_markets.keys())
        else:
            markets_to_search = [market] if market in self.target_markets else ['new_york']
        
        # Search queries for finding companies with workflow pain
        for market_key in markets_to_search:
            market_config = self.target_markets[market_key]
            
            validation_queries = [
                f"creative team growing pains {market_config['query_suffix']} 50-200 employees",
                f"marketing operations challenges {market_config['query_suffix']}",
                f"Series A Series B companies {market_config['query_suffix']} hiring creative",
                f"fast growing startups {market_config['query_suffix']} marketing team",
            ]
            
            for query in validation_queries:
                try:
                    search_results = self._search(query)
                    prospects = self._extract_validation_prospects(search_results, market_key)
                    results['prospects'].extend(prospects)
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    print(f"Search error for query '{query}': {e}")
                    
        # Deduplicate and score
        results['prospects'] = self._score_validation_prospects(results['prospects'])
        
        # Find decision makers for top prospects
        for prospect in results['prospects'][:10]:
            try:
                decision_makers = self._find_decision_makers(prospect)
                results['decision_makers'].extend(decision_makers)
            except Exception as e:
                print(f"Error finding decision makers: {e}")
                
        return results
    
    def find_pilot_candidates(self, validated_prospects: List[Dict]) -> Dict:
        """
        Week 2-3 Priority: Find best candidates for pilot program
        """
        pilot_candidates = []
        
        for prospect in validated_prospects[:5]:  # Top 5 validated prospects
            company_name = prospect.get('company_name', '')
            if not company_name:
                continue
                
            # Deep dive search on each validated prospect
            queries = [
                f"{company_name} creative team size",
                f"{company_name} marketing operations",
                f"site:linkedin.com/company {company_name}",
            ]
            
            company_intel = {
                'company': company_name,
                'signals': [],
                'pilot_score': 0
            }
            
            for query in queries:
                try:
                    results = self._search(query)
                    signals = self._extract_pilot_signals(results)
                    company_intel['signals'].extend(signals)
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    print(f"Error researching {company_name}: {e}")
                    
            company_intel['pilot_score'] = self._calculate_pilot_score(company_intel)
            pilot_candidates.append(company_intel)
            
        return {
            'pilot_candidates': sorted(pilot_candidates, 
                                      key=lambda x: x['pilot_score'], 
                                      reverse=True)[:3]
        }
    
    def scale_outreach_targets(self, market: str, target_count: int = 50) -> Dict:
        """
        Week 5-6 Priority: Find 50 target companies for scaled outreach
        """
        targets = []
        
        # Get market configuration
        market_config = self.target_markets.get(market, self.target_markets['new_york'])
        
        # Search each sector in the market
        for sector in market_config['sectors']:
            query = f"{sector} companies {market_config['query_suffix']} {market_config['companies_size']}"
            
            try:
                results = self._search(query, num_results=20)
                companies = self._extract_outreach_targets(results, market, sector)
                targets.extend(companies)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Outreach search error for {sector}: {e}")
                
        # Find LinkedIn contacts for top targets
        for target in targets[:min(target_count, len(targets))]:
            company_name = target.get('company_name', '')
            if not company_name:
                continue
                
            linkedin_query = f"site:linkedin.com/in creative director {company_name} OR CMO OR marketing operations"
            try:
                results = self._search(linkedin_query, num_results=5)
                target['contacts'] = self._extract_linkedin_contacts(results)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"LinkedIn search error for {company_name}: {e}")
                
        return {
            'outreach_targets': targets[:target_count],
            'by_sector': self._group_by_sector(targets),
            'by_market': market,
            'total_found': len(targets)
        }
    
    def _search(self, query: str, num_results: int = 10) -> Dict:
        """Execute search via Serper API using requests"""
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': num_results,
            'gl': 'us',
            'hl': 'en'
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Serper API error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def _extract_validation_prospects(self, search_results: Dict, market: str) -> List[Dict]:
        """Extract companies showing workflow pain signals"""
        prospects = []
        
        for result in search_results.get('organic', []):
            text = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
            
            # Pain signals to look for
            pain_signals = {
                'growing_pains': any(term in text for term in 
                                   ['growing pains', 'scaling challenges', 'rapid growth']),
                'workflow_issues': any(term in text for term in 
                                     ['workflow', 'coordination', 'collaboration challenges']),
                'hiring_creative': any(term in text for term in 
                                     ['hiring creative', 'hiring marketing', 'building team']),
                'series_funding': any(term in text for term in 
                                    ['series a', 'series b', 'raised', 'funding']),
                'operational': any(term in text for term in 
                                 ['operations', 'efficiency', 'productivity'])
            }
            
            if sum(pain_signals.values()) >= 2:  # At least 2 pain signals
                prospects.append({
                    'title': result.get('title'),
                    'snippet': result.get('snippet'),
                    'link': result.get('link'),
                    'company_name': self._extract_company_name(result),
                    'pain_signals': pain_signals,
                    'market': market,
                    'validation_score': sum(pain_signals.values()) / len(pain_signals)
                })
                
        return prospects
    
    def _score_validation_prospects(self, prospects: List[Dict]) -> List[Dict]:
        """Score and deduplicate prospects"""
        # Deduplicate by company name
        seen_companies = {}
        for prospect in prospects:
            company = prospect.get('company_name', '')
            if not company:
                continue
                
            if company not in seen_companies:
                seen_companies[company] = prospect
            else:
                # Keep the one with higher score
                if prospect.get('validation_score', 0) > seen_companies[company].get('validation_score', 0):
                    seen_companies[company] = prospect
                    
        # Sort by validation score
        unique_prospects = list(seen_companies.values())
        unique_prospects.sort(key=lambda x: x.get('validation_score', 0), reverse=True)
        
        return unique_prospects
    
    def _extract_company_name(self, result: Dict) -> str:
        """Extract company name from search result"""
        title = result.get('title', '')
        # Remove common suffixes
        for suffix in [' - LinkedIn', ' | Glassdoor', ' Inc.', ' LLC', ' Corp.']:
            title = title.replace(suffix, '')
        # Take first part before dash or pipe
        if ' - ' in title:
            title = title.split(' - ')[0]
        if ' | ' in title:
            title = title.split(' | ')[0]
        return title.strip()
    
    def _find_decision_makers(self, prospect: Dict) -> List[Dict]:
        """Find decision makers for a prospect company"""
        company = prospect.get('company_name', '')
        if not company:
            return []
            
        decision_makers = []
        roles = ['Creative Director', 'CMO', 'VP Marketing', 'Marketing Operations Manager']
        
        for role in roles:
            query = f"site:linkedin.com/in {role} {company}"
            try:
                results = self._search(query, num_results=3)
                for result in results.get('organic', []):
                    decision_makers.append({
                        'company': company,
                        'role': role,
                        'linkedin_url': result.get('link'),
                        'name': self._extract_name_from_title(result.get('title', '')),
                        'snippet': result.get('snippet')
                    })
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error finding {role} at {company}: {e}")
                continue
                
        return decision_makers
    
    def _extract_name_from_title(self, title: str) -> str:
        """Extract name from LinkedIn title"""
        name = title.split(' - ')[0].strip()
        name = name.replace(' on LinkedIn', '').replace(' | LinkedIn', '')
        return name
    
    def _extract_pilot_signals(self, search_results: Dict) -> List[str]:
        """Extract signals for pilot scoring"""
        signals = []
        
        for result in search_results.get('organic', []):
            text = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
            
            signal_terms = [
                'workflow', 'project management', 'collaboration',
                'creative team', 'marketing operations', 'delays',
                'efficiency', 'productivity', 'scaling', 'growing'
            ]
            
            for term in signal_terms:
                if term in text and term not in signals:
                    signals.append(term)
                    
        return signals
    
    def _calculate_pilot_score(self, company_intel: Dict) -> float:
        """Calculate pilot candidate score"""
        signals = company_intel.get('signals', [])
        
        # High value signals
        high_value = ['workflow', 'delays', 'scaling', 'project management']
        medium_value = ['creative team', 'marketing operations', 'efficiency']
        
        score = 0.0
        for signal in signals:
            if signal in high_value:
                score += 0.3
            elif signal in medium_value:
                score += 0.2
            else:
                score += 0.1
                
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_outreach_targets(self, search_results: Dict, market: str, sector: str) -> List[Dict]:
        """Extract companies for outreach"""
        targets = []
        
        for result in search_results.get('organic', []):
            targets.append({
                'company_name': self._extract_company_name(result),
                'title': result.get('title'),
                'snippet': result.get('snippet'),
                'link': result.get('link'),
                'market': market,
                'sector': sector,
                'date_found': datetime.now().isoformat()
            })
            
        return targets
    
    def _extract_linkedin_contacts(self, search_results: Dict) -> List[Dict]:
        """Extract LinkedIn contacts from search results"""
        contacts = []
        
        for result in search_results.get('organic', []):
            if 'linkedin.com/in' in result.get('link', ''):
                contacts.append({
                    'name': self._extract_name_from_title(result.get('title', '')),
                    'linkedin_url': result.get('link'),
                    'title_snippet': result.get('snippet', '')
                })
                
        return contacts
    
    def _group_by_sector(self, targets: List[Dict]) -> Dict[str, List[Dict]]:
        """Group targets by sector"""
        by_sector = {}
        for target in targets:
            sector = target.get('sector', 'unknown')
            if sector not in by_sector:
                by_sector[sector] = []
            by_sector[sector].append(target)
        return by_sector