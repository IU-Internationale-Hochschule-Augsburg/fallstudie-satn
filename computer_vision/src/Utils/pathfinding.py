from computer_vision.src.Classes.TaskPipeline.TaskForward import TaskForward
from computer_vision.src.Classes.TaskPipeline.TaskTurn import TaskTurn
import math


class LastStartPosition:
    data = {
        "xCoord": None,
        "yCoord": None,
        "xDirect": None,
        "yDirect": None
    }

class LastZumoPos:
    data = {
        "xCoord": None,
        "yCoord": None,
        "xDirect": None,
        "yDirect": None
    }

def get_zumo_direction(zumo_pos:dict):
    if LastZumoPos.data.get("xCoord") is None:
        LastZumoPos.data["xCoord"] = zumo_pos.get("xCoord")
        LastZumoPos.data["yCoord"] = zumo_pos.get("yCoord")
        return None
    if zumo_pos.get("xCoord") != LastZumoPos.data.get("xCoord") or zumo_pos.get("yCoord") != LastZumoPos.data.get("yCoord"):
        LastZumoPos.data["xCoord"] = zumo_pos.get("xCoord")
        LastZumoPos.data["yCoord"] = zumo_pos.get("yCoord")
        LastZumoPos.data["xDirect"] = zumo_pos.get("xCoord") - LastZumoPos.data.get("xCoord")
        LastZumoPos.data["yDirect"] = zumo_pos.get("yCoord") - LastZumoPos.data.get("yCoord")
    zumo_pos["xDirect"] = LastZumoPos.data["xDirect"]
    zumo_pos["yDirect"] = LastZumoPos.data["yDirect"]
    return zumo_pos

def get_next_task(positions: dict):
    zumo: dict = positions.get("zumo")
    zumo: dict = get_zumo_direction(zumo)
    if zumo is None:
        return TaskForward(100)
    for obj in positions.get("objects"):
        # check if there is an object that is getting pushed by zumo
        if ((obj.get("xCoord") - zumo.get("xCoord")) ** 2) + ((obj.get("yCoord") - zumo.get("yCoord")) ** 2) <= (
                (zumo.get("dx") + zumo.get("dy")) * .55) ** 2:
            # there is an object very close to zumo
            pushing_dest = get_pushing_dest(zumo, obj)
            if zumo.get("xCoord") == pushing_dest.get("xCoord") and zumo.get("yCoord") == pushing_dest.get(
                    "yCoord") and (
                    abs(vector_to_angle(pushing_dest.get("xDirect"), pushing_dest.get("yDirect"))) - vector_to_angle(
                zumo.get("xDirect"), zumo.get("yDirect"))) <= 2:
                # zumo is on pushing destination
                return TaskForward()
            # zumo is not on pushing destination
            return get_task_for_destination(zumo, pushing_dest)

    # check if zumo is on last init position
    if LastStartPosition.data.get("xCoord") is None or (
            zumo.get("xCoord") == LastStartPosition.data.get("xCoord") and zumo.get(
        "yCoord") == LastStartPosition.data.get("yCoord") and
            abs(vector_to_angle(LastStartPosition.data.get("xDirect"), LastStartPosition.data.get("yDirect")) - vector_to_angle(
                zumo.get("xDirect"), zumo.get("yDirect"))) <= 2):
        # find obj the farthest away from under right corner
        target = min(positions.get("objects"), key=lambda d: d["xCoord"] + d["yCoord"])
        LastStartPosition.data = get_pushing_dest(zumo, target)
    # drive back to last init pos
    return get_task_for_destination(zumo, LastStartPosition.data)


def get_pushing_dest(zumo_pos: dict, object_dest: dict):
    """
    This function returns the position from where the Zumo should push the given object
    :param zumo_pos:
    :param object_dest:
    :return: pushing position
    :rtype: dict
    """
    pushing_dest = {
        "xDirect": 1920 - object_dest.get("xCoord"),
        "yDirect": 1080 - object_dest.get("yCoord"),
        "xCoord": object_dest.get("xCoord") - zumo_pos.get("dx"),
    }
    pushing_dest["yCoord"] = object_dest.get("yCoord") - (
                (pushing_dest.get("yDirect") / pushing_dest.get("xDirect")) * zumo_pos.get("dy"))
    return pushing_dest


def get_task_for_destination(zumo_pos: dict, destination: dict):
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
        if (zumo_pos.get("xDirect") / zumo_pos.get("yDirect")) % (vector_x / vector_y) == 0:
            return TaskForward()
        else:
            LastZumoPos.data["xDirect"] = vector_x
            LastZumoPos.data["yDirect"] = vector_y
            return TaskTurn(
                vector_to_angle(vector_x, vector_y) - vector_to_angle(zumo_pos.get("xDirect"), zumo_pos.get("yDirect"))
            )
    LastZumoPos.data["xDirect"] = destination.get("xDirect")
    LastZumoPos.data["yDirect"] = destination.get("yDirect")
    return TaskTurn(
        vector_to_angle(zumo_pos.get("xDirect"), zumo_pos.get("yDirect")) - vector_to_angle(destination.get("xDirect"),
                                                                                  destination.get("yDirect"))
    )


def vector_to_angle(x, y):
    """
    This function returns the angle of the given vector. 0, 1 is 0°
    :param x:
    :param y:
    :return: angle
    :rtype: float
    """
    angle_rad = math.atan2(x, y)  # x vor y um 0° bei (0,1) zu bekommen
    angle_deg = math.degrees(angle_rad)
    return angle_deg
