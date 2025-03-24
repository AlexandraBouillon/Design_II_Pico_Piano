# Pico W Design II Project - BLE and Audio

This project is a learning exercise for designing circuits and programming the Raspberry Pi Pico W. The project consists of two parts:

- **Part 1**: Programming a Raspberry Pi Pico W to send note data over Bluetooth Low Energy (BLE) based on button presses.
- **Part 2**: A Python client that receives the note data from the Pico W and plays corresponding sounds on a speaker.

## Overview

### Part 1: Raspberry Pi Pico W (MicroPython)
The Pico W is programmed to:
- Send note data over BLE when buttons are pressed.
- Advertise a BLE service for receiving note data.
- Play a melody when two specific buttons are pressed together.

### Part 2: Python BLE Client (Computer or Raspberry Pi)
The Python client:
- Connects to the Pico W via BLE.
- Receives note data from the Pico W.
- Generates and plays audio corresponding to the received notes.

## Requirements

### Part 1: Raspberry Pi Pico W (MicroPython)
#### Hardware Requirements:
- Raspberry Pi Pico W.
- Push buttons connected to the GPIO pins of the Pico W.
- A speaker connected to the computer or a Raspberry Pi for audio playback (Part 2).

#### Software Requirements:
- MicroPython firmware on the Pico W.
- A suitable editor for MicroPython, such as Thonny.

### Part 2: Python BLE Client
#### Hardware Requirements:
- Bluetooth-enabled computer or Raspberry Pi.

#### Software Requirements:
- Python 3.x.
- `bleak` library for BLE communication: `pip install bleak`.
- `pyaudio` for audio playback: `pip install pyaudio`.
- `numpy` for audio signal generation: `pip install numpy`.

## Setup and Instructions

### Part 1: Raspberry Pi Pico W (MicroPython)
1. **Prepare the Pico W**:
   - Flash MicroPython onto the Raspberry Pi Pico W.
   - Connect to the Pico W via serial terminal (e.g., Thonny).

2. **Upload the MicroPython Code**:
   - Copy the provided code into a new file named `main.py` and upload it to the Pico W.
   - The Pico W will start advertising a BLE service, waiting for a connection from a client.

3. **Button Connections**:
   - Connect buttons to the specified GPIO pins (e.g., GP15, GP13, GP12, etc.) on the Pico W.
   - Each button corresponds to a note in the musical scale (C4 to C5).

4. **Power the Pico W**:
   - Ensure BLE is working by checking the terminal output.

### Part 2: Python BLE Client
1. **Install Dependencies**:

2. **Run the Client Script**:
- Save the second provided Python script (client code) into a file named `client.py`.
- Run the script with Python:
  ```
  python client.py
  ```

3. **Connect to the Pico W**:
- The script will automatically search for the Pico W with the advertisement name "Pico W UART".
- Once a connection is established, it will start listening for note data.

4. **Play Notes**:
- When a button is pressed on the Pico W, the corresponding note will be sent via BLE.
- The Python client will generate and play the tone associated with that note.

5. **Play Melody**:
- If both GP15 and GP13 buttons are pressed simultaneously on the Pico W, a melody ("Mary Had a Little Lamb") will play.

## BLE Communication

- The Pico W advertises a BLE service with a custom characteristic for transmitting note data.
- The Python client subscribes to this characteristic and receives note index data.
- The client uses the note index to generate and play the corresponding frequency from predefined frequencies of notes.

## Melody Example

The melody "Mary Had a Little Lamb" is hardcoded in the Pico W. It is played when both GP15 and GP13 buttons are pressed at the same time. Each note has a corresponding duration, and the notes are transmitted over BLE.

## Troubleshooting

### BLE Connection Issues:
- Ensure that the Pico W is properly powered and that BLE advertising is running.
- The BLE client may take a few seconds to discover the Pico W, especially if it is not in range.

### Audio Playback:
- Ensure your computer or Raspberry Pi has a working audio output device (e.g., speakers or headphones).

## Project Goals
- Learn about BLE communication between devices.
- Gain experience programming with MicroPython on the Pico W.
- Understand how to generate and manipulate audio data programmatically.
