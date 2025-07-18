import RPi.GPIO as GPIO
import time

# Relay number to GPIO pin mapping
RELAY_PINS = {
    1: 2,   2: 3,   3: 4,   4: 17,
    5: 27,  6: 22,  7: 10,  8: 9,
    9: 11, 10: 5, 11: 6, 12: 13,
   13: 19, 14: 26, 15: 14, 16: 15
}

# Slot name to relay number mapping
SLOT_TRIGGERS = {
    "A1": [3, 12, 13, 14],
    "A2": [3, 7, 13, 14],
    "A3": [3, 7, 12, 14],
    "A4": [3, 7, 12, 13],

    "B1": [2, 12, 13, 14],
    "B2": [2, 7, 13, 14],
    "B3": [2, 7, 12, 14],
    "B4": [2, 7, 12, 13],

    "C1": [5, 12, 13, 14],
    "C2": [5, 7, 13, 14],
    "C3": [5, 7, 12, 14],
    "C4": [5, 7, 12, 13],

    "F1": [6, 12, 13, 14],
    "F2": [6, 7, 13, 14],
    "F3": [6, 7, 12, 14],
    "F4": [6, 7, 12, 13]
}

GPIO.setmode(GPIO.BCM)

# Setup all relay pins
for pin in RELAY_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # OFF (active LOW)

try:
    while True:
        slot = input("\nEnter slot code (A1 to F4) or 'end' to quit: ").strip().upper()

        if slot == "END":
            print("Exiting...")
            break

        if slot not in SLOT_TRIGGERS:
            print("Invalid slot. Try A1 to F4.")
            continue

        relays = SLOT_TRIGGERS[slot]
        print(f"Activating {slot}: relays {relays}")

        for r in relays:
            GPIO.output(RELAY_PINS[r], GPIO.LOW)
            print(f"Relay {r} ON")

        time.sleep(2)

        for r in relays:
            GPIO.output(RELAY_PINS[r], GPIO.HIGH)
            print(f"Relay {r} OFF")

except KeyboardInterrupt:
    print("\nInterrupted by user.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
