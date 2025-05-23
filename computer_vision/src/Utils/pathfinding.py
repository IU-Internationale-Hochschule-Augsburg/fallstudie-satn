from computer_vision.src.Classes.TaskPipeline.TaskForward import TaskForward
from computer_vision.src.Classes.TaskPipeline.TaskTurn import TaskTurn
import math


def get_next_task(positions):
    pass


def get_task_for_destination(zumo_pos, destination):
    """
    This function returns the next task to drive from the given position of the Zumo to the destination.
    :param zumo_pos: Position of the Zumo
    :param destination: The destination position
    :return: Task to do next
    :rtype: Task
    """
    if zumo_pos.xCoord == destination.xCoord and destination.yCoord == destination.yCoord:
        vector_x = destination.xCoord - zumo_pos.xCoord
        vector_y = destination.yCoord - zumo_pos.yCoord
        if (zumo_pos.xDirec / zumo_pos.yDirec) % (vector_x / vector_y) == 0:
            return TaskForward()
        else:
            return TaskTurn(
                vector_to_angle(vector_x, vector_y) - vector_to_angle(zumo_pos.xDirec, zumo_pos.yDirec)
            )
    return TaskTurn(
        vector_to_angle(zumo_pos.xDirec, zumo_pos.yDirec) - vector_to_angle(destination.xDirec, destination.yDirec)
    )


def vector_to_angle(x, y):
    angle_rad = math.atan2(x, y)  # x vor y um 0° bei (0,1) zu bekommen
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg

# TODO:
#   - direc format (Winkel oder Vektor)
#   - object id possible?
