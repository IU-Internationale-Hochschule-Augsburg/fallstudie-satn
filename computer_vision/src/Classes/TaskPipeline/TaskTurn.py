from Task import Task


class TaskTurn(Task):
    """
    This class represent a task to drive forward
    """

    def __init__(self, angle:float = 90.0):
        """
        :param angle: how far to turn, defaults to 90.0
        :type angle: float, optional
        """
        if angle <= -360 or angle >= 360:
            angle = angle%360
        self.type: str = "turn"
        self.angle: float = angle

    def to_json(self):
        return vars(self)
