import unittest

from computer_vision.src.Utils.pathfinding import get_task_for_destination, get_pushing_dest, get_next_task, \
    LastStartPosition


class TestPathfinding(unittest.TestCase):
    def test_get_next_task_init(self):
        global last_start_position
        LastStartPosition.data = {
            "xCoord": None,
            "yCoord": None,
            "xDirec": None,
            "yDirec": None,
        }
        # globals()["last_start_position"] = None
        positions = {
            "zumo": {
                "xCoord": 1,
                "yCoord": 1,
                "xDirec": 10,
                "yDirec": 10,
            },
            "objects": [
                {
                    "xCoord": 450,
                    "yCoord": 50,
                },
                {
                    "xCoord": 50,
                    "yCoord": 50,
                }, {
                    "xCoord": 150,
                    "yCoord": 350,
                }
            ]
        }
        resp1 = get_next_task(positions)
        resp2 = get_task_for_destination(positions.get("zumo"), get_pushing_dest(positions.get("zumo"), {
            "xCoord": 50,
            "yCoord": 50,
        }))
        self.assertTrue(vars(resp1) == vars(resp2))

    def test_get_next_task_after_init(self):
        LastStartPosition.data = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirec": 40,
            "yDirec": 40,
        }
        positions = {
            "zumo": {
                "xCoord": 1,
                "yCoord": 1,
                "xDirec": 10,
                "yDirec": 10,
            },
            "objects": [
                {
                    "xCoord": 450,
                    "yCoord": 50,
                },
                {
                    "xCoord": 50,
                    "yCoord": 50,
                }, {
                    "xCoord": 150,
                    "yCoord": 350,
                }
            ]
        }
        resp1 = get_next_task(positions)
        resp2 = get_task_for_destination(positions.get("zumo"), LastStartPosition.data)
        self.assertTrue(vars(resp1) == vars(resp2))

    def test_get_next_task_while_pushing(self):
        LastStartPosition.data = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirec": 40,
            "yDirec": 40,
        }
        positions = {
            "zumo": {
                "xCoord": 143,
                "yCoord": 343,
                "xDirec": 10,
                "yDirec": 10,
            },
            "objects": [
                {
                    "xCoord": 450,
                    "yCoord": 50,
                },
                {
                    "xCoord": 60,
                    "yCoord": 60,
                }, {
                    "xCoord": 150,
                    "yCoord": 350,
                }
            ]
        }
        resp1 = get_next_task(positions)
        resp2 = get_task_for_destination(positions.get("zumo"), get_pushing_dest(positions.get("zumo"), {
            "xCoord": 150,
            "yCoord": 350,
        }))
        self.assertTrue(vars(resp1) == vars(resp2))

    if __name__ == '__main__':
        unittest.main()
