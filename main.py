#!./venv/bin/python3
import sys
import os

## importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
## from rescuer import Rescuer


from center import Center

path = "data_225v_100x80"



def main(data_folder_name):
   
    # Set the path to config files and data files for the environment
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))

    
    # Instantiate the environment
    env = Env(data_folder)
    
    # config files for the agents
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    explorer_file = os.path.join(data_folder, "explorer_config.txt")
    
    # Instantiate agents rescuer and explorer
    resc = Rescuer(env, rescuer_file)
    center = Center()
    center.path = path
    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    max = 4
    for i in range(0,max):
        Explorer(env, explorer_file, resc, i, max, center)

    print(f"Explorers: {center.explorers_count}")
    # Run the environment simulator
    env.run()
    
        
if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", path)
        
    main(data_folder_name)
