from pykka import ActorRegistry
from .task_agent import TaskAgent
from .monitor_agent import MonitorAgent

class AgentCoordinator:
    """Coordinates communication between agents"""
    
    def __init__(self):
        self.task_agent = TaskAgent.start()
        self.monitor_agent = MonitorAgent.start()
    
    def create_task(self, title):
        """Create a new task"""
        return self.task_agent.ask({
            'type': 'create_task',
            'title': title
        })
    
    def list_tasks(self):
        """Get all tasks"""
        return self.task_agent.ask({
            'type': 'list_tasks'
        })
    
    def start_monitoring(self):
        """Start system monitoring"""
        return self.monitor_agent.ask({
            'type': 'start_monitoring'
        })
    
    def get_metrics(self):
        """Get current metrics"""
        return self.monitor_agent.ask({
            'type': 'get_metrics'
        })
    
    def shutdown(self):
        """Shutdown all agents"""
        ActorRegistry.stop_all()