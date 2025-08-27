from typing import Dict, List
import json
from datetime import datetime

class CalmOpsAutomation:
    def __init__(self, search_service, llm_service):
        self.search = search_service
        self.llm = llm_service
        
    async def week1_validation_campaign(self) -> Dict:
        """
        Automate Week 1: Validate Problem with 10 Target Prospects
        """
        print("Starting Week 1: Problem Validation")
        
        # Search all target markets
        all_prospects = []
        for market in ['new_york', 'new_jersey', 'south_florida', 'los_angeles']:
            results = await self.search.validate_problem_search(market, week_number=1)
            all_prospects.extend(results['prospects'])
            
        # Get top 10 prospects
        top_prospects = sorted(all_prospects, 
                             key=lambda x: x['validation_score'], 
                             reverse=True)[:10]
        
        # Generate personalized outreach for each
        outreach_messages = []
        for prospect in top_prospects:
            message = await self._generate_validation_outreach(prospect)
            outreach_messages.append({
                'prospect': prospect,
                'message': message,
                'decision_makers': await self.search._find_decision_makers(prospect)
            })
            
        return {
            'week': 1,
            'task': 'Validate Problem',
            'prospects_identified': len(top_prospects),
            'outreach_ready': outreach_messages,
            'next_steps': 'Send LinkedIn messages and schedule calls'
        }
    
    async def _generate_validation_outreach(self, prospect: Dict) -> str:
        """Generate personalized LinkedIn outreach message"""
        prompt = f"""
        Create a personalized LinkedIn message for this prospect:
        
        Company: {prospect['company_name']}
        Signals: {json.dumps(prospect['pain_signals'])}
        Context: {prospect['snippet']}
        
        Use this template but personalize it:
        "Hi [Name],
        
        I noticed [Company] recently [specific observation from signals].
        
        I'm researching workflow challenges that creative/marketing teams face as they scale. 
        Would you spare 15 minutes to share what's working (and what's not) with your current processes?
        
        Not selling anything - just gathering insights from leaders like yourself.
        
        [Your name]"
        
        Make it specific to their situation. Keep it under 100 words.
        """
        
        message = await self.llm.generate(prompt, model="llama3.1:70b")
        return message
    
    async def week2_pilot_identification(self, validated_prospects: List[Dict]) -> Dict:
        """
        Automate Week 2-3: Identify best pilot candidates
        """
        print("Starting Week 2: Pilot Program Identification")
        
        # Deep research on validated prospects
        pilot_candidates = await self.search.find_pilot_candidates(validated_prospects)
        
        # Generate pilot pitch for each
        pilot_pitches = []
        for candidate in pilot_candidates['pilot_candidates']:
            pitch = await self._generate_pilot_pitch(candidate)
            pilot_pitches.append({
                'company': candidate['company'],
                'pitch': pitch,
                'pilot_score': candidate['pilot_score']
            })
            
        return {
            'week': 2,
            'task': 'Pilot Program Setup',
            'pilot_candidates': pilot_pitches,
            'recommended_approach': 'Start with highest scoring candidate'
        }
    
    async def _generate_pilot_pitch(self, candidate: Dict) -> str:
        """Generate pilot program pitch"""
        prompt = f"""
        Create a pilot program pitch for:
        Company: {candidate['company']}
        Signals: {json.dumps(candidate['signals'])}
        
        Use this framework:
        "I'm launching CalmOps to help mid-market creative teams optimize workflows.
        
        Based on [specific observation about their company], I believe we could help you [specific benefit].
        
        I'm looking for 3 strategic partners to pilot the program at $3,000 (normally $8,500).
        
        You get: Full 2-week assessment, detailed recommendations, implementation roadmap
        I get: Real-world testing, case study, and feedback
        
        Interested in being a pilot partner?"
        
        Make it specific to their situation.
        """
        
        pitch = await self.llm.generate(prompt, model="llama3.1:70b")
        return pitch
    
    async def week5_scale_outreach(self, case_study: Dict = None) -> Dict:
        """
        Automate Week 5-6: Scale outreach to 50 companies
        """
        print("Starting Week 5: Scaled Outreach Campaign")
        
        # Get 50 targets across all markets
        all_targets = []
        for market in ['new_york', 'new_jersey', 'south_florida', 'los_angeles']:
            results = await self.search.scale_outreach_targets(market, target_count=15)
            all_targets.extend(results['outreach_targets'])
            
        # Generate outreach sequences
        outreach_sequences = []
        for target in all_targets[:50]:
            sequence = await self._generate_outreach_sequence(target, case_study)
            outreach_sequences.append({
                'company': target['company_name'],
                'contacts': target.get('contacts', []),
                'sequence': sequence
            })
            
        return {
            'week': 5,
            'task': 'Scale Outreach',
            'total_targets': len(outreach_sequences),
            'outreach_sequences': outreach_sequences,
            'expected_response_rate': '30%',
            'expected_meetings': 15
        }
    
    async def _generate_outreach_sequence(self, target: Dict, case_study: Dict = None) -> List[str]:
        """Generate 3-touch outreach sequence"""
        prompt = f"""
        Create a 3-touch outreach sequence for:
        Company: {target['company_name']}
        Sector: {target.get('sector')}
        Market: {target.get('market')}
        
        Touch 1 (LinkedIn): Brief introduction referencing specific company signal
        Touch 2 (Email - 3 days later): Share case study insight
        Touch 3 (LinkedIn - 7 days later): Final value-focused message
        
        {f"Reference this case study: {json.dumps(case_study)}" if case_study else ""}
        
        Keep each message under 75 words. Focus on their potential pain points.
        """
        
        sequence = await self.llm.generate(prompt, model="llama3.1:70b")
        return sequence.split('\n\n')  # Split into 3 messages