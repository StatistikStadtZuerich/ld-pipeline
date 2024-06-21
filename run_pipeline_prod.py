import os
import requests
import main
from pipeline import Pipeline
from pipeline.base import Utils
Utils.is_jupyter_notebook = True
env = main.Env.prod

def run_pipeline():
    
    pipeline = Pipeline(env)
    utils = Utils()
    
    # Check if start signal has arrived
    if utils.check_start_signal(env):
        utils.print_formatted('Pipeline started ...')
    else:
        utils.print_formatted('There is no start signal.')
        return
    
    # Update pipe tables
    main.step(name="copyHDBToPipeTables", env=env)
    
    # Generate triple files
    generate_triple_files()
    
    # Upload triple files to Stardog
    main.step(name="uploadToStardog", env=env)

    # Set finish signal
    utils.set_finish_signal(env)
    utils.print_formatted('Pipeline is finished.')
    

def generate_triple_files():
    names = [ 'code', 'cube', 'groupCode', 'hierarchy', 'legalFoundation',
         'measureUnit', 'measure', 'property', 'room', 'time', 'observation' ]

    names = ['cube']

    options = {
        'db_batch_size': 100000,
        'write_batch_size': 600000,
        'max_iteration': None
    }

    for name in names:
        main.step(name=f"{name}Templating", env=env, options=options)

if __name__ == "__main__":
    run_pipeline()