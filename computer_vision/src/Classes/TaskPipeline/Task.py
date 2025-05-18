from abc import ABC, abstractmethod

class Task(ABC):
    """
    Abstract base class defining the interface for all Task implementations.
    Concrete subclasses must implement the to_json method.
    """

    @abstractmethod
    def to_json(self) -> dict:
        """
        Serialize the Task instance into a JSON-compatible dictionary.

        :return: A dict representing the object's state
        """
        return vars(self)