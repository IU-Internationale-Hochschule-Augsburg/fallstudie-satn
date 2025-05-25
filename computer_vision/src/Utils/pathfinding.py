from computer_vision.src.Classes.TaskPipeline.TaskForward import TaskForward
from computer_vision.src.Classes.TaskPipeline.TaskTurn import TaskTurn
import math

last_start_position = None


def get_next_task(positions):
    global last_start_position
    for obj in positions.objects:
        # check if there is an object that is getting pushed by zumo
        if ((obj.xCoord - positions.zumo.xCoord) ** 2) + ((obj.yCoord - positions.zumo.yCoord) ** 2) <= (
                (positions.zumo.xCoord + positions.zumo.xCoord) * .55) ** 2:
            #there is an object very close to zumo
            pushing_dest = get_pushing_dest(positions.zumo, obj)
            if positions.zumo.xCoord == pushing_dest.xCoord and positions.zumo.yCoord == pushing_dest.yCoord and (
                    pushing_dest.xDirec / pushing_dest.yDirec) % (positions.zumo.xDirec / positions.zumo.yDirec) == 0:
                #zumo is on pushing destination
                return TaskForward()
            #zumo is not on pushing destination
            return get_task_for_destination(positions.zumo ,pushing_dest)

    #check if zumo is on last init position
    if last_start_position is None or (positions.zumo.xCoord == last_start_position.xCoord and positions.zumo.yCoord == last_start_position.yCoord and (
            last_start_position.xDirec / last_start_position.yDirec) % (positions.zumo.xDirec / positions.zumo.yDirec) == 0):
        #find obj the farthest away from under right corner
        target = min(positions.objects, key=lambda d: d["xCoord"] + d["yCoord"])
        last_start_position = get_pushing_dest(positions.zumo, target)
    #drive back to last init pos
    return get_task_for_destination(positions.zumo, last_start_position)

def get_pushing_dest(zumo_pos, object_dest):
    pushing_dest = {} #todo: replace with object
    pushing_dest.xDirec = 1920 - object_dest.XCoord
    pushing_dest.yDirec = 1080 - object_dest.YCoord
    pushing_dest.xCoord = object_dest.xCoord - zumo_pos.xVect
    pushing_dest.yCoord = object_dest.yCoord - ((pushing_dest.yDirec / pushing_dest.xDirec) * zumo_pos.yVect)
    return pushing_dest


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
