
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
  1. **Spectrum Monitoring**: Uses RTL-SDR and a quantized TensorFlow Lite deep learning model to infer spectrum occupancy. The model (`model.tflite`) was trained on the **collected dataset**.
  2. **Control Channel Management**: Handles SU communication, allocates channels dynamically, and queues requests based on a First-Come-First-Served (FCFS) protocol.
- **`model.tflite`**: Pre-trained and quantized deep learning model for detecting spectrum holes.
<!-- - **`figures/`**:
  - `gnuradio_block_diag.png`: Diagram of the GNU Radio block used for data collection.
  - `spectrum_plots.png`: Visual representation of spectrum usage by PUs and SUs during data collection. -->

<!-- ### `simulation/`
This folder contains a notebook for simulating spectrum sensing using the **SDR dataset** from the DeepSense paper:

- **`sdr_simulation.ipynb`**: Simulates SDR-based spectrum sensing by training and evaluating a model using the SDR dataset for inference. -->

### `datasets/`
This folder contains information and data for both the collected and SDR datasets:
- **`collected_dataset/`**:
  - `iq_samples.npz`: Compressed dataset of I/Q samples captured during real-world experiments with labeled occupancy states.
  - `data_description.txt`: Detailed description of data collection using GNU Radio.
  - `gnuradio_block_diag.png`: Diagram of the GNU Radio block used for data collection.
  - **`model_training_collected.ipynb`**: Notebook for training the model using the **collected dataset**.

  - **`model_testing_quantization.ipynb`**: A notebook to load and test the collected dataset. It includes steps to:
    - Load the pre-trained model.
    - Apply float16 Post-Training Quantization (PTQ) on the model and test it.
- **`sdr_dataset/`**:
  - Example input/output files for the SDR dataset simulation.
  - `data_description.txt`: Notes on the DeepSense SDR dataset.
  - **`bin2hdf5 AND preprocess.ipynb`**: Converts raw SDR dataset binary files into HDF5 format for efficient processing, AND prepares the SDR dataset for training and evaluation.
  - **`model_training_sdr.ipynb`**: Notebook for training the model using the **SDR dataset**.
    
---

## System Overview

### FDMA-Based Design
The system operates under FDMA, with dedicated frequency bands assigned as follows:
- **PU1**: 433 MHz
- **PU2**: 500 MHz
- **Control Channel**: 440 MHz (used by the CU for communication with SUs).

### Communication Protocol
A basic communication protocol inspired by TCP ensures reliable message delivery. Each data frame is structured as follows:

| Field       | Description                                  |
|-------------|----------------------------------------------|
| `source`    | Address of the sender (e.g., PU1: `2`, SU2: `5`) |
| `message`   | Type of message (e.g., `PU`, `start`, `end`) |
| `destination` | Address of the receiver (e.g., CU: `1`)     |

Example Arduino transmission:
```cpp
String dataToSend = String(PU_Address);
dataToSend += String(",PU,");
dataToSend += String(nodeAddress);
```

Example Python response at the CU:
```python
if destination == ownAddress:
    print("Received:", request)
    message_1 = f"{source},ACK,{destination}"
    send_data(message_1)
```

### Spectrum Monitoring
The CU continuously monitors the spectrum using an RTL-SDR antenna and a deep learning model trained on the **collected dataset**. The model identifies spectrum holes by analyzing real-time RF data.

---

## Dataset Overview

### Collected Dataset
- **Generated using GNU Radio** with real-world experiments involving PUs and SUs.
- Includes 300,000 labeled I/Q samples representing spectrum occupancy states.

### SDR Dataset
- Obtained from the **[DeepSense paper](https://github.com/wineslab/deepsense-spectrum-sensing-datasets/tree/main)**.
- Used in the simulation notebook (`sdr_simulation.ipynb`) for model training and testing.

---

## Libraries and Tools
- **Arduino (C++)**:
  - RadioHead Library for LoRa communication.
- **Raspberry Pi (Python)**:
  - `rtlsdr` for spectrum monitoring.
  - `adafruit_rfm9x` for LoRa transceiver communication.
  - TensorFlow Lite for deploying the quantized DL model.

---
