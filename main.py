import tkinter as tk
import math
import random

root = tk.Tk()
canvas = tk.Canvas(root, height=1000, width=1000, bg="black")
canvas.pack()

all_planets = []

G = 6.674 * 10**-11
time_step = 1000000000
scale_factor = 1e-12
radius_scale = 1e-2

class Planet:
    def __init__(self, name, mass, radius, coordinates, velocity, color):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.coordinates = coordinates
        self.velocity = velocity
        self.color = color
        self.canvas_item = None
        self.label = None
        self.path = []
        self.create_on_canvas()

    def create_on_canvas(self):
        x0, y0 = [coord * scale_factor for coord in self.coordinates]
        r_scaled = self.radius * radius_scale
        x1 = x0 + r_scaled
        y1 = y0 + r_scaled
        self.canvas_item = canvas.create_oval(x0, y0, x1, y1, fill=self.color)
        self.label = canvas.create_text(x0 + r_scaled/2, y0 + r_scaled/2, text=self.get_info(), fill="white")

    def get_info(self):
        return f"{self.name}\nMass: {self.mass:.2e} kg\nRadius: {self.radius} km\nVelocity: ({self.velocity[0]:.2e}, {self.velocity[1]:.2e}) m/s"

    def update_position(self):
        x0, y0 = [coord * scale_factor for coord in self.coordinates]
        r_scaled = self.radius * radius_scale
        x1 = x0 + r_scaled
        y1 = y0 + r_scaled
        canvas.coords(self.canvas_item, x0, y0, x1, y1)
        canvas.coords(self.label, x0 + r_scaled/2, y0 + r_scaled/2)
        canvas.itemconfig(self.label, text=self.get_info())
        self.path.append((x0 + r_scaled / 2, y0 + r_scaled / 2))
        if len(self.path) > 1:
            canvas.create_line(self.path[-2], self.path[-1], fill=self.color, width=1)

def create_stars(num_stars):
    for _ in range(num_stars):
        x = random.randint(0, 1000)
        y = random.randint(0, 1000)  
        size = random.randint(1, 3)  
        canvas.create_oval(x, y, x + size, y + size, fill="white")

def calculate_gravitational_force(planet1, planet2):
    r = ((planet2.coordinates[0] - planet1.coordinates[0])**2 +
         (planet2.coordinates[1] - planet1.coordinates[1])**2)**0.5
    if r == 0:
        return 0, 0
    force = G * planet1.mass * planet2.mass / r**2
    angle = math.atan2(planet2.coordinates[1] - planet1.coordinates[1],
                       planet2.coordinates[0] - planet1.coordinates[0])
    fx = force * math.cos(angle)
    fy = force * math.sin(angle)
    return fx, fy

def check_collision(p1, p2):
    distance = math.sqrt((p2.coordinates[0] - p1.coordinates[0]) ** 2 + (p2.coordinates[1] - p1.coordinates[1]) ** 2)
    combined_radius = (p1.radius + p2.radius) * 3e9
    return distance < combined_radius

def merge_planets(p1, p2):
    new_mass = p1.mass + p2.mass
    new_radius = (p1.radius**3 + p2.radius**3)**(1/3)
    new_coordinates = [
        (p1.coordinates[0] * p1.mass + p2.coordinates[0] * p2.mass) / new_mass,
        (p1.coordinates[1] * p1.mass + p2.coordinates[1] * p2.mass) / new_mass
    ]
    new_velocity = [
        (p1.velocity[0] * p1.mass + p2.velocity[0] * p2.mass) / new_mass,
        (p1.velocity[1] * p1.mass + p2.velocity[1] * p2.mass) / new_mass
    ]
    new_color = merge_colors(p1.color, p2.color)
    new_planet = Planet(f"Merged Planet ({p1.name} & {p2.name})", new_mass, new_radius, new_coordinates, new_velocity, new_color)
    return new_planet

def merge_colors(color1, color2):
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    r = (r1 + r2) // 2
    g = (g1 + g2) // 2
    b = (b1 + b2) // 2
    new_color = f"#{r:04x}{g:04x}{b:04x}"
    return new_color

def update_velocities():
    for i, planet1 in enumerate(all_planets):
        total_fx, total_fy = 0, 0
        for j, planet2 in enumerate(all_planets):
            if i != j:
                fx, fy = calculate_gravitational_force(planet1, planet2)
                total_fx += fx
                total_fy += fy
        ax = total_fx / planet1.mass
        ay = total_fy / planet1.mass
        planet1.velocity[0] += ax * time_step
        planet1.velocity[1] += ay * time_step

def update_positions():
    i = 0
    while i < len(all_planets):
        planet1 = all_planets[i]
        planet1.coordinates[0] += planet1.velocity[0] * time_step
        planet1.coordinates[1] += planet1.velocity[1] * time_step
        planet1.update_position()
        j = i + 1
        merged = False
        while j < len(all_planets):
            planet2 = all_planets[j]
            if check_collision(planet1, planet2):
                new_planet = merge_planets(planet1, planet2)
                all_planets.append(new_planet)
                to_remove = [planet1, planet2]
                for planet in to_remove:
                    if planet in all_planets:
                        all_planets.remove(planet)
                        canvas.delete(planet.canvas_item)
                        if planet.label:
                            canvas.delete(planet.label)
                merged = True
                break
            j += 1
        if not merged:
            i += 1

def simulate():
    update_velocities()
    update_positions()
    root.after(10, simulate)

create_stars(100)
planet1 = Planet("Planet 1", 5.972 * 10**28, 6371, [5.972 * 10**14, 300], [0, 600], "red")
planet2 = Planet("Planet 2", 9.000 * 10**26, 5000, [24 * 10**13, 5.972 * 10**13], [0, 600], "blue")
planet3 = Planet("Planet 3", 7.348 * 10**30, 9000, [23 * 10**13, 5.972 * 10**14], [1000, 0], "green")
planet4 = Planet("Planet 4", 7.348 * 10**30, 9000, [5.972 * 10**14, 4 * 10**14], [-1000, 0], "orange")

all_planets.append(planet1)
all_planets.append(planet2)
all_planets.append(planet3)
all_planets.append(planet4)

simulate()
root.mainloop()
