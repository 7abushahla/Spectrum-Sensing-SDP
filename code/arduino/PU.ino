#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 2

#define PU_Frequency 433.0
#define CN_Frequency 440.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

uint8_t PU_Address = 2;
uint8_t nodeAddress = 1;

unsigned long startTime = 0;

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
  setFrequency(PU_Frequency);

  startTime = millis();
}

float Count = 0;

void loop() {

  ACK();
  
  if(Count != 0){
    if (millis() - startTime < 50000) {
      sendAndReceive();
    }else{
      return;

    }
  }
  
}

void ACK(){
  if(Count == 0){
    setFrequency(CN_Frequency);
    String dataToSend = String(PU_Address);
    dataToSend += String(",PU,"); 
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
        if (str == (String)PU_Address){
          Serial.print("Got reply: ");
          Serial.println((char*)buf);
          Count = 1;
          setFrequency(PU_Frequency);
        }
      } else {
        Serial.println("Receive failed");
      }
    } else {
      Serial.println("No reply, is there a listener around?");

    }

    Serial.print("count in start: "); Serial.println(Count);
  }
}


void setFrequency(float frequency) {
  if (!rf95.setFrequency(frequency)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(frequency);
}

void sendAndReceive() {
  Serial.println("Sending to rf95_server");
  // Send a message to rf95_server
  
  char radiopacket[20] = "Hello World #      ";
  static int16_t packetnum = 0; // packet counter, we increment per xmission
  itoa(packetnum++, radiopacket + 13, 10);
  Serial.print("Sending "); Serial.println(radiopacket);
  radiopacket[19] = 0;

  Serial.println("Sending..."); delay(10);
  rf95.send((uint8_t *)radiopacket, 20);

  // Serial.println("Waiting for packet to complete..."); delay(10);
  // rf95.waitPacketSent();
}
