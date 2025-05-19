from src.Classes.TaskPipeline.Task import Task

class MockTask(Task):
    def __init__(self, name):
        self.name = name

    def to_json(self):
        return {"name": self.name}

    def __eq__(self, other):
        return isinstance(other, MockTask) and self.name == other.name