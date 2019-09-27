#include "functions.h"

String rssi = "RSSI --";
String snr = "SNR --";
String aux ;
String cTxp = String(initTxPower);

void cbk(int packetSize) {
  packet ="";
  packSize = String(packetSize,DEC);
  for (int i = 0; i < packetSize; i++) { 
    packet += (char) LoRa.read(); 
  }
   
  clearDisplay();
    
  if(packet[0]=='E'&&packet[1]=='N'){
    aux = packet[3];
    if(packetSize>3)
      aux+=packet[4];
    if(packet[2]=='D'){
      display.drawString(0, 0, "Tests with TxPower "+String(aux));
      display.drawString(0, 15," have ended!");
      cTxp = String(aux.toInt()+1);
    }
    else{
      display.drawString(0, 0, "Changing Spreading Factor");
      display.drawString(0, 15," to "+String(aux));
      LoRa.setSpreadingFactor(aux.toInt());
      cTxp = String(minTxPower);
    }
    
    Serial.println(packet);
  }
  else if(validMessage.equals(packet)){
    rssi = "RSSI " + String(LoRa.packetRssi(), DEC) ;
    snr = "SNR " + String(LoRa.packetSnr(),DEC);
    display.drawString(0, 0, rssi); 
    display.drawString(0, 10, snr);
    display.drawString(0, 20, "SF: "+String(LoRa.getSpreadingFactor()));
    display.drawString(0, 30, "TxPower: "+cTxp); 
    display.drawString(0, 40, "Received "+ packSize + " bytes");
    Serial.println(rssi+" "+snr);
  }   
  else
    display.drawString(0 , 0 , "Broken package!");
  display.display();
}

void setup() {
  pinMode(16,OUTPUT);
  generalSetup("Receiver");
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    cbk(packetSize);
  }
  delay(10);
}
