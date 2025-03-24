import asyncio
from bleak import BleakClient, BleakScanner
import pyaudio
import wave
import time
import struct
import numpy as np

# Audio setup
CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
NOTE_DURATION = 0.2  # seconds

# Note frequencies (C4 to C5)
NOTE_FREQUENCIES = [
    261.63,  # C4  - GP15 (lowest note)
    293.66,  # D4  - GP13
    329.63,  # E4  - GP12
    349.23,  # F4  - GP11
    392.00,  # G4  - GP9
    440.00,  # A4  - GP16
    493.88,  # B4  - GP17
    523.25,  # C5  - GP10 (highest note)
]

# BLE UART Service UUIDs (matching Pico W)
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class AudioServer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )
        self.running = True
        self.connected = False

    def generate_tone(self, frequency):
        """Generate a sine wave tone at the given frequency"""
        samples = np.arange(int(RATE * NOTE_DURATION))
        note = np.sin(2 * np.pi * frequency * samples / RATE).astype(np.float32)
        # Apply simple envelope to avoid clicks
        envelope = np.minimum(np.linspace(0, 1, 1000), 1.0)
        note[:1000] *= envelope
        note[-1000:] *= envelope[::-1]
        return note.tobytes()

    def handle_note(self, note_index):
        """Handle a received note index"""
        try:
            if 0 <= note_index < len(NOTE_FREQUENCIES):
                frequency = NOTE_FREQUENCIES[note_index]
                print(f"[RECEIVED] Note index: {note_index}, Frequency: {frequency:.2f} Hz")
                
                # Generate and play the tone
                audio_data = self.generate_tone(frequency)
                self.stream.write(audio_data)
                print(f"[AUDIO] Played tone at {frequency:.2f} Hz")
            else:
                print(f"[ERROR] Invalid note index: {note_index}")
        except Exception as e:
            print(f"[ERROR] Error processing note data: {str(e)}")

    async def find_pico_device(self):
        print("[BLE] Scanning for Pico W UART device...")
        devices = await BleakScanner.discover()
        for device in devices:
            print(f"[SCAN] Found device: {device.name} ({device.address})")
            if device.name and "Pico W UART" in device.name:
                print(f"[SCAN] Found Pico W UART device at {device.address}")
                return device.address
        return None

    async def start(self):
        while self.running:
            try:
                device_address = await self.find_pico_device()
                if not device_address:
                    print("[ERROR] Pico W UART device not found")
                    print("[BLE] Retrying scan in 5 seconds...")
                    await asyncio.sleep(5)
                    continue

                print(f"[BLE] Connecting to {device_address}...")
                async with BleakClient(device_address, timeout=20.0) as client:
                    print(f"[CONNECTION] Connected to Pico W UART")
                    self.connected = True

                    # Get services for debugging
                    services = await client.get_services()
                    print("\n[BLE] Available services:")
                    for service in services:
                        print(f"Service: {service.uuid}")
                        for char in service.characteristics:
                            print(f"  Characteristic: {char.uuid}")
                            print(f"  Properties: {char.properties}")
                    
                    def notification_handler(sender, data):
                        """Handle incoming notifications"""
                        if data and len(data) == 1:
                            self.handle_note(data[0])
                    
                    # Enable notifications
                    await client.start_notify(UART_TX_CHAR_UUID, notification_handler)
                    print("[READY] Listening for note data...")
                    
                    # Keep connection alive
                    while self.running and self.connected:
                        await asyncio.sleep(1)
                        
            except Exception as e:
                print(f"[ERROR] {str(e)}")
                self.connected = False
                print("[BLE] Retrying connection in 5 seconds...")
                await asyncio.sleep(5)

    def cleanup(self):
        self.running = False
        print("[SERVER] Cleaning up resources...")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print("[SERVER] Shutdown complete")

async def main():
    server = AudioServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Received shutdown signal")
    finally:
        server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
