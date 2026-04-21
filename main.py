from parser import Parser


def test_parser(map_path: str):
    print(f"Testing parser with map: {map_path}")
    try:
        p = Parser(map_path)
        p.load()
        print(f"nb drones parsed: {p.nb_drones}")
        print(f"Hubs loaded ({len(p.hubs)}):")
        for name, hub in p.hubs.items():
            print(f" - [{hub.type.upper()}] {name} (x:{hub.x}, y:{hub.y}) | Capacity:{hub.max_drones} | Colour: {hub.color}")
            print(f"Connexions chargées : {len(p.connections)}")
    except Exception as e:
        print(f"Erreur lors du test : {e}")


if __name__ == "__main__":
    test_parser("maps/challenger/01_the_impossible_dream.txt")
