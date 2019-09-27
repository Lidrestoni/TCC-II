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

class WaitingAction{
	private:
		unsigned int cnt;
	public:
		WaitingAction(){
			this->cnt=0;
		}
		bool waiting(){
			return this->cnt>0;
		}
		void tickTack(){
			this->cnt-= this->cnt>0;
		}
		void setCounterTo(unsigned int n){
			if(n>0)
				this->cnt = n;
		}
};
WaitingAction *raiseSF = new WaitingAction();

SSD1306 display(0x3c, 21, 22);
String packSize = "--";
String packet ;
unsigned int TxPower = minTxPower;
int counter = 0;

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
	counter = -1;  
}

void setTxPowerTo(unsigned int n, unsigned int delay){
		if(n>=minTxPower&&TxPower!=n){
			if(n>maxTxPower){
				if(delay)
					raiseSF->setCounterTo(delay);
				else{
					raiseSpreadingFactor();
					TxPower = minTxPower;
				}
			}
			else{
				LoRa.setTxPower(TxPower);
				TxPower = n;
			}
			counter = -1;
		}
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
