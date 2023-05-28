import pygame
import random
from pygame.locals import *
import math
from dataclasses import dataclass
from typing import List

from multiprocessing import Process

import yaml
from yaml.loader import SafeLoader
import argparse

import tkinter as tk
from tkinter import ttk

BACKGROUND_COLOR = (255, 255, 255)
BOID_COLOR = (0, 0, 0)


@dataclass
class Config:
    width: int = 1000
    height: int = 1000
    num_boids: int = 80
    max_speed: float = 3.0
    separation_radius: float = 30.0
    alignment_radius: float = 100.0
    cohesion_radius: float = 50.0
    separation_force: float = 0.08
    alignment_force: float = 0.008
    cohesion_force: float = 0.01

def convert_yaml_to_dataclass(config: dict) -> Config:
    return Config(config["width"], 
                  config["height"], 
                  config["num_boids"],
                  config["max_speed"],
                  config["separation_radius"],
                  config["alignment_radius"],
                  config["cohesion_radius"],
                  config["separation_force"],
                  config["alignment_force"],
                  config["cohesion_force"])

class Boid:
    def __init__(self, x: float, y: float, config: Config):
        self.config = config
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1),
                                       random.uniform(-1, 1))
        self.velocity.normalize_ip()
        self.velocity *= config.max_speed
        

    def set_screen(self, screen):
        self.screen = screen

    def get_position_tuple(self):
        return (self.position.x, self.position.y)
    
    def get_position(self):
        return self.position
        
    def get_velocity(self):
        return self.velocity

    def update(self, boids):
        separation_vector = pygame.Vector2(0, 0)
        alignment_vector = pygame.Vector2(0, 0)
        cohesion_vector = pygame.Vector2(0, 0)
        separation_count = 0
        alignment_count = 0
        cohesion_count = 0

        for other_boid in boids:
            distance = self.position.distance_to(other_boid.get_position())

            if distance > 0:
                if distance < self.config.separation_radius:
                    diff = self.position - other_boid.get_position()
                    diff.normalize_ip()
                    diff /= distance
                    separation_vector += diff
                    separation_count += 1

                if distance < self.config.alignment_radius:
                    alignment_vector += other_boid.get_velocity()
                    alignment_count += 1

                if distance < self.config.cohesion_radius:
                    cohesion_vector += other_boid.get_position()
                    cohesion_count += 1

        if separation_count > 0:
            separation_vector /= separation_count
            separation_vector.normalize_ip()
            separation_vector *= self.config.max_speed
            separation_vector -= self.get_velocity()
            if separation_vector.length() > self.config.separation_force:
                separation_vector.scale_to_length(self.config.separation_force)

        if alignment_count > 0:
            alignment_vector /= alignment_count
            alignment_vector.normalize_ip()
            alignment_vector *= self.config.max_speed
            alignment_vector -= self.get_velocity()
            if alignment_vector.length() > self.config.alignment_force:
                alignment_vector.scale_to_length(self.config.alignment_force)

        if cohesion_count > 0:
            cohesion_vector /= cohesion_count
            cohesion_vector -= self.get_position()
            cohesion_vector.normalize_ip()
            cohesion_vector *= self.config.max_speed
            cohesion_vector -= self.get_velocity()
            if cohesion_vector.length() > self.config.cohesion_force:
                cohesion_vector.scale_to_length(self.config.cohesion_force)

        self.velocity += separation_vector + alignment_vector + cohesion_vector
        if self.velocity.length() > self.config.max_speed:
            self.velocity.scale_to_length(self.config.max_speed)
        
        self.position += self.velocity

        # Wrap around the screen
        if self.position.x > self.config.width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = self.config.width

        if self.position.y > self.config.height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = self.config.height


class GraphicInterface:
    def __init__(self, config: Config):
        # Initialize Pygame
        self.config = config
        pygame.init()
        self.screen = pygame.display.set_mode((config.width, config.width))
        pygame.display.set_caption("Boids Simulation")
        self.clock = pygame.time.Clock()

        # Game loop
        self.running = False
        self.screen.fill(BACKGROUND_COLOR)
        self.initialize_control_panel()
    
    def __del__(self):
        pygame.quit()
        self.panel_process.join()

    def initialize_control_panel(self):
        # Create a Tkinter window
        self.window = tk.Tk()
        self.window.title("Boids Control Panel")

        # Create a frame to hold the sliders
        self.frame = ttk.Frame(self.window, padding="20")
        self.frame.pack()

        # Create sliders for each parameter
        self.parameter1_label = ttk.Label(self.frame, text="Parameter 1")
        self.parameter1_label.grid(column=0, row=0, padx=5, pady=5)
        parameter1_slider = ttk.Scale(self.frame, from_=0, to=100, command=self.__update_parameter1)
        parameter1_slider.grid(column=1, row=0, padx=5, pady=5)

        self.parameter2_label = ttk.Label(self.frame, text="Parameter 2")
        self.parameter2_label.grid(column=0, row=1, padx=5, pady=5)
        parameter2_slider = ttk.Scale(self.frame, from_=0, to=100, command=self.__update_parameter2)
        parameter2_slider.grid(column=1, row=1, padx=5, pady=5)

        self.parameter3_label = ttk.Label(self.frame, text="Parameter 3")
        self.parameter3_label.grid(column=0, row=2, padx=5, pady=5)
        parameter3_slider = ttk.Scale(self.frame, from_=0, to=100, command=self.__update_parameter3)
        parameter3_slider.grid(column=1, row=2, padx=5, pady=5)

        self.panel_process = Process(target=self.window.mainloop)

    def __update_parameter1(self, value: str):
        parameter = float(value)
        self.parameter1_label.config(text="Parameter 1: {:.4f}".format(parameter))

    def __update_parameter2(self, value: str):
        parameter = float(value)
        self.parameter2_label.config(text="Parameter 2: {:.4f}".format(parameter))

    def __update_parameter3(self, value: str):
        parameter = float(value)
        self.parameter3_label.config(text="Parameter 3: {:.4f}".format(parameter))

    def draw_boid(self, boid):
        position = (boid.get_position().x, boid.position.y)
        angle = math.atan2(boid.get_velocity().y, boid.get_velocity().x)
        rotated_points = []
        for point in [(0, -5), (3, 1), (0, 5), (-3, 1)]:
            rotated_x = math.cos(angle) * point[0] - math.sin(angle) * point[1]
            rotated_y = math.sin(angle) * point[0] + math.cos(angle) * point[1]
            rotated_points.append((position[0] + rotated_x, position[1] + rotated_y))
        pygame.draw.polygon(self.screen, BOID_COLOR, rotated_points)

    
    def start(self, boids):
        self.running = True
        self.panel_process.start()
        while self.running:
            self.screen.fill(BACKGROUND_COLOR)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
            
            for boid in boids:
                boid.update(boids)
                self.draw_boid(boid)

            pygame.display.flip()
            self.clock.tick(60)


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
    
    config = convert_yaml_to_dataclass(data["boids"])

    boids = [Boid(random.randint(0, config.width), random.randint(0, config.height), config)
         for _ in range(config.num_boids)]
    
    ui = GraphicInterface(config)
    ui.start(boids)





