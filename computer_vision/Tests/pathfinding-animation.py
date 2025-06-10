import copy
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from src.Classes.TaskPipeline.Task import Task
from src.Classes.TaskPipeline.TaskForward import TaskForward
from src.Classes.TaskPipeline.TaskTurn import TaskTurn
from src.Utils.pathfinding import get_next_task

positions = {
    "zumo": {
        "xCoord": 1,
        "yCoord": 1,
        "dx": 10,
        "dy": 10,
        "xDirect": 1,
        "yDirect": 0
    },
    "objects": [
        {
            "xCoord": 450,
            "yCoord": 50,
        }, {
            "xCoord": 50,
            "yCoord": 50,
        }, {
            "xCoord": 150,
            "yCoord": 350,
        }, {
            "xCoord": 1150,
            "yCoord": 350,
        }, {
            "xCoord": 500,
            "yCoord": 800,
        }, {
            "xCoord": 150,
            "yCoord": 800,
        }
    ]
}


def update_positions(positions: dict, task: Task):
    if type(task) == TaskForward:
        # Calculate the length of the direction vector
        zumo = positions.get("zumo")
        length = math.hypot(zumo.get("xDirect"), zumo.get("yDirect"))
        if length == 0:
            raise ValueError("Direction vector cannot be zero.")
        # Normalize the direction vector
        unit_x = zumo.get("xDirect") / length
        unit_y = zumo.get("yDirect") / length

        # Scale by distance
        delta_x = unit_x * task.duration
        delta_y = unit_y * task.duration

        # Compute pushed objects
        updated_objects = []
        for obj in positions.get("objects"):
            if math.isclose(obj.get("xCoord") - zumo.get('dx'), zumo.get("xCoord"), abs_tol=10,
                            rel_tol=0) and math.isclose(
                obj.get("yCoord") - zumo.get('dy'), zumo.get("yCoord"), abs_tol=10):
                obj["xCoord"] = obj.get("xCoord") + delta_x
                obj["yCoord"] = obj.get("yCoord") + delta_y

            # Keep only objects within the allowed bounds
            if obj.get("xCoord") <= 1920 and obj.get("yCoord") <= 1080:
                updated_objects.append(obj)

            # Update the original list
            positions["objects"] = updated_objects

        # Compute new position
        if zumo.get("xCoord") + delta_x > 1920 - zumo.get("dx"):
            positions["zumo"]["yCoord"] = 1920 - zumo.get("dx") - zumo.get("xCoord") * unit_y
            positions["zumo"]["xCoord"] = 1920 - zumo.get("dx")
        elif zumo.get("yCoord") + delta_y > 1080 - zumo.get("dy"):
            positions["zumo"]["xCoord"] = 1080 - zumo.get("dy") - zumo.get("yCoord") * unit_x
            positions["zumo"]["yCoord"] = 1080 - zumo.get("dy")
        else:
            positions["zumo"]["xCoord"] = zumo.get("xCoord") + delta_x
            positions["zumo"]["yCoord"] = zumo.get("yCoord") + delta_y

    if type(task) == TaskTurn:
        angle_rad = math.radians(task.angle)
        positions["zumo"]["xDirect"] = math.sin(angle_rad)
        positions["zumo"]["yDirect"] = math.cos(angle_rad)

    return positions


def animate_positions(data_sequence, interval=1000, save_path=None):
    """
    Creates and optionally saves an animation of Zumo's position and direction over time.

    Parameters:
        data_sequence (list): List of data snapshots, each a dict with keys "zumo" and "objects".
        interval (int): Delay between frames in milliseconds.
        save_path (str): Optional path to save the animation (e.g., "animation.mp4" or "pathfinding.gif").
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.xlim(0, 1920)
    plt.ylim(0, 1080)
    ax.set_aspect('equal', adjustable='box')

    # Draw border
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(2)
        spine.set_color('black')

    zumo_dot, = ax.plot([], [], 'bo', markersize=10)
    objects_dots, = ax.plot([], [], 'ro', linestyle='', markersize=10)

    def init():
        return zumo_dot, objects_dots

    def update(frame_data):
        for patch in list(ax.patches):
            patch.remove()

        zumo = frame_data["zumo"]
        zumo_x, zumo_y = zumo["xCoord"], zumo["yCoord"]
        dir_x, dir_y = zumo["xDirect"], zumo["yDirect"]

        # Normalize direction vector
        norm = math.hypot(dir_x, dir_y)
        if norm != 0:
            dir_x /= norm
            dir_y /= norm

        arrow_length = 100
        arrow = plt.Arrow(zumo_x, zumo_y,
                          dir_x * arrow_length,
                          dir_y * arrow_length,
                          width=30, color='blue')
        ax.add_patch(arrow)

        zumo_dot.set_data([zumo_x], [zumo_y])

        obj_x = [obj["xCoord"] for obj in frame_data["objects"]]
        obj_y = [obj["yCoord"] for obj in frame_data["objects"]]
        objects_dots.set_data(obj_x, obj_y)

        return zumo_dot, objects_dots, arrow

    ani = animation.FuncAnimation(
        fig, update,
        frames=data_sequence,
        init_func=init,
        blit=False,
        interval=interval
    )

    if save_path:
        if save_path.endswith(".gif"):
            ani.save(save_path, writer="imagemagick", fps=1000 // interval)
        else:
            ani.save(save_path, fps=1000 // interval)
    else:
        plt.show()


seq = []
for i in range(50):
    task = get_next_task(positions)
    print(i, vars(task))
    positions = update_positions(positions, task)
    print(positions)
    seq.append(copy.deepcopy(positions))

print(seq)
animate_positions(seq, save_path="../../Projekt Management/Presentation/pathfinding/pathfinding.gif")
