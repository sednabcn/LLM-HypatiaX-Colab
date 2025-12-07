"""Base agent class"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, name: str, role: str, tools: Optional[List] = None):
        self.name = name
        self.role = role
        self.tools = tools or []
        self.memory = []
        self.created_at = datetime.now()

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Any:
        """Execute agent task"""
        pass

    def remember(self, item: Any):
        """Store item in agent memory"""
        self.memory.append({"timestamp": datetime.now().isoformat(), "content": item})

    def recall(self, n: int = 10) -> List:
        """Recall last n items from memory"""
        return self.memory[-n:]

    def clear_memory(self):
        """Clear agent memory"""
        self.memory = []

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', role='{self.role}')"
