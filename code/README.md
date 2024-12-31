
# Code for Centralized Cognitive Radio Spectrum Sensing System

This folder contains all the code and resources for implementing our centralized cognitive radio spectrum sensing system. The system is designed to simulate a real-world centralized Cognitive Radio (CR) network operating under Frequency Division Multiple Access (FDMA). It employs distinct frequency bands for Primary User (PU) activities and a dedicated control channel for communication between the Central Node (CU) and Secondary Users (SUs).

## Folder Structure

### `arduino/`
This folder contains Arduino `.ino` files for Primary Users (PU) and Secondary Users (SU):
- **`PU.ino`**: Used by both PUs (PU1 and PU2). Frequencies and addresses are specified in the code:
  - PU1: `433 MHz`, Address: `2`
  - PU2: `500 MHz`, Address: `3`
- **`SU_Click.ino`**: Used by both SUs (SU1 and SU2). Frequencies and addresses are specified:
  - SU1: `Dummy Frequency: 440 MHz`, Address: `4`
  - SU2: `Dummy Frequency: 440 MHz`, Address: `5`
- These `.ino` files use the [RadioHead Library](http://www.airspayce.com/mikem/arduino/RadioHead/) for LoRa communication.

### `raspberry_pi/`
This folder contains Python code for the central node running on a Raspberry Pi:
- **`central_node.py`**: Implements two parallel tasks:
  1. **Spectrum Monitoring**: Uses RTL-SDR and a quantized TensorFlow Lite deep learning model to infer spectrum occupancy.
  2. **Control Channel Management**: Handles SU communication, allocates channels dynamically, and queues requests based on a First-Come-First-Served (FCFS) protocol.
- **`model.tflite`**: Pre-trained and quantized deep learning model for detecting spectrum holes.
<!-- - **`data_preprocessing.ipynb`**: Notebook for processing the collected I/Q samples into a labeled dataset. -->

### `simulation/`
This folder contains resources for simulating spectrum sensing using the SDR dataset:
- **`sdr_simulation.ipynb`**: Simulates SDR-based spectrum sensing using the DeepSense dataset.
- **`figures/`**:
  - `gnuradio_block_diag.png`: Diagram of the GNU Radio block used for data collection.
  - `spectrum_plots.png`: Visual representation of spectrum usage by PUs and SUs.

### `datasets/`
This folder contains the labeled dataset and related files:
- **`iq_samples.npz`**: Compressed dataset with labeled I/Q samples (300,000 samples).
- **`data_description.txt`**: Detailed description of the data collection process, including GNU Radio configurations and labeling methodology.

---

## System Overview

### FDMA-Based Design
The system operates under FDMA, with dedicated frequency bands assigned as follows:
- **PU1**: 433 MHz
- **PU2**: 500 MHz
- **Control Channel**: 440 MHz (used by the CU for communication with SUs).

### Communication Protocol
A basic communication protocol inspired by TCP ensures reliable message delivery:
- **PUs**: Operate on dedicated frequencies and transmit to the CU using a predefined format.
- **SUs**: Send transmission requests to the CU via the control channel. The CU queues requests and allocates frequencies dynamically.
- **Acknowledgment (ACK)**: The CU acknowledges SU requests before they begin transmission.

Example communication (Arduino):
```cpp
String dataToSend = String(PU_Address);
dataToSend += String(",PU,");
dataToSend += String(nodeAddress);
```
Example response (Python, CU):
```python
if destination == ownAddress:
    print("Received:", request)
    message_1 = f"{source},ACK,{destination}"
    send_data(message_1)
```

### Spectrum Monitoring
The CU continuously monitors the spectrum using an RTL-SDR antenna and a deep learning model. The model identifies spectrum holes by analyzing real-time RF data.

---

## Dataset
The dataset reflects simple real-world scenarios with two PUs and two SUs. It was collected using GNU Radio with RTL-SDR antennas tuned to 433 MHz and 500 MHz, covering the following conditions:
1. Both frequencies unoccupied.
2. Only 433 MHz occupied.
3. Only 500 MHz occupied.
4. Both frequencies occupied.

The collected I/Q samples were labeled and compressed into `.npz` format for training the TensorFlow Lite model.

---

## Libraries and Tools
- **Arduino (C++)**:
  - RadioHead Library for LoRa communication.
- **Raspberry Pi (Python)**:
  - `rtlsdr` for spectrum monitoring.
  - `adafruit_rfm9x` for LoRa transceiver communication.
  - TensorFlow Lite for deploying the quantized DL model.
