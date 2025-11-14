"""Agent-based expression mapping"""
from typing import Dict, Any, List
from agents.base.agent import BaseAgent

class AgentMapper:
    """Map queries using AI agents"""
    
    def __init__(self, agents: List[BaseAgent] = None):
        self.agents = agents or []
    
    def add_agent(self, agent: BaseAgent):
        """Add agent to mapper"""
        self.agents.append(agent)
    
    def map(self, query: str) -> Dict[str, Any]:
        """Map query using agent workflow"""
        results = []
        current_task = {'query': query}
        
        for agent in self.agents:
            result = agent.execute(current_task)
            results.append({
                'agent': agent.name,
                'output': result
            })
            current_task.update(result)
        
        return {
            'query': query,
            'expression': current_task.get('expression'),
            'method': 'agent',
            'workflow': results
        }
