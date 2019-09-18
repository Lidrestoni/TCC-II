#include <LoRa.h>  
#include "SSD1306.h" 


#define SCK     5    // GPIO5  -- SX1278's SCK
#define MISO    19   // GPIO19 -- SX1278's MISnO
#define MOSI    27   // GPIO27 -- SX1278's MOSI
#define SS      18   // GPIO18 -- SX1278's CS
#define RST     14   // GPIO14 -- SX1278's RESET
#define DI0     26   // GPIO26 -- SX1278's IRQ(Interrupt Request)

#define maxCounter 600
#define minTxPower 2
#define maxTxPower 17
unsigned int counter = 0;

SSD1306 display(0x3c, 21, 22);
String packSize = "--";
String packet ;
unsigned int TxPower = minTxPower;

void raiseTxPower(){
  TxPower++;
  if(TxPower<=maxTxPower)
    LoRa.resetTxPower(TxPower);  
}

void setup() {
  pinMode(16,OUTPUT);
  pinMode(2,OUTPUT);
  
  digitalWrite(16, LOW);    // set GPIO16 low to reset OLED
  delay(50); 
  digitalWrite(16, HIGH); // while OLED is running, must set GPIO16 in high
  
  Serial.begin(115200);
  while (!Serial);
  Serial.println();
  Serial.println("LoRa Sender Test");
  
  SPI.begin(SCK,MISO,MOSI,SS);
  LoRa.setPins(SS,RST,DI0);
  if (!LoRa.begin(915E6, TxPower)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("init ok");
  display.init();
  display.flipScreenVertically();  
  display.setFont(ArialMT_Plain_10);
  
  delay(1500);
}

void loop() {
  display.clear();
  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.setFont(ArialMT_Plain_10);
  
  if(counter>maxCounter){
    if(counter<maxCounter+7){
      display.drawString(0, 0, "Tests with TxPower "+String(TxPower));
      display.drawString(0, 15," have ended!");
      display.display();

      // send packet
      LoRa.beginPacket();
      LoRa.print("END"+String(TxPower));
      LoRa.endPacket();
    }
    else{
      raiseTxPower();
      if(TxPower>maxTxPower){
        display.drawString(0, 0, "Maximum TxPower of "+String(maxTxPower+1));
        display.drawString(0, 15, " has been reached!");
        display.display();
      }
      else{
        counter = -1;
      }  
    }
  }
  else{
   display.drawString(0, 0, "Sending packet: ");
   display.drawString(90, 0, String(counter));
   display.drawString(0, 15, "Tx Power: ");
   display.drawString(60, 15, String(TxPower));
   Serial.println(String(counter));
   display.display();

   // send packet
   LoRa.beginPacket();
   LoRa.print("oi ");
   LoRa.print(counter);
   LoRa.print(" ");
   LoRa.print(TxPower);
   LoRa.endPacket();
  }
  
  counter++;
  digitalWrite(2, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(2, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
