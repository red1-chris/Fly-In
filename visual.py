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

    def to_pixel(x_logic, y_logic):
        # SCALE : space in pix between 2 units from file
        # if SCALE = 50 then point (1, 1) becomes (50, 50)
        SCALE = 60
        # OFFSET : to avoid being on the edge of the screen
        OFFSET_X = 100
        OFFSET_Y = 100

        pixel_x = x_logic * SCALE + OFFSET_X
        pixel_y = y_logic * SCALE + OFFSET_Y

        return (int(pixel_x), int(pixel_y))
    
    def draw_everything(screen, simulation):
        # Drawing Lines
        for conn in simulation.connections:
            h1, h2 = conn.zones
            # convert logical positions (ex: 2, 3) in pixels (ex: 220, 280)
            start_point = to_pixel(h1.x, h1.y)
            end_point = to_pixel(h2.x, h2.y)
            #Drawing lines with new coordonates
            pygame.draw.line(screen, (150, 150, 150), start_point, end_point, 2)