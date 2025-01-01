"""Task management agent"""
from datetime import datetime
from .base_agent import BaseAgent
from .models.task import Task

class TaskAgent(BaseAgent):
    """Agent responsible for task management"""
    
    def __init__(self):
        super().__init__()
        self.tasks = []
    
    def handle_create_task(self, message):
        """Handle task creation"""
        task = Task(
            id=len(self.tasks) + 1,
            title=message.get('title')
        )
        self.tasks.append(task)
        return {'status': 'success', 'task': vars(task)}
    
    def handle_list_tasks(self, _):
        """Return list of all tasks"""
        return {'tasks': [vars(task) for task in self.tasks]}
    
    def handle_update_task(self, message):
        """Update task status"""
        task_id = message.get('task_id')
        new_status = message.get('status')
        
        for task in self.tasks:
            if task.id == task_id:
                task.status = new_status
                if new_status == 'completed':
                    task.completed_at = datetime.now()
                return {'status': 'success', 'task': vars(task)}
        
        return {'error': 'Task not found'}