import pygame
import random
from pygame.locals import *
from typing import Tuple, List
import tkinter as tk
from tkinter import ttk
import math
from multiprocessing import Process

from boids import Boid

BACKGROUND_COLOR = (255, 255, 255)
BOID_COLOR = (0, 0, 0)


class Sliders:
    def __init__(self, frame: ttk.Frame, config: dict):
        self.sliders = []
        self.frame = frame
        row = 0
        for k, _ in config.items():
            if (k == "width" or k == "height" or k == "num_boids"):
                continue
            bounds = self.__get_param_bounds(k)
            self.sliders.append(Slider(config, self.frame, k, row, bounds[0], bounds[1]))
            row += 1
    
    def __get_param_bounds(self, key: str) -> Tuple[float, float]:
        if key == "max_speed":
            return (0.2, 3)
        elif key == "separation_radius":
            return (3, 100)
        elif key == "alignment_radius":
            return (3, 200)
        elif key == "cohesion_radius":
            return (3, 200)
        elif key == "separation_force":
            return (0, 1.2)
        elif key == "alignment_force":
            return (0.002, 0.05)
        elif key == "cohesion_force":
            return (0.005, 0.08)
        else:
            raise AttributeError(f"[CRITICAL] Key {key} not supported to find slider bounds!")

class Slider:
    def __init__(self, config: dict, frame: ttk.Frame, key: str, row: int, min: float, max: float):
        self.config = config
        self.key = key
        self.label = ttk.Label(frame, text="{:s} : {:.4f}".format(key, 0.0))
        self.label.grid(column=0, row=row, padx=5, pady=5)
        self.slider = ttk.Scale(frame, from_=min, to=max, value=config[key], command=self.__update_parameter)
        self.slider.grid(column=1, row=row, padx=5, pady=5)

    def __update_parameter(self, value):
        self.config.update({self.key: float(value)})
        self.label.config(text="{:s} : {:.4f}".format(self.key, float(value)))

class GraphicInterface:
    def __init__(self, config: dict):
        # Initialize Pygame
        self.config = config
        pygame.init()
        self.screen = pygame.display.set_mode((config["width"], config["width"]))
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
        self.sliders = Sliders(self.frame, self.config)

        self.panel_process = Process(target=self.window.mainloop)

    def draw_boid(self, boid: Boid):
        position = (boid.get_position().x, boid.position.y)
        angle = math.atan2(boid.get_velocity().y, boid.get_velocity().x)
        rotated_points = []
        for point in [(0, -5), (3, 1), (0, 5), (-3, 1)]:
            rotated_x = math.cos(angle) * point[0] - math.sin(angle) * point[1]
            rotated_y = math.sin(angle) * point[0] + math.cos(angle) * point[1]
            rotated_points.append((position[0] + rotated_x, position[1] + rotated_y))
        pygame.draw.polygon(self.screen, BOID_COLOR, rotated_points)

    
    def start(self, boids: List[Boid]):
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