import unittest

from src.Utils.pathfinding import get_task_for_destination, get_pushing_dest, get_next_task, \
    LastStartPosition, LastZumoPos


class TestPathfinding(unittest.TestCase):
    def test_get_next_task_init(self):
        LastZumoPos.data = {
            "xCoord": 1,
            "yCoord": 1,
            "xDirect": 10,
            "yDirect": 10
        }

        LastStartPosition.data = {
            "xCoord": None,
            "yCoord": None,
            "xDirect": None,
            "yDirect": None,
        }
        # globals()["last_start_position"] = None
        positions = {
            "zumo": {
                "xCoord": 1,
                "yCoord": 1,
                "dx": 10,
                "dy": 10,
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
        LastZumoPos.data = {
            "xCoord": 1,
            "yCoord": 1,
            "xDirect": 10,
            "yDirect": 10
        }

        LastStartPosition.data = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirect": 40,
            "yDirect": 40,
        }
        positions = {
            "zumo": {
                "xCoord": 1,
                "yCoord": 1,
                "dx": 10,
                "dy": 10,
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
        LastZumoPos.data = {
            "xCoord": 143,
            "yCoord": 343,
            "xDirect": 10,
            "yDirect": 10
        }

        LastStartPosition.data = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirect": 40,
            "yDirect": 40,
        }
        positions = {
            "zumo": {
                "xCoord": 143,
                "yCoord": 343,
                "dx": 10,
                "dy": 10,
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
