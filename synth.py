import math
import struct
import pydub
import numpy as np
import pygame

def nota(freq: float) -> list[float]:
    x = range(0, 22050)
    y = [math.sin(2 * math.pi * freq * i / 22050)*(math.exp(-i/1500)) for i in x]
    
    return x, y

def salva_nota(y):

    samples = [int(s * 32767) for s in y]
    byte_data = struct.pack('<' + 'h' * len(samples), *samples)

    audio = pydub.AudioSegment(byte_data, frame_rate=22050, sample_width=2, channels=1)
    return audio


freq_4 = {}
freq_4['Do'] = 261.63
freq_4['Do#'] = 277.18
freq_4['Re'] = 293.66
freq_4['Re#'] = 311.13
freq_4['Mi'] = 329.63
freq_4['Fa'] = 349.23
freq_4['Fa#'] = 369.99
freq_4['Sol'] = 392
freq_4['Sol#'] = 415.30
freq_4['La'] = 440
freq_4['La#'] = 466.16
freq_4['Si'] = 493.88

frequenze = {}

def espandi_note(ottava4):
    for ottava in range(1, 9):
        for nota, freq in freq_4.items():
            new_freq = freq / (2 ** ( 4 - ottava))
            frequenze[f'{nota}-{ottava}'] = round(new_freq, 2)
    return frequenze
freq_table = espandi_note(freq_4)
print(freq_table)

def play(nota_):
    _, y = nota(freq_table[nota_]) # _, y perchè mettere x, y è inutile tanto non ci serve x
    audio = salva_nota(y)
    sound = pygame.mixer.Sound(buffer=audio.raw_data)
    pygame.mixer.Sound.play(sound)

