from src.Classes.TaskPipeline.Task import Task
from src.Classes.TaskPipeline.TaskList import TaskList

class TaskPipeline():
    """
    High-level manager for a sequence of Tasks, delegating storage responsibilities to TaskList.
    """
    def __init__(self):
        # Create a new TaskList to hold and persist tasks
        self.taskList = TaskList()
    
    def push_task(self, task: Task) -> bool:
        """
        Add a new task to the pipeline.

        :param task: A Task object to enqueue
        :return: True if enqueued successfully, False otherwise
        """
        return self.taskList.push_task(task)

    def pop_task(self) -> Task:
        """
        Retrieve and remove the most recent task from the pipeline.

        :return: The dequeued Task, or None if none exist
        """
        return self.taskList.pop_task()