#-*- encoding: utf-8 -*-
import serial
import glob
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
	dis = input()
	f.write(hoje[7:-1]+" 115200 "+dis)
	while True:
		with serial.Serial('/dev/ttyUSB0', 115200) as ser:
			x = ser.readline()
			f.write(str(datetime.now().strftime("%H:%M:%S.%f"))+" "+x)
