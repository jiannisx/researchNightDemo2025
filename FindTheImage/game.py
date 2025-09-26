# game.py (refactor για 2 παιχνίδια)
import sys
import pygame
from manager import GameManager

def main():
    clock = pygame.time.Clock()
    game = GameManager()

    running = True
    while running:
        running = game.handle_events()
        game.draw()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
