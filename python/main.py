from boids import Boid
from ui import GraphicInterface

from multiprocessing import Manager
import yaml
from yaml.loader import SafeLoader
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Boids Simulator',
        description='A Simulation of the movements of bird flocks using the Boids genetic algorithm'
    )   
    parser.add_argument('config_path')

    args = parser.parse_args()

    data = dict()

    with open(args.config_path) as f:
        data = yaml.load(f, Loader=SafeLoader)

    print("==========")
    print("PARAMETERS")
    print("==========")
        
    for k, v in data["boids"].items():
        print(f"{k} : {v}")

    print("==========")

    manager = Manager()
    config = manager.dict(data["boids"]) 

    boids = [Boid(config=config) for _ in range(config["num_boids"])]
    
    ui = GraphicInterface(config)
    ui.start(boids)
