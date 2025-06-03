from src.Classes.TaskPipeline.TaskForward import TaskForward
from src.Classes.TaskPipeline.TaskTurn import TaskTurn
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


def get_zumo_direction(zumo_pos: dict):
    """
    Gets direction of Zumo based on last and current position

    :param zumo_pos: zumo position data
    :return: zumo position data including direction
    :rtype: dict
    """
    if LastZumoPos.data.get("xCoord") is None:
        LastZumoPos.data["xCoord"] = zumo_pos.get("xCoord")
        LastZumoPos.data["yCoord"] = zumo_pos.get("yCoord")
        return None
    if zumo_pos.get("xCoord") != LastZumoPos.data.get("xCoord") or zumo_pos.get("yCoord") != LastZumoPos.data.get(
            "yCoord"):
        LastZumoPos.data["xDirect"] = zumo_pos.get("xCoord") - LastZumoPos.data.get("xCoord")
        LastZumoPos.data["yDirect"] = zumo_pos.get("yCoord") - LastZumoPos.data.get("yCoord")
        LastZumoPos.data["xCoord"] = zumo_pos.get("xCoord")
        LastZumoPos.data["yCoord"] = zumo_pos.get("yCoord")
    elif LastZumoPos.data.get("xDirect") is None:
        return None
    zumo_pos["xDirect"] = LastZumoPos.data.get("xDirect")
    zumo_pos["yDirect"] = LastZumoPos.data.get("yDirect")
    return zumo_pos


def get_next_task(positions: dict):
    """
    Returns the next task for the Zumo based on the given positions.

    :param positions:
    :return:
    """
    zumo: dict = positions.get("zumo")
    zumo: dict = get_zumo_direction(zumo)
    if zumo is None:
        return TaskForward(100)
    for obj in positions.get("objects"):
        # check if there is an object that is getting pushed by zumo
        if ((obj.get("xCoord") - zumo.get("xCoord")) ** 2) + ((obj.get("yCoord") - zumo.get("yCoord")) ** 2) <= (
                (zumo.get("dx") + zumo.get("dy")) * .55) ** 2:
            # there is an object very close to zumo
            pushing_dest = get_pushing_pos(zumo, obj)
            if (math.isclose(zumo.get("xCoord"), pushing_dest.get("xCoord"), abs_tol=2)
                    and math.isclose(zumo.get("yCoord"), pushing_dest.get("yCoord"), abs_tol=2)
                    and math.isclose(vector_to_angle(pushing_dest.get("xDirect"), pushing_dest.get("yDirect")),
                                     vector_to_angle(zumo.get("xDirect"), zumo.get("yDirect")), abs_tol=2)):
                # zumo is on pushing destination
                print("Pushing Forward")
                return TaskForward()
            # zumo is not on pushing destination
            print("Aimed Destination: ", LastStartPosition.data)
            return get_task_for_destination(zumo, pushing_dest)

    # check if zumo is on last init position
    if LastStartPosition.data.get("xCoord") is None or (
            zumo.get("xCoord") == LastStartPosition.data.get("xCoord") and zumo.get(
        "yCoord") == LastStartPosition.data.get("yCoord") and
            abs(vector_to_angle(LastStartPosition.data.get("xDirect"),
                                LastStartPosition.data.get("yDirect")) - vector_to_angle(
                zumo.get("xDirect"), zumo.get("yDirect"))) <= 2):
        # find obj the farthest away from under right corner
        target: dict = min(positions.get("objects"), key=lambda d: d["xCoord"] + d["yCoord"])
        LastStartPosition.data = get_pushing_pos(zumo, target)
    # drive back to last init pos
    print("Aimed Destination: ", LastStartPosition.data)
    return get_task_for_destination(zumo, LastStartPosition.data)


def get_pushing_pos(zumo_pos: dict, object_pos: dict):
    """
    Returns the position from where the Zumo should push the given object

    :param zumo_pos:
    :param object_pos:
    :return: pushing position
    :rtype: dict
    """
    pushing_dest: dict = {
        "xDirect": 1920 - object_pos.get("xCoord"),
        "yDirect": 1080 - object_pos.get("yCoord"),
        "xCoord": object_pos.get("xCoord") - zumo_pos.get("dx"),
    }
    pushing_dest["yCoord"] = object_pos.get("yCoord") - (
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
    # Check if position is the same
    if zumo_pos.get("xCoord") == destination.get("xCoord") and zumo_pos.get("yCoord") == destination.get("yCoord"):
        # We are already at the destination, check if orientation matches
        vector_x = destination.get("xDirect")
        vector_y = destination.get("yDirect")
        current_angle = vector_to_angle(zumo_pos.get("xDirect"), zumo_pos.get("yDirect"))
        desired_angle = vector_to_angle(vector_x, vector_y)

        if math.isclose(current_angle, desired_angle, abs_tol=1e-3):
            return TaskForward()  # Already aligned
        else:
            LastZumoPos.data["xDirect"] = vector_x
            LastZumoPos.data["yDirect"] = vector_y
            return TaskTurn(desired_angle - current_angle)

    # Not at destination, need to turn toward movement vector
    vector_x = destination.get("xCoord") - zumo_pos.get("xCoord")
    vector_y = destination.get("yCoord") - zumo_pos.get("yCoord")

    desired_angle = vector_to_angle(vector_x, vector_y)
    current_angle = vector_to_angle(zumo_pos.get("xDirect"), zumo_pos.get("yDirect"))

    if math.isclose(current_angle, desired_angle, abs_tol=2):
        return TaskForward()

    angle_diff = desired_angle - current_angle
    LastZumoPos.data["xDirect"] = vector_x
    LastZumoPos.data["yDirect"] = vector_y

    return TaskTurn(angle_diff)


def vector_to_angle(x: int, y: int):
    """
    This function returns the angle of the given vector. 0, 1 is 0°

    :param x:
    :param y:
    :return: angle
    :rtype: float
    """
    angle_rad: float = math.atan2(x, y)
    angle_deg: float = math.degrees(angle_rad)
    return angle_deg
