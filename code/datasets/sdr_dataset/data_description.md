
# SDR Dataset Description

This document describes the "SDR 802.11 a/g" dataset, which was utilized for simulating spectrum sensing scenarios.

## Overview
The "SDR 802.11 a/g" dataset was chosen for its non-synthetic nature, emulating real-world Wi-Fi communications. The dataset consists of I/Q samples captured across four non-overlapping 5 MHz-wide channels, providing a total bandwidth of 20 MHz.

## Data Collection Process

### Hardware and Software Configuration
1. **Hardware**:
   - Five USRP N210 SDRs were used, with four acting as Wi-Fi transmitters and one as the receiver.
   - The transmitters utilized 64 sub-carriers, and the receiver was configured with a sampling rate of 20 MS/s to capture the entire bandwidth.

2. **Software**:
   - GNU Radio was used to configure and manage the SDRs for data collection.

### Experimental Setup
- **Channels**: Data was collected over four non-overlapping 5 MHz-wide channels.
- **Days**: Data collection occurred over two distinct days.
- **Variations**: Transmitters were positioned and oriented differently to introduce diverse SNR and channel effects.

### Data Files
- The dataset comprises 32 binary (`.bin`) files, evenly split across the two days of data collection.
- Each file represents a specific channel occupancy pattern. For example:
  - `1101_day2.bin`: On the second day, the first, second, and fourth channels were actively transmitting.

## Data Preparation

### Format Conversion
- **Raw Data**: The `.bin` files contain complex I/Q data representing time-series signals.
- **HDF5 Conversion**: A Python script converts the `.bin` files into HDF5 (`.h5`) format for easier processing.
- **Training and Testing Datasets**: The `.h5` files are processed to prepare the datasets for model training and evaluation.

### Label Encoding
The dataset uses a one-hot encoding method to convert channel availability labels into a format suitable for deep learning models:
1. **Original Labels**: Labels are four-element arrays indicating channel occupancy (e.g., `[0, 1, 0, 1]`).
2. **Mapping**:
   - A dictionary maps each unique pattern (e.g., `[0, 1, 0, 1]`) to a numerical value.
   - Indices of matching data points are replaced with the corresponding numerical value.
3. **One-Hot Encoding**: This process simplifies the labels for use in model training.

---

## Summary
The SDR dataset provides a comprehensive representation of Wi-Fi channel occupancy patterns, leveraging real-world scenarios and advanced encoding techniques. It serves as a robust foundation for training and evaluating spectrum sensing models.
