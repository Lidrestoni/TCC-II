#include "functions.h"

void setup() {
  pinMode(16,OUTPUT);
  pinMode(2,OUTPUT);
  generalSetup("Sender");
}

void loop() {
  clearDisplay();
      
  if(msgCounter>=nPackets){
    if(msgCounter<nPackets+endOfTestsDelay){
      display.drawString(0, 0, "Tests with TxPower "+String(TxPower));
      display.drawString(0, 15," have ended!");
      if(TxPower+1>maxTxPower){
        display.drawString(0, 30, "Changing Spreading Factor");
        display.drawString(0, 45, " to " + String(LoRa.getSpreadingFactor()+1>maxSf? minSf: LoRa.getSpreadingFactor()+1));  
      }
      
      display.display();

      // send packet
      LoRa.beginPacket();
      LoRa.print("END");
      LoRa.endPacket();
    }
    else
      raiseTxPower();
  }
  else{
   display.drawString(0, 0, "Sending packet: "+String(msgCounter+1)+" / "+String(nPackets));
   display.drawString(0, 15, "Tx Power: "+String(TxPower));
   display.drawString(0, 30, "Spreading Factor: "+String(LoRa.getSpreadingFactor()));
   Serial.println(String(msgCounter+1));
   display.display();

   // send packet
   LoRa.beginPacket();
   LoRa.print(validMessage);
   LoRa.endPacket();
  }
  
  msgCounter++;
  digitalWrite(2, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(2, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
