from computer_vision.src.Classes.TaskPipeline.TaskForward import TaskForward
from computer_vision.src.Classes.TaskPipeline.TaskTurn import TaskTurn
import math

class LastStartPosition:
    data = {
        "xCoord": None,
        "yCoord": None,
        "xDirec": None,
        "yDirec": None
    }

def get_next_task(positions: dict):
    zumo:dict = positions.get("zumo")
    for obj in positions.get("objects"):
        # check if there is an object that is getting pushed by zumo
        if ((obj.get("xCoord") - zumo.get("xCoord")) ** 2) + ((obj.get("yCoord") - zumo.get("yCoord")) ** 2) <= (
                (zumo.get("xCoord") + zumo.get("xCoord")) * .55) ** 2:
            # there is an object very close to zumo
            pushing_dest = get_pushing_dest(zumo, obj)
            if zumo.get("xCoord") == pushing_dest.get("xCoord") and zumo.get("yCoord") == pushing_dest.get("yCoord") and (
                    abs(vector_to_angle(pushing_dest.get("xDirec"), pushing_dest.get("yDirec"))) - vector_to_angle(zumo.get("xDirec"), zumo.get("yDirec"))) <= 2:
                # zumo is on pushing destination
                return TaskForward()
            # zumo is not on pushing destination
            return get_task_for_destination(zumo, pushing_dest)

    # check if zumo is on last init position
    if LastStartPosition.data.get("xCoord") is None or (
            zumo.get("xCoord") == LastStartPosition.data.get("xCoord") and zumo.get("yCoord") == LastStartPosition.data.get("yCoord") and
            abs(vector_to_angle(LastStartPosition.data.get("xDirec"),LastStartPosition.data.get("yDirec")) - vector_to_angle(zumo.get("xDirec"), zumo.get("yDirec"))) <= 2):
        # find obj the farthest away from under right corner
        target = min(positions.get("objects"), key=lambda d: d["xCoord"] + d["yCoord"])
        LastStartPosition.data = get_pushing_dest(zumo, target)
    # drive back to last init pos
    return get_task_for_destination(zumo, LastStartPosition.data)


def get_pushing_dest(zumo_pos: dict, object_dest: dict):
    pushing_dest = {
        "xDirec": 1920 - object_dest.get("xCoord"),
        "yDirec": 1080 - object_dest.get("yCoord"),
        "xCoord": object_dest.get("xCoord") - zumo_pos.get("xDirec"),
    }
    pushing_dest["yCoord"] = object_dest.get("yCoord") - ((pushing_dest.get("yDirec") / pushing_dest.get("xDirec")) * zumo_pos.get("yDirec"))
    return pushing_dest


def get_task_for_destination(zumo_pos:dict, destination:dict):
    """
    This function returns the next task to drive from the given position of the Zumo to the destination.
    :param zumo_pos: Position of the Zumo
    :param destination: The destination position
    :return: Task to do next
    :rtype: Task
    """
    if zumo_pos.get("xCoord") == destination.get("xCoord") and destination.get("yCoord") == destination.get("yCoord"):
        vector_x = destination.get("xCoord") - zumo_pos.get("xCoord")
        vector_y = destination.get("yCoord") - zumo_pos.get("yCoord")
        if (zumo_pos.get("xDirec") / zumo_pos.get("yDirec")) % (vector_x / vector_y) == 0:
            return TaskForward()
        else:
            return TaskTurn(
                vector_to_angle(vector_x, vector_y) - vector_to_angle(zumo_pos.get("xDirec"), zumo_pos.get("yDirec"))
            )
    return TaskTurn(
        vector_to_angle(zumo_pos.get("xDirec"), zumo_pos.get("yDirec")) - vector_to_angle(destination.get("xDirec"), destination.get("yDirec"))
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
