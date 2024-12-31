import time
import board
import busio
import digitalio
import adafruit_rfm9x
import tensorflow as tf
import numpy as np

import threading

import matplotlib.pyplot as plt
from rtlsdr import RtlSdr

# Set the time interval (seconds) for sending packets
transmit_interval = 1

# Define radio parameters
RADIO_FREQ_MHZ = 440.0  # Frequency of the radio in Mhz

# Define pins connected to the chip
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)
# Initialize SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialize RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23

# Central node code
ownAddress = 1 
queue = []

frequency = [433, 500]
status = [0, 0]  # 0 = free #this is the DL output
primary_users = [2, 3] #PU IDs

TF_LITE_MODEL_FILE_NAME = "./model.tflite"
interpreter = tf.lite.Interpreter(model_path = TF_LITE_MODEL_FILE_NAME)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
interpreter.resize_tensor_input(input_details[0]['index'], (1, 1024, 2, 1))
interpreter.resize_tensor_input(output_details[0]['index'], (1, 16))
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

''' 
ids/addresses:
PU1: 2 
PU2: 3
SU1: 4
SU2: 5
'''

primary_1_flag = False
primary_2_flag = False

# Initialize first RTL-SDR device
sdr1 = RtlSdr(serial_number='000000101')
sdr1.sample_rate = 2.048e6
sdr1.center_freq = 433e6
sdr1.gain = 30

# Initialize second RTL-SDR device
sdr2 = RtlSdr(serial_number='000000102')
sdr2.sample_rate = 2.048e6
sdr2.center_freq = 500e6  # Change this to the desired center frequency for the second device
sdr2.gain = 52.5

# Function to update plot for the first device
def update_plot1(samples):
    plt.figure(1)  # Create or select the first figure
    plt.clf()  # Clear the current plot
    plt.psd(samples, NFFT=1024, Fs=sdr1.sample_rate/1e6, Fc=sdr1.center_freq/1e6)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Relative power (dB)')
    plt.pause(0.01)  # Pause to allow the plot to update

# Function to update plot for the second device
def update_plot2(samples):
    plt.figure(2)  # Create or select the second figure
    plt.clf()  # Clear the current plot
    plt.psd(samples, NFFT=1024, Fs=sdr2.sample_rate/1e6, Fc=sdr2.center_freq/1e6)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Relative power (dB)')
    plt.pause(0.01)  # Pause to allow the plot to update
    

def send_data(data):
    rfm9x.send(bytes(data, "UTF-8"))
    print("sent: ", data)

c = 0

def updateStatus():
    global c
    start_time = time.time()
    while(time.time() - start_time) <15:
    # if (c<15):
        global status
        status = [1, 0]
        c+=1
    status = [0, 0]
    # else:
    #     status = [0, 0]
    #     c = 0


def main():
    global primary_1_flag 
    global primary_2_flag

    while True:
        message = ""  # Initialize message variable

        packet = rfm9x.receive(timeout=0.2)  # non-blocking receive
        if packet is not None:

            request = ''.join([chr(byte) for byte in packet])
            arr = request.split(",")
            source = int(arr[0])
            message = arr[1]
            destination = int(arr[-1])

            if destination == ownAddress:
                print("recieved:", request)
                print("src: {}, dest: {} ".format(source, destination))

                if(source == primary_users[0]):
                    primary_1_flag = True
                elif (source == primary_users[1]):
                    primary_2_flag = True

                if source not in queue and message!="end":
                    if(message!="PU"):
                        queue.append(source)
                    message_1 = str(source) + "," + "ACK," + str(destination)
                    send_data(message_1)

                    time.sleep(1)


            print("Queue:", queue)

        
        index_of_free = [index for index, value in enumerate(status) if value == 0]

        #case: 1 free channel
        if (len(index_of_free)==1 or (len(index_of_free)==2 and len(queue)==1)):
            freq_to_allocate = frequency [index_of_free[0]]
            # print(freq_to_allocate)

            # Send data
            if(len(queue)!=0 and message!="end" and len(index_of_free)!=0):
                if(freq_to_allocate == frequency[0] and primary_1_flag==False):
                    message = str(queue[0]) + "," + str(freq_to_allocate)+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                elif(freq_to_allocate == frequency[0] and primary_1_flag==True):
                    message = str(queue[0]) + "," + str(-1)+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                    #updateStatus()

                    if(status[0]==0):
                        primary_1_flag=False

                # elif(status[0]==0):
                #     primary_1_flag==False
                elif(freq_to_allocate == frequency[1] and primary_2_flag==False):
                    message = str(queue[0]) + "," + str(freq_to_allocate)+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                
                elif(freq_to_allocate == frequency[1] and primary_2_flag==True):
                    message = str(queue[0]) + "," + str(-1)+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                    #updateStatus()

                    if(status[1]==0):
                        primary_2_flag=False

        #case: 2 free channels
        elif (len(index_of_free)==2 and len(queue)==2):
            freq_to_allocate = frequency # freq_to_allocate = [433, 500]
            # print(freq_to_allocate)

            # Send data
            if(len(queue)!=0 and message!="end" and len(index_of_free)!=0):
                if(freq_to_allocate [0] == frequency[0] and primary_1_flag==False):
                    message = str(queue[0]) + "," + str(freq_to_allocate [0])+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                elif(freq_to_allocate [0] == frequency[0] and primary_1_flag==True):
                    message = str(queue[0]) + "," + str(-1)+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                    #updateStatus()

                    if(status[0]==0):
                        primary_1_flag=False

                # elif(status[0]==0):
                #     primary_1_flag==False
                if(freq_to_allocate [1] == frequency[1] and primary_2_flag==False):
                    message = str(queue[1]) + "," + str(freq_to_allocate [1])+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                
                elif(freq_to_allocate [1] == frequency[1] and primary_2_flag==True):
                    message = str(queue[1]) + "," + str(-1)+","+ str(destination)
                    send_data(message)
                    time.sleep(transmit_interval)
                    #updateStatus()

                    if(status[1]==0):
                        primary_2_flag=False
                    
        
        if(message == "end" and len(queue)!=0 and source==queue[0]):
            queue.pop(0)
            message = ""
            print("Queue:", queue)
        
        elif(message == "end" and len(queue)!=0 and source==queue[1]):
            queue.pop(1)
            message = ""
            print("Queue:", queue)
        

# # Close RTL-SDR devices
# sdr1.close()
# sdr2.close()
            
# Create a thread
thread = threading.Thread(target=main)
# Start the thread
thread.start()

# Continuously capture and plot samples for both devices
try:
    while True:
        samples1 = sdr1.read_samples(1024)  # Capture samples for first device
        #print(sampl500e6es1)
        real_part = np.real(samples1)
        imaginary_part = np.imag(samples1)

        # Create a 2-column array
        I_Q_matrix = np.column_stack((real_part, imaginary_part))
        #print(I_Q_matrix)
        X_test_reshaped = I_Q_matrix.reshape(1, 1024, 2, 1)
        interpreter.set_tensor(input_details[0]['index'], X_test_reshaped.astype(np.float32))
        interpreter.invoke()
        tflite_model_predictions = interpreter.get_tensor(output_details[0]['index'])
        #print("Prediction results shape:", tflite_model_predictions.shape)
        prediction_classes = np.argmax(tflite_model_predictions, axis=1)
        status[0]= int(prediction_classes)
        #print("sdr1: ")
        #print(prediction_classes)
        update_plot1(samples1)  # Update plot for first device
        del samples1

        samples2 = sdr2.read_samples(1024)  # Capture samples for second device
        real_part = np.real(samples2)
        imaginary_part = np.imag(samples2)

        # Create a 2-column array
        I_Q_matrix = np.column_stack((real_part, imaginary_part))
        #print(I_Q_matrix)
        X_test_reshaped = I_Q_matrix.reshape(1, 1024, 2, 1)
        interpreter.set_tensor(input_details[0]['index'], X_test_reshaped.astype(np.float32))
        interpreter.invoke()
        tflite_model_predictions = interpreter.get_tensor(output_details[0]['index'])
        #print("Prediction results shape:", tflite_model_predictions.shape)

        prediction_classes = np.argmax(tflite_model_predictions, axis=1)
        status[1]= int(prediction_classes)
        #print("sdr2: ")
        #print(prediction_classes)
        update_plot2(samples2)  # Update plot for second device

        del samples2

        # print("Status:", status)
        # print("Queue:", queue)

except KeyboardInterrupt:  # Exit gracefully on Ctrl+C
    pass

# Close RTL-SDR devices
sdr1.close()
sdr2.close()