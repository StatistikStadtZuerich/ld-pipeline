import os
import shutil
import unittest
from pipeline import Copy, Env
from pipeline.base import Environment


class TestCopy(unittest.TestCase):

    @staticmethod
    def __abs_path(rel_path):
        return os.path.join(os.path.dirname(__file__), rel_path)

    def test_simple_copy(self):
        tmp_dir = TestCopy.__abs_path('tmp')
        os.mkdir(tmp_dir)

        try:
            input_file = self.__abs_path('data/copy-text.txt')
            output_file = self.__abs_path('tmp/copy-target.txt')

            copy = Copy(input_file, output_file)
            copy.run(Environment(Env.test))

            content = open(output_file, 'r').read()
            self.assertEqual(content, 'Hello World\n')

        finally:
            shutil.rmtree(tmp_dir)

