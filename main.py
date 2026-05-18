import sys
import os
import pygame
from parser import Parser
from simulation import Simulation
from visual import main_visual

def get_map_files(directory="maps"):
    map_files = []
    if not os.path.exists(directory):
        return map_files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                relative_path = os.path.join(root, file)
                map_files.append(relative_path)
    return sorted(map_files)

def run_menu(screen, map_files):
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont("Arial", 28, bold=True)
    font_item = pygame.font.SysFont("Arial", 16)

    WHITE = (255, 255, 255)
    DARK_BG = (20, 20, 25)
    HOVER_COLOR = (0, 200, 255)
    LIGHT_GREY = (200, 200, 200)

    buttons = []
    start_y = 120
    for i, map_path in enumerate(map_files):
        display_name = map_path.replace("maps" + os.sep, "")
        rect = pygame.Rect(50, start_y + (i * 35), 450, 30)
        buttons.append({"rect": rect, "path": map_path, "name": display_name})
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                for btn in buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        return btn["path"]
        screen.fill(DARK_BG)
        title_surface = font_title.render("Fly-in Drone Simulator - Menu", True, HOVER_COLOR)
        screen.blit(title_surface, (50, 40))

        subtitle_surface = font_item.render("Select a map to start the simulation:", True, LIGHT_GREY)
        screen.blit(subtitle_surface, (50, 80))

        for btn in buttons:
            is_hovered = btn["rect"].collidepoint(mouse_pos)
            color = HOVER_COLOR if is_hovered else WHITE

            if is_hovered:
                pygame.draw.rect(screen, (30, 40, 50), btn["rect"], border_radius=4)

            text_surface = font_item.render(btn["name"], True, color)
            screen.blit(text_surface, (btn["rect"].x + 10, btn["rect"].y + 5))
        
        pygame.display.flip()
        clock.tick(30)


def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fly-In Drone Simulator")

    map_files = get_map_files("maps")
    if not map_files:
        print("No map files found in 'maps' directory.")
        print("create a map directory and add .txt map files to it.")
        pygame.quit()
        sys.exit(1)

    while True:
        selected_map = run_menu(screen, map_files)
        if selected_map is None:
            break
        print(f"\nLoading map: {selected_map}...")
        try:
            parser = Parser(selected_map)
            parser.load()
            simulation = Simulation(parser)

            print("Starting Simulation...")
            main_visual(simulation, screen)
            print("Returning to Menu.")
        except Exception as e:
            print(f"Error while loading map: {e}")
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
