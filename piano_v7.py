import machine
import time
import bluetooth
import struct
from micropython import const

print("Starting program...")

def advertising_payload(name=None, services=None):
    print("Creating advertising payload...")
    payload = bytearray()
    if name:
        name_bytes = name.encode('utf-8')
        payload += struct.pack("BB", len(name_bytes) + 1, 0x09) + name_bytes
    if services:
        for uuid in services:
            b = bytes(uuid)
            payload += struct.pack("BB", len(b) + 1, 0x03 if len(b) == 2 else 0x05 if len(b) == 4 else 0x07) + b
    print(f"Advertising payload created: {payload}")
    return payload

# Define button pins with internal pull-up resistors
buttons = {
    "GP15": machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP),
    "GP13": machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP),
    "GP12": machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP),
    "GP11": machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP),
    "GP10": machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP),
    "GP9": machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_UP),
    "GP17": machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP),
    "GP16": machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP),
}

# Define note indices (0-7 for one octave)
notes = {
    "GP15": 0,  # C4 (lowest note)
    "GP13": 1,  # D4
    "GP12": 2,  # E4
    "GP11": 3,  # F4
    "GP9":  4,  # G4
    "GP16": 5,  # A4
    "GP17": 6,  # B4
    "GP10": 7   # C5 (highest note)
}

led = machine.Pin("LED", machine.Pin.OUT)

print("Buttons and LED setup complete")

# BLE UART Service
UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
UART_TX_CHAR_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

# Simplified service with just one characteristic
UART_SERVICE = (
    UART_SERVICE_UUID,
    (
        (UART_TX_CHAR_UUID, bluetooth.FLAG_NOTIFY),
    ),
)

print("Starting BLE...")
ble = bluetooth.BLE()
ble.active(True)
print("BLE activated")

print("Registering services...")
((tx_handle,),) = ble.gatts_register_services((UART_SERVICE,))
print(f"Services registered, TX handle: {tx_handle}")

# Set a larger MTU size
ble.config(mtu=100)

adv_payload = advertising_payload(name="Pico W UART", services=[UART_SERVICE_UUID])
print("Starting advertising...")
ble.gap_advertise(100, adv_payload)  # Increased advertising interval
print("Advertising started")

is_connected = False
conn_handle = None

def on_ble_irq(event, data):
    global is_connected, conn_handle
    try:
        if event == 1:  # _IRQ_CENTRAL_CONNECT
            conn_handle = data[0]
            is_connected = True
            print(f"Connected! Handle: {conn_handle}")
            # Flash LED to indicate connection
            for _ in range(3):
                led.on()
                time.sleep_ms(100)
                led.off()
                time.sleep_ms(100)
        elif event == 2:  # _IRQ_CENTRAL_DISCONNECT
            is_connected = False
            conn_handle = None
            print("Disconnected!")
            print("Restarting advertising...")
            ble.gap_advertise(100, adv_payload)
            print("Advertising restarted")
        elif event == 3:  # _IRQ_CONNECTION_UPDATE
            print("Connection parameters updated")
        elif event == 4:  # _IRQ_COMPLETE
            print("Operation completed")
    except Exception as e:
        print(f"Error in IRQ handler: {e}")

ble.irq(on_ble_irq)

def send_note(note_index):
    global conn_handle
    if not is_connected or conn_handle is None:
        print("Not connected")
        return False
    
    try:
        # Send note index with notify
        ble.gatts_notify(conn_handle, tx_handle, bytes([note_index]))
        print(f"Sent note index: {note_index}")
        return True
    except OSError as e:
        print(f"Failed to send data: {e}")
        return False

print("Waiting for connection...")

print("Entering main loop...")
last_press_time = 0
debounce_delay = 150  # ms

def play_melody():
    if not is_connected:
        print("Not connected - can't play melody")
        return
        
    # Complete "Mary Had a Little Lamb"
    melody = [
        2, 1, 0, 1,    # E D C D
        2, 2, 2,       # E E E (quarter notes)
        1, 1, 1,       # D D D (quarter notes)
        2, 4, 4,       # E G G
        2, 1, 0, 1,    # E D C D
        2, 2, 2, 2,    # E E E E
        1, 1, 2, 1,    # D D E D
        0              # C (final note)
    ]
    
    # Duration for each note (in milliseconds)
    # 1 = quarter note, 2 = half note
    durations = [
        400, 400, 400, 400,  # E D C D
        400, 400, 800,       # E E E
        400, 400, 800,       # D D D
        400, 400, 800,       # E G G
        400, 400, 400, 400,  # E D C D
        400, 400, 400, 400,  # E E E E
        400, 400, 400, 400,  # D D E D
        1200                 # C (final note)
    ]
    
    # Play each note with its duration
    for note, duration in zip(melody, durations):
        if is_connected:
            send_note(note)
            led.on()
            time.sleep_ms(duration)  # Hold the note
            led.off()
            time.sleep_ms(50)  # Brief pause between notes
        else:
            break
    
    # Pause before allowing replay
    time.sleep_ms(500)

# Modify the main loop to check for melody trigger
while True:
    current_time = time.ticks_ms()
    
    # Check if both GP15 and GP13 are pressed together to trigger melody
    if not buttons["GP15"].value() and not buttons["GP13"].value():
        print("Playing melody...")
        play_melody()
        time.sleep_ms(500)  # Prevent immediate replay
        continue
        
    for pin_name, button in buttons.items():
        if not button.value():  # Button is pressed
            if time.ticks_diff(current_time, last_press_time) > debounce_delay:
                note_index = notes[pin_name]
                print(f"Button pressed on pin: {pin_name}, Note index: {note_index}")
                led.on()
                if is_connected:
                    if send_note(note_index):
                        # Flash LED briefly to indicate successful send
                        led.off()
                        time.sleep_ms(50)
                        led.on()
                last_press_time = current_time
        else:
            led.off()
    time.sleep_ms(10)
