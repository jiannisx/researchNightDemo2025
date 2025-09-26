import time
from Utils.utils import *
from Gui.Gui import *

# PyGame Initialization
pygame.init()
pygame.mixer.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Βρες την Εικόνα")

# Global variables (μπορείτε να αλλάξετε αυτές τις διαδρομές)
TARGET_IMAGE_PATH = "FindTheImage\\dataset\\landscape.jpg"  # διαδρομή εικόνας-στόχου (global για και τα δύο παιχνίδια)
IMAGES_FOLDER = "FindTheImage\\dataset"  # φάκελος dataset (global)
SOUNDS_FOLDER = "FindTheImage\\sounds"  # φάκελος ήχων

# --- ΣΤΑΤΙΚΕΣ ΕΙΚΟΝΕΣ ΓΙΑ ΤΟ 2Ο ΠΑΙΧΝΙΔΙ (σταθερές, θα τις αλλάξετε εσείς) ---
SECOND_GAME_IMAGES = [
    "FindTheImage\\dataset\\landscape_1.jpg",
    "FindTheImage\\dataset\\dog.jpg",
    "FindTheImage\\dataset\\santorini.jpg",
    "FindTheImage\\dataset\\poppy.jpg"
]
# Το ποια από αυτές είναι αρχικά "active" (θα την αλλάξετε με το επιθυμητό path)
SECOND_GAME_ACTIVE_PATH = SECOND_GAME_IMAGES[0]

# Για τα επόμενα στάδια του 2ου παιχνιδιού, θα χρησιμοποιήσουμε placeholders —
# θα αντικαταστήσετε τα paths ανάλογα:
SECOND_STAGE_IMAGES = {
    # όταν πατήσει την active της πρώτης οθόνης -> δείχνει αυτές τις δύο
    "stage1": ["FindTheImage\\dataset\\landscape_wrong.jpg", "FindTheImage\\dataset\\landscape_2.jpg"],
    # μετά -> τελική δύο εικόνες (una θα είναι active)
    "stage2": ["FindTheImage\\dataset\\landscape.jpg", "FindTheImage\\dataset\\landscape_3.jpg"]
}
# Από αυτές, σε κάθε stage επιλέγουμε ποια είναι active (paths)
SECOND_STAGE1_ACTIVE = SECOND_STAGE_IMAGES["stage1"][1]
SECOND_STAGE2_ACTIVE = SECOND_STAGE_IMAGES["stage2"][0]

# Fonts
font_small = pygame.font.SysFont("Arial", 16)
font_medium = pygame.font.SysFont("Arial", 20)
font_medium_bold = pygame.font.SysFont("Arial", 20, bold=True)
font_large = pygame.font.SysFont("Arial", 24)
font_title = pygame.font.SysFont("Arial", 32, bold=True)

# Sound effects
try:
    correct_sound = pygame.mixer.Sound(os.path.join(SOUNDS_FOLDER, "correct.wav"))
    wrong_sound = pygame.mixer.Sound(os.path.join(SOUNDS_FOLDER, "wrong.wav"))
except:
    # placeholder ήχοι
    try:
        correct_sound = pygame.mixer.Sound(buffer=bytearray([0] * 44))
        wrong_sound = pygame.mixer.Sound(buffer=bytearray([0] * 44))
    except:
        correct_sound = None
        wrong_sound = None
    print("Προειδοποίηση: Δεν βρέθηκαν τα αρχεία ήχων. Χρήση placeholder.")

# --- Κεντρική διαχείριση παιχνιδιού (GameManager) ---
class GameManager:
    def __init__(self, language="greek"):
        # state: 'home', 'playing1', 'results1', 'playing2', 'results2'
        self.state = "home"
        self.language = language

        # Κοινά στοιχεία
        self.target_image = load_target_image(TARGET_IMAGE_PATH)
        self.dataset_images, self.dataset_paths = load_images_from_folder(IMAGES_FOLDER)

        # Game1 variables (διατηρούμε παρόμοια λειτουργικότητα)
        self.game1_images = self.dataset_images[:]  # list of Surfaces (όχι απαραίτητα χρησιμοποιούνται όλα)
        self.game1_paths = self.dataset_paths[:]
        self.game1_images_per_page = 1
        self.game1_current_page = 0
        self.game1_total_pages = (len(self.game1_images) + self.game1_images_per_page - 1) // self.game1_images_per_page
        self.game1_image_buttons = []
        self.game1_attempts = 0
        self.game1_start_time = 0
        self.game1_elapsed = 0.0
        self.game1_correct_found = False

        # Game2 variables (πολυβάθμια ροή)
        # Σταθερές εικόνες (χρησιμοποιήστε τα global paths που ορίσατε παραπάνω)
        self.game2_stage = 0  # 0: initial 4, 1: stage1 (2 images), 2: stage2 (2 images)
        self.game2_attempts = 0
        self.game2_start_time = 0
        self.game2_elapsed = 0.0
        self.game2_finished = False

        # Φορτώνουμε τις εικόνες για το 2ο παιχνίδι από τα σταθερά paths
        self.game2_all_paths = SECOND_GAME_IMAGES[:]  # αρχικά 4 paths
        self.game2_stage1_paths = SECOND_STAGE_IMAGES["stage1"][:]
        self.game2_stage2_paths = SECOND_STAGE_IMAGES["stage2"][:]

        # active paths (οι μόνες εικόνες που έχουν listener per stage)
        self.game2_active_stage0 = SECOND_GAME_ACTIVE_PATH
        self.game2_active_stage1 = SECOND_STAGE1_ACTIVE
        self.game2_active_stage2 = SECOND_STAGE2_ACTIVE

        # Buttons/Images surfaces for game2 (θα γεμιστούν)
        self.game2_buttons_stage0 = []  # list of ImageButton
        self.game2_buttons_stage1 = []
        self.game2_buttons_stage2 = []

        # History για results (θα κρατήσει (time, attempts) για game1 & game2)
        self.history = {
            "game1": None,  # (elapsed_time, attempts)
            "game2": None
        }

        # Buttons (γενικά)
        self.next_button = Button(WIDTH - 150, HEIGHT - 80, 120, 50, "Επόμενο" if language == "greek" else "Next")
        self.prev_button = Button(30, HEIGHT - 80, 160, 50, "Προηγούμενο" if language == "greek" else "Previous")
        self.finish_button = Button(WIDTH - 150, 20, 120, 50, "Τέλος" if language == "greek" else "Give Up")
        self.select_button = Button(WIDTH // 2 - 60, HEIGHT - 80, 120, 50,
                                    "Επιλογή" if language == "greek" else "Select")

        # background
        try:
            self.background_image = pygame.image.load("FindTheImage/background.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
        except:
            self.background_image = None

        # αρχικοποίηση κουμπιών για game1
        self.game1_image_buttons = self.create_game1_image_buttons()

        # αρχικοποίηση κουμπιών για game2 (stage0)
        self.build_game2_stage0_buttons()
        self.build_game2_stage1_buttons()
        self.build_game2_stage2_buttons()

    # ------------------ Game1 helpers ------------------
    def create_game1_image_buttons(self):
        buttons = []
        start_idx = self.game1_current_page * self.game1_images_per_page
        end_idx = min(start_idx + self.game1_images_per_page, len(self.game1_images))
        positions = [(WIDTH // 2 - 150, HEIGHT // 2 - 150)]
        for i in range(start_idx, end_idx):
            pos_idx = i - start_idx
            if pos_idx < len(positions):
                img = self.game1_images[i]
                path = self.game1_paths[i] if i < len(self.game1_paths) else None
                btn = ImageButton(img, positions[pos_idx][0], positions[pos_idx][1], 300, 300, path, clickable=True)
                buttons.append((i, btn))
        return buttons

    # ------------------ Game2 builders ------------------
    def build_game2_stage0_buttons(self):
        # 4 εικόνες σε 2x2 grid στο κέντρο
        self.game2_buttons_stage0 = []
        imgs = []
        for p in self.game2_all_paths:
            imgs.append(safe_load_image(p, fallback_size=(150,150)))
        # θέσεις
        start_x = WIDTH // 2 - 320//2
        start_y = HEIGHT // 2 - 150
        spacing_x = 170
        spacing_y = 170
        coords = [
            (start_x, start_y),
            (start_x + spacing_x, start_y),
            (start_x, start_y + spacing_y),
            (start_x + spacing_x, start_y + spacing_y),
        ]
        for i, img in enumerate(imgs):
            path = self.game2_all_paths[i] if i < len(self.game2_all_paths) else None
            clickable = True  # όλες είναι "κουμπιά" αλλά μόνο η active θα έχει listener στην λογική του παιχνιδιού
            btn = ImageButton(img, coords[i][0], coords[i][1], 150, 150, path, clickable=clickable)
            self.game2_buttons_stage0.append(btn)

    def build_game2_stage1_buttons(self):
        self.game2_buttons_stage1 = []
        imgs = [safe_load_image(p, fallback_size=(180,180)) for p in self.game2_stage1_paths]
        # θέσεις στην μέση
        x1 = WIDTH//2 - 200
        x2 = WIDTH//2 + 20
        y = HEIGHT//2 - 90
        btn1 = ImageButton(imgs[0], x1, y, 180, 180, self.game2_stage1_paths[0], clickable=True)
        btn2 = ImageButton(imgs[1], x2, y, 180, 180, self.game2_stage1_paths[1], clickable=True)
        self.game2_buttons_stage1 = [btn1, btn2]

    def build_game2_stage2_buttons(self):
        self.game2_buttons_stage2 = []
        imgs = [safe_load_image(p, fallback_size=(200,200)) for p in self.game2_stage2_paths]
        x1 = WIDTH//2 - 220
        x2 = WIDTH//2 + 20
        y = HEIGHT//2 - 80
        btn1 = ImageButton(imgs[0], x1, y, 200, 200, self.game2_stage2_paths[0], clickable=True)
        btn2 = ImageButton(imgs[1], x2, y, 200, 200, self.game2_stage2_paths[1], clickable=True)
        self.game2_buttons_stage2 = [btn1, btn2]

    # ------------------ Event Handling ------------------
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Home screen
            if self.state == "home":
                # dynamic buttons
                play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Παίξε" if self.language == "greek" else "Play")
                play_button.check_hover(mouse_pos)
                # language buttons
                greek_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Ελληνικά")
                english_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50, "English")
                greek_button.check_hover(mouse_pos)
                english_button.check_hover(mouse_pos)
                if play_button.is_clicked(mouse_pos, event):
                    # ξεκινά το Game1
                    self.start_game1()
                if greek_button.is_clicked(mouse_pos, event):
                    self.__init__("greek")
                if english_button.is_clicked(mouse_pos, event):
                    self.__init__("english")

            # ---------------- Game 1 playing ----------------
            elif self.state == "playing1":
                # εικόνες
                for idx, btn in self.game1_image_buttons:
                    if btn.is_clicked(mouse_pos, event):
                        # Κάθε κλικ αυξάνει attempts (μόνο όταν παίζει)
                        self.game1_attempts += 1
                        # compare by path (όπως ζητήσατε)
                        if btn.image_path == TARGET_IMAGE_PATH:
                            # σωστό
                            self.game1_elapsed = time.time() - self.game1_start_time
                            self.game1_correct_found = True
                            if correct_sound:
                                correct_sound.play()
                            # overlay πράσινο
                            overlay = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                            overlay.fill((0, 255, 0, 128))
                            screen.blit(overlay, btn.rect)
                            pygame.display.flip()
                            pygame.time.delay(400)
                            # καταγραφή ιστορικού
                            self.history["game1"] = (self.game1_elapsed, self.game1_attempts)
                            self.state = "results1"
                            break
                        else:
                            # λάθος
                            if wrong_sound:
                                wrong_sound.play()
                            overlay = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                            overlay.fill((255, 0, 0, 128))
                            screen.blit(overlay, btn.rect)
                            pygame.display.flip()
                            pygame.time.delay(300)
                # next / prev λειτουργικότητα (σαν σελίδες)
                if self.next_button.is_clicked(mouse_pos, event) and self.game1_current_page < self.game1_total_pages - 1:
                    self.game1_current_page += 1
                    self.game1_image_buttons = self.create_game1_image_buttons()
                    self.game1_attempts += 1
                if self.prev_button.is_clicked(mouse_pos, event) and self.game1_current_page > 0:
                    self.game1_current_page -= 1
                    self.game1_image_buttons = self.create_game1_image_buttons()
                    self.game1_attempts += 1
                if self.select_button.is_clicked(mouse_pos, event):
                    # επιλέγει την εικόνα κάτω από το κέντρο
                    self.game1_attempts += 1
                    found = False
                    for idx, btn in self.game1_image_buttons:
                        if btn.image_path == TARGET_IMAGE_PATH:
                            found = True
                            self.game1_elapsed = time.time() - self.game1_start_time
                            self.game1_correct_found = True
                            if correct_sound:
                                correct_sound.play()
                            overlay = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                            overlay.fill((0, 255, 0, 128))
                            screen.blit(overlay, btn.rect)
                            pygame.display.flip()
                            pygame.time.delay(400)
                            self.history["game1"] = (self.game1_elapsed, self.game1_attempts)
                            self.state = "results1"
                            break
                    if not found:
                        if wrong_sound:
                            wrong_sound.play()
                        # βάλε κόκκινο overlay στην εικόνα που έδειχνε στη σελίδα
                        for idx, btn in self.game1_image_buttons:
                            if btn.image_path != TARGET_IMAGE_PATH:  # δηλαδή είναι λάθος
                                overlay = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                                overlay.fill((255, 0, 0, 128))
                                screen.blit(overlay, btn.rect)
                                pygame.display.flip()
                                pygame.time.delay(300)
                                break

                if self.finish_button.is_clicked(mouse_pos, event):
                    self.game1_elapsed = time.time() - self.game1_start_time
                    self.history["game1"] = (self.game1_elapsed, self.game1_attempts)
                    self.state = "results1"

            # ---------------- Results 1 ----------------
            elif self.state == "results1":
                # Εμφανίζουμε κουμπί Next Game -> θα πηγαίνει στο game2
                next_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50,
                                     "Επόμενο Παιχνίδι" if self.language == "greek" else "Next Game")
                if next_button.is_clicked(mouse_pos, event):
                    # ξεκινάμε game2
                    self.start_game2()

            # ---------------- Game 2 playing ----------------
            elif self.state == "playing2":
                # stage0: 4 εικόνες
                if self.game2_stage == 0:
                    for btn in self.game2_buttons_stage0:
                        # όλες "κουμπιά" αλλά μόνο μία είναι active σε logic
                        if btn.is_clicked(mouse_pos, event):
                            # Αυξάνουμε attempts (μόνο όταν παίζει)
                            self.game2_attempts += 1
                            # αν είναι η active εικόνα (με σύγκριση path)
                            if btn.image_path == self.game2_active_stage0:
                                # προχωράμε στο stage1
                                if correct_sound:
                                    correct_sound.play()
                                self.game2_stage = 1
                                # (ανανεώνουμε το χρόνο αν χρειάζεται)
                                # αφήνουμε attempts όπως είναι (έχει ήδη αυξηθεί)
                            else:
                                # λάθος πάτημα -> κόκκινο overlay
                                if wrong_sound:
                                    wrong_sound.play()
                                overlay = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                                overlay.fill((255, 0, 0, 128))
                                screen.blit(overlay, btn.rect)
                                pygame.display.flip()
                                pygame.time.delay(250)
                elif self.game2_stage == 1:
                    # εμφανίζονται 2 εικόνες (stage1). Μόνο μία από αυτές είναι active (game2_active_stage1)
                    for btn in self.game2_buttons_stage1:
                        # αν πατηθεί οποιοδήποτε, μετράει σαν προσπάθεια
                        if btn.is_clicked(mouse_pos, event):
                            self.game2_attempts += 1
                            if btn.image_path == self.game2_active_stage1:
                                if correct_sound:
                                    correct_sound.play()
                                self.game2_stage = 2
                            else:
                                if wrong_sound:
                                    wrong_sound.play()
                                overlay = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                                overlay.fill((255, 0, 0, 128))
                                screen.blit(overlay, btn.rect)
                                pygame.display.flip()
                                pygame.time.delay(250)
                elif self.game2_stage == 2:
                    for btn in self.game2_buttons_stage2:
                        if btn.is_clicked(mouse_pos, event):
                            self.game2_attempts += 1
                            if btn.image_path == self.game2_active_stage2:
                                # τελείωσε το 2ο παιχνίδι
                                self.game2_elapsed = time.time() - self.game2_start_time
                                if correct_sound:
                                    correct_sound.play()
                                # αποθηκεύουμε history και πηγαίνουμε σε results2
                                self.history["game2"] = (self.game2_elapsed, self.game2_attempts)
                                self.state = "results2"
                            else:
                                if wrong_sound:
                                    wrong_sound.play()
                                overlay = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                                overlay.fill((255, 0, 0, 128))
                                screen.blit(overlay, btn.rect)
                                pygame.display.flip()
                                pygame.time.delay(250)

                # Επιπλέον: κουμπί Finish για να παρατήσει
                if self.finish_button.is_clicked(mouse_pos, event):
                    self.game2_elapsed = time.time() - self.game2_start_time
                    self.history["game2"] = (self.game2_elapsed, self.game2_attempts)
                    self.state = "results2"

            # ---------------- Results 2 ----------------
            elif self.state == "results2":
                # Κουμπί Next Game -> προς το παρόν επιστρέφει στην αρχική (όπως ζητήσατε)
                next_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50,
                                     "Επόμενο Παιχνίδι" if self.language == "greek" else "Next Game")
                if next_button.is_clicked(mouse_pos, event):
                    # για τώρα επιστροφή στην αρχική
                    self.__init__(self.language)  # reset όλα

        return True

    # ------------------ State Starters ------------------
    def start_game1(self):
        print(self.game1_paths)
        idx = self.game1_paths.index(TARGET_IMAGE_PATH)
        self.game1_paths.pop(idx)
        self.game1_images.pop(idx)
        insert_idx = max(len(self.game1_images) - 5, 0) + random.randint(0, min(4, len(self.game1_images)-max(len(self.game1_images)-5,0)))
        self.game1_paths.insert(insert_idx, TARGET_IMAGE_PATH)
        self.game1_images.insert(insert_idx, self.target_image)

        self.state = "playing1"
        self.game1_attempts = 0
        self.game1_start_time = time.time()
        self.game1_elapsed = 0.0
        self.game1_correct_found = False
        self.game1_current_page = 0
        self.game1_image_buttons = self.create_game1_image_buttons()

    def start_game2(self):
        self.state = "playing2"
        self.game2_stage = 0
        self.game2_attempts = 0
        self.game2_start_time = time.time()
        self.game2_elapsed = 0.0
        self.game2_finished = False
        # rebuild stage buttons in case paths changed
        self.build_game2_stage0_buttons()
        self.build_game2_stage1_buttons()
        self.build_game2_stage2_buttons()

    # ------------------ Drawing ------------------
    def draw(self):
        # background
        if self.background_image:
            screen.blit(self.background_image, (0,0))
        else:
            screen.fill((50,50,50))

        if self.state == "home":
            self.draw_home_screen()
        elif self.state == "playing1":
            self.draw_playing1()
        elif self.state == "results1":
            self.draw_results_screen(game=1)
        elif self.state == "playing2":
            self.draw_playing2()
        elif self.state == "results2":
            self.draw_results_screen(game=2)

    def draw_home_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT)
        screen.blit(overlay, (0,0))
        title = font_title.render("Βρες την Εικόνα" if self.language == "greek" else "Find the Image", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        # Play button
        play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Παίξε" if self.language == "greek" else "Play")
        play_button.check_hover(pygame.mouse.get_pos())
        play_button.draw(screen)
        # language buttons
        greek_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Ελληνικά")
        greek_button.check_hover(pygame.mouse.get_pos())
        greek_button.draw(screen)
        english_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50, "English")
        english_button.check_hover(pygame.mouse.get_pos())
        english_button.draw(screen)

    def draw_playing1(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT)
        screen.blit(overlay, (0,0))
        title_text = font_medium_bold.render("Ψάχνουμε αυτή την εικόνα:" if self.language == "greek" else "Find this image:", True, BLACK)
        screen.blit(title_text, (50,20))
        # target μικρό στην πάνω αριστερή γωνία
        target_rect = pygame.Rect(50,50,150,150)
        screen.blit(pygame.transform.scale(self.target_image,(150,150)), target_rect)
        # page text
        page_font = pygame.font.SysFont(None, 24)
        page_text = page_font.render(f"Σελίδα {self.game1_current_page+1}/{self.game1_total_pages}" if self.language=="greek" else f"Page {self.game1_current_page+1}/{self.game1_total_pages}", True, BLACK)
        screen.blit(page_text, (WIDTH//2 - 40, HEIGHT//2 - 180))
        # image buttons
        for _, btn in self.game1_image_buttons:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)
        # navigation buttons
        self.next_button.check_hover(pygame.mouse.get_pos()); self.prev_button.check_hover(pygame.mouse.get_pos())
        self.next_button.draw(screen); self.prev_button.draw(screen)
        self.finish_button.check_hover(pygame.mouse.get_pos()); self.finish_button.draw(screen)
        self.select_button.check_hover(pygame.mouse.get_pos()); self.select_button.draw(screen)
        # χρόνος
        self.game1_elapsed = time.time() - self.game1_start_time
        time_text = font_medium_bold.render(f"Χρόνος: {self.game1_elapsed:.1f}s", True, BLACK)
        screen.blit(time_text, (WIDTH - time_text.get_width() - 20, 80))

    def draw_playing2(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT)
        screen.blit(overlay,(0,0))
        title_text = font_medium_bold.render("Ψάχνουμε αυτή την εικόνα:" if self.language == "greek" else "Find this image:", True, BLACK)
        screen.blit(title_text, (50,20))
        # target πάνω αριστερά (ίδιο target και folder όπως ζητήσατε)
        screen.blit(pygame.transform.scale(self.target_image,(150,150)), (50,50))
        # εμφανίζουμε το stage που βρισκόμαστε
        stage_text = font_medium.render(f"Εύρεση παρόμοιας ή ίδιας εικόνας" if self.language=="greek" else f"Search for a similar or the same image", True, BLACK)
        screen.blit(stage_text, (WIDTH//2 - 130, HEIGHT//2 - 200))

        # Stage 0: 4 εικόνες
        if self.game2_stage == 0:
            for btn in self.game2_buttons_stage0:
                # only the active path will proceed in logic (στο handle_events συγκρίνουμε paths)
                btn.check_hover(pygame.mouse.get_pos())
                btn.draw(screen)
        elif self.game2_stage == 1:
            for btn in self.game2_buttons_stage1:
                btn.check_hover(pygame.mouse.get_pos())
                btn.draw(screen)
        elif self.game2_stage == 2:
            for btn in self.game2_buttons_stage2:
                btn.check_hover(pygame.mouse.get_pos())
                btn.draw(screen)

        # finish button & time
        self.finish_button.check_hover(pygame.mouse.get_pos()); self.finish_button.draw(screen)
        self.game2_elapsed = time.time() - self.game2_start_time
        time_text = font_medium_bold.render(f"Χρόνος: {self.game2_elapsed:.1f}s", True, BLACK)
        screen.blit(time_text, (WIDTH - time_text.get_width() - 20, 80))

    def draw_results_screen(self, game=1):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT)
        screen.blit(overlay,(0,0))
        title = font_title.render("Τέλος Παιχνιδιού" if self.language=="greek" else "Game Over", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

        # Εμφάνιση των αποτελεσμάτων και των δύο παιχνιδιών σε δύο στήλες
        col1_x = WIDTH//4 - 120
        col2_x = WIDTH*3//4 - 120
        header1 = font_medium_bold.render("Παιχνίδι 1" if self.language=="greek" else "Game 1", True, BLACK)
        header2 = font_medium_bold.render("Παιχνίδι 2" if self.language=="greek" else "Game 2", True, BLACK)
        screen.blit(header1, (col1_x, 110))
        screen.blit(header2, (col2_x, 110))

        # Χρόνοι & προσπάθειες από history
        g1 = self.history.get("game1")
        g2 = self.history.get("game2")

        # Ετοιμάζουμε times για χρωματισμό (μπορεί να είναι None)
        t1 = g1[0] if g1 else None
        a1 = g1[1] if g1 else None
        t2 = g2[0] if g2 else None
        a2 = g2[1] if g2 else None

        # Βρίσκουμε καλύτερο/χειρότερο χρόνο για highlight (όταν υπάρχουν και τα δύο)
        best = None
        worst = None
        if t1 is not None and t2 is not None:
            if t1 < t2 and a1 != 0:
                best = ("g1", t1)
                worst = ("g2", t2)
            else:
                best = ("g2", t2)
                worst = ("g1", t1)

        # Σχεδίαση για game1
        if t1 is not None:
            color = BLACK
            if best and best[0]=="g1": color = DARK_GREEN
            if worst and worst[0]=="g1": color = DARK_RED
            time_text = font_large.render(f"Χρόνος: {t1:.2f}s" if self.language=="greek" else f"Time: {t1:.2f}s", True, color)
            screen.blit(time_text, (col1_x, 150))

            color_attempts = BLACK
            if a2 is not None:
                if a1 < a2 and a1 != 0: color_attempts = DARK_GREEN
                elif a1 > a2: color_attempts = DARK_RED
            attempts_text = font_large.render(f"Προσπάθειες: {a1}" if self.language=="greek" else f"Attempts: {a1}", True, color_attempts)
            screen.blit(attempts_text, (col1_x, 200))
        else:
            screen.blit(font_large.render("Χρόνος: -" if self.language=="greek" else "Time: -", True, BLACK), (col1_x, 150))
            screen.blit(font_large.render("Προσπάθειες: -" if self.language=="greek" else "Attempts: -", True, BLACK), (col1_x, 200))

        # Σχεδίαση για game2
        next_button = None
        if t2 is not None:
            color = BLACK
            if best and best[0]=="g2": color = DARK_GREEN
            if worst and worst[0]=="g2": color = DARK_RED
            time_text = font_large.render(f"Χρόνος: {t2:.2f}s" if self.language=="greek" else f"Time: {t2:.2f}s", True, color)
            screen.blit(time_text, (col2_x, 150))
            color_attempts = BLACK
            if a1 is not None:  # αν υπάρχει και πρώτο παιχνίδι για να συγκρίνουμε
                if a2 < a1 or a1 == 0: color_attempts = DARK_GREEN
                elif a2 > a1: color_attempts = DARK_RED
            attempts_text = font_large.render(f"Προσπάθειες: {a2}" if self.language=="greek" else f"Attempts: {a2}", True, color_attempts)
            screen.blit(attempts_text, (col2_x, 200))
            next_button = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50,
                                 "Παίξε Ξανά" if self.language=="greek" else "Play Again")
        else:
            screen.blit(font_large.render("Χρόνος: -" if self.language=="greek" else "Time: -", True, BLACK), (col2_x, 150))
            screen.blit(font_large.render("Προσπάθειες: -" if self.language=="greek" else "Attempts: -", True, BLACK), (col2_x, 200))
            next_button = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50,
                                 "Επόμενο Παιχνίδι" if self.language=="greek" else "Next Game")

        next_button.check_hover(pygame.mouse.get_pos())
        next_button.draw(screen)
