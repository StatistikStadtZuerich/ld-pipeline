import shutil
from ..base import Step, Environment


class Copy(Step):
    """
    The Copy step reads the source file and writes its contents to the destination file,
    creating it if it doesn’t exist, and overwriting it if it does.
    """

    def __init__(self, source, target):
        """
        Copy file from source to target
        :param source absolute filepath (or relative to runner file)
        :param target absolute filepath (or relative to runner file)
        """
        super().__init__()
        self._source = source
        self._target = target

    def run(self, environment: Environment):
        shutil.copyfile(self._source, self._target)
