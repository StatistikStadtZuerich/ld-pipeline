import stardog
import os
import pandas as pd
from datetime import datetime
from pipeline.base import Env, Environment

def print_formatted(msg):
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{formatted_datetime} - {msg}")

def get_stardog_graph_uri(env: Env):
    environment = Environment(env)
    return environment.config.get("stardog_graph_uri")

def execute_sparql(query, env: Env):
    environment = Environment(env)
    cert_path = environment.config.get("stardog_cert_path")
    stardog_database = environment.config.get("stardog_database")
    stardog_endpoint = environment.config.get("stardog_endpoint")
    stardog_username = environment.config.get("stardog_username")
    stardog_password = environment.config.get("stardog_password")
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    conn_details = {
        'endpoint': stardog_endpoint,
        'username': stardog_username,
        'password': stardog_password
    }
    results = None
    try:
        with stardog.Admin(**conn_details) as admin:
            with stardog.Connection(stardog_database, **conn_details) as conn:
                results = conn.select(query)
    except Exception as e:
        print_formatted(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    
    df = None
    if results:
        data = []
        for binding in results['results']['bindings']:
            row = {var: binding[var]['value'] for var in results['head']['vars']}
            data.append(row)
        df = pd.DataFrame(data)
    return df