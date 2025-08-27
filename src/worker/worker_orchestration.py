def handle_orchestrated_task(task: dict) -> str:
    """Handle multi-step orchestrated tasks"""
    
    intent = task.get("intent", "")
    
    # Check if this is a business task that needs orchestration
    if intent in ["validate_prospects", "create_assessment_framework", "daily_business_ops"]:
        
        outputs = []
        subtasks = TASK_TEMPLATES.get(intent, {}).get("subtasks", [])
        
        for subtask in subtasks:
            model = pick_model(subtask["intent"], ROUTING)
            
            # Build context with previous outputs
            context_prompt = ""
            if outputs:
                context_prompt = f"\nPrevious step output:\n{outputs[-1]}\n"
            
            prompt = f"""{system_prompt()}
{context_prompt}
Task: {subtask['instruction']}

Provide specific, actionable output.
"""
            
            result = call_ollama(model, prompt)
            outputs.append(result)
            
            # Save intermediate results
            save_artifact(result, f"{intent}_step_{len(outputs)}")
        
        # Combine all outputs into final artifact
        final_output = "\n\n---\n\n".join(outputs)
        return final_output
    
    # Fall back to regular processing
    return None
