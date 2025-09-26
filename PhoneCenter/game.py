import pygame
import random
import os
import time

# Αρχικοποίηση Pygame
pygame.init()

# Οθόνη
WIDTH, HEIGHT = 1100, 730
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Βρες το Όνομα στον Τηλεφωνικό Κατάλογο")

# Χρώματα - ΟΛΑ ΤΑ ΧΡΩΜΑΤΑ ΣΕ ΜΕΤΑΒΛΗΤΕΣ
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
BUTTON_COLOR = (240, 240, 240)
BUTTON_HOVER_COLOR = (220, 220, 220)
SEMI_TRANSPARENT = (255, 255, 255, 180)  # ΚΥΡΙΟ OVERLAY COLOR
RED_COLOR = (200, 0, 0)
GREEN_COLOR = (0, 150, 0)
BLUE_COLOR = (0, 0, 200)
TEXT_COLOR_BLACK = BLACK
TEXT_COLOR_WHITE = WHITE

# Γραμματοσειρές - ΜΕΓΑΛΥΤΕΡΕΣ ΚΑΙ BOLD
font_small = pygame.font.SysFont("Arial", 18)
font_medium = pygame.font.SysFont("Arial", 22, bold=True)
font_large = pygame.font.SysFont("Arial", 26, bold=True)
font_title = pygame.font.SysFont("Arial", 36, bold=True)


# Κλάση Button με left align
class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, left_align=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont(None, 26, bold=True)
        self.left_align = left_align  # Νέο attribute για left align

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        text_surf = self.font.render(self.text, True, BLACK)

        # Left align ή center ανάλογα με τη ρύθμιση
        if self.left_align:
            text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)

        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# Κλάση για τη διαχείριση του παιχνιδιού
class PhoneBookGame:
    def __init__(self, language="greek"):
        self.language = language
        self.state = "home"  # 'home', 'playing', 'results'

        # Φόρτωση δεδομένων από το αρχείο
        self.phone_data = self.load_phone_data("PhoneNumbers.txt")

        # Διαχωρισμός σε σελίδες των 10 εγγραφών
        self.entries_per_page = 10
        self.pages = self.split_into_pages(self.phone_data)
        self.current_double_page = 0  # Κάθε double page έχει 2 σελίδες (20 εγγραφές)
        self.total_double_pages = (len(self.pages) + 1) // 2  # Στρογγυλοποίηση προς τα πάνω

        # Μεταβλητές παιχνιδιού
        self.target_name = None
        self.target_phone = None
        self.target_index = None
        self.start_time = 0
        self.elapsed_time = 0
        self.attempts = 0
        self.score = 0
        self.selected_number = 1  # Ο αριθμός που επιλέχθηκε από το πληκτρολόγιο
        self.found_name = False  # Νέο flag για να ξέρουμε αν βρέθηκε το όνομα

        # Κουμπιά (θα αρχικοποιηθούν στη δημιουργία τους)
        self.next_button = None
        self.prev_button = None
        self.finish_button = None
        self.create_buttons()

        # Φόρτωση εικόνων
        self.background_image = None
        self.closed_book_image = None
        self.phonebook_image = None
        self.phonebook_image_flipped = None
        self.load_images()

        # Δημιουργία πληκτρολογίου
        self.numpad_buttons = []
        self.create_numpad()

        # Κουμπιά ονομάτων στις σελίδες
        self.name_buttons_left = []
        self.name_buttons_right = []

    def load_images(self):
        """Φόρτωση όλων των εικόνων"""
        try:
            self.background_image = pygame.image.load("background.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
        except:
            print("Δεν βρέθηκε το background.jpg - χρήση μονόχρωμου φόντου")
            self.background_image = None

        try:
            self.closed_book_image = pygame.image.load("closedBook.jpg")
            self.closed_book_image = pygame.transform.scale(self.closed_book_image, (600, 400))
        except:
            print("Δεν βρέθηκε το closedBook.jpg - χρήση placeholder")
            self.closed_book_image = None

        try:
            self.phonebook_image = pygame.image.load("openBook.png")
            # ΜΕΓΑΛΥΤΕΡΟ ΜΕΓΕΘΟΣ ΒΙΒΛΙΟΥ
            self.phonebook_image = pygame.transform.scale(self.phonebook_image, (420, 350))
            # Δημιουργία αναστραμμένης έκδοσης για τη δεξιά σελίδα
            self.phonebook_image_flipped = pygame.transform.flip(self.phonebook_image, True, False)
        except:
            print("Δεν βρέθηκε το openBook.png - χρήση placeholder")
            self.phonebook_image = None
            self.phonebook_image_flipped = None

    def create_buttons(self):
        """Δημιουργία/ενημέρωση κουμπιών με τη σωστή γλώσσα"""
        if self.language == "greek":
            self.next_button = Button(WIDTH - 150, HEIGHT - 80, 120, 50, "Επόμενο")
            self.prev_button = Button(30, HEIGHT - 80, 120, 50, "Προηγούμενο")
            self.finish_button = Button(WIDTH - 320, 20, 120, 50, "Παράδωση")
        else:
            self.next_button = Button(WIDTH - 150, HEIGHT - 80, 120, 50, "Next")
            self.prev_button = Button(30, HEIGHT - 80, 120, 50, "Previous")
            self.finish_button = Button(WIDTH - 320, 20, 120, 50, "Give Up")

    def load_phone_data(self, filename):
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        name = parts[0]
                        phone = parts[1]
                        data.append((name, phone))
            print(f"Φορτώθηκαν {len(data)} εγγραφές από το {filename}")
        except FileNotFoundError:
            print(f"Το αρχείο {filename} δεν βρέθηκε.")
            # ΔΕΝ ΔΗΜΙΟΥΡΓΟΥΜΕ SAMPLE DATA - ΕΠΙΤΡΕΠΟΥΜΕ ΚΕΝΗ ΛΙΣΤΑ
            data = []
        return data

    def split_into_pages(self, data):
        pages = []
        for i in range(0, len(data), self.entries_per_page):
            page = data[i:i + self.entries_per_page]
            pages.append(page)
        return pages

    def create_numpad(self):
        self.numpad_buttons = []
        numpad_width = 60
        numpad_height = 60
        numpad_spacing = 10
        start_x = WIDTH // 2 - (3 * numpad_width + 2 * numpad_spacing) // 2
        start_y = HEIGHT - 200

        numbers = [['1', '2', '3'],
                   ['4', '5', '6'],
                   ['7', '8', '9']]

        for row_idx, row in enumerate(numbers):
            for col_idx, num in enumerate(row):
                x = start_x + col_idx * (numpad_width + numpad_spacing)
                y = start_y + row_idx * (numpad_height + numpad_spacing)
                btn = Button(x, y, numpad_width, numpad_height, num)
                self.numpad_buttons.append(btn)

    def get_current_pages(self):
        """Επιστρέφει τις δύο τρέχουσες σελίδες"""
        left_page_index = self.current_double_page * 2
        right_page_index = left_page_index + 1

        left_page = self.pages[left_page_index] if left_page_index < len(self.pages) else []
        right_page = self.pages[right_page_index] if right_page_index < len(self.pages) else []

        return left_page, right_page

    def create_name_buttons(self):
        """Δημιουργεί τα κουμπιά για τις δύο τρέχουσες σελίδες"""
        self.name_buttons_left = []
        self.name_buttons_right = []

        left_page, right_page = self.get_current_pages()

        # Αριστερή σελίδα - ΜΙΚΡΟΤΕΡΟ ΠΛΑΤΟΣ ΚΑΙ ΠΙΟ ΔΕΞΙΑ
        start_x_left = 180  # Από 160 ΣΕ 180 (20 pixels πιο δεξιά)
        start_y = 120
        button_width = 320  # Από 380 ΣΕ 320 (60 pixels μικρότερο πλάτος)
        button_height = 28
        spacing = 3

        for i, (name, phone) in enumerate(left_page):
            y = start_y + i * (button_height + spacing)
            btn = Button(start_x_left, y, button_width, button_height, f"{name} - {phone}", left_align=True)
            self.name_buttons_left.append((btn, name))

        # Δεξιά σελίδα - ΜΙΚΡΟΤΕΡΟ ΠΛΑΤΟΣ ΚΑΙ ΠΙΟ ΔΕΞΙΑ
        start_x_right = 610  # Από 590 ΣΕ 610 (20 pixels πιο δεξιά)
        for i, (name, phone) in enumerate(right_page):
            y = start_y + i * (button_height + spacing)
            btn = Button(start_x_right, y, button_width, button_height, f"{name} - {phone}", left_align=True)
            self.name_buttons_right.append((btn, name))

    def start_game(self):
        # ΕΛΕΓΧΟΣ ΑΝ ΥΠΑΡΧΟΥΝ ΔΕΔΟΜΕΝΑ
        if len(self.phone_data) == 0:
            print("Δεν υπάρχουν δεδομένα για να ξεκινήσει το παιχνίδι!")
            return

        self.state = "playing"
        self.current_double_page = 0
        self.attempts = 0
        self.selected_number = 1
        self.start_time = time.time()
        self.elapsed_time = 0
        self.found_name = False

        # Επιλογή τυχαίου ονόματος ως στόχου
        self.target_index = random.randint(0, len(self.phone_data) - 1)
        self.target_name, self.target_phone = self.phone_data[self.target_index]

        print(f"Στόχος: {self.target_name} - {self.target_phone}")
        print(f"Συνολικές double σελίδες: {self.total_double_pages}")

        # Δημιουργία κουμπιών για την πρώτη double σελίδα
        self.create_name_buttons()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == "home":
                play_text = "Παίξε" if self.language == "greek" else "Play"
                play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, play_text)
                greek_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50, "Ελληνικά")
                english_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 190, 200, 50, "English")

                play_button.check_hover(mouse_pos)
                greek_button.check_hover(mouse_pos)
                english_button.check_hover(mouse_pos)

                if play_button.is_clicked(mouse_pos, event):
                    self.start_game()
                if greek_button.is_clicked(mouse_pos, event):
                    self.language = "greek"
                    self.create_buttons()
                if english_button.is_clicked(mouse_pos, event):
                    self.language = "english"
                    self.create_buttons()

            elif self.state == "playing":
                # Έλεγχος για πλήκτρα αριθμητικής πληκτρολογίου
                for btn in self.numpad_buttons:
                    if btn.is_clicked(mouse_pos, event):
                        try:
                            num = int(btn.text)
                            self.selected_number = num
                            print(f"Επιλέχθηκε αριθμός: {num}")
                        except ValueError:
                            pass

                # Έλεγχος για κουμπιά next/prev
                if self.next_button.is_clicked(mouse_pos, event):
                    new_page = self.current_double_page + self.selected_number
                    if new_page < self.total_double_pages:
                        self.current_double_page = new_page
                        self.create_name_buttons()
                        self.attempts += 1
                        print(f"Μετάβαση {self.selected_number} double pages μπροστά: {self.current_double_page + 1}")

                if self.prev_button.is_clicked(mouse_pos, event):
                    new_page = self.current_double_page - self.selected_number
                    if new_page >= 0:
                        self.current_double_page = new_page
                        self.create_name_buttons()
                        self.attempts += 1
                        print(f"Μετάβαση {self.selected_number} double pages πίσω: {self.current_double_page + 1}")

                # Έλεγχος για κουμπιά ονομάτων
                for btn, name in self.name_buttons_left:
                    if btn.is_clicked(mouse_pos, event):
                        self.attempts += 1
                        print(f"Πατήθηκε: {name}")
                        if name == self.target_name:
                            self.elapsed_time = time.time() - self.start_time
                            self.calculate_score()
                            self.found_name = True
                            self.state = "results"
                            print("Σωστή απάντηση!")

                for btn, name in self.name_buttons_right:
                    if btn.is_clicked(mouse_pos, event):
                        self.attempts += 1
                        print(f"Πατήθηκε: {name}")
                        if name == self.target_name:
                            self.elapsed_time = time.time() - self.start_time
                            self.calculate_score()
                            self.found_name = True
                            self.state = "results"
                            print("Σωστή απάντηση!")

                if self.finish_button.is_clicked(mouse_pos, event):
                    self.elapsed_time = time.time() - self.start_time
                    self.calculate_score()
                    self.found_name = False
                    self.state = "results"
                    print("Παραίτηση από το παιχνίδι")

            elif self.state == "results":
                play_again_text = "Παίξε Ξανά" if self.language == "greek" else "Play Again"
                home_text = "Αρχική" if self.language == "greek" else "Home"

                play_again_button = Button(WIDTH // 2 - 100, HEIGHT - 160, 200, 50, play_again_text)
                home_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50, home_text)

                play_again_button.check_hover(mouse_pos)
                home_button.check_hover(mouse_pos)

                if play_again_button.is_clicked(mouse_pos, event):
                    self.start_game()
                if home_button.is_clicked(mouse_pos, event):
                    self.state = "home"

        return True

    def calculate_score(self):
        time_score = max(0, 1000 - int(self.elapsed_time * 10))
        attempt_factor = max(0.1, 1.0 - (self.attempts * 0.05))
        self.score = int(time_score * attempt_factor)

    def draw_transparent_overlay(self):
        """Σχεδιάζει το SEMI_TRANSPARENT overlay πάνω από το background"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT)
        screen.blit(overlay, (0, 0))

    def draw(self):
        # Σχεδίαση φόντου
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((100, 100, 100))

        # Προσθήκη SEMI_TRANSPARENT overlay σε ΟΛΕΣ τις οθόνες
        self.draw_transparent_overlay()

        if self.state == "home":
            self.draw_home_screen()
        elif self.state == "playing":
            self.draw_playing_screen()
        elif self.state == "results":
            self.draw_results_screen()

    def draw_home_screen(self):
        # Σχεδίαση κλειστού βιβλίου
        if self.closed_book_image:
            book_overlay = pygame.Surface((600, 400), pygame.SRCALPHA)
            book_overlay.fill(SEMI_TRANSPARENT)
            screen.blit(self.closed_book_image, (WIDTH // 2 - 300, HEIGHT // 2 - 200))
            screen.blit(book_overlay, (WIDTH // 2 - 300, HEIGHT // 2 - 200))

        title = font_title.render("Βρες το Όνομα" if self.language == "greek" else "Find the Name", True,
                                  TEXT_COLOR_BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        play_text = "Παίξε" if self.language == "greek" else "Play"
        play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, play_text)
        greek_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50, "Ελληνικά")
        english_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 190, 200, 50, "English")

        mouse_pos = pygame.mouse.get_pos()
        play_button.check_hover(mouse_pos)
        greek_button.check_hover(mouse_pos)
        english_button.check_hover(mouse_pos)

        play_button.draw(screen)
        greek_button.draw(screen)
        english_button.draw(screen)

    def draw_playing_screen(self):
        # Σχεδίαση στόχου και πληροφοριών
        target_text = font_medium.render(
            f"Ψάχνουμε: {self.target_name}" if self.language == "greek" else f"Find: {self.target_name}", True,
            TEXT_COLOR_BLACK)
        screen.blit(target_text, (50, 20))

        current_time = time.time() - self.start_time
        time_text = font_medium.render(
            f"Χρόνος: {current_time:.1f}s" if self.language == "greek" else f"Time: {current_time:.1f}s", True,
            TEXT_COLOR_BLACK)
        screen.blit(time_text, (WIDTH - time_text.get_width() - 20, 20))

        attempts_text = font_medium.render(
            f"Προσπάθειες: {self.attempts}" if self.language == "greek" else f"Attempts: {self.attempts}", True,
            TEXT_COLOR_BLACK)
        screen.blit(attempts_text, (WIDTH - attempts_text.get_width() - 20, 50))

        # Σχεδίαση ανοιχτών βιβλίων
        if self.phonebook_image and self.phonebook_image_flipped:
            screen.blit(self.phonebook_image, (140, 100))
            screen.blit(self.phonebook_image_flipped, (560, 100))
        else:
            pygame.draw.rect(screen, WHITE, (140, 100, 420, 350))
            pygame.draw.rect(screen, BLACK, (140, 100, 420, 350), 2)
            pygame.draw.rect(screen, WHITE, (560, 100, 420, 350))
            pygame.draw.rect(screen, BLACK, (560, 100, 420, 350), 2)

        # Αρίθμηση σελίδων
        left_page_num = self.current_double_page * 2 + 1
        right_page_num = left_page_num + 1

        left_page_text = font_medium.render(
            f"Σελίδα {left_page_num}" if self.language == "greek" else f"Page {left_page_num}", True, TEXT_COLOR_BLACK)
        right_page_text = font_medium.render(
            f"Σελίδα {right_page_num}" if self.language == "greek" else f"Page {right_page_num}", True,
            TEXT_COLOR_BLACK)

        screen.blit(left_page_text, (320, 70))
        screen.blit(right_page_text, (740, 70))

        # Σχεδίαση ονομάτων στις σελίδες
        mouse_pos = pygame.mouse.get_pos()

        for btn, _ in self.name_buttons_left:
            btn.check_hover(mouse_pos)
            btn.draw(screen)

        for btn, _ in self.name_buttons_right:
            btn.check_hover(mouse_pos)
            btn.draw(screen)

        # Σχεδίαση κουμπιών πλοήγησης
        self.next_button.check_hover(mouse_pos)
        self.prev_button.check_hover(mouse_pos)
        self.finish_button.check_hover(mouse_pos)

        self.next_button.draw(screen)
        self.prev_button.draw(screen)
        self.finish_button.draw(screen)

        # Σχεδίαση αριθμητικής πληκτρολογίου
        keyboard_start_y = HEIGHT - 220
        numpad_width = 60
        numpad_height = 60
        numpad_spacing = 10
        start_x = WIDTH // 2 - (3 * numpad_width + 2 * numpad_spacing) // 2

        numbers = [['1', '2', '3'],
                   ['4', '5', '6'],
                   ['7', '8', '9']]

        for row_idx, row in enumerate(numbers):
            for col_idx, num in enumerate(row):
                x = start_x + col_idx * (numpad_width + numpad_spacing)
                y = keyboard_start_y + row_idx * (numpad_height + numpad_spacing)
                btn = Button(x, y, numpad_width, numpad_height, num)
                btn.check_hover(mouse_pos)
                btn.draw(screen)

        # ΟΔΗΓΙΕΣ
        instructions = font_medium.render(
            f"Πατήστε Next/Prev για {self.selected_number} σελίδες" if self.language == "greek" else f"Press Next/Prev for {self.selected_number} pages",
            True, BLUE_COLOR)

        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 260))

    def draw_results_screen(self):
        title = font_title.render("Τέλος Παιχνιδιού" if self.language == "greek" else "Game Over", True,
                                  TEXT_COLOR_BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        if self.found_name:
            name_text = font_large.render(
                f"Βρήκατε: {self.target_name}" if self.language == "greek" else f"Found: {self.target_name}", True,
                TEXT_COLOR_BLACK)
        else:
            name_text = font_large.render(
                f"Δεν βρέθηκε: {self.target_name}" if self.language == "greek" else f"Not found: {self.target_name}",
                True,
                TEXT_COLOR_BLACK)

        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 180))

        time_text = font_large.render(
            f"Χρόνος: {self.elapsed_time:.2f}s" if self.language == "greek" else f"Time: {self.elapsed_time:.2f}s",
            True, TEXT_COLOR_BLACK)
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 230))

        attempts_text = font_large.render(
            f"Προσπάθειες: {self.attempts}" if self.language == "greek" else f"Attempts: {self.attempts}", True,
            TEXT_COLOR_BLACK)
        screen.blit(attempts_text, (WIDTH // 2 - attempts_text.get_width() // 2, 280))

        score_text = font_large.render(f"Score: {self.score}" if self.language == "greek" else f"Score: {self.score}",
                                       True, TEXT_COLOR_BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 330))

        play_again_text = "Παίξε Ξανά" if self.language == "greek" else "Play Again"
        home_text = "Αρχική" if self.language == "greek" else "Home"

        play_again_button = Button(WIDTH // 2 - 100, HEIGHT - 160, 200, 50, play_again_text)
        home_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50, home_text)

        mouse_pos = pygame.mouse.get_pos()
        play_again_button.check_hover(mouse_pos)
        home_button.check_hover(mouse_pos)

        play_again_button.draw(screen)
        home_button.draw(screen)


# Κύρια λειτουργία
def main():
    clock = pygame.time.Clock()
    game = PhoneBookGame()

    running = True
    while running:
        running = game.handle_events()
        game.draw()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()