import glob
import logging
import os
import shutil
from datetime import datetime

from .base import Base
from .environment import Environment


class Utils(Base):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Utils, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def start_signal_folder(env: Environment) -> str:
        folder = env.config.get("start_signal_folder")
        if folder is None:
            raise ValueError("start_signal_folder must be set")
        return folder

    @staticmethod
    def is_pipeline_running(environment: Environment):
        start_signal_folder = Utils.start_signal_folder(environment)
        search_path = os.path.join(start_signal_folder, "Running_pipeline_*.txt")
        files = glob.glob(search_path)
        if len(files) > 0:
            logging.debug("Found pipeline running: %s", files)
            return True
        else:
            return False

    @staticmethod
    def check_start_signal(environment: Environment):
        if Utils.is_pipeline_running(environment):
            return False

        start_signal_folder = Utils.start_signal_folder(environment)
        search_path = os.path.join(start_signal_folder, "Start_pipeline_*.txt")
        files = glob.glob(search_path)

        if len(files) == 0:
            return False

        for file in files:
            filename = os.path.basename(file)
            running_signal = filename.replace("Start_", "Running_")
            running_signal_path = os.path.join(start_signal_folder, running_signal)
            with open(running_signal_path, "w") as f:
                f.write(f"{datetime.now()}")
            done_folder = os.path.join(start_signal_folder, "done")
            if not os.path.exists(done_folder):
                os.makedirs(done_folder)
            shutil.move(file, os.path.join(done_folder, filename))
            break

        return True

    @staticmethod
    def set_finish_signal(environment: Environment):
        start_signal_folder = Utils.start_signal_folder(environment)
        search_path = os.path.join(start_signal_folder, "Running_pipeline_*.txt")
        files = glob.glob(search_path)

        if len(files) == 0:
            return False

        for file in files:
            filename = os.path.basename(file)
            finished_signal = filename.replace("Running_", "Finished_")
            finished_signal_path = os.path.join(start_signal_folder, finished_signal)
            with open(finished_signal_path, "w") as f:
                f.write(f"{datetime.now()}")
            done_folder = os.path.join(start_signal_folder, "done")
            if not os.path.exists(done_folder):
                os.makedirs(done_folder)
            shutil.move(file, os.path.join(done_folder, filename))
            break

    def set_start_signal_fuseki_index(self, environment: Environment):
        """
        Create start-signal for the 'create_fuseki_index'-script
        """
        output_path = environment.config.get("output_path")
        current_datetime = datetime.now().strftime("%Y%m%d%H%M")
        file_name = f"start_fuseki_index_{current_datetime}.txt"
        file_path = os.path.join(output_path, file_name)
        with open(file_path, "w") as file:
            file.write(f"{datetime.now()}")
        self.logger.debug(f"Start signal '{file_name}' has been created.")

