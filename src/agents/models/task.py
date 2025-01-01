"""Task model definition"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Task:
    """Represents a task in the system"""
    id: int
    title: str
    status: str = 'pending'
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None