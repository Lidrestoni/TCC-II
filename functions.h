#include <LoRa.h>
#include "SSD1306.h"
#include "constants.h"

#define SCK     5    // GPIO5  -- SX1278's SCK
#define MISO    19   // GPIO19 -- SX1278's MISnO
#define MOSI    27   // GPIO27 -- SX1278's MOSI
#define SS      18   // GPIO18 -- SX1278's CS
#define RST     14   // GPIO14 -- SX1278's RESET
#define DI0     26   // GPIO26 -- SX1278's IRQ(Interrupt Request)
#define endOfTestsDelay 7

SSD1306 display(0x3c, 21, 22);
String packSize = "--";
String packet ;
unsigned int TxPower = minTxPower;
int msgCounter = 0;

int countCorrectCharIn(String msg){
  int cnt = 0;
  if(msg.length()<validMessage.length()-2 or msg.length()>validMessage.length()+2)
    return -1;
  int sml = validMessage.length()>msg.length()? msg.length() :  validMessage.length();
  for(int i=0; i<sml; i++)
    if(msg[i]==validMessage[i])
      cnt+=1;
  return cnt;
}

void startSFandTXPat(unsigned int sf, unsigned int txp){
	LoRa.setSpreadingFactor(sf);
	LoRa.setTxPower(txp);
	TxPower = txp;
}

void raiseSpreadingFactor(){
	unsigned int sf = LoRa.getSpreadingFactor()+1;
	if(sf<=maxSf)
		LoRa.setSpreadingFactor(sf);
	else
		LoRa.setSpreadingFactor(minSf);
  msgCounter=0;
}

int raiseTxPower(){
  if(msgCounter>1){
    msgCounter=0;
    if(TxPower+1>maxTxPower){
      raiseSpreadingFactor();
      TxPower = minTxPower;
      return 2;  
    }
    else{
      TxPower+=1;
      return 1;
    }
  }
  return 0;  
}

void generalSetup(String nm){
	digitalWrite(16, LOW);    // set GPIO16 low to reset OLED
	delay(50); 
	digitalWrite(16, HIGH); // while OLED is running, must set GPIO16 in high
  
	Serial.begin(115200);
	while (!Serial);
	Serial.println();
	Serial.println("LoRa "+nm+" Test");
	SPI.begin(SCK,MISO,MOSI,SS);
	LoRa.setPins(SS,RST,DI0);
	if (!LoRa.begin(915E6, TxPower)) {
		Serial.println("Starting LoRa failed!");
		while (1);
	}
	startSFandTXPat(initSf,initTxPower);
	Serial.println("init ok");
	display.init();
	display.flipScreenVertically();  
	display.setFont(ArialMT_Plain_10);
  
	delay(1500);
}

void clearDisplay(){
	display.clear();
	display.setTextAlignment(TEXT_ALIGN_LEFT);
	display.setFont(ArialMT_Plain_10);
}
