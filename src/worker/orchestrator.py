#!/usr/bin/env python3
# orchestrator.py - breaks down complex business tasks

import json
import yaml
from typing import List, Dict

TASK_TEMPLATES = {
    "validate_prospects": {
        "subtasks": [
            {
                "model": "phi3:medium",
                "intent": "research",
                "instruction": "identify 10 companies with 50-200 employees in creative/marketing space. return as structured list with company name, employee count, and industry"
            },
            {
                "model": "mistral:latest", 
                "intent": "research",
                "instruction": "for each company found, research their creative team structure and identify the creative director or marketing ops lead. include linkedin urls if possible"
            },
            {
                "model": "mistral:latest",
                "intent": "outreach",
                "instruction": "write personalized linkedin outreach for each decision maker. mention specific company detail. ask about workflow challenges. keep under 150 words"
            },
            {
                "model": "llama3.1:70b-instruct-q4_K_M",
                "intent": "plan",
                "instruction": "create tracking spreadsheet template with columns: company, contact, message sent, response, pain points, budget indicator, next step"
            }
        ]
    },
    
    "create_assessment_framework": {
        "subtasks": [
            {
                "model": "llama3.1:70b-instruct-q4_K_M",
                "intent": "plan", 
                "instruction": "design 15-question diagnostic survey for creative teams. focus on workflow bottlenecks, tool usage, collaboration issues"
            },
            {
                "model": "mistral:latest",
                "intent": "build",
                "instruction": "create workflow mapping template with stages: ideation, creation, review, revision, approval, distribution"
            },
            {
                "model": "llama3.1:70b-instruct-q4_K_M",
                "intent": "plan",
                "instruction": "draft sample recommendations report template with sections: executive summary, current state, gaps identified, recommendations, implementation roadmap"
            }
        ]
    },
    
    "daily_business_ops": {
        "subtasks": [
            {
                "model": "phi3:medium",
                "intent": "research",
                "instruction": "check all recent artifacts for responses or feedback that need processing"
            },
            {
                "model": "mistral:latest",
                "intent": "outreach",
                "instruction": "generate 5 new prospect outreach messages based on successful templates"
            },
            {
                "model": "llama3.1:70b-instruct-q4_K_M",
                "intent": "plan",
                "instruction": "create today's priority list based on business goals and pending tasks"
            }
        ]
    }
}

def decompose_task(high_level_task: str) -> List[Dict]:
    """Break down high-level business task into model-specific subtasks"""
    
    if high_level_task in TASK_TEMPLATES:
        return TASK_TEMPLATES[high_level_task]["subtasks"]
    
    # Default decomposition for unknown tasks
    return [
        {
            "model": "llama3.1:70b-instruct-q4_K_M",
            "intent": "plan",
            "instruction": f"break down this task into 3-5 specific steps: {high_level_task}"
        }
    ]

def execute_orchestrated_task(task_name: str, context: dict = None) -> dict:
    """Execute all subtasks and collect results"""
    
    subtasks = decompose_task(task_name)
    results = {}
    previous_outputs = []
    
    for i, subtask in enumerate(subtasks):
        # Add context from previous steps
        enhanced_instruction = subtask["instruction"]
        if previous_outputs:
            enhanced_instruction += f"\n\nContext from previous steps:\n{json.dumps(previous_outputs[-1], indent=2)}"
        
        # This is where you'd call your ollama model
        # For now, we'll just structure it
        results[f"step_{i+1}"] = {
            "model": subtask["model"],
            "intent": subtask["intent"],
            "instruction": enhanced_instruction,
            "status": "queued"
        }
        
        # In real implementation, this would be the model output
        previous_outputs.append(f"Output from step {i+1}")
    
    return results

if __name__ == "__main__":
    # Test the orchestrator
    result = execute_orchestrated_task("validate_prospects")
    print(json.dumps(result, indent=2))
