import os
import redis
import json
import time
import requests
from datetime import datetime, timedelta

class CalmOpsWorker:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=6379,
            decode_responses=True
        )
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.ollama_host = 'http://host.docker.internal:11434'
        
        # Test connections
        print(f"Worker initialized. Serper API: {bool(self.serper_api_key)}")
        self.test_ollama()
        
    def test_ollama(self):
        try:
            resp = requests.get(f"{self.ollama_host}/api/tags")
            models = [m['name'] for m in resp.json().get('models', [])]
            print(f"Ollama models available: {models}")
        except Exception as e:
            print(f"Warning: Ollama not reachable: {e}")
    
    def run(self):
        print("CalmOps Worker listening for tasks...")
        while True:
            try:
                task_json = self.redis_client.brpop('nanika_queue', timeout=5)
                if task_json:
                    task = json.loads(task_json[1])
                    print(f"Processing: {task['type']} - {task.get('week', 'N/A')}")
                    
                    # Route to appropriate task handler
                    handlers = {
                        'validate_problem': self.task1_validate_problem,
                        'create_framework': self.task2_create_framework,
                        'generate_landing': self.task3_generate_landing,
                        'find_pilots': self.task4_find_pilots,
                        'create_case_study': self.task5_create_case_study,
                        'setup_operations': self.task6_setup_operations,
                        'launch_content': self.task7_launch_content,
                        'develop_referrals': self.task8_develop_referrals,
                        'scale_outreach': self.task9_scale_outreach,
                        'close_full_price': self.task10_close_full_price
                    }
                    
                    handler = handlers.get(task['type'], self.unknown_task)
                    result = handler(task)
                    
                    # Save result
                    self.redis_client.setex(
                        f"result:{task['id']}", 
                        3600, 
                        json.dumps(result)
                    )
                    print(f"Completed task {task['id']}")
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
    
    def search_companies(self, query):
        """Common search function using Serper"""
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://google.serper.dev/search',
            headers=headers,
            json={'q': query, 'num': 10},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def analyze_with_ollama(self, prompt, model="llama3.1:70b"):
        """Use Ollama for analysis"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get('response', '')
            return "Analysis unavailable"
        except Exception as e:
            return f"Analysis failed: {e}"
    
    # TASK 1: Validate Problem (Week 1)
    def task1_validate_problem(self, task):
        """Find 10 companies with workflow challenges"""
        market = task.get('market', 'new_york')
        
        # Search for companies with pain signals
        queries = [
            f"Series A Series B companies {market} hiring creative marketing",
            f"growing companies {market} 50-200 employees workflow challenges",
            f"creative agencies {market} scaling project management"
        ]
        
        all_prospects = []
        for query in queries:
            results = self.search_companies(query)
            if results:
                for item in results.get('organic', []):
                    snippet = item.get('snippet', '').lower()
                    title = item.get('title', '')
                    
                    # Look for pain signals
                    pain_signals = {
                        'hiring': 'hiring' in snippet,
                        'growing': 'growing' in snippet or 'growth' in snippet,
                        'scaling': 'scaling' in snippet,
                        'workflow': 'workflow' in snippet,
                        'challenges': 'challenges' in snippet
                    }
                    
                    if sum(pain_signals.values()) >= 2:
                        all_prospects.append({
                            'company': self.extract_company_name(title),
                            'snippet': item.get('snippet'),
                            'link': item.get('link'),
                            'pain_signals': pain_signals,
                            'pain_score': sum(pain_signals.values())
                        })
        
        # Sort by pain score
        all_prospects.sort(key=lambda x: x['pain_score'], reverse=True)
        top_10 = all_prospects[:10]
        
        # Generate outreach messages with Ollama
        outreach_messages = []
        for prospect in top_10[:3]:  # Just top 3 for demo
            prompt = f"""
            Create a LinkedIn outreach message for this prospect:
            Company: {prospect['company']}
            Context: {prospect['snippet']}
            
            Use this template but personalize:
            "Hi [Name],
            I noticed [Company] recently [specific observation].
            I'm researching workflow challenges that creative/marketing teams face as they scale. 
            Would you spare 15 minutes to share what's working (and what's not) with your current processes?
            Not selling anything - just gathering insights from leaders like yourself."
            
            Keep under 100 words.
            """
            
            message = self.analyze_with_ollama(prompt)
            outreach_messages.append({
                'company': prospect['company'],
                'message': message
            })
        
        return {
            'task': 'Week 1: Validate Problem',
            'prospects_found': len(all_prospects),
            'top_10_prospects': top_10,
            'outreach_messages': outreach_messages,
            'success_metric': f"{len(top_10)}/10 prospects identified",
            'next_steps': "Send LinkedIn messages and schedule calls"
        }
    
    # TASK 2: Create MVP Framework (Week 1-2)
    def task2_create_framework(self, task):
        """Generate assessment framework documents"""
        prompt = """
        Create a simple 2-week workflow assessment framework for creative teams:
        
        Include:
        1. Day-by-day schedule
        2. List of 10 key diagnostic questions
        3. Simple workflow mapping approach
        4. Recommendations report outline
        
        Format as a practical framework that can be explained in 10 minutes.
        """
        
        framework = self.analyze_with_ollama(prompt)
        
        return {
            'task': 'Week 2: Create MVP Framework',
            'framework': framework,
            'deliverables': [
                'Assessment schedule',
                'Diagnostic questionnaire',
                'Workflow mapping template',
                'Report template'
            ],
            'success_metric': 'Complete methodology documented'
        }
    
    # TASK 3: Generate Landing Page (Week 2)
    def task3_generate_landing(self, task):
        """Generate landing page copy and structure"""
        prompt = """
        Create landing page copy for CalmOps workflow consulting:
        
        Header: "Streamline Creative Workflows in 2 Weeks, Not 6 Months"
        
        Include sections for:
        - Problem (3 pain points)
        - Solution (3 benefits)
        - Process (3 steps)
        - Pricing ($8,500)
        - Call to action
        
        Keep it concise and conversion-focused.
        """
        
        landing_copy = self.analyze_with_ollama(prompt)
        
        return {
            'task': 'Week 2: Build Landing Page',
            'landing_copy': landing_copy,
            'tools_needed': ['Squarespace', 'Calendly'],
            'estimated_cost': '$200-500',
            'success_metric': 'Professional site live'
        }
    
    # TASK 4: Find Pilot Candidates (Week 2-3)
    def task4_find_pilots(self, task):
        """Identify best pilot candidates from validated prospects"""
        prospects = task.get('validated_prospects', [])
        
        if not prospects:
            # Search for them if not provided
            validation_result = self.task1_validate_problem(task)
            prospects = validation_result.get('top_10_prospects', [])
        
        # Score for pilot fit
        pilot_scores = []
        for prospect in prospects[:5]:
            prompt = f"""
            Score this company as a pilot candidate (0-10):
            {json.dumps(prospect, indent=2)}
            
            Consider:
            - Clear pain signals
            - Company size (50-200 ideal)
            - Likely budget availability
            - Potential for case study
            
            Return just a number 0-10 and brief reason.
            """
            
            score_response = self.analyze_with_ollama(prompt)
            pilot_scores.append({
                'company': prospect.get('company'),
                'score': score_response,
                'prospect_data': prospect
            })
        
        # Generate pilot pitch
        pitch_template = """
        I'm launching CalmOps to help mid-market creative teams optimize workflows.
        
        Instead of $8,500, I'm offering 3 strategic partners a pilot at $3,000.
        
        You get: Full 2-week assessment, recommendations, roadmap
        I get: Real-world testing and case study
        
        Interested in being a pilot partner?
        """
        
        return {
            'task': 'Week 2-3: Find Pilots',
            'pilot_candidates': pilot_scores[:3],
            'pilot_pitch': pitch_template,
            'success_metric': '3 pilot candidates identified',
            'next_steps': 'Send pilot proposals'
        }
    
    # TASK 5: Create Case Study (Week 4)
    def task5_create_case_study(self, task):
        """Generate case study from pilot results"""
        pilot_data = task.get('pilot_data', {
            'company': 'Example Agency',
            'size': '75 employees',
            'challenges': 'Project delays, communication gaps',
            'results': '30% faster project delivery'
        })
        
        prompt = f"""
        Create a 1-page case study from this pilot:
        {json.dumps(pilot_data, indent=2)}
        
        Include:
        - Challenge (2-3 sentences)
        - Solution (what we did)
        - Results (3 quantified improvements)
        - Client testimonial
        - ROI calculation
        
        Make it compelling and specific.
        """
        
        case_study = self.analyze_with_ollama(prompt)
        
        return {
            'task': 'Week 4: Create Case Study',
            'case_study': case_study,
            'success_metric': 'Compelling case study created',
            'next_use': 'Content marketing and sales'
        }
    
    # TASK 6: Setup Operations (Week 3-4)
    def task6_setup_operations(self, task):
        """Business operations checklist"""
        return {
            'task': 'Week 3-4: Setup Operations',
            'checklist': [
                {'item': 'Register LLC', 'status': 'pending', 'cost': '$200-500'},
                {'item': 'Get EIN', 'status': 'pending', 'cost': 'Free'},
                {'item': 'Business bank account', 'status': 'pending', 'cost': '$0-25/mo'},
                {'item': 'Liability insurance', 'status': 'pending', 'cost': '$50-100/mo'},
                {'item': 'Service agreement template', 'status': 'pending', 'cost': 'Time'},
                {'item': 'QuickBooks setup', 'status': 'pending', 'cost': '$25/mo'}
            ],
            'total_cost': '$1,000-1,500',
            'success_metric': 'Legal entity ready for payments'
        }
    
    # TASK 7: Launch Content Marketing (Week 4-5)
    def task7_launch_content(self, task):
        """Generate content marketing pieces"""
        case_study = task.get('case_study', 'Recent pilot showed 30% improvement')
        
        prompt = f"""
        Create 3 LinkedIn post ideas based on this case study:
        {case_study}
        
        Each post should:
        - Share a specific insight
        - Be under 200 words
        - Include a hook and call to action
        """
        
        content_ideas = self.analyze_with_ollama(prompt)
        
        return {
            'task': 'Week 4-5: Launch Content',
            'content_ideas': content_ideas,
            'publishing_schedule': {
                'Monday': 'Case study article',
                'Wednesday': 'Workflow tip',
                'Friday': 'Lessons learned'
            },
            'success_metric': '500+ views, 50+ subscribers'
        }
    
    # TASK 8: Develop Referral System (Week 5)
    def task8_develop_referrals(self, task):
        """Create referral program materials"""
        prompt = """
        Create a simple referral program for CalmOps:
        
        1. Email template asking for referrals
        2. Incentive structure (20% commission)
        3. Tracking system outline
        
        Keep it simple and easy to execute.
        """
        
        referral_program = self.analyze_with_ollama(prompt)
        
        return {
            'task': 'Week 5: Develop Referrals',
            'referral_program': referral_program,
            'success_metric': '2-3 warm referrals',
            'implementation': 'Send to pilot clients'
        }
    
    # TASK 9: Scale Outreach (Week 5-6)
    def task9_scale_outreach(self, task):
        """Find 50 target companies for outreach"""
        markets = task.get('markets', ['new_york', 'new_jersey', 'south_florida', 'los_angeles'])
        
        all_targets = []
        for market in markets:
            query = f"creative agencies {market} 50-200 employees marketing teams"
            results = self.search_companies(query)
            
            if results:
                for item in results.get('organic', []):
                    all_targets.append({
                        'company': self.extract_company_name(item.get('title', '')),
                        'market': market,
                        'link': item.get('link'),
                        'snippet': item.get('snippet', '')
                    })
        
        # Generate outreach sequence
        prompt = """
        Create a 3-touch outreach sequence:
        1. Initial LinkedIn message
        2. Follow-up email (3 days later)
        3. Final message (7 days later)
        
        Reference case study results. Keep each under 100 words.
        """
        
        outreach_sequence = self.analyze_with_ollama(prompt)
        
        return {
            'task': 'Week 5-6: Scale Outreach',
            'targets_found': len(all_targets),
            'target_companies': all_targets[:50],
            'outreach_sequence': outreach_sequence,
            'success_metric': '15+ calls scheduled',
            'expected_conversion': '30% response rate'
        }
    
    # TASK 10: Close Full Price Clients (Week 6-7)
    def task10_close_full_price(self, task):
        """Generate sales materials for full-price offering"""
        prompt = """
        Create a sales pitch for $8,500 CalmOps assessment:
        
        Include:
        1. Value proposition (3 points)
        2. ROI justification
        3. Urgency creator
        4. Objection handlers (top 3)
        5. Close technique
        
        Use case study as social proof.
        """
        
        sales_pitch = self.analyze_with_ollama(prompt)
        
        return {
            'task': 'Week 6-7: Close Full Price',
            'sales_pitch': sales_pitch,
            'pricing': '$8,500',
            'success_metric': '2 clients = $17,000 revenue',
            'pipeline_needed': '10 qualified prospects for 2 closes'
        }
    
    def extract_company_name(self, title):
        """Extract company name from search result title"""
        # Remove common suffixes
        for suffix in [' - LinkedIn', ' | Glassdoor', ' Inc.', ' LLC']:
            title = title.replace(suffix, '')
        return title.split('-')[0].split('|')[0].strip()
    
    def unknown_task(self, task):
        return {'error': f"Unknown task type: {task.get('type')}"}

if __name__ == "__main__":
    worker = CalmOpsWorker()
    worker.run()