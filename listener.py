#-*- encoding: utf-8 -*-
import serial
import glob
import os
from datetime import date
from datetime import datetime

hoje = "testes/"+date.today().strftime("%Y-%m-%d_")
files = glob.glob(hoje+"*")
files.sort()
n="0"
if files:
	n=files[len(files)-1][len(hoje):]
fileName = hoje+str(int(n)+1)

with open(fileName, "w") as f:
	print("O arquivo '"+fileName+"' foi criado com sucesso! Gravando resultados ...")
	print("Qual a distância (em centímetros) entre os dispositivos? ", end = " ")
	try:
		dis = input()
		f.write(hoje[7:-1]+" 115200 "+dis+"\n")
		while True:
			with serial.Serial('/dev/ttyUSB0', 115200, timeout = None) as ser:
				x = ser.readline()
				try:
					f.write(str(datetime.now().strftime("%H:%M:%S.%f"))+" "+x.decode().replace("\n", "").replace("\r", "")+"\n")
				except:
					continue
	except:
		print("\nArquivo '"+fileName+"' salvo com sucesso!")
		raise
