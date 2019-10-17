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
brkPackages= 0
rcvPackages = 0

def writeToLog(msg):
	with open("../TCC-II-logs/log", "a") as f:
		f.write(date.today().strftime("%Y-%m-%d_")+"|"+datetime.now().strftime("%H:%M:%S.%f")+"  ---->  "+msg+"\n")

def printAndWriteToLog(msg):
	print(msg)
	writeToLog(msg)
	
def raiseTxPower():
	global rcvPackages, brkPackages, TxPower, SF
	brkPackages=rcvPackages=0;
	TxPower+=1
	if(TxPower>constants["maxTxPower"]):
		TxPower= constants["minTxPower"]
		SF+=1
		if(SF>constants["maxSf"]):
			SF = constants["minSf"]
	
def writeToFile(f, fName, msg):
	try:
		f.write(msg)
	except Exception as e:
		printAndWriteToLog("Não consegui registrar a  mensagem '"+msg+"'")
		raise
		
def closingFileProcedures(fileName, deleteFile):
	global rcvPackages, brkPackages
	if(deleteFile==True):
		printAndWriteToLog("Arquivo '"+fileName+"' fechado e excluído! Execução interrompida antes do recebimento da mensagem de fim de teste")
		os.remove(fileName)
	else:
		printAndWriteToLog("Arquivo '"+fileName+"' foi salvo! "+str(rcvPackages)+" pacotes foram recebidos. Destes, "+str(brkPackages)+" foram vieram corrompidos")
	brkPackages=rcvPackages=0

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
		writeToFile(f, fileName,hoje[7:-1]+" 115200 "+dis+" "+str(SF)+" "+str(TxPower)+" "+str(constants["nPackets"])+" "+constants["validMessage"]+"\n")
		while True:
			usbs = glob.glob('/dev/ttyUSB*')
			usbs.sort()
			if(len(usbs)==0):
				printAndWriteToLog("Nenhum ttyUSB encontrado")
				closingFileProcedures(fileName, True)
				break
			try:
				with serial.Serial(usbs[0], 115200, timeout = None) as ser:
					try:
						x = ser.readline()
						x = x.decode().replace("\n", "").replace("\r", "")
					except:
						printAndWriteToLog("A linha não pôde ser lida "+str(x))
						continue
					if(x.strip()=="END"):
						if(rcvPackages>0):
							closingFileProcedures(fileName, False)
							raiseTxPower()
							keepTesting = True
							break
					else:
						try:
							f.write(str(datetime.now().strftime("%H:%M:%S.%f"))+" "+x+"\n")
							rcvPackages+=1
							if(len(x)>3 and x[:3]=="BRK"):
								brkPackages+=1
						except:
							printAndWriteToLog("Não consegui escrever '"+x+"' no arquivo")
							continue	
			except:
				continue							
printAndWriteToLog("Fim dos testes")
