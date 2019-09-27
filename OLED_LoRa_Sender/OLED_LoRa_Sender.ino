#include "functions.h"

void setup() {
  pinMode(16,OUTPUT);
  pinMode(2,OUTPUT);
  generalSetup("Sender");
}

void loop() {
  clearDisplay();
  int sf = LoRa.getSpreadingFactor();
  sf = sf+1>maxSf? minSf : sf+1;
  
  if(raiseSF->waiting()){
      display.drawString(0, 0, "Changing Spreading Factor");
      display.drawString(0,15, " to "+String(sf));
      display.display();

      // send packet
      LoRa.beginPacket();
      LoRa.print("ENS"+String(sf));
      LoRa.endPacket(); 
      raiseSF->tickTack();
      if(!raiseSF->waiting())
        setTxPowerTo(TxPower+1,0);
        
  }
  else if(counter>nPackets){
    if(counter<nPackets+endOfTestsDelay){
      display.drawString(0, 0, "Tests with TxPower "+String(TxPower));
      display.drawString(0, 15," have ended!");
      display.display();

      // send packet
      LoRa.beginPacket();
      LoRa.print("END"+String(TxPower));
      LoRa.endPacket();
    }
    else
      setTxPowerTo(TxPower+1,endOfTestsDelay); 
  }
  else{
   display.drawString(0, 0, "Sending packet: ");
   display.drawString(90, 0, String(counter));
   display.drawString(0, 15, "Tx Power: ");
   display.drawString(60, 15, String(TxPower));
   display.drawString(0, 30, "Spreading Factor: ");
   display.drawString(90, 30, String(LoRa.getSpreadingFactor()));
   Serial.println(String(counter));
   display.display();

   // send packet
   LoRa.beginPacket();
   LoRa.print(validMessage);
   /*LoRa.print(LoRa.getSpreadingFactor());
   LoRa.print(" ");
   LoRa.print(counter);
   LoRa.print(" ");r
   LoRa.print(TxPower);*/
   LoRa.endPacket();
  }
  
  counter++;
  digitalWrite(2, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(2, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
