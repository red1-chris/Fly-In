import pygame
import sys

def to_pixel(x_logic, y_logic, scale, offset_x=50, offset_y=50):
    # converts coordinates into pixels using scale and offsets to center the map
    pixel_x = x_logic * scale + offset_x
    pixel_y = y_logic * scale + offset_y
    return (int(pixel_x), int(pixel_y))

def draw_everything(screen, simulation, scale, offset_x, offset_y, turn_count):
    font_hud = pygame.font.SysFont("Arial", 16, bold=True)
    font_title = pygame.font.SysFont("Arial", 20, bold=True)
    
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (150, 150, 150)
    
    is_finished = all(drone.is_arrived for drone in simulation.drones)
        
    if is_finished:
        status_text = f"Simulation over in {turn_count - 1} turns !"
        status_color = (50, 255, 50) # Vert brillant
    else:
        status_text = f"Tour : #{turn_count}"
        status_color = WHITE # Blanc
    
    text_turn = font_title.render(status_text, True, status_color)
    screen.blit(text_turn, (20, 20))
    for conn in simulation.connections:
        h1, h2 = conn.zones
        start_point = to_pixel(h1.x, h1.y, scale, offset_x, offset_y)
        end_point = to_pixel(h2.x, h2.y, scale, offset_x, offset_y)
        pygame.draw.line(screen, GREY, start_point, end_point, 2)
                            
    for name, hub in simulation.hubs.items():
        center = to_pixel(hub.x, hub.y, scale, offset_x, offset_y)
        color = (0, 200, 255)
        if hub.type == "start_hub" or hub.name.lower() == "start":
            color = (50, 255, 50)
        elif hub.type == "end_hub" or hub.name.lower() == "goal":
            color = (255, 50, 50)
        elif hub.type == "restricted":
            color = (255, 165, 0)
        elif hub.type == "blocked":
            color = (100, 100, 100)
            
        hub_rect = pygame.Rect(center[0] - 15, center[1] - 15, 30, 30)
        pygame.draw.rect(screen, color, hub_rect)
        pygame.draw.rect(screen, BLACK, hub_rect, 2)

        text_surface = font_hud.render(hub.name, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (center[0], center[1] - 25)
        screen.blit(text_surface, text_rect)

    hub_drone_counts = {}
    for drone in simulation.drones:
        hub = drone.current_hub
        if hub not in hub_drone_counts:
            hub_drone_counts[hub] = 0
        index_on_hub = hub_drone_counts[hub]
        hub_drone_counts[hub] += 1
        
        base_pos = to_pixel(hub.x, hub.y, scale, offset_x, offset_y)
        row = index_on_hub // 3
        col = index_on_hub % 3

        pixel_offset_x = (col - 1) * 10
        pixel_offset_y = (row - 1) * 10

        d_pos = (base_pos[0] + pixel_offset_x, base_pos[1] + pixel_offset_y)
        radius = 7
        width_line = 1

        pygame.draw.circle(screen, GREY, d_pos, radius)
        pygame.draw.circle(screen, BLACK, d_pos, radius, width_line)

        offset = int(radius * 0.6)

        start_line1 = (d_pos[0] - offset, d_pos[1] - offset)
        end_line1 = (d_pos[0] + offset, d_pos[1] + offset)
        pygame.draw.line(screen, BLACK, start_line1, end_line1, width_line)

        start_line2 = (d_pos[0] - offset, d_pos[1] + offset)
        end_line2 = (d_pos[0] + offset, d_pos[1] - offset)
        pygame.draw.line(screen, BLACK, start_line2, end_line2, width_line)

def auto_scaling(simulation, screen_width, screen_height):
    if not simulation.hubs:
        return 60, 50, 50
        
    max_x = max(h.x for h in simulation.hubs.values())
    max_y = max(h.y for h in simulation.hubs.values())

    max_x = max_x if max_x != 0 else 1
    max_y = max_y if max_y != 0 else 1

    scale_x = (screen_width - 200) / max_x
    scale_y = (screen_height - 200) / max_y

    scale = min(scale_x, scale_y)
    
    if scale > 150:
        scale = 150

    offset_x = (screen_width - max_x * scale) / 2
    offset_y = (screen_height - max_y * scale) / 2

    return scale, offset_x, offset_y

def main_visual(simulation, screen=None):
    pygame.init()
    if screen is None:
        current_w, current_h = 1000, 800
        screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
    else:
        current_w, current_h = screen.get_size()

    pygame.display.set_caption("Fly-In Drone Simulator")
    clock = pygame.time.Clock()

    SIM_STEP_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SIM_STEP_EVENT, 1000)

    scale, offset_x, offset_y = auto_scaling(simulation, current_w, current_h)

    font_btn = pygame.font.SysFont("Arial", 14, bold=True)
    turn_count = 1
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        btn_rect = pygame.Rect(current_w - 160, 20, 140, 35)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.VIDEORESIZE:
                current_w, current_h = event.w, event.h
                screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
                scale, offset_x, offset_y = auto_scaling(simulation, current_w, current_h)
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Si on clique sur le bouton "Retour Menu", on quitte la boucle de la simulation
                if btn_rect.collidepoint(mouse_pos):
                    running = False
                
            elif event.type == SIM_STEP_EVENT:
                    moves = simulation.next_step()
                    if moves:
                        print(f"#{turn_count}")
                        print(" ".join(moves))
                        turn_count += 1
                    if all(drone.is_arrived for drone in simulation.drones):
                        pygame.time.set_timer(SIM_STEP_EVENT, 0)

        screen.fill((20, 20, 25))

        draw_everything(screen, simulation, scale, offset_x, offset_y, turn_count)

        is_hovered = btn_rect.collidepoint(mouse_pos)
        btn_color = (0, 180, 230) if is_hovered else (40, 50, 65)
        text_color = (255, 255, 255) if is_hovered else (200, 210, 220)
        
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
        pygame.draw.rect(screen, (0, 0, 0), btn_rect, 1, border_radius=6)
        
        text_btn = font_btn.render("< Back to Menu", True, text_color)
        t_rect = text_btn.get_rect()
        t_rect.center = btn_rect.center
        screen.blit(text_btn, t_rect)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.time.set_timer(SIM_STEP_EVENT, 0)