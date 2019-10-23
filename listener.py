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
	if(all((it in b[4]) for it in ['{','}'])):
		nm = str(b[2]).split("[")[0]
		constants[nm] = []
		for l in b[4][1:-3].split(","):
			constants[nm].append((int if b[1]=="int" else str)(l))
	else:
		constants[str(b[2])] = ((int)(b[4][:-2])) if b[1]=="int" else ((str)(b[4][1:-3]))
SF = constants["initSf"]
TxPower = constants["initTxPower"]
hoje = "testes/"+date.today().strftime("%Y-%m-%d_")
brkPackages= 0
rcvPackages = 0

class ValidMessage:
	__validMessageCounter=0
	__validMessage = ""  
	def __makeValidMessageOfSize(self, siz):
		if(siz==len(constants["originalMessage"])):
			self.__validMessage = constants["originalMessage"]
		elif(siz<len(constants["originalMessage"])):
			self.__validMessage = constants["originalMessage"][:siz]
		else:
			self.__validMessage = "";
		while(siz>len(constants["originalMessage"])):
			self.__validMessage+=constants["originalMessage"]
			siz-=len(constants["originalMessage"])
			self.__validMessage+=constants["originalMessage"][:siz]
     
	def __init__(self):
		self.__validMessageCounter=0
		if(constants["validMessageArraySize"]>0):
			self.__makeValidMessageOfSize(constants["validMessageArray"][0])
	def ret(self):
		return self.__validMessage
	def len(self):
		return len(self.__validMessage)  
	def charat(self, pos):
		return self.__validMessage[pos]  
	def next(self):
		self.__validMessageCounter+=1
		if(self.__validMessageCounter<constants["validMessageArraySize"]):
			self.__makeValidMessageOfSize(constants["validMessageArray"][self.__validMessageCounter])
		else:
			self.__makeValidMessageOfSize(constants["validMessageArray"][constants["validMessageArraySize"]-1]+self.__validMessageCounter-constants["validMessageArraySize"]+1)
	def matches(msg2):
		return self.__validMessage==msg2  
validMessage = ValidMessage() 


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
			validMessage.next()
	
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
		printAndWriteToLog("SF: "+str(SF)+", TxPower: "+str(TxPower)+", Expecting message: \""+validMessage.ret()+"\"")
		writeToFile(f, fileName,hoje[7:-1]+" 115200 "+dis+" "+str(SF)+" "+str(TxPower)+" "+str(constants["nPackets"])+" "+validMessage.ret()+"\n")
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
						brkPackages+=1
						x = str(x).replace("\n", "").replace("\r", "")
						if(x[:2]=="b'"):
							x = x[2:-1]
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
