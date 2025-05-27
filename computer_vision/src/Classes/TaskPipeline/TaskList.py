from src.Classes.TaskPipeline.Task import Task
import pickle
from collections import deque

class TaskList():
    """
    A persistent stack of Task objects, saved and loaded from a local pickle database.
    """

    def __init__(self):
        # Internal list to hold Task instances in memory
        self.stack = deque()

    def push_task(self, task: Task) -> bool:
        """
        Push a Task onto the stack and save the updated stack to persistence.

        :param task: An object implementing the Task interface
        :return: True if push succeeded, False on any exception
        """
        # Ensure the internal stack is loaded from disk before modification
        self.init_pipeline()
        try:
            self.stack.append(task)
        except Exception:
            # If appending fails, return False to indicate error
            return False
        # Persist the modified stack to disk
        self.save_pipeline()
        return True

    def pop_task(self) -> Task:
        """
        Pop and return the most recently added Task, saving the new state.

        :return: The last Task in the stack, or None if stack is empty
        """
        # Load the current stack state from disk
        self.init_pipeline()
        if len(self.stack) > 0:
            # Remove last task from list
            task = self.stack.popleft()
            # Save the updated stack back to disk
            self.save_pipeline()
            return task
        # If there are no tasks, return None
        return None

    def init_pipeline(self):
        """
        Initialize the in-memory stack from the persisted pickle file.
        If the file does not exist or is empty, resets to an empty list.
        """
        try:
            with open('./localDB.pik', 'rb') as dbfile:
                loaded = pickle.load(dbfile)
                if isinstance(loaded, list):
                    self.stack = deque(loaded)  
                elif isinstance(loaded, deque):
                    self.stack = loaded
                else:
                    self.stack = deque()
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            self.stack = deque()

    def save_pipeline(self):
        """
        Persist the current in-memory stack to the pickle file.
        Overwrites the existing file to reflect the latest state.
        """
        with open('./localDB.pik', 'wb') as dbfile:
            # Dump the entire stack in binary format
            pickle.dump(self.stack, dbfile)