#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 2

#define DEFAULT_CHANNEL_FREQ 440.0
#define MAX_TOKENS 10

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

// Address of the receiver Arduino Uno
uint8_t ArduinoAddress = 5;
// Address of the SU
uint8_t nodeAddress = 1;

void setup() {
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.begin(9600);
  while (!Serial);

  Serial.println("Arduino LoRa TX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1);
  }
  Serial.println("LoRa radio init OK!");

  // Set default frequency
  setFrequency(440.0);
}

float newFrequencyReceived = 0;
float Count = 0;
float Send_data_Count = 0;

void loop() {
  ///send request
  if(Send_data_Count == 11){
    Send_data_Count == 12;
    return;
  }


  if(Count == 0){
    //Count = 1;
    // Serial.print("Count: "); Serial.println(Count);
    String dataToSend = String(ArduinoAddress);
    dataToSend += String(",start,"); 
    dataToSend += String(nodeAddress);

    // Send data packet
    rf95.send((uint8_t*)dataToSend.c_str(), dataToSend.length());
    rf95.waitPacketSent();

    ///////////////////////////////////////////////////////////

    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    Serial.println("Waiting for reply..."); delay(0);
    if (rf95.waitAvailableTimeout(1000)) {
      // Should be a reply message for us now   
      if (rf95.recv(buf, &len)) {
        String str = "";
        str += (char)buf[0];
        if (str == (String)ArduinoAddress){
          Serial.print("Got reply: ");
          Serial.println((char*)buf);
          Count = 1;
        }
      } else {
        Serial.println("Receive failed");
      }
    } else {
      Serial.println("No reply, is there a listener around?");

    }

    Serial.print("count in start: "); Serial.println(Count);
  }else if (Send_data_Count == 10){
    setFrequency(DEFAULT_CHANNEL_FREQ);

    
    String dataToSend = String(ArduinoAddress);
    dataToSend += String(",end,"); 
    dataToSend += String(nodeAddress);

    // Send data packet
    rf95.send((uint8_t*)dataToSend.c_str(), dataToSend.length());
    rf95.waitPacketSent();
    delay(1000);
    rf95.send((uint8_t*)dataToSend.c_str(), dataToSend.length());
    rf95.waitPacketSent();
    delay(1000);
    rf95.send((uint8_t*)dataToSend.c_str(), dataToSend.length());
    delay(1000);
    //rf95.waitPacketSent();
    Send_data_Count = 11;
  }
  //wait for reply
  
    // Listen for new channel frequency
  if(Count != 0) listenForChannelFrequency();

  if(newFrequencyReceived > 0 && newFrequencyReceived != DEFAULT_CHANNEL_FREQ) {
    sendData();
  } 

}

void setFrequency(float frequency) {
  if (!rf95.setFrequency(frequency)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  //Serial.print("Set Freq to: "); Serial.println(frequency);
}

int split(char *str, char *delimiters, char *tokens[]) {
    int token_count = 0;
    char *token = strtok(str, delimiters);

    while (token != NULL && token_count < MAX_TOKENS) {
        tokens[token_count++] = token;
        token = strtok(NULL, delimiters);
    }

    return token_count;
}

void listenForChannelFrequency() {
  //Serial.println("Listening for new channel frequency...");

  // Set the radio to listen on the default frequency
  //if(Send_data_Count == 0 || Send_data_Count == 10)
  setFrequency(DEFAULT_CHANNEL_FREQ);
  newFrequencyReceived = DEFAULT_CHANNEL_FREQ;
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  // Listen for a packet on the default frequency (437 MHz)
  if (rf95.waitAvailableTimeout(1000)) {
    if (rf95.recv(buf, &len)) {
      String str = "";
      str += (char)buf[0];
      if (str == (String)ArduinoAddress){
        // float newFrequency = atof((char*)buf);
        String str1 = "";
        for (int i = 0; i < len; i++) {
            str1 += (char)buf[i];
        }

        char input[str1.length() + 1];
        str1.toCharArray(input, sizeof(input));

        char *delimiters = ",";
        char *tokens[MAX_TOKENS]; // Array to store the split tokens
        int token_count = split(input, delimiters, tokens);

        float newFrequency = atof((char*)tokens[1]);
        newFrequencyReceived = newFrequency;
        // Set new frequency
        Serial.println(newFrequencyReceived);
        setFrequency(newFrequencyReceived);
        //Serial.print("New Frequency set to: ");
        Serial.println(newFrequencyReceived);
      }
      // Extract frequency from received packet
      
    } else {
      Serial.println("Receive failed");
    }
  } else {
    //Serial.println("No new channel frequency received.");
  }
}

void sendData() {
  if(Send_data_Count <= 10){
    Serial.println("Sending to rf95_server");
    // Send a message to rf95_server
    
    char radiopacket[20] = "Hello World #      ";
    static int16_t packetnum = 0; // packet counter, we increment per xmission
    itoa(packetnum++, radiopacket + 13, 10);
    Serial.print("Sending "); Serial.println(radiopacket);
    radiopacket[19] = 0;

    Serial.println("Sending..."); delay(10);
    rf95.send((uint8_t *)radiopacket, 20);

    Serial.println("Waiting for packet to complete..."); delay(10);
    rf95.waitPacketSent();
    delay(1000); // Add a delay between sending and receiving
    Send_data_Count = Send_data_Count + 1;
  }
    
  
}

