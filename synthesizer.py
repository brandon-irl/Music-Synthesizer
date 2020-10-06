#!python
import random
import math
import sounddevice
import numpy as np
import matplotlib.pyplot as plt
import mido

MASTER_VOLUME = 0.02
HALF_LIFE = 0.3

overtones = {i: (1 / i ** 1.5) for i in range(1, 8)}


class Audio:
    def play(self, samplerate=8000):
        time_array = np.linspace(0, self.length, int(self.length * samplerate))
        pressure_array = np.zeros_like(time_array)
        sounddevice.play(pressure_array, samplerate=samplerate)
        for i, t in enumerate(time_array):
            pressure_array[i] = self.get_pressure(t.item())
        sounddevice.wait()


class Note(Audio):
    def __init__(self, frequency, volume=1):
        self.frequency = frequency
        self.volume = volume
        self.length = 1.5

    def get_pressure(self, t):
        if 0 <= t <= self.length:
            volume = MASTER_VOLUME * self.volume * 2 ** (-t / HALF_LIFE)
            result = 0
            for overtone, overtone_volume in overtones.items():
                result += overtone_volume * math.sin(
                    t * math.tau * self.frequency * overtone
                )
            return volume * result
        else:
            return 0


# plt.plot(pressure_array[:60])
# plt.show()


class Sequence(Audio):
    def __init__(self, members):
        self.members = tuple(members)
        self.length = max(note.length + offset for offset, note in self.members)

    def get_pressure(self, t):
        return sum(note.get_pressure(t - offset) for offset, note in self.members)


class MidiSequence(Sequence):
    def __init__(self, path):
        midi = mido.MidiFile(path)
        members = []
        current_time = 0
        for message in midi:
            current_time += message.time
            if message.type != "note_on":
                continue
            members.append(
                (
                    current_time,
                    Note(
                        440 * 2 ** ((message.note - 69) / 12),
                        volume=(message.velocity / 127),
                    ),
                )
            )
        Sequence.__init__(self, members)


if __name__ == "__main__":
    midi_sequence = MidiSequence("turkish_march.mid")
    midi_sequence.play()
