import stardog
import os
import glob
import pandas as pd
from datetime import datetime
from .environment import Env, Environment

from .base import Base


class Utils(Base):
    _instance = None
    is_jupyter_notebook = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Utils, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def print_formatted(self, msg, error=False):
        if Utils.is_jupyter_notebook:
            now = datetime.now()
            formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{formatted_datetime} - {msg}")
        if error:
            self.logger.error(msg)
        else:
            self.logger.info(msg)

    def get_stardog_graph_uri(self, env: Env):
        environment = Environment(env)
        return environment.config.get("stardog_graph_uri")

    def execute_sparql(self, query, env: Env):
        environment = Environment(env)
        cert_path = environment.config.get("stardog_cert_path")
        stardog_database = environment.config.get("stardog_database")
        stardog_endpoint = environment.config.get("stardog_endpoint")
        stardog_username = environment.config.get("stardog_username")
        stardog_password = environment.config.get("stardog_password")
        os.environ["REQUESTS_CA_BUNDLE"] = cert_path
        conn_details = {
            "endpoint": stardog_endpoint,
            "username": stardog_username,
            "password": stardog_password,
        }
        results = None
        try:
            # with stardog.Admin(**conn_details) as admin:
            with stardog.Connection(stardog_database, **conn_details) as conn:
                results = conn.select(query)
        except Exception as e:
            self.print_formatted(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

        df = None
        if results:
            data = []
            for binding in results["results"]["bindings"]:
                row = {var: binding[var]["value"] for var in results["head"]["vars"]}
                data.append(row)
            df = pd.DataFrame(data)
        return df
        
    def is_pipeline_running(self, env: Env):
        environment = Environment(env)
        start_signal_folder = environment.config.get("start_signal_folder")
        response_file_path = f"{start_signal_folder}/pipeline_response.txt"
        with open(response_file_path, 'r') as file:
            content = file.read().strip()
            if content.startswith("Running_pipeline_") or content.startswith("Finished_pipeline_"):
                return True
        return False
    
    def check_start_signal(self, env: Env):
        environment = Environment(env)
        start_signal_folder = environment.config.get("start_signal_folder")
        response_file_path = f"{start_signal_folder}/pipeline_response.txt"
        search_path = os.path.join(start_signal_folder, 'Start_pipeline_*.txt')
        files = glob.glob(search_path)
        
        if len(files) == 0:
            return False
        
        if self.is_pipeline_running(env):
            return False
            
        for file in files:
            filename = os.path.basename(file)
            running_signal = filename.replace("Start_", "Running_")
            with open(response_file_path, 'w') as file:
                file.write(running_signal)
            break
        
        return True
        
    def set_finish_signal(self, env: Env):
        environment = Environment(env)
        start_signal_folder = environment.config.get("start_signal_folder")
        response_file_path = f"{start_signal_folder}/pipeline_response.txt"
        try:
            with open(response_file_path, 'r') as file:
                content = file.read().strip()
                if content.startswith("Running_"):
                    finished_content = content.replace("Running_", "Finished_")
                    with open(response_file_path, 'w') as file:
                        file.write(finished_content)
                    self.print_formatted("Pipeline status updated to finished.")
                else:
                    self.print_formatted("No running pipeline found.", error=True)
        except Exception as e:
            self.print_formatted(f"An error occurred while setting finish signal: {e}", error=True)
