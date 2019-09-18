#include <LoRa.h>
#include "SSD1306.h" 

#define SCK     5    // GPIO5  -- SX1278's SCK
#define MISO    19   // GPIO19 -- SX1278's MISO
#define MOSI    27   // GPIO27 -- SX1278's MOSI
#define SS      18   // GPIO18 -- SX1278's CS
#define RST     14   // GPIO14 -- SX1278's RESET
#define DI0     26   // GPIO26 -- SX1278's IRQ(Interrupt Request)

SSD1306 display(0x3c, 21, 22);
String rssi = "RSSI --";
String snr = "SNR --";
String packSize = "--";
String packet ;
String TxPower ;

void cbk(int packetSize) {
  packet ="";
  packSize = String(packetSize,DEC);
  for (int i = 0; i < packetSize; i++) { 
    packet += (char) LoRa.read(); 
  }
  
  display.clear();
  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.setFont(ArialMT_Plain_10);
    
  if(packet[0]=='E'&&packet[1]=='N'&&packet[2]=='D'){
    TxPower = packet[3];
    if(packetSize>3){
      TxPower+=packet[4];
    }
    display.drawString(0, 0, "Tests with TxPower "+String(TxPower));
    display.drawString(0, 15," have ended!");
    Serial.println(packet);
  }
  else{
    rssi = "RSSI " + String(LoRa.packetRssi(), DEC) ;
    snr = "SNR " + String(LoRa.packetSnr(),DEC);
    display.drawString(0 , 20 , "Received "+ packSize + " bytes");
    display.drawStringMaxWidth(0 , 36 , 128, packet);
    display.drawString(0, 0, rssi); 
    display.drawString(0, 10, snr); 
    Serial.println(packet+")RSSI: "+rssi+ " SNR: "+snr);
  }   
  display.display();
}

void setup() {
  pinMode(16,OUTPUT);
  digitalWrite(16, LOW);    // set GPIO16 low to reset OLED
  delay(50); 
  digitalWrite(16, HIGH); // while OLED is running, must set GPIO16 in high、
  
  Serial.begin(115200);
  while (!Serial);
  Serial.println();
  Serial.println("LoRa Receiver Callback");
  SPI.begin(SCK,MISO,MOSI,SS);
  LoRa.setPins(SS,RST,DI0);  
  if (!LoRa.begin(915E6,1)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.receive();
  Serial.println("init ok");
  display.init();
  display.flipScreenVertically();  
  display.setFont(ArialMT_Plain_10);
   
  delay(1500);
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) { cbk(packetSize);  }
  delay(10);
}
