import serial
import time
from NerfController import NerfController

PORT = "COM4"      # Change to your Arduino port

nerf = NerfController(PORT)

while True:
    nerf.firingUpdateLoop(True, True)
    time.sleep(0.05)

print("Serial connection closed.")
