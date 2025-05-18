from MockTask import MockTask
from src.Classes.TaskPipeline.TaskList import TaskList
import unittest
import os

class TestTaskList(unittest.TestCase):

    def setUp(self):
        if os.path.exists('localDB.pik'):
            os.remove('localDB.pik')

    def tearDown(self):
        if os.path.exists('localDB.pik'):
            os.remove('localDB.pik')

    def test_push_and_pop_task(self):
        task_list = TaskList()
        task = MockTask("Task1")
        self.assertTrue(task_list.push_task(task))
        popped = task_list.pop_task()
        self.assertEqual(task, popped)

    def test_pop_from_empty_stack(self):
        task_list = TaskList()
        popped = task_list.pop_task()
        self.assertIsNone(popped)

    def test_persistence(self):
        task_list = TaskList()
        task = MockTask("PersistentTask")
        task_list.push_task(task)

        new_task_list = TaskList()
        new_task_list.init_pipeline()
        self.assertEqual(new_task_list.pop_task(), task)