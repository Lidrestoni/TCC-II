#include "functions.h"

void cbk(int packetSize) {
  packet = "";
  packSize = String(packetSize, DEC);
  for (int i = 0; i < packetSize; i++) {
    packet += (char) LoRa.read();
  }
  
  if (packetSize==3) {
    int aux = raiseTxPower();
    if (aux==1) {
      clearDisplay();
      display.drawString(0, 0, "Tests with TxPower " + String(TxPower-1));
      display.drawString(0, 15, " have ended!");
    }
    else if(aux==2){
      clearDisplay();
      display.drawString(0, 0, "Tests with TxPower " + String(maxTxPower));
      display.drawString(0, 15, " have ended!");
      display.drawString(0, 30, "Changing Spreading Factor");
      display.drawString(0, 45, " to " + String(LoRa.getSpreadingFactor()));
    }
    Serial.println("END");
  }
  else{
    clearDisplay();
    display.drawString(0, 0, "RSSI: " + String(LoRa.packetRssi(), DEC));
    display.drawString(0, 12, "SNR: " + String(LoRa.packetSnr(), DEC));
    if (validMessage.equals(packet)) {
      msgCounter += 1;
      display.drawString(0, 24, "Received packet " + String(msgCounter) + " / " + String(nPackets));
      display.drawString(0, 36, "TxPower: " + String(TxPower));
      display.drawString(0, 48, "SF: " + String(LoRa.getSpreadingFactor()));
      Serial.println(String(LoRa.packetRssi(), DEC) + " " + String(LoRa.packetSnr(), DEC));
    }
    else {
      int a = countCorrectCharIn(packet);
      if(a>=0){
        display.drawString(0 , 24 , "Received broken message! ");
        display.drawString(0 , 36 , "Correct char: "+String(a)+" / "+String(validMessage.length()) );
        Serial.println("BRK "+String(a)+" "+String(LoRa.packetRssi(), DEC) + " " + String(LoRa.packetSnr(), DEC));
      }
    }
  }
  display.display();
}

void setup() {
  pinMode(16, OUTPUT);
  generalSetup("Receiver");
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    cbk(packetSize);
  }
  delay(10);
}
