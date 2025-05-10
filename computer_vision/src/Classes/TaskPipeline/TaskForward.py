from Task import Task

class TaskForward(Task):
    """
    This class represent a task to drive forward
    """

    def __init__(self, duration:int = 1000):
        """
        :param duration: how long to drive forward in milliseconds, defaults to 1000
        :type duration: int, optional
        """
        self.type:str = "forward"
        self.duration:int = duration
    
    def to_json(self):
        return vars(self)
