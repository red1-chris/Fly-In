import pygame
import sys


def main_visual(simulation):
    # initiate pygame mods
    pygame.init()
    # create window (width, height) by pixels
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Fly-In Drone Simulator")
    # clock to simulate FPS
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            # if user clicks the cross, quit
            if event.type == pygame.QUIT:
                running = False
        # filling screen with a font(R, G, B)
        screen.fill((20, 20, 25))

        # [calling drawing functions]
        # 1.Draw conn (lines)
        # 2.Draw hubs (circles)
        # 3. Draw drones (circles with moving)

        # refresh the screen
        pygame.display.flip()
        # limits the FPS
        clock.tick(60)
    pygame.quit()