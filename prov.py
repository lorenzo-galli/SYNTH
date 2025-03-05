import pygame
import synth
import cevent
import time
import random

# Definiamo alcune costanti per l'interfaccia grafica
WIDTH, HEIGHT = 1280, 800
BUTTON_RADIUS = 20
FONT_SIZE1 = 30
FONT_SIZE2 = 15
FALLING_SPEED = 2      # Pixels per frame (default for Easy)
SPAWN_INTERVAL = 2500  # Milliseconds between falling notes (default for Easy)

class Gioco(cevent.CEvent):

    def __init__(self):
        self.schermata = None
        self.ottava = 4
        self.font = None  # Imposta a None prima di inizializzare il font
        self.running = True
        self.state = "menu"  # "menu" or "game"

        # Button positions for changing octave (gameplay)
        self.button_up_center = (100, 700)
        self.button_down_center = (1130, 700)

        self.schermata = [
            (0, 0, 1260, 800)
        ]

        self.white_keys = [
            (265, 600, 50, 150, 'Do'),
            (315, 600, 50, 150, 'Re'),
            (365, 600, 50, 150, 'Mi'),
            (415, 600, 50, 150, 'Fa'),
            (465, 600, 50, 150, 'Sol'),
            (515, 600, 50, 150, 'La'),
            (565, 600, 50, 150, 'Si')
        ]

        self.black_keys = [
            (295, 600, 40, 90, 'Do#'),
            (345, 600, 40, 90, 'Re#'),
            (445, 600, 40, 90, 'Fa#'),
            (495, 600, 40, 90, 'Sol#'),
            (545, 600, 40, 90, 'La#'),
        ]

        self.white_keys_plus = [
            (615, 600, 50, 150, 'Do'),
            (665, 600, 50, 150, 'Re'),
            (715, 600, 50, 150, 'Mi'),
            (765, 600, 50, 150, 'Fa'),
            (815, 600, 50, 150, 'Sol'),
            (865, 600, 50, 150, 'La'),
            (915, 600, 50, 150, 'Si'),
        ]

        self.black_keys_plus = [
            (645, 600, 40, 90, 'Do#'),
            (695, 600, 40, 90, 'Re#'),
            (795, 600, 40, 90, 'Fa#'),
            (845, 600, 40, 90, 'Sol#'),
            (895, 600, 40, 90, 'La#'),
        ]
        
        # Dizionari per la gestione del gioco
        self.illuminated_keys = {}
        self.keydown_event = set()
        self.trail_data = {} 

        # Falling note management and score tracking
        self.falling_notes = []
        self.last_spawn_time = 0
        self.score = 0

        # --- Menu and level selection ---
        self.start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 60)
        self.easy_button_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 100, 50)
        self.medium_button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 150, 100, 50)
        self.hard_button_rect = pygame.Rect(WIDTH//2 + 50, HEIGHT//2 - 150, 100, 50)
        self.selected_level = "Easy"  # default level

        # Exit button in-game (to return to menu)
        self.exit_button_rect = pygame.Rect(WIDTH - 120, 20, 100, 40)
        
        # Mouse state for gameplay
        self.mouse_pressed = False

    def on_init(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        pygame.init()
        self.schermata = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Synth")
        try:
            self.font1 = pygame.font.Font(None, FONT_SIZE1)
            self.font2 = pygame.font.Font(None, FONT_SIZE2)
        except pygame.error as e:
            print(f"Errore nel caricare il font: {e}")
            exit()

    def on_cleanup(self):
        pygame.quit()

    def spawn_falling_note(self):
        key_list = random.choice([self.white_keys, self.black_keys,
                                   self.white_keys_plus, self.black_keys_plus])
        x, y, w, h, note = random.choice(key_list)
        if key_list in [self.white_keys, self.black_keys]:
            note_full = f'{note}-{self.ottava}'
            color = (0, 200, 200) if key_list == self.white_keys else (0, 200, 140)
        else:
            note_full = f'{note}-{self.ottava + 1}'
            color = (0, 200, 200) if key_list == self.white_keys_plus else (0, 200, 140)
        falling_note = {
            "note": note_full,
            "center_x": x + w // 2,
            "y": -20,
            "color": color
        }
        self.falling_notes.append(falling_note)

    def update_falling_notes(self):
        for note in self.falling_notes[:]:
            note["y"] += FALLING_SPEED
            if note["y"] > HEIGHT:
                self.falling_notes.remove(note)

    def check_falling_collision(self, note_played):
        # Check if a falling note that matches is within the hit zone (e.g., y between 550 and 650)
        for falling in self.falling_notes[:]:
            if falling["note"] == note_played and 550 <= falling["y"] <= 650:
                self.falling_notes.remove(falling)
                self.score += 10

    # --- Menu event handling ---
    def handle_menu_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.start_button_rect.collidepoint(mouse_pos):
                self.state = "game"
                self.score = 0
                self.falling_notes.clear()
                self.last_spawn_time = pygame.time.get_ticks()
            elif self.easy_button_rect.collidepoint(mouse_pos):
                self.selected_level = "Easy"
                global SPAWN_INTERVAL, FALLING_SPEED
                SPAWN_INTERVAL = 2500
                FALLING_SPEED = 2
            elif self.medium_button_rect.collidepoint(mouse_pos):
                self.selected_level = "Medium"
                SPAWN_INTERVAL = 2000
                FALLING_SPEED = 3
            elif self.hard_button_rect.collidepoint(mouse_pos):
                self.selected_level = "Hard"
                SPAWN_INTERVAL = 1500
                FALLING_SPEED = 4

    def draw_start_page(self):
        self.schermata.fill((50, 50, 50))
        title = self.font1.render("Synth Game", True, (255, 255, 255))
        self.schermata.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        # Draw level selection buttons
        pygame.draw.rect(self.schermata, (0, 200, 0), self.easy_button_rect)
        easy_text = self.font2.render("Easy", True, (0, 0, 0))
        self.schermata.blit(easy_text, (self.easy_button_rect.centerx - easy_text.get_width()//2,
                                        self.easy_button_rect.centery - easy_text.get_height()//2))
        pygame.draw.rect(self.schermata, (200, 200, 0), self.medium_button_rect)
        medium_text = self.font2.render("Medium", True, (0, 0, 0))
        self.schermata.blit(medium_text, (self.medium_button_rect.centerx - medium_text.get_width()//2,
                                          self.medium_button_rect.centery - medium_text.get_height()//2))
        pygame.draw.rect(self.schermata, (200, 0, 0), self.hard_button_rect)
        hard_text = self.font2.render("Hard", True, (0, 0, 0))
        self.schermata.blit(hard_text, (self.hard_button_rect.centerx - hard_text.get_width()//2,
                                        self.hard_button_rect.centery - hard_text.get_height()//2))
        # Draw start button
        pygame.draw.rect(self.schermata, (0, 0, 200), self.start_button_rect)
        start_text = self.font1.render("START", True, (255, 255, 255))
        self.schermata.blit(start_text, (self.start_button_rect.centerx - start_text.get_width()//2,
                                         self.start_button_rect.centery - start_text.get_height()//2))
        pygame.display.flip()

    # --- In-game events (gameplay) ---
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        # In-game: Check exit button first.
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.exit_button_rect.collidepoint(event.pos):
                self.state = "menu"
                return
            else:
                mouse_pos = event.pos
                self.mouse_pressed = True
                # Check black keys
                for x, y, w, h, note in self.black_keys:
                    if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                        note_played = f'{note}-{self.ottava}'
                        synth.play(note_played)
                        self.illuminated_keys[note_played] = pygame.time.get_ticks()
                        self.keydown_event.add(note_played)
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 140)}
                        # Check falling collision
                        self.check_falling_collision(note_played)
                        return
                # Check black keys plus
                for x, y, w, h, note in self.black_keys_plus:
                    if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                        note_played = f'{note}-{self.ottava + 1}'
                        synth.play(note_played)
                        self.illuminated_keys[note_played] = pygame.time.get_ticks()
                        self.keydown_event.add(note_played)
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 140)}
                        self.check_falling_collision(note_played)
                        return
                # Check white keys
                for x, y, w, h, note in self.white_keys:
                    if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                        note_played = f'{note}-{self.ottava}'
                        synth.play(note_played)
                        self.illuminated_keys[note_played] = pygame.time.get_ticks()
                        self.keydown_event.add(note_played)
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 200)}
                        self.check_falling_collision(note_played)
                        return
                # Check white keys plus
                for x, y, w, h, note in self.white_keys_plus:
                    if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                        note_played = f'{note}-{self.ottava + 1}'
                        synth.play(note_played)
                        self.illuminated_keys[note_played] = pygame.time.get_ticks()
                        self.keydown_event.add(note_played)
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 200)}
                        self.check_falling_collision(note_played)
                        return

        if event.type == pygame.MOUSEBUTTONUP:
            self.mouse_pressed = False
            mouse_pos = event.pos
            for key_group, octave, _ in [
                (self.black_keys, self.ottava, None),
                (self.black_keys_plus, self.ottava + 1, None),
                (self.white_keys, self.ottava, None),
                (self.white_keys_plus, self.ottava + 1, None),
            ]:
                for x, y, w, h, note in key_group:
                    if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                        note_played = f'{note}-{octave}'
                        if note_played in self.keydown_event:
                            self.keydown_event.remove(note_played)
                            if note_played in self.trail_data:
                                del self.trail_data[note_played]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                if self.ottava < 7:
                    self.ottava += 1
            if event.key == pygame.K_z:
                if self.ottava > 1:
                    self.ottava -= 1

            note_played = None
            if event.key == pygame.K_a:
                note_played = f'Do-{self.ottava}'
            elif event.key == pygame.K_w:
                note_played = f'Do#-{self.ottava}'
            elif event.key == pygame.K_s:
                note_played = f'Re-{self.ottava}'
            elif event.key == pygame.K_e:
                note_played = f'Re#-{self.ottava}'
            elif event.key == pygame.K_d:
                note_played = f'Mi-{self.ottava}'
            elif event.key == pygame.K_f:
                note_played = f'Fa-{self.ottava}'
            elif event.key == pygame.K_t:
                note_played = f'Fa#-{self.ottava}'
            elif event.key == pygame.K_g:
                note_played = f'Sol-{self.ottava}'
            elif event.key == pygame.K_y:
                note_played = f'Sol#-{self.ottava}'
            elif event.key == pygame.K_h:
                note_played = f'La-{self.ottava}'
            elif event.key == pygame.K_u:
                note_played = f'La#-{self.ottava}'
            elif event.key == pygame.K_j:
                note_played = f'Si-{self.ottava}'
            elif event.key == pygame.K_k:
                note_played = f'Do-{self.ottava + 1}'
            elif event.key == pygame.K_o:
                note_played = f'Do#-{self.ottava + 1}'
            elif event.key == pygame.K_l:
                note_played = f'Re-{self.ottava + 1}'
            elif event.key == pygame.K_p:
                note_played = f'Re#-{self.ottava + 1}'
            elif event.key == pygame.K_v:
                note_played = f'Mi-{self.ottava + 1}'
            elif event.key == pygame.K_b:
                note_played = f'Fa-{self.ottava + 1}'
            elif event.key == pygame.K_n:    
                note_played = f'Sol-{self.ottava + 1}'
            elif event.key == pygame.K_m:
                note_played = f'La-{self.ottava + 1}'
            elif event.key == pygame.K_COMMA:
                note_played = f'Si-{self.ottava + 1}'

            if note_played:
                synth.play(note_played)
                self.illuminated_keys[note_played] = pygame.time.get_ticks()
                self.keydown_event.add(note_played)
                for x, y, w, h, note in self.white_keys:
                    if f'{note}-{self.ottava}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 200)}
                for x, y, w, h, note in self.white_keys_plus:
                    if f'{note}-{self.ottava + 1}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 200)}
                for x, y, w, h, note in self.black_keys:
                    if f'{note}-{self.ottava}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 140)}
                for x, y, w, h, note in self.black_keys_plus:
                    if f'{note}-{self.ottava + 1}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 140)}
                self.check_falling_collision(note_played)

        if event.type == pygame.KEYUP:
            note_played = None
            if event.key == pygame.K_a:
                note_played = f'Do-{self.ottava}'
            elif event.key == pygame.K_w:
                note_played = f'Do#-{self.ottava}'
            elif event.key == pygame.K_s:
                note_played = f'Re-{self.ottava}'
            elif event.key == pygame.K_e:
                note_played = f'Re#-{self.ottava}'
            elif event.key == pygame.K_d:
                note_played = f'Mi-{self.ottava}'
            elif event.key == pygame.K_f:
                note_played = f'Fa-{self.ottava}'
            elif event.key == pygame.K_t:
                note_played = f'Fa#-{self.ottava}'
            elif event.key == pygame.K_g:
                note_played = f'Sol-{self.ottava}'
            elif event.key == pygame.K_y:
                note_played = f'Sol#-{self.ottava}'
            elif event.key == pygame.K_h:
                note_played = f'La-{self.ottava}'
            elif event.key == pygame.K_u:
                note_played = f'La#-{self.ottava}'
            elif event.key == pygame.K_j:
                note_played = f'Si-{self.ottava}'
            elif event.key == pygame.K_k:
                note_played = f'Do-{self.ottava + 1}'
            elif event.key == pygame.K_o:
                note_played = f'Do#-{self.ottava + 1}'
            elif event.key == pygame.K_l:
                note_played = f'Re-{self.ottava + 1}'
            elif event.key == pygame.K_p:
                note_played = f'Re#-{self.ottava + 1}'
            elif event.key == pygame.K_v:
                note_played = f'Mi-{self.ottava + 1}'
            elif event.key == pygame.K_b:
                note_played = f'Fa-{self.ottava + 1}'
            elif event.key == pygame.K_n:    
                note_played = f'Sol-{self.ottava + 1}'
            elif event.key == pygame.K_m:
                note_played = f'La-{self.ottava + 1}'
            elif event.key == pygame.K_COMMA:
                note_played = f'Si-{self.ottava + 1}'

            if note_played in self.keydown_event:
                self.keydown_event.remove(note_played)
                if note_played in self.trail_data:
                    del self.trail_data[note_played]

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            self.mouse_pressed = True
            # (Existing mouse event handling for keys would go here)

        if event.type == pygame.MOUSEBUTTONUP:
            self.mouse_pressed = False
            mouse_pos = event.pos
            # (Existing mouse button up handling for keys would go here)

        if event.type == pygame.MOUSEMOTION and self.mouse_pressed:
            mouse_pos = event.pos
            # (Existing mouse motion handling for keys would go here)

    def draw(self):
        """ Disegna la schermata di gioco """
        self.schermata.fill((255, 255, 255))
        text = self.font1.render(f'OCTAVE: {self.ottava}', True, (0, 0, 0))
        self.schermata.blit(text, (40, 40))
        pygame.draw.rect(self.schermata, (0, 0, 0), (35, 30, 120, 35), 4)
        pygame.draw.circle(self.schermata, (0, 100, 0), self.button_up_center, BUTTON_RADIUS)
        pygame.draw.circle(self.schermata, (0, 0, 0), self.button_up_center, BUTTON_RADIUS, 4)
        pygame.draw.circle(self.schermata, (100, 0, 0), self.button_down_center, BUTTON_RADIUS)
        pygame.draw.circle(self.schermata, (0, 0, 0), self.button_down_center, BUTTON_RADIUS, 4)

        for x, y, w, h, note in self.white_keys:
            color = (255, 255, 255)
            if f'{note}-{self.ottava}' in self.keydown_event:
                color = (0, 200, 200)
            pygame.draw.rect(self.schermata, color, (x, y, w, h))
            pygame.draw.rect(self.schermata, (0, 0, 0), (x, y, w, h), 2)

        for x, y, w, h, note in self.white_keys_plus:
            color = (255, 255, 255)
            if f'{note}-{self.ottava + 1}' in self.keydown_event:
                color = (0, 200, 200)
            pygame.draw.rect(self.schermata, color, (x, y, w, h))
            pygame.draw.rect(self.schermata, (0, 0, 0), (x, y, w, h), 2)

        for x, y, w, h, note in self.black_keys:
            color = (0, 0, 0)
            if f'{note}-{self.ottava}' in self.keydown_event:
                color = (0, 200, 140)
            pygame.draw.rect(self.schermata, color, (x, y, w, h))

        for x, y, w, h, note in self.black_keys_plus:
            color = (0, 0, 0)
            if f'{note}-{self.ottava + 1}' in self.keydown_event:
                color = (0, 200, 140)
            pygame.draw.rect(self.schermata, color, (x, y, w, h))

        # Disegna la scia
        for note, data in self.trail_data.items():
            pygame.draw.line(self.schermata, data["color"],
                             (data["x"] + 25, data["y"] - 100),
                             (data["x"] + 25, 600), 3)
            data["y"] -= 1

        # Disegna le falling notes
        for falling in self.falling_notes:
            pygame.draw.circle(self.schermata, falling["color"],
                               (falling["center_x"], int(falling["y"])), 15)

        # Mostra il punteggio
        score_text = self.font1.render(f"Score: {self.score}", True, (0, 0, 0))
        self.schermata.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))

        # Disegna il pulsante Exit per tornare al menu
        pygame.draw.rect(self.schermata, (200, 0, 0), self.exit_button_rect)
        exit_text = self.font2.render("Exit", True, (255, 255, 255))
        self.schermata.blit(exit_text, (self.exit_button_rect.centerx - exit_text.get_width()//2,
                                         self.exit_button_rect.centery - exit_text.get_height()//2))

        pygame.display.flip()

    def on_execute(self):
        self.on_init()
        while self.running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if self.state == "menu":
                    self.handle_menu_event(event)
                elif self.state == "game":
                    self.on_event(event)
            if self.state == "game":
                if current_time - self.last_spawn_time >= SPAWN_INTERVAL:
                    self.last_spawn_time = current_time
                    self.spawn_falling_note()
                self.update_falling_notes()
                self.draw()
            elif self.state == "menu":
                self.draw_start_page()
        self.on_cleanup()

# Esegui il gioco
gioco = Gioco()
gioco.on_execute()
