import pygame
import sys



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
        # Drawing lines with new coordinates
        pygame.draw.line(screen, (150, 150, 150), start_point,
                            end_point, 2)
    for name, hub in simulation.hubs.items():
        # Convert for center of circle
        center = to_pixel(hub.x, hub.y)
        color = (0, 200, 255)
        if hub.type == "start_hub": color = (50, 255, 50)
        elif hub.type == "end_hub": color = (255, 50, 50)
        # Draw hub (15 pix large)
        pygame.draw.circle(screen, color, center, 15)
        pygame.draw.circle(screen, (0, 0, 0), center, 15, 2)

    for drone in simulation.drones:
        if not drone.is_arrived:
            d_pos = to_pixel(drone.current_hub.x, drone.current_hub.y)
            pygame.draw.circle(screen, (255, 255, 0), d_pos, 8)

def auto_scaling(simulation, screen_width, screen_height):
    # find coordinates max from file
    # searching for biggest X and Y values
    max_x = max(h.x for h in simulation.hubs.values())
    max_y = max(h.y for h in simulation.hubs.values())

    # Dividing screen size by those maxes to find ratio
    # keeping 20% marging
    scale_x = (screen_width * 0.8) / max_x if max_x != 0 else 1
    scale_y = (screen_height * 0.8) / max_y if max_y != 0 else 1

    return min(scale_x, scale_y)

def main_visual(simulation):
    # initiate pygame mods
    pygame.init()
    # create window (width, height) by pixels
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Fly-In Drone Simulator")
    # clock to simulate FPS
    clock = pygame.time.Clock()
    SIM_STEP_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SIM_STEP_EVENT, 1000)

    running = True
    while running:
        for event in pygame.event.get():
            # if user clicks the cross, quit
            if event.type == pygame.QUIT:
                running = False
        # filling screen with a font(R, G, B)
        screen.fill((20, 20, 25))

        draw_everything(screen, simulation)

        # refresh the screen
        pygame.display.flip()
        # limits the FPS
        clock.tick(60)
    pygame.quit()
