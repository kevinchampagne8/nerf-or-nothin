import serial
import time

class NerfController:
    """
    Low-level interface to the Nerf gun. Translates high-level functions to the correct two-byte sequence accepted by the Arduino
    controlling the Nerf gun's movements and actions.
    """ 
    FIRE_WARMUP = 0.500 # seconds to wait between revving and firing.
    FIRE_DURATION = 0.250 # seconds to hold the rev and fire button down.
    FIRE_COOLDOWN = 3.000 # seconds to wait before reving/firing again. Only happens after a succesful fire.

    def __init__(self, PORT, BAUD_RATE=9600):
        self._pan_position = 100
        self._tilt_position = 100
        self._rev = False
        self._fire = False
        self._last_rev_time = 0
        self._last_fire_time = 0
        self._ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        self.setRev(False, True)
        self.setFire(False, True)
        self.pan(self._pan_position)
        self.tilt(self._tilt_position)
        self._scan_direction = 1

    def __del__(self):
        if hasattr(self, '_ser') and self._ser.is_open:
            self._ser.close()
    
    def send_command(self, command: int, value: int):
        self._ser.write(bytes([command, value]))

    def pan(self, position: int):
        if position < 0:
            position = 0
        if position > 200:
            position = 200
        self._pan_position = position
        self.send_command(2, position)

    def tilt(self, position: int):
        if position < 0:
            position = 0
        if position > 200:
            position = 200
        self._tilt_position = position
        self.send_command(3, position)

    def setRev(self, on: bool, force: bool = False):
        if on and not self._rev or force:
            self.send_command(4, 1)
            if not force:
                self._last_rev_time = time.time()
        elif not on and self._rev or force:
            self.send_command(4, 0)
        self._rev = on

    def setFire(self, on: bool, force: bool = False):
        if on and not self._fire or force:
            self.send_command(5, 1)
            if not force:
                self._last_fire_time = time.time()
        elif not on and self._fire or force:
            self.send_command(5, 0)
        self._fire = on

    def firingUpdateLoop(self, rev: bool, fire: bool):
        # Important guardrails.
        # First, never try to fire if the gun is not revving.
        if fire and not rev:
            raise ValueError("Cannot fire without revving.")

        time_since_last_fire = time.time() - self._last_fire_time

        # Second, don't fire between the cooldown period.
        if time_since_last_fire > self.FIRE_DURATION and time_since_last_fire < self.FIRE_COOLDOWN:
            need_to_reload = False
            if self._fire:
                need_to_reload = True
            self.setFire(False)
            self.setRev(False)
            if need_to_reload:
                self.reload()
            return

        if self._rev and fire and time.time() - self._last_rev_time >= self.FIRE_WARMUP:
            self.setFire(True)
        else:
            self.setFire(False)
        self.setRev(rev)

    def moveLeft(self):
        self.pan(self._pan_position + 1)
    
    def moveRight(self):
        self.pan(self._pan_position - 1)
    
    def moveUp(self):
        self.tilt(self._tilt_position + 1)
    
    def moveDown(self):
        self.tilt(self._tilt_position - 1)

    def moveBy(self, dX: int, dY: int, maxSpeed: int = 7):
        self.pan(self._pan_position - dX)
        self.tilt(self._tilt_position - dY)

    def setScanDirection(self, direction: int):
        """ Allow the user to override the scan direction in case a person leaves the frame. """
        if direction == 0:
            direction = self._scan_direction
        direction /= abs(direction)
        self._scan_direction = direction

    def scan(self):
        """
        Just alternate back and forth
        """
        if self._scan_direction == 1:
            self.moveRight()
            if self._pan_position <= 0:
                self._scan_direction = -1
        else:
            self.moveLeft()
            if self._pan_position >= 200:
                self._scan_direction = 1

    def reload(self):
        """
        Tilt the gun down to guide the rounds into the feeder.
        """
        old_position = self._tilt_position
        self.tilt(25)
        time.sleep(1)
        self.tilt(old_position)