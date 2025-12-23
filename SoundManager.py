import winsound
import random
import time

class SoundManager:
    def __init__(self):
        self.prev_detected = False
        self.lastSoundPlayed = 0

    def _play_sound(self, sound_type, choices):
        """Play a sound and update the last played timestamp."""
        winsound.PlaySound(f"sounds/{sound_type}_{random.randint(1, choices)}.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        self.lastSoundPlayed = time.time()

    def handleSound(self, person_detected):
        if person_detected and not self.prev_detected:
            self._play_sound("active", 7)
        if not person_detected and self.lastSoundPlayed < time.time() - 5:
            self._play_sound("search", 5)
        self.prev_detected = person_detected

