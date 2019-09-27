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
	constants[str(b[2])] = (int if b[2]=="int" else str)(b[4][:-2])

SF = constants["initSf"]
TxPower = constants["initTxPower"]
hoje = "testes/"+date.today().strftime("%Y-%m-%d_")

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
		print("O arquivo '"+fileName+"' foi criado com sucesso! Gravando resultados ...")
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
					if(x[0]=='E' and x[1]=='N'):
						if(x[2]=='D'):
							if(voidMessage==False):
								aux = x[3]
								if(len(x)>4):
									aux+=x[4]
								TxPower = int(aux)
								print("\nArquivo '"+fileName+"' foi salvo com sucesso!\nAguardando novo teste...")
								testEnd = True
								f.close()
								break
						elif(x[2]=='S'):
							aux = x[3]
							if(len(x)>4):
								aux+=x[4]
							SF = int(aux)
					else:
						voidMessage = False
						try:
							f.write(str(datetime.now().strftime("%H:%M:%S.%f"))+" "+x+"\n")
						except:
							continue
		except:
			if(voidMessage==True):
				os.remove(fileName)
				print("Erro inesperado! O arquivo "+fileName+" foi excluído!")
			else:
				print("\nArquivo '"+fileName+"' foi salvo com sucesso!\n Fim dos Testes!")
			raise

