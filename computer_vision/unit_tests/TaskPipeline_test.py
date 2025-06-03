from MockTask import MockTask
import unittest
from unittest.mock import patch
import os
from src.Classes.ObjectDetection.ObjectDetection import ObjectDetection
from src.Classes.TaskPipeline.TaskForward import TaskForward
from src.Classes.TaskPipeline.TaskPipeline import TaskPipeline
import src.Utils.pathfinding

class TestTaskPipeline(unittest.TestCase):

    def setUp(self):
        if os.path.exists('localDB.pik'):
            os.remove('localDB.pik')

    def tearDown(self):
        if os.path.exists('localDB.pik'):
            os.remove('localDB.pik')

    def test_pipeline_push_and_pop(self):
        pipeline = TaskPipeline()
        task = MockTask("PipelineTask")
        self.assertTrue(pipeline.push_task(task))
        popped = pipeline.pop_task()
        self.assertEqual(task, popped)

    @patch('src.Classes.TaskPipeline.TaskPipeline.get_next_task', return_value=TaskForward())
    @patch.object(ObjectDetection, 'handle_object_detection_from_source', return_value={})
    def test_pipeline_pop_empty(self, mock_od, mock_get_task):
        expected_result = TaskForward()
        pipeline = TaskPipeline()
        result = pipeline.pop_task()
        mock_get_task.assert_called_with({})
        mock_od.assert_called_once()
        self.assertEqual(vars(expected_result), vars(result))

    @patch.object(ObjectDetection, 'handle_object_detection_from_source', return_value=None)
    def test_pipeline_pop_empty_od_fail(self, mock_od):
        pipeline = TaskPipeline()
        result = pipeline.pop_task()
        mock_od.assert_called_once()
        self.assertIsNone(result)