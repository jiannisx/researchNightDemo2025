import pygame
import random
import os
from FindTheImage.Utils.colors import *

def safe_load_image(path, fallback_size=(100, 100), fill_color=None):
    """Προσπαθεί να φορτώσει εικόνα, αλλιώς δημιουργεί surface placeholder."""
    if path and os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return img
        except Exception as e:
            print(f"Προβλημα φόρτωσης εικόνας {path}: {e}")
    # placeholder
    surf = pygame.Surface(fallback_size)
    if fill_color is None:
        fill_color = (random.randint(50, 220), random.randint(50, 220), random.randint(50, 220))
    surf.fill(fill_color)
    return surf

def load_images_from_folder(folder):
    images = []
    paths = []
    if os.path.exists(folder) and os.path.isdir(folder):
        for file in os.listdir(folder):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                p = os.path.join(folder, file)
                images.append(safe_load_image(p))
                paths.append(p)
    else:
        print(f"Ο φάκελος {folder} δεν υπάρχει. Δημιουργία placeholder images.")
        for i in range(6):
            images.append(safe_load_image(None, fallback_size=(100,100)))
            paths.append(f"placeholder_{i}")
    return images, paths

def load_target_image(target_image_path):
    return safe_load_image(target_image_path, fallback_size=(150,150), fill_color=(200,50,50))
