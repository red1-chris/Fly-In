import pygame
from simulation import Simulation


def to_pixel(
        x_logic: float,
        y_logic: float,
        scale: float,
        offset_x: float = 50,
        offset_y: float = 50
) -> tuple:
    """Convert logical map coordinates to pixel coordinates"""
    pixel_x = x_logic * scale + offset_x
    pixel_y = y_logic * scale + offset_y
    return (int(pixel_x), int(pixel_y))


def draw_everything(
        screen: pygame.Surface,
        simulation: Simulation,
        scale: float,
        offset_x: float,
        offset_y: float,
        turn_count: int
) -> None:
    """Draw all hubs, connections and drones for the current turn"""
    font_hud = pygame.font.SysFont("Arial", 13, bold=True)
    font_title = pygame.font.SysFont("Arial", 20, bold=True)

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (150, 150, 150)
    TRANSIT_COLOR = (255, 255, 0)

    is_finished = all(drone.is_arrived for drone in simulation.drones)

    if is_finished:
        status_text = f"Simulation over in {turn_count - 1} turns !"
        status_color = (50, 255, 50)
    else:
        status_text = f"Turn : #{turn_count}"
        status_color = WHITE

    text_turn = font_title.render(status_text, True, status_color)
    screen.blit(text_turn, (20, 20))

    for conn in simulation.connections:
        h1, h2 = conn.zones
        start_point = to_pixel(h1.x, h1.y, scale, offset_x, offset_y)
        end_point = to_pixel(h2.x, h2.y, scale, offset_x, offset_y)
        pygame.draw.line(screen, GREY, start_point, end_point, 2)

    COLOR_MAP = {
        "red":     (220, 50,  50),
        "blue":    (50,  100, 220),
        "green":   (50,  200, 50),
        "yellow":  (220, 220, 50),
        "orange":  (255, 165, 0),
        "purple":  (160, 50,  200),
        "cyan":    (0,   200, 220),
        "brown":   (160, 100, 50),
        "gold":    (220, 180, 0),
        "lime":    (150, 255, 50),
        "magenta": (220, 50,  220),
        "gray":    (150, 150, 150),
        "grey":    (150, 150, 150),
        "white":   (240, 240, 240),
        "black":   (30,  30,  30),
    }

    for name, hub in simulation.hubs.items():
        center = to_pixel(hub.x, hub.y, scale, offset_x, offset_y)
        if hub.type == "start_hub" or hub.name.lower() == "start":
            color = (50, 255, 50)
        elif hub.type == "end_hub" or hub.name.lower() == "goal":
            color = (255, 50, 50)
        elif hub.type == "restricted":
            color = (255, 165, 0)
        elif hub.type == "blocked":
            color = (100, 100, 100)
        else:
            color = COLOR_MAP.get(hub.color, (0, 200, 255))

        hub_rect = pygame.Rect(center[0] - 15, center[1] - 15, 30, 30)
        pygame.draw.rect(screen, color, hub_rect)
        pygame.draw.rect(screen, BLACK, hub_rect, 2)

        text_surface = font_hud.render(hub.name, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (center[0], center[1] - 25)
        screen.blit(text_surface, text_rect)

    hub_drone_counts = {}
    for drone in simulation.drones:
        if drone.in_transit:
            prev_pos = to_pixel(
                drone.prev_hub.x, drone.prev_hub.y, scale, offset_x, offset_y
            )
            curr_pos = to_pixel(
                drone.current_hub.x, drone.current_hub.y,
                scale, offset_x, offset_y
            )
            d_pos = (
                (prev_pos[0] + curr_pos[0]) // 2,
                (prev_pos[1] + curr_pos[1]) // 2,
            )
            radius = 7
            width_line = 1
            pygame.draw.circle(screen, TRANSIT_COLOR, d_pos, radius)
            pygame.draw.circle(screen, BLACK, d_pos, radius, width_line)
            off = int(radius * 0.6)
            pygame.draw.line(screen, BLACK,
                             (d_pos[0] - off, d_pos[1]),
                             (d_pos[0] + off, d_pos[1]), width_line)
            pygame.draw.line(screen, BLACK,
                             (d_pos[0], d_pos[1] - off),
                             (d_pos[0], d_pos[1] + off), width_line)
        else:
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

            d_pos = (base_pos[0] + pixel_offset_x,
                     base_pos[1] + pixel_offset_y)
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


def auto_scaling(
        simulation: Simulation,
        screen_width: int,
        screen_height: int
) -> tuple:
    """Compute scale and offsets to fit all hubs within the screen"""
    if not simulation.hubs:
        return 60, 50, 50

    xs = [h.x for h in simulation.hubs.values()]
    ys = [h.y for h in simulation.hubs.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = max_x - min_x if max_x != min_x else 1
    span_y = max_y - min_y if max_y != min_y else 1

    margin = 100
    scale_x = (screen_width - margin * 2) / span_x
    scale_y = (screen_height - margin * 2) / span_y
    scale = min(scale_x, scale_y)

    if scale > 150:
        scale = 150

    offset_x = (screen_width - span_x * scale) / 2 - min_x * scale
    offset_y = (screen_height - span_y * scale) / 2 - min_y * scale

    return scale, offset_x, offset_y


def main_visual(
        simulation: Simulation,
        screen: pygame.Surface | None = None,
        capacity_info: bool = False
) -> str:
    """Run the pygame visualisation loop for one simulation
    Advances the simulation one turn per second via a timer event"""
    pygame.init()
    if screen is None:
        current_w, current_h = 1000, 800
        screen = pygame.display.set_mode((current_w, current_h),
                                         pygame.RESIZABLE)
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
        restart_rect = pygame.Rect(current_w - 160, 65, 140, 35)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            elif event.type == pygame.VIDEORESIZE:
                current_w, current_h = event.w, event.h
                screen = pygame.display.set_mode((current_w, current_h),
                                                 pygame.RESIZABLE)
                scale, offset_x, offset_y = auto_scaling(simulation,
                                                         current_w, current_h)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(mouse_pos):
                    running = False
                if restart_rect.collidepoint(mouse_pos):
                    return "restart"
            elif event.type == SIM_STEP_EVENT:
                moves = simulation.next_step()
                if moves:
                    print(f"#{turn_count}")
                    print(" ".join(moves))
                    if capacity_info:
                        for line in simulation.capacity_info():
                            print(line)
                    turn_count += 1
                if all(drone.is_arrived for drone in simulation.drones):
                    pygame.time.set_timer(SIM_STEP_EVENT, 0)

        screen.fill((20, 20, 25))
        draw_everything(screen, simulation, scale, offset_x,
                        offset_y, turn_count)

        is_hovered = btn_rect.collidepoint(mouse_pos)
        btn_color = (0, 180, 230) if is_hovered else (40, 50, 65)
        text_color = (255, 255, 255) if is_hovered else (200, 210, 220)

        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
        pygame.draw.rect(screen, (0, 0, 0), btn_rect, 1, border_radius=6)

        text_btn = font_btn.render("< Back to Menu", True, text_color)
        t_rect = text_btn.get_rect()
        t_rect.center = btn_rect.center
        screen.blit(text_btn, t_rect)

        is_hovered_r = restart_rect.collidepoint(mouse_pos)
        btn_color_r = (0, 200, 100) if is_hovered_r else (40, 65, 50)
        text_color_r = (255, 255, 255) if is_hovered_r else (200, 220, 210)

        pygame.draw.rect(screen, btn_color_r, restart_rect, border_radius=6)
        pygame.draw.rect(screen, (0, 0, 0), restart_rect, 1, border_radius=6)

        text_restart = font_btn.render("Restart", True, text_color_r)
        r_rect = text_restart.get_rect()
        r_rect.center = restart_rect.center
        screen.blit(text_restart, r_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.time.set_timer(SIM_STEP_EVENT, 0)
    return "menu"
