import redis
import json
import time
from datetime import datetime
from typing import Dict, List
from calmops_search_service import CalmOpsSearchService, CalmOpsPriority

class CalmOpsWorker:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.search_service = CalmOpsSearchService()
        
    def run(self):
        """Main worker loop"""
        print("CalmOps Worker started...")
        
        while True:
            try:
                # Check for tasks in queue
                task_json = self.redis_client.brpop('calmops_queue', timeout=5)
                
                if task_json:
                    task = json.loads(task_json[1])
                    self.process_task(task)
                else:
                    # No tasks, wait
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Worker error: {e}")
                time.sleep(5)
    
    def process_task(self, task: Dict):
        """Process different task types"""
        task_type = task.get('type')
        task_id = task.get('id')
        
        print(f"Processing task {task_id} of type {task_type}")
        
        try:
            if task_type == 'validate_problem':
                result = self.validate_problem_task(task)
            elif task_type == 'find_pilots':
                result = self.find_pilots_task(task)
            elif task_type == 'scale_outreach':
                result = self.scale_outreach_task(task)
            # New task handlers added for additional automation workflows
            elif task_type == 'search_prospects':
                # Generic prospect search across arbitrary keywords
                result = self.search_prospects_task(task)
            elif task_type == 'generate_outreach_draft':
                # Generate a personalised outreach draft (stubbed)
                result = self.generate_outreach_draft_task(task)
            elif task_type == 'create_mvp_rubric':
                # Generate an MVP assessment rubric (stubbed)
                result = self.create_mvp_rubric_task(task)
            else:
                result = {'error': f'Unknown task type: {task_type}'}
                
            # Store result
            self.redis_client.setex(
                f'result:{task_id}',
                3600,  # Expire after 1 hour
                json.dumps(result)
            )
            
            # Save to file
            self.save_to_artifact(result, task_type)
            
        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
            error_result = {'error': str(e), 'task_id': task_id}
            self.redis_client.setex(f'result:{task_id}', 3600, json.dumps(error_result))
    
    def validate_problem_task(self, task: Dict) -> Dict:
        """Week 1: Find and validate prospects"""
        market = task.get('market', 'all')
        
        print(f"Searching for validation prospects in {market}")
        results = self.search_service.validate_problem_search(market)
        
        # Enhance with additional analysis
        top_prospects = results['prospects'][:10]
        
        return {
            'task_id': task.get('id'),
            'type': 'validation',
            'market': market,
            'total_prospects_found': len(results['prospects']),
            'top_10_prospects': top_prospects,
            'decision_makers': results['decision_makers'],
            'timestamp': datetime.now().isoformat(),
            'next_action': 'Send personalized LinkedIn messages to decision makers'
        }
    
    def find_pilots_task(self, task: Dict) -> Dict:
        """Week 2-3: Find pilot candidates"""
        validated_prospects = task.get('validated_prospects', [])
        
        if not validated_prospects:
            return {'error': 'No validated prospects provided'}
            
        print(f"Finding pilot candidates from {len(validated_prospects)} prospects")
        results = self.search_service.find_pilot_candidates(validated_prospects)
        
        return {
            'task_id': task.get('id'),
            'type': 'pilot_identification',
            'pilot_candidates': results['pilot_candidates'],
            'timestamp': datetime.now().isoformat(),
            'recommendation': 'Start with highest scoring candidate for pilot'
        }
    
    def scale_outreach_task(self, task: Dict) -> Dict:
        """Week 5-6: Scale outreach"""
        market = task.get('market', 'new_york')
        target_count = task.get('target_count', 50)
        
        print(f"Finding {target_count} outreach targets in {market}")
        results = self.search_service.scale_outreach_targets(market, target_count)
        
        return {
            'task_id': task.get('id'),
            'type': 'scaled_outreach',
            'market': market,
            'targets_found': results['total_found'],
            'outreach_targets': results['outreach_targets'],
            'by_sector': results['by_sector'],
            'timestamp': datetime.now().isoformat()
        }
    
    def save_to_artifact(self, result: Dict, task_type: str):
        """Save results to artifact file"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        artifact_dir = f'/data/artifacts/{date_str}'
        os.makedirs(artifact_dir, exist_ok=True)
        
        filename = f'{artifact_dir}/{task_type}_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"Saved artifact to {filename}")

    # --------------------------------------------------------------------------
    # Additional task handlers for extended CalmOps automation
    def search_prospects_task(self, task: Dict) -> Dict:
        """
        Generic prospect search across user‑supplied keywords.  This task takes
        a list of search keywords and returns a deduplicated list of companies
        matching workflow pain signals.  Note: this is a simplified stub using
        existing validation extraction logic.

        Expected task structure:
        {
            'id': '<task_id>',
            'type': 'search_prospects',
            'keywords': ['workflow challenges', 'marketing operations problems']
        }
        """
        keywords = task.get('keywords', [])
        if not isinstance(keywords, list) or not keywords:
            return {'error': 'No keywords provided', 'task_id': task.get('id')}

        prospects: List[Dict] = []
        for kw in keywords:
            try:
                # Use internal search to find relevant results
                search_results = self.search_service._search(kw)
                # Reuse validation extraction logic; market not relevant here
                extracted = self.search_service._extract_validation_prospects(search_results, market='custom')
                prospects.extend(extracted)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error during prospect search for '{kw}': {e}")
                continue

        # Deduplicate and score as in validation
        unique_prospects = self.search_service._score_validation_prospects(prospects)

        return {
            'task_id': task.get('id'),
            'type': 'search_prospects',
            'keywords': keywords,
            'total_prospects_found': len(unique_prospects),
            'prospects': unique_prospects,
            'timestamp': datetime.now().isoformat()
        }

    def generate_outreach_draft_task(self, task: Dict) -> Dict:
        """
        Generate a personalised outreach draft for a single prospect.  This is a
        placeholder implementation that returns a template message.  In a full
        implementation this would call an LLM (e.g., via Ollama) and create a
        Gmail draft via the Gmail API.

        Expected task structure:
        {
            'id': '<task_id>',
            'type': 'generate_outreach_draft',
            'prospect': { 'company_name': 'Acme', 'pain_signals': {...}, 'snippet': '...' }
        }
        """
        prospect = task.get('prospect', {}) or {}
        company = prospect.get('company_name', 'your company')
        snippet = prospect.get('snippet', '')
        pain_signals = prospect.get('pain_signals', {})

        # Compose a simple message template.  Replace with LLM call as needed.
        message = (
            f"Hi there,\n\n"
            f"I came across {company} and noticed you might be dealing with some of these issues: "
            f"{', '.join([k for k,v in pain_signals.items() if v])}. "
            f"I'd love to chat briefly about how we help teams improve workflow efficiency.\n\n"
            f"Best,\nCalmOps"
        )

        return {
            'task_id': task.get('id'),
            'type': 'generate_outreach_draft',
            'prospect': prospect,
            'draft_message': message,
            'timestamp': datetime.now().isoformat(),
            'note': 'This is a stubbed outreach draft. Integrate with LLM and Gmail API for production.'
        }

    def create_mvp_rubric_task(self, task: Dict) -> Dict:
        """
        Generate a simple MVP assessment rubric.  This stub returns a static
        rubric based on provided features and goals.  In production, integrate
        an LLM to construct criteria and weightings and persist to Notion.

        Expected task structure:
        {
            'id': '<task_id>',
            'type': 'create_mvp_rubric',
            'features': ['feature A', 'feature B'],
            'goals': ['goal 1', 'goal 2']
        }
        """
        features = task.get('features', [])
        goals = task.get('goals', [])
        if not features or not goals:
            return {
                'task_id': task.get('id'),
                'error': 'Features and goals must be provided',
                'type': 'create_mvp_rubric'
            }

        # Construct a basic rubric: each feature scored against each goal
        rubric = []
        weight = round(1 / len(features), 2) if features else 0.0
        for feature in features:
            criteria = []
            for goal in goals:
                criteria.append({
                    'goal': goal,
                    'weight': weight,
                    'description': f"How well does {feature} support {goal}?"
                })
            rubric.append({
                'feature': feature,
                'criteria': criteria
            })

        return {
            'task_id': task.get('id'),
            'type': 'create_mvp_rubric',
            'features': features,
            'goals': goals,
            'rubric': rubric,
            'timestamp': datetime.now().isoformat(),
            'note': 'This is a stub rubric; customise or integrate with LLM for more complex logic.'
        }

if __name__ == "__main__":
    worker = CalmOpsWorker()
    worker.run()