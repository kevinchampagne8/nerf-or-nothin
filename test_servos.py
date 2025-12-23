import serial
import time
import math

PORT = "COM4"      # Change to your Arduino port
BAUD_RATE = 9600

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Allow Arduino to reset

start = time.time()
while True:
    t = time.time() - start
    x = int(100 + math.sin(t) * 40)
    y = int(100 + math.cos(t) * 40)
    print(f"X: {x}, Y: {y}")
    ser.write(bytes([2, int(x)]))
    ser.write(bytes([3, int(y)]))
    time.sleep(0.05)

ser.close()
print("Serial connection closed.")
