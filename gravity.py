import pygame
import math
from pygame import gfxdraw
import numpy as np
import random
from numba import jit

pygame.init()
width = 1280
height = 720
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gravity")

G = 6.674 * pow(10, -11)
globes = []
moons = []
click = False
clicked = False
earthm = 5.972 * pow(10, 24)


@jit(nopython=True)
def draw_orbit(orbit: np.array, globes: np.array):
    i = -1
    while i < 1000:
        i += 1
        for globe in globes:
            a = globe
            b = orbit[0]
            ba = a - b
            r = math.sqrt(pow(ba[0], 2) + pow(ba[1], 2))
            c = earthm * G / pow(r, 2)
            dot = ba[0]
            det = -ba[1]
            angle = math.atan2(det, dot)
            sin = math.sin(angle)
            cos = math.cos(angle)

            orbit[2][0] = c * cos
            orbit[2][1] = - c * sin

            orbit[1][0] += orbit[2][0]
            orbit[1][1] += orbit[2][1]

            orbit[0][0] += orbit[1][0]
            orbit[0][1] += orbit[1][1]
        x = int(orbit[0][0] / pow(10, 4)) + width // 2
        y = int(orbit[0][1] / pow(10, 4)) + height // 2
        if x > 5000 or x < -5000 or y > 5000 or x < -5000:
            i = 10000
        for globe in globes:
            a = globe
            b = orbit[0]
            ba = a - b
            r = math.sqrt(pow(ba[0], 2) + pow(ba[1], 2))
            if r < 600000:
                i = 10000
        yield x, y


class moon:
    def __init__(self, x, y, velx, vely, radius, globes):
        self.x = (x - width // 2) * pow(10, 4)
        self.y = (y - height // 2) * pow(10, 4)
        self.coords = [[self.x, self.y], [velx, vely], [0, 0]]
        self.radius = radius
        self.trace = [[x, y]]
        self.globes = globes

    def gravity(self):
        for globe in self.globes:
            a = np.array(globe.coords)
            b = np.array(self.coords[0])
            ba = a - b
            r = np.linalg.norm(ba)
            c = globe.mass * G / pow(r, 2)
            dot = ba[0]
            det = -ba[1]
            angle = math.atan2(det, dot)
            sin = math.sin(angle)
            cos = math.cos(angle)

            self.coords[2][0] = c * cos
            self.coords[2][1] = - c * sin

            self.coords[1][0] += self.coords[2][0]
            self.coords[1][1] += self.coords[2][1]

            self.coords[0][0] += self.coords[1][0]
            self.coords[0][1] += self.coords[1][1]

    def out_of_bounds(self, x, y):
        for i in self.globes:
            a = np.array(i.coords)
            b = np.array(self.coords[0])
            ba = a - b
            r = np.linalg.norm(ba)
            if r < 600000:
                return True
        if x > 5000 or x < -5000 or y > 5000 or x < -5000:
            return True
        else:
            return False

    def draw(self):
        j = self.trace[0]
        for i, k in zip(self.trace[1::], range(1, len(self.trace))):
            if len(self.trace) - k <= 199:
                pygame.draw.aaline(win, (55 + len(self.trace) - k, 55 + len(self.trace) - k, 55 + len(self.trace) - k),
                                   j, i)
                j = i
            else:
                self.trace.pop(0)
        x = int(self.coords[0][0] / pow(10, 4)) + width // 2
        y = int(self.coords[0][1] / pow(10, 4)) + height // 2
        self.trace.append([x, y])
        if not self.out_of_bounds(x, y):
            draw_circle(win, x, y, self.radius, (0, 0, 0))
            return True

    def show(self):
        self.gravity()
        return self.draw()


class globe:
    def __init__(self, x, y, m):
        self.x = x * pow(10, 4)
        self.y = y * pow(10, 4)
        self.coords = [self.x, self.y]
        self.mass = m

    def draw_globe(self):
        x = int(self.coords[0] / pow(10, 4)) + width // 2
        y = int(self.coords[1] / pow(10, 4)) + height // 2
        draw_circle(win, x, y, 40, (0, 0, 0))


def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def initiate():
    global globes
    globelen = random.randint(1, 3)
    distance = 400
    # earthm = 5.972 * pow(10, 24)
    # moonm = 7.34767309 * pow(10, 22)
    for i in range(globelen):
        x = i * distance - (globelen - 1) * distance // 2
        y = 0
        globes.append(globe(x, y, earthm))


def draw_orbitt(orbit):
    for i in range(200):
        orbit.gravity()
        x = int(orbit.coords[0][0] / pow(10, 4)) + width // 2
        y = int(orbit.coords[0][1] / pow(10, 4)) + height // 2
        try:
            if not orbit.out_of_bounds(x, y):
                if i % 5 == 0:
                    co = 55 + i // 5
                    draw_circle(win, x, y, 2, (co, co, co))
            else:
                break
        except:
            pass


def create_moon(mx, my, x, y, radius):
    global click, clicked, moons

    def velocity(mx, my, x, y):
        a = np.array([x, y])
        b = np.array([mx, my])
        ba = a - b
        r = np.linalg.norm(ba)
        dot = ba[0]
        det = -ba[1]
        angle = math.atan2(det, dot)
        sin = math.sin(angle)
        cos = math.cos(angle)
        vx = r * 100 * cos
        vy = -r * 100 * sin
        return vx, vy

    if click and not clicked:
        x, y = mx, my
        clicked = True
        radius = random.randint(10, 20)
        draw_circle(win, x, y, radius, (55, 55, 55))
    elif click:
        vx, vy = velocity(mx, my, x, y)
        orbit = moon(x, y, vx, vy, radius, globes)
        coords = []
        for i in globes:
            coords.append(i.coords)
        coords = np.array(coords)
        i = -1
        for xx, yy in draw_orbit(np.array(orbit.coords), coords):
            i += 1
            try:
                if not i % 10:
                    draw_circle(win, xx, yy, 2, (55 + i // 5, 55 + i // 5, 55 + i // 5))
            except:
                break
        # draw_orbitt(orbit)
        pygame.draw.aaline(win, (55, 55, 55), [mx, my], [x, y])
        draw_circle(win, x, y, radius, (55, 55, 55))

    elif not click and clicked:
        clicked = False
        vx, vy = velocity(mx, my, x, y)
        moons.append(moon(x, y, vx, vy, radius, globes))
    return x, y, radius


def main():
    global click, clicked
    run = True
    initiate()
    click = False
    clicked = False
    clock = pygame.time.Clock()
    mx, my = 0, 0
    x, y = 0, 0
    radius = 0
    while run:
        clock.tick(300)
        win.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        x, y, radius = create_moon(mx, my, x, y, radius)
        click = False
        if pygame.mouse.get_pressed()[0]:
            click = True
            mx, my = pygame.mouse.get_pos()
        i = 0
        while i in range(len(moons)):
            if not moons[i].show():
                moons.pop(i)
                i = i - 1
            i += 1
        for i in globes:
            i.draw_globe()
        pygame.display.update()


if __name__ == "__main__":
    main()
pygame.quit()
