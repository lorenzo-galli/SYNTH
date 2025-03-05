import pygame
import synth
import cevent
import time

# Definiamo alcune costanti per l'interfaccia grafica
WIDTH, HEIGHT = 1280, 800
BUTTON_RADIUS = 20
FONT_SIZE1 = 30
FONT_SIZE2 = 15

class Gioco(cevent.CEvent):

    def __init__(self):
        self.schermata = None
        self.ottava = 4
        self.font = None  # Imposta a None prima di inizializzare il font
        self.running = True
        self.button_up_center = (100, 700)  # Centro del bottone per aumentare l'ottava
        self.button_down_center = (1130, 700)  # Centro del bottone per diminuire l'ottava

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
        
        # Dizionario per tenere traccia dei tasti premuti, includendo l'ottava
        self.illuminated_keys = {}
        self.keydown_event = set()  # Aggiunto per tenere traccia dei tasti premuti
        self.mouse_pressed = False
        # Dizionario per la gestione delle scie
        self.trail_data = {} 

    def on_init(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        pygame.init()  # inizializza Pygame
        self.schermata = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Synth")  # Titolo della finestra

        # Inizializza il font (verifica che il font venga caricato correttamente)
        try:
            self.font1 = pygame.font.Font(None, FONT_SIZE1)  # Font di default
            self.font2 = pygame.font.Font(None, FONT_SIZE2)
        except pygame.error as e:
            print(f"Errore nel caricare il font: {e}")
            exit()  # Termina il gioco se non riesce a caricare il font

    def on_cleanup(self):
        pygame.quit()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        if event.type == pygame.KEYDOWN:
            # Cambio ottava
            if event.key == pygame.K_x:
                if self.ottava < 7:
                    self.ottava += 1
            if event.key == pygame.K_z:
                if self.ottava > 1:
                    self.ottava -= 1

            # Riproduzione delle note in base all'ottava e illuminazione dei tasti
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

            # Se è stata premuta una nota, riproducila e illumina il tasto
            if note_played:
                synth.play(note_played)
                self.illuminated_keys[note_played] = pygame.time.get_ticks()
                self.keydown_event.add(note_played)  # Aggiungi alla lista dei tasti premuti
                # Inizia la scia
                for x, y, w, h, note in self.white_keys:
                    if f'{note}-{self.ottava}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 200)}  # Colore e posizione iniziale

                for x, y, w, h, note in self.white_keys_plus:
                    if f'{note}-{self.ottava + 1}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 200)}  # Colore e posizione iniziale

                for x, y, w, h, note in self.black_keys:
                    if f'{note}-{self.ottava}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 140)}  # Colore e posizione iniziale

                for x, y, w, h, note in self.black_keys_plus:
                    if f'{note}-{self.ottava + 1}' == note_played:
                        self.trail_data[note_played] = {"x": x, "y": 600, "color": (0, 200, 140)}  # Colore e posizione iniziale

        # Gestire il rilascio del tasto
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

            # Se il tasto è stato rilasciato, rimuovi l'illuminazione
            if note_played and note_played in self.keydown_event:
                self.keydown_event.remove(note_played)

            if note_played:
                self.keydown_event.discard(note_played)
                del self.trail_data[note_played]  # Rimuovi la scia quando il tasto è rilasciato

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            self.mouse_pressed = True  # Il mouse è stato premuto
            
            # Verifica se è stato cliccato un tasto
            for x, y, w, h, note in self.black_keys:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    note_played = f'{note}-{self.ottava}'
                    synth.play(note_played)
                    self.illuminated_keys[note_played] = pygame.time.get_ticks()
                    self.keydown_event.add(note_played)
                    return  # Esce dalla funzione se un tasto è stato cliccato
            
            # Verifica se è stato cliccato un tasto
            for x, y, w, h, note in self.black_keys_plus:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    note_played = f'{note}-{self.ottava + 1}'
                    synth.play(note_played)
                    self.illuminated_keys[note_played] = pygame.time.get_ticks()
                    self.keydown_event.add(note_played)
                    return  # Esce dalla funzione se un tasto è stato cliccato
                
            # Verifica se è stato cliccato un tasto
            for x, y, w, h, note in self.white_keys:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    if note not in [self.black_keys + self.black_keys_plus]:
                        note_played = f'{note}-{self.ottava}'
                    synth.play(note_played)
                    self.illuminated_keys[note_played] = pygame.time.get_ticks()
                    self.keydown_event.add(note_played)
                    return  # Esce dalla funzione se un tasto è stato cliccato
            
            # Verifica se è stato cliccato un tasto
            for x, y, w, h, note in self.white_keys_plus:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    if note not in [self.black_keys + self.black_keys_plus]:
                        note_played = f'{note}-{self.ottava + 1}'
                    synth.play(note_played)
                    self.illuminated_keys[note_played] = pygame.time.get_ticks()
                    self.keydown_event.add(note_played)
                    return  # Esce dalla funzione se un tasto è stato cliccato

        if event.type == pygame.MOUSEBUTTONUP:
            self.mouse_pressed = False 


            mouse_pos = event.pos

            for x, y, w, h, note in self.black_keys:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    note_played = f'{note}-{self.ottava}'
                    if note_played in self.keydown_event:
                        self.keydown_event.remove(note_played)  # Rimuovi l'illuminazione al rilascio del mouse

            
            
            for x, y, w, h, note in self.black_keys_plus:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    note_played = f'{note}-{self.ottava + 1}'
                    if note_played in self.keydown_event:
                        self.keydown_event.remove(note_played)  # Rimuovi l'illuminazione al rilascio del mouse

                
            
            for x, y, w, h, note in self.white_keys:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    if note not in [self.black_keys + self.black_keys_plus]:
                        note_played = f'{note}-{self.ottava}'
                    if note_played in self.keydown_event:
                        self.keydown_event.remove(note_played)  # Rimuovi l'illuminazione al rilascio del mouse

            
        
            for x, y, w, h, note in self.white_keys_plus:
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    if note not in [self.black_keys + self.black_keys_plus]:
                        note_played = f'{note}-{self.ottava + 1}'
                    if note_played in self.keydown_event:
                        self.keydown_event.remove(note_played)  # Rimuovi l'illuminazione al rilascio del mouse

        if event.type == pygame.MOUSEMOTION and self.mouse_pressed:
            # Gestire il movimento del mouse mentre è premuto
            mouse_pos = event.pos
            for x, y, w, h, note in self.black_keys:
                note_played = f'{note}-{self.ottava}'
                
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    # Se il mouse entra in una nuova zona, accende quella e spegne la precedente
                    if note_played not in self.keydown_event:
                        for note in list(self.keydown_event):
                            self.keydown_event.remove(note)
                            del self.illuminated_keys[note]
                    break

            for x, y, w, h, note in self.black_keys_plus:
                note_played = f'{note}-{self.ottava + 1}' 
                
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    # Se il mouse entra in una nuova zona, accende quella e spegne la precedente
                    if note_played not in self.keydown_event:
                        for note in list(self.keydown_event):
                            self.keydown_event.remove(note)
                            del self.illuminated_keys[note]
                    break
            
            for x, y, w, h, note in self.white_keys:
                note_played = f'{note}-{self.ottava}'
                
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    if note not in [self.black_keys + self.black_keys_plus]:
                    # Se il mouse entra in una nuova zona, accende quella e spegne la precedente
                        if note_played not in self.keydown_event:
                            for note in list(self.keydown_event):
                                self.keydown_event.remove(note)
                                del self.illuminated_keys[note]
                        break

            for x, y, w, h, note in self.white_keys_plus:
                note_played = f'{note}-{self.ottava + 1}' 
                
                if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                    if note not in [self.black_keys + self.black_keys_plus]:
                    # Se il mouse entra in una nuova zona, accende quella e spegne la precedente
                        if note_played not in self.keydown_event:
                            for note in list(self.keydown_event):
                                self.keydown_event.remove(note)
                                del self.illuminated_keys[note]
                        break

            

    def draw(self):
        """ Funzione per disegnare gli elementi grafici sulla finestra """
        self.schermata.fill((255, 255, 255))  # Riempi lo sfondo con il bianco

        # Disegna il titolo "Ottava corrente"
        text = self.font1.render(f'OCTAVE: {self.ottava}', True, (0, 0, 0))
        self.schermata.blit(text, (40, 40))
        pygame.draw.rect(self.schermata, (0, 0, 0), (35, 30, 120, 35), 4)

        # Disegna i pulsanti circolari per cambiare l'ottava
        pygame.draw.circle(self.schermata, (0, 100, 0), self.button_up_center, BUTTON_RADIUS)  # Verde per "su"
        pygame.draw.circle(self.schermata, (0, 0, 0), self.button_up_center, BUTTON_RADIUS, 4)  # contorno
        pygame.draw.circle(self.schermata, (100, 0, 0), self.button_down_center, BUTTON_RADIUS)  # Rosso per "giù"
        pygame.draw.circle(self.schermata, (0, 0, 0), self.button_down_center, BUTTON_RADIUS, 4) 

        # Disegna i tasti bianchi
        for x, y, w, h, note in self.white_keys:
            color = (255, 255, 255)  # Colore di default
            if f'{note}-{self.ottava}' in self.keydown_event:  # Modificato qui
                color = (0, 200, 200)  # Illumina di blu
            pygame.draw.rect(self.schermata, color, (x, y, w, h))  # Corpo
            pygame.draw.rect(self.schermata, (0, 0, 0), (x, y, w, h), 2)  # Bordo

        for x, y, w, h, note in self.white_keys_plus:
            color = (255, 255, 255)  # Colore di default
            if f'{note}-{self.ottava + 1}' in self.keydown_event:  # Modificato qui
                color = (0, 200, 200)  # Illumina di blu
            pygame.draw.rect(self.schermata, color, (x, y, w, h))  # Corpo
            pygame.draw.rect(self.schermata, (0, 0, 0), (x, y, w, h), 2)  # Bordo

        # Disegna i tasti neri
        for x, y, w, h, note in self.black_keys:
            color = (0, 0, 0)  # Colore di default
            if f'{note}-{self.ottava}' in self.keydown_event:  # Modificato qui
                color = (0, 200, 140)  # Illumina di blu
            pygame.draw.rect(self.schermata, color, (x, y, w, h))

        for x, y, w, h, note in self.black_keys_plus:
            color = (0, 0, 0)  # Colore di default
            if f'{note}-{self.ottava + 1}' in self.keydown_event:  # Modificato qui
                color = (0, 200, 140)  # Illumina di blu
            pygame.draw.rect(self.schermata, color, (x, y, w, h))

        # Aggiungi il testo sui pulsanti
        up_text = self.font2.render("UP", True, (255, 255, 255))
        down_text = self.font2.render("DOWN", True, (255, 255, 255))
        self.schermata.blit(up_text, (self.button_up_center[0] - up_text.get_width() / 2, self.button_up_center[1] - up_text.get_height() / 2))
        self.schermata.blit(down_text, (self.button_down_center[0] - down_text.get_width() / 2, self.button_down_center[1] - down_text.get_height() / 2))


        # Disegna le scie
        for note, data in self.trail_data.items():
            pygame.draw.line(self.schermata, data["color"], (data["x"] + 25, data["y"] - 100), (data["x"] + 25, 600), 3)
            data["y"] -= 1  # Sposta la scia verso l'alto

        
        # Mostra tutto sulla finestra
        pygame.display.flip()

    def on_execute(self):
        self.on_init()

        while self.running:
            for event in pygame.event.get():
                self.on_event(event)

            # Disegnare l'interfaccia
            self.draw()

        self.on_cleanup()

# Esegui il gioco
gioco = Gioco()
gioco.on_execute()
