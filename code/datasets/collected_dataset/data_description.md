
# Data Collection Description

This document describes the process of collecting the dataset used for training and testing the spectrum sensing model.

## Overview
The dataset was collected to reflect simple real-world scenarios with two Primary Users (PUs) and two Secondary Users (SUs) operating in a centralized Cognitive Radio (CR) network. The goal was to simulate and capture spectrum occupancy conditions for training and deploying a deep learning model.

## Data Collection Process

### Hardware Setup
1. **GNU Radio**: Used to facilitate data collection.
2. **RTL-SDR Antennas**: Two antennas were tuned to distinct, non-overlapping frequencies (433 MHz and 500 MHz).
3. **Arduino Devices**: Two devices programmed to act as PUs transmitting messages at the specified frequencies.

### Configuration
- **Sampling Rate**: Set to `2.4×10^6` samples per second for both I and Q channels, resulting in a total RTL-SDR bandwidth of `8 MHz`.
- **Gain Settings**:
  - RF Gain: `1×10^3 dB`
  - IF and BB Gains: `20 dB` each within the RTL-SDR Source block.
- **Frequencies**:
  - PU1: `433 MHz`
  - PU2: `500 MHz`

### Scenarios
The experiment covered the following scenarios:
1. Both frequencies unoccupied.
2. Only `433 MHz` occupied.
3. Only `500 MHz` occupied.
4. Both frequencies occupied.

Each scenario lasted for `30 seconds`, which was sufficient to gather a substantial dataset of I/Q samples.

### GNU Radio Configuration
- Two RTL-SDR Source blocks were connected to file sinks for storing raw I/Q data samples captured by the antennas.
- Screenshots of the spectrum under different scenarios were taken to visually confirm signal activity.

## Data Labeling
1. Energy Detection: Used to determine the occupancy status of each frequency band.
2. Thresholding: Established a specific threshold level by analyzing the active signals' decibel levels during transmission.
3. Label Assignment: Binary values (`1` for occupied, `0` for unoccupied) were assigned to each frequency band.

## Dataset Preparation
1. **Data Storage**: Raw data captured by GNU Radio was stored in binary files.
2. **Compression**: The data was converted and compressed into `.npz` format.
3. **Input Dimensions**: Each input sample consisted of two columns (real and imaginary parts of I/Q samples) with dimensions `(300,000, 1024, 2)`.

## Result
The collected dataset comprised `300,000` I/Q samples representing various spectrum occupancy scenarios. This dataset was instrumental in training and validating the deep learning model deployed on the Raspberry Pi.
