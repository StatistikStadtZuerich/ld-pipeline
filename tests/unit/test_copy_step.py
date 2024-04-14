import os
import shutil
import unittest
from unittest.mock import MagicMock
from pipeline import Copy, Env
from pipeline.base import Environment


class TestCopy(unittest.TestCase):

    @staticmethod
    def __abs_path(rel_path):
        return os.path.join(os.path.dirname(__file__), rel_path)

    def test_simple_copy(self):
        tmp_dir = TestCopy.__abs_path('tmp')
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        env.get_config_value = MagicMock(return_value=self.__abs_path('tmp') + '/')

        try:
            input_file = TestCopy.__abs_path('data/copy-text.txt')
            output_file = 'copy-target.txt'

            copy = Copy(input_file, output_file)
            copy.run(env)

            with open(TestCopy.__abs_path('tmp/' + output_file), 'r') as file:
                content = file.read()
            self.assertEqual(content, 'Hello World\n')

        finally:
            shutil.rmtree(tmp_dir)

if __name__ == '__main__':
    unittest.main()
