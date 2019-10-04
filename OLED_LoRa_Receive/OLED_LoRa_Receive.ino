#include "functions.h"

String rssi = "RSSI --";
String snr = "SNR --";
String aux ;
String cTxp = String(initTxPower);
int counter = 0;

void cbk(int packetSize) {
  packet = "";
  packSize = String(packetSize, DEC);
  for (int i = 0; i < packetSize; i++) {
    packet += (char) LoRa.read();
  }

  clearDisplay();

  if (packet[0] == 'E' && packet[1] == 'N') {
    aux = packet[3];
    if (packetSize > 3)
      aux += packet[4];
    if (packet[2] == 'D') {
      display.drawString(0, 0, "Tests with TxPower " + String(aux));
      display.drawString(0, 15, " have ended!");
      cTxp = String(aux.toInt() + 1);
    }
    else {
      display.drawString(0, 0, "Changing Spreading Factor");
      display.drawString(0, 15, " to " + String(aux));
      LoRa.setSpreadingFactor(aux.toInt());
      cTxp = String(minTxPower);
    }
    counter = 0;
    Serial.println(packet);
  }
  else if (validMessage.equals(packet)) {
    counter += 1;
    rssi = "RSSI: " + String(LoRa.packetRssi(), DEC) ;
    snr = "SNR: " + String(LoRa.packetSnr(), DEC);
    display.drawString(0, 0, "Recebido pacote " + String(counter) + " / " + String(nPackets));
    display.drawString(0, 12, rssi);
    display.drawString(0, 24, snr);
    display.drawString(0, 36, "SF: " + String(LoRa.getSpreadingFactor()));
    display.drawString(0, 48, "TxPower: " + cTxp);
    Serial.println(rssi + " " + snr);
  }
  else {
    display.drawString(0 , 0 , "Broken! Message received:");
    display.drawStringMaxWidth(0, 15, 128, packet);
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
