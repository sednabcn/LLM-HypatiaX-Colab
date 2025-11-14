"""Hybrid workflow combining multiple technologies"""
from typing import Dict, Any, List, Optional

class HybridWorkflow:
    """Workflow that combines NER, Transformers, LLM, and Agents"""
    
    def __init__(self):
        self.agents = []
        self.history = []
    
    def add_agent(self, agent):
        """Add agent to workflow"""
        self.agents.append(agent)
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute hybrid workflow"""
        result = {
            'query': query,
            'steps': []
        }
        
        # Execute each agent in sequence
        task = {'query': query}
        for agent in self.agents:
            step_result = agent.execute(task)
            result['steps'].append({
                'agent': agent.name,
                'result': step_result
            })
            # Pass result to next agent
            task.update(step_result)
        
        # Store in history
        self.history.append(result)
        
        return result
    
    def get_history(self, n: int = 10) -> List[Dict]:
        """Get last n executions"""
        return self.history[-n:]
