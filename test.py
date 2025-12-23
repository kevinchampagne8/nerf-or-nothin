import serial
import time

PORT = "COM4"      # Change to your Arduino port
BAUD_RATE = 9600

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Allow Arduino to reset

print("Enter two numbers from 0–255 separated by space to send.")
print("Type 'q' to quit.")

try:
    while True:
        user_input = input("> ")

        if user_input.lower() == "q":
            break

        parts = user_input.split()
        if len(parts) != 2:
            print("Error: please enter two numbers separated by space")
            continue

        try:
            value1 = int(parts[0])
            value2 = int(parts[1])
            if 0 <= value1 <= 255 and 0 <= value2 <= 255:
                ser.write(bytes([value1, value2]))
                print(f"Sent bytes: {value1} {value2}")

                # Read one line back from Arduino
                response = ser.readline()
                if response:
                    print("Arduino:", response.decode(errors="ignore").strip())
                else:
                    print("Arduino: (no response)")

            else:
                print("Error: numbers must be between 0 and 255")
        except ValueError:
            print("Error: please enter valid numbers")

finally:
    ser.close()
    print("Serial connection closed.")
