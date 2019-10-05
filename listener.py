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

def printAndWriteToLog(msg):
	print(msg)
	writeToLog(msg)
	
def getNextTxPower(sf, txp):
	txp+=1
	if(txp>constants["maxTxPower"]):
		txp = constants["minTxPower"]
		sf+=1
		if(sf>constants["maxSf"]):
			sf = constants["minSf"]
	return sf, txp
	
def writeToFile(f, fName, msg):
	try:
		f.write(msg)
	except Exception as e:
		printAndWriteToLog("Não consegui registrar a  mensagem '"+msg+"'")
		raise
		
def closingFileProcedures(fileName, rcvPackages, deleteFile):
	if(deleteFile==True):
		printAndWriteToLog("Arquivo '"+fileName+"' fechado e excluído! Execução interrompida antes do recebimento da mensagem de fim de teste")
		os.remove(fileName)
	else:
		printAndWriteToLog("Arquivo '"+fileName+"' foi salvo! "+str(rcvPackages)+" pacotes foram recebidos")
	return 0
	
def foundBrokenPackage(n, fil):
	fil.write(str(datetime.now().strftime("%H:%M:%S.%f"))+" BROKEN\n")
	return n+1

brkPackages=rcvPackages = 0
keepTesting = True
print("Qual a distância (em centímetros) entre os dispositivos? ", end = " ")
while(True):
	try:
		dis = input()
		break
	except:
		continue
		
while(keepTesting==True):
	files = glob.glob(hoje+"*")
	files.sort(key= lambda x: int(x.split("_")[1]))
	n="0"
	if files:
		n=files[len(files)-1][len(hoje):]
	fileName = hoje+str(int(n)+1)

	keepTesting = False
	with open(fileName, "w") as f:
		printAndWriteToLog("O arquivo '"+fileName+"' foi criado com sucesso! Gravando resultados ...")
		printAndWriteToLog("SF: "+str(SF)+", TxPower: "+str(TxPower))
		writeToFile(f, fileName,hoje[7:-1]+" 115200 "+dis+" "+str(SF)+" "+str(TxPower)+" "+str(constants["nPackets"])+"\n")
		while True:
			usbs = glob.glob('/dev/ttyUSB*')
			usbs.sort()
			if(len(usbs)==0):
				printAndWriteToLog("Nenhum ttyUSB encontrado")
				closingFileProcedures(fileName, rcvPackages, True)
				break
			try:
				with serial.Serial(usbs[0], 115200, timeout = None) as ser:
					try:
						x = ser.readline()
						x = x.decode().replace("\n", "").replace("\r", "")
					except:
						printAndWriteToLog("A linha não pôde ser lida "+len(x))
						continue
					
					if(len(x)>3):
						if(x[0]=='E' and x[1]=='N' and x[2]=='D'):
							aux = int(x[3:])
							if(aux==TxPower):
								SF,TxPower = getNextTxPower(SF, aux)
								brkPackages=rcvPackages = closingFileProcedures(fileName, rcvPackages, False)
								keepTesting = True
								break
						else:
							try:
								f.write(str(datetime.now().strftime("%H:%M:%S.%f"))+" "+x+"\n")
								if(len(x)>6+len(constants["validMessage"])-3 and x[:6]=="BROKEN"):
									brkPackages+=1
								else:
									rcvPackages+=1
							except:
								printAndWriteToLog("Não consegui escrever '"+x+"' no arquivo")
								continue
			except:
				brkPackages = foundBrokenPackage(brkPackages, f)
				continue
								
printAndWriteToLog("Fim dos testes")
