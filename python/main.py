from boids import Boid
from ui import GraphicInterface

from multiprocessing import Manager
import yaml
from yaml.loader import SafeLoader
import argparse


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(
        prog='Boids Simulator',
        description='A Simulation of the movements of bird flocks using the Boids genetic algorithm'
    )
    main_parser.add_argument('-c', '--config', default="", help="Absolute path to default initial configuration")
    args = main_parser.parse_args()

    data = dict()

    if args.config:
        print("Using Parsed Configuration!")
        with open(args.config) as f:
            data = yaml.load(f, Loader=SafeLoader)
    else:
        print("Using Default Configuration!")
        data = {
            "boids": {
                "width": 1000,
                "height": 1000,
                "num_boids": 80,
                "max_speed": 3,
                "separation_radius": 15,
                "alignment_radius": 100,
                "cohesion_radius": 100,
                "separation_force": 0.8,
                "alignment_force": 0.008,
                "cohesion_force": 0.01
            }
        }

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
