import unittest
from unittest.mock import patch

from src.Classes.TaskPipeline.TaskForward import TaskForward
from src.Classes.TaskPipeline.TaskTurn import TaskTurn
import src.Utils.pathfinding as pathfinding


class TestPathfinding(unittest.TestCase):
    def test_get_zumo_direction_moved(self):
        pathfinding.LastZumoPos.data = {
            "xCoord": 1,
            "yCoord": 1,
            "xDirect": 0,
            "yDirect": 0
        }

        zumo_pos = {
            "xCoord": 2,
            "yCoord": 3,
        }

        expected_result = {
            "xCoord": 2,
            "yCoord": 3,
            "xDirect": 1,
            "yDirect": 2
        }
        result = pathfinding.get_zumo_direction(zumo_pos)
        self.assertEqual(pathfinding.LastZumoPos.data.get("xCoord"), zumo_pos.get("xCoord"))
        self.assertEqual(pathfinding.LastZumoPos.data.get("yCoord"), zumo_pos.get("yCoord"))
        self.assertEqual(expected_result, result)

    def test_get_zumo_direction_not_moved(self):
        pathfinding.LastZumoPos.data = {
            "xCoord": 0,
            "yCoord": 0,
            "xDirect": 5,
            "yDirect": 5
        }

        zumo_pos = {
            "xCoord": 0,
            "yCoord": 0,
        }

        expected_result = {
            "xCoord": 0,
            "yCoord": 0,
            "xDirect": 5,
            "yDirect": 5
        }

        result = pathfinding.get_zumo_direction(zumo_pos)
        self.assertEqual(expected_result, result)
        self.assertEqual(pathfinding.LastZumoPos.data.get("xCoord"), zumo_pos.get("xCoord"))
        self.assertEqual(pathfinding.LastZumoPos.data.get("yCoord"), zumo_pos.get("yCoord"))

    def test_get_zumo_direction_init(self):
        pathfinding.LastZumoPos.data = {
            "xCoord": None,
            "yCoord": None,
            "xDirect": None,
            "yDirect": None
        }

        zumo_pos = {
            "xCoord": 0,
            "yCoord": 0,
        }

        expected_result = None
        res = pathfinding.get_zumo_direction(zumo_pos)
        self.assertEqual(expected_result, res)
        self.assertEqual(pathfinding.LastZumoPos.data.get("xCoord"), zumo_pos.get("xCoord"))
        self.assertEqual(pathfinding.LastZumoPos.data.get("yCoord"), zumo_pos.get("yCoord"))

    @patch("src.Utils.pathfinding.get_zumo_direction", return_value=None)
    def test_get_next_task_init_direction(self, mock_get_zumo_direction):
        positions = {
            "zumo": {
                "xCoord": 1,
                "yCoord": 1,
                "dx": 10,
                "dy": 10,
            }}

        expected_result = TaskForward(100)
        res = pathfinding.get_next_task(positions)
        mock_get_zumo_direction.assert_called_with(positions.get("zumo"))
        self.assertEqual(vars(expected_result), vars(res))

    @patch("src.Utils.pathfinding.get_zumo_direction", return_value={
        "xCoord": 1,
        "yCoord": 1,
        "dx": 10,
        "dy": 10,
        "xDirect": 10,
        "yDirect": 10
    })
    def test_get_next_task_init_target(self, mock_get_zumo_direction):
        pathfinding.LastStartPosition.data = {
            "xCoord": None,
            "yCoord": None,
            "xDirect": None,
            "yDirect": None,
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

        expected_result = pathfinding.get_task_for_destination(pathfinding.get_zumo_direction({}),
                                                               pathfinding.get_pushing_pos(positions.get("zumo"), {
                                                                   "xCoord": 50,
                                                                   "yCoord": 50,
                                                               }))
        result = pathfinding.get_next_task(positions)
        mock_get_zumo_direction.assert_called_with(positions.get("zumo"))
        self.assertEqual(vars(expected_result), vars(result))

    @patch("src.Utils.pathfinding.get_zumo_direction", return_value={
        "xCoord": 1,
        "yCoord": 1,
        "dx": 10,
        "dy": 10,
        "xDirect": 10,
        "yDirect": 10
    })
    def test_get_next_task_after_init(self, mock_get_zumo_direction):
        pathfinding.LastStartPosition.data = {
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
        expected_result = pathfinding.get_task_for_destination(pathfinding.get_zumo_direction({}),
                                                               pathfinding.LastStartPosition.data)
        result = pathfinding.get_next_task(positions)
        mock_get_zumo_direction.assert_called_with(positions.get("zumo"))
        self.assertEqual(vars(expected_result), vars(result))

    @patch("src.Utils.pathfinding.get_zumo_direction", return_value={
        "xCoord": 143,
        "yCoord": 343,
        "dx": 10,
        "dy": 10,
        "xDirect": 10,
        "yDirect": 10
    })
    def test_get_next_task_while_pushing(self, mock_get_zumo_direction):
        pathfinding.LastStartPosition.data = {
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

        expected_result = pathfinding.get_task_for_destination(pathfinding.get_zumo_direction({}),
                                                               pathfinding.get_pushing_pos(positions.get("zumo"), {
                                                                   "xCoord": 150,
                                                                   "yCoord": 350,
                                                               }))
        result = pathfinding.get_next_task(positions)
        mock_get_zumo_direction.assert_called_with(positions.get("zumo"))
        self.assertEqual(vars(expected_result), vars(result))

    @patch("src.Utils.pathfinding.get_pushing_pos", return_value={
        "xCoord": 143,
        "yCoord": 343,
        "dx": 10,
        "dy": 10,
        "xDirect": 10,
        "yDirect": 10
    })
    @patch("src.Utils.pathfinding.get_zumo_direction", return_value={
        "xCoord": 143,
        "yCoord": 343,
        "dx": 10,
        "dy": 10,
        "xDirect": 10,
        "yDirect": 10
    })
    def test_get_next_task_while_pushing_on_pushing_pos(self, mock_get_zumo_direction, mock_get_pushing_pos):
        # mock aliases are flipped since patches get stacked
        pathfinding.LastStartPosition.data = {
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

        expected_result = TaskForward()
        result = pathfinding.get_next_task(positions)
        mock_get_zumo_direction.assert_called_with(positions.get("zumo"))
        mock_get_pushing_pos.assert_called_with(pathfinding.get_zumo_direction({}), {
            "xCoord": 150,
            "yCoord": 350,
        })
        self.assertEqual(vars(expected_result), vars(result))

    def test_get_pushing_pos(self):
        zumo_pos = {"dx": 10, "dy": 5}
        object_pos = {"xCoord": 960, "yCoord": 540}
        expected_result = {
            "xDirect": 960,
            "yDirect": 540,
            "xCoord": 950,
            "yCoord": 537.1875
        }
        result = pathfinding.get_pushing_pos(zumo_pos, object_pos)
        self.assertEqual(expected_result, result)

        zumo_pos = {"dx": 20, "dy": 10}
        object_pos = {"xCoord": 1800, "yCoord": 1000}
        expected_result = {
            "xDirect": 120,
            "yDirect": 80,
            "xCoord": 1780,
            "yCoord": 993.3333333333334
        }
        result = pathfinding.get_pushing_pos(zumo_pos, object_pos)
        self.assertEqual(expected_result, result)

    def test_get_task_for_destination_on_destination(self):
        zumo_pos = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirect": 10,
            "yDirect": 20,
        }

        destination = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirect": 1,
            "yDirect": 2,
        }

        expected_result = TaskForward()
        result = pathfinding.get_task_for_destination(zumo_pos, destination)
        self.assertEqual(vars(expected_result), vars(result))

    def test_get_task_for_destination_on_destination_wrong_direction(self):
        zumo_pos = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirect": 10,
            "yDirect": 0,
        }

        destination = {
            "xCoord": 10,
            "yCoord": 20,
            "xDirect": 1,
            "yDirect": 1,
        }

        expected_result = TaskTurn(-45)
        result = pathfinding.get_task_for_destination(zumo_pos, destination)
        self.assertEqual(vars(expected_result), vars(result))

    def test_vector_to_angle(self):
        # down = 0°
        self.assertEqual(0, pathfinding.vector_to_angle(0, 1))
        # up = 180°
        self.assertEqual(180, pathfinding.vector_to_angle(0, -2))
        # right = 90°
        self.assertEqual(90, pathfinding.vector_to_angle(3, 0))
        # left = -90°
        self.assertEqual(-90, pathfinding.vector_to_angle(-4, 0))

    if __name__ == '__main__':
        unittest.main()
