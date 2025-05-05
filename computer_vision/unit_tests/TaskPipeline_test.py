from MockTask import MockTask
import unittest
import os
from src.Classes.TaskPipeline.TaskPipeline import TaskPipeline

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

    def test_pipeline_pop_empty(self):
        pipeline = TaskPipeline()
        self.assertIsNone(pipeline.pop_task())