import pygame
import random
from pygame.locals import *
from copy import deepcopy

class Boid:
    def __init__(self, config: dict):
        self.config = config
        x = random.randint(0, config["width"])
        y = random.randint(0, config["height"])
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1),
                                       random.uniform(-1, 1))
        self.velocity.normalize_ip()
        self.velocity *= config["max_speed"]

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
        copy_params = deepcopy(self.config)

        for other_boid in boids:
            distance = self.position.distance_to(other_boid.get_position())

            if distance > 0:
                if distance < copy_params["separation_radius"]:
                    diff = self.position - other_boid.get_position()
                    diff.normalize_ip()
                    diff /= distance
                    separation_vector += diff
                    separation_count += 1

                if distance < copy_params["alignment_radius"]:
                    alignment_vector += other_boid.get_velocity()
                    alignment_count += 1

                if distance < copy_params["cohesion_radius"]:
                    cohesion_vector += other_boid.get_position()
                    cohesion_count += 1

        if separation_count > 0:
            separation_vector /= separation_count
            separation_vector.normalize_ip()
            separation_vector *= copy_params["max_speed"]
            separation_vector -= self.get_velocity()
            if separation_vector.length() > copy_params["separation_force"]:
                separation_vector.scale_to_length(copy_params["separation_force"])

        if alignment_count > 0:
            alignment_vector /= alignment_count
            alignment_vector.normalize_ip()
            alignment_vector *= copy_params["max_speed"]
            alignment_vector -= self.get_velocity()
            if alignment_vector.length() > copy_params["alignment_force"]:
                alignment_vector.scale_to_length(copy_params["alignment_force"])

        if cohesion_count > 0:
            cohesion_vector /= cohesion_count
            cohesion_vector -= self.get_position()
            cohesion_vector.normalize_ip()
            cohesion_vector *= copy_params["max_speed"]
            cohesion_vector -= self.get_velocity()
            if cohesion_vector.length() > copy_params["cohesion_force"]:
                cohesion_vector.scale_to_length(copy_params["cohesion_force"])

        self.velocity += separation_vector + alignment_vector + cohesion_vector
        if self.velocity.length() > copy_params["max_speed"]:
            self.velocity.scale_to_length(copy_params["max_speed"])
        
        self.position += self.velocity

        # Wrap around the screen
        if self.position.x > copy_params["width"]:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = copy_params["width"]

        if self.position.y > copy_params["height"]:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = copy_params["height"]









