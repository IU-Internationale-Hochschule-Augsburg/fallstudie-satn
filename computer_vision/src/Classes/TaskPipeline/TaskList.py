from src.Classes.TaskPipeline.Task import Task
import pickle

class TaskList():
    """
    A persistent stack of Task objects, saved and loaded from a local pickle database.
    """

    def __init__(self):
        # Internal list to hold Task instances in memory
        self.stack = []

    def push_task(self, task: Task) -> bool:
        """
        Push a Task onto the stack and save the updated stack to persistence.

        :param task: An object implementing the Task interface
        :return: True if push succeeded, False on any exception
        """
        # Ensure the internal stack is loaded from disk before modification
        self.init_stack()
        try:
            self.stack.append(task)
        except Exception:
            # If appending fails, return False to indicate error
            return False
        # Persist the modified stack to disk
        self.save_stack()
        return True

    def pop_task(self) -> Task:
        """
        Pop and return the most recently added Task, saving the new state.

        :return: The last Task in the stack, or None if stack is empty
        """
        # Load the current stack state from disk
        self.init_stack()
        if len(self.stack) > 0:
            # Remove last task from list
            task = self.stack.pop()
            # Save the updated stack back to disk
            self.save_stack()
            return task
        # If there are no tasks, return None
        return None

    def init_stack(self):
        """
        Initialize the in-memory stack from the persisted pickle file.
        If the file does not exist or is empty, resets to an empty list.
        """
        try:
            with open('localDB.pik', 'rb') as dbfile:
                # Load the pickled stack into memory
                loaded = pickle.load(dbfile)
                if isinstance(loaded, list):
                    self.stack = loaded
                else:
                    # Fallback if data is in unexpected format
                    self.stack = []
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            # No valid data on disk—start with an empty stack
            self.stack = []

    def save_stack(self):
        """
        Persist the current in-memory stack to the pickle file.
        Overwrites the existing file to reflect the latest state.
        """
        with open('localDB.pik', 'wb') as dbfile:
            # Dump the entire stack in binary format
            pickle.dump(self.stack, dbfile)