#-*- encoding: utf-8 -*-
import serial
import glob
import os
from datetime import date
from datetime import datetime

constants = {}
with open("constants.h") as f:
	plaintext = f.read()
for a in plaintext.splitlines():
	b = a.split(' ', 4)
	constants[str(b[2])] = (int if b[1]=="int" else str)(b[4][:-2])
SF = constants["initSf"]
TxPower = constants["initTxPower"]
hoje = "testes/"+date.today().strftime("%Y-%m-%d_")

def writeToLog(msg):
	with open("log", "a") as f:
		f.write(date.today().strftime("%Y-%m-%d_")+"|"+datetime.now().strftime("%H:%M:%S.%f")+"  ---->  "+msg+"\n")
def getNextTxPower(sf, txp):
	txp+=1
	if(txp>constants["maxTxPower"]):
		txp = constants["minTxPower"]
		sf+=1
		if(sf>constants["maxSf"]):
			sf = constants["minSf"]
	return sf, txp

voidMessage = True
testEnd = True
print("Qual a distância (em centímetros) entre os dispositivos? ", end = " ")
while(True):
	try:
		dis = input()
		break
	except:
		continue
while(testEnd==True):
	files = glob.glob(hoje+"*")
	files.sort(key= lambda x: int(x.split("_")[1]))
	n="0"
	if files:
		n=files[len(files)-1][len(hoje):]
	fileName = hoje+str(int(n)+1)

	voidMessage = True
	testEnd = False
	with open(fileName, "w") as f:
		rcvPackages = 0
		print("O arquivo '"+fileName+"' foi criado com sucesso! Gravando resultados ...")
		writeToLog("Arquivo "+fileName+" criado")
		print("SF: "+str(SF)+", TxPower: "+str(TxPower))
	
		try:
			f.write(hoje[7:-1]+" 115200 "+dis+" "+str(SF)+" "+str(TxPower)+" "+str(constants["nPackets"])+"\n")
			while True:
				with serial.Serial('/dev/ttyUSB0', 115200, timeout = None) as ser:
					try:
						x = ser.readline()
						x = x.decode().replace("\n", "").replace("\r", "")
					except:
						continue
						
					if(len(x)>3):
						if(x[0]=='E' and x[1]=='N'):
							if(x[2]=='D'):
								if(voidMessage==False):
									aux = x[3]
									if(len(x)>4):
										aux+=x[4]
									SF,TxPower = getNextTxPower(SF, int(aux))
									print("\nArquivo '"+fileName+"' foi salvo com sucesso!\nAguardando novo teste...")
									writeToLog(str(rcvPackages)+" pacotes salvos no arquivo "+fileName)
									testEnd = True
									f.close()
									break
							elif(x[2]=='S'):
								continue
						else:
							voidMessage = False
							try:
								f.write(str(datetime.now().strftime("%H:%M:%S.%f"))+" "+x+"\n")
								rcvPackages+=1
							except:
								continue
		except Exception as e:
			if(voidMessage==True):
				os.remove(fileName)
				print("Erro inesperado! O arquivo "+fileName+" foi excluído!")
				writeToLog(str(e))
				writeToLog("Arquivo "+fileName+" excluído. "+str(rcvPackages)+" pacotes haviam sido recebidos")
			else:
				print("\nArquivo '"+fileName+"' foi salvo com sucesso!\n Fim dos Testes!")
			raise

