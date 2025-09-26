import pygame

class ImageButton:
    def __init__(self, image, x, y, width, height, image_path=None, clickable=True):
        self.original_image = image
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.image_path = image_path
        self.clickable = clickable  # αν False, το πάτημα δεν ενεργοποιεί το listener

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # αν hover, σχεδιάζουμε ένα απλό περίγραμμα
        if self.is_hovered:
            pygame.draw.rect(surface, (255,255,255), self.rect, 3)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if not self.clickable:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False