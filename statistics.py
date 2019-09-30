import glob
import errno
import os
import math

def makeVStatistics(ptsplit, rssi, snr, n):
	vRssi = vSnr = 0
	for i in range(1, len(ptsplit)):
		try:
			lin = ptsplit[i].split(" ")
			vRssi = vRssi+ (float(lin[2])-float(rssi))**2
			vSnr = vSnr+ (float(lin[4])-float(snr))**2
		except:
			continue
	try:
		vRssi/=int(n)
		vSnr/=int(n)
	except:
		vRssi=vSnr=0
	return vRssi, vSnr	

def makeStatistics(pt):
	ptsplit = pt.splitlines()
	lin = ptsplit[0].split(" ")
	data = lin[0]
	baud = lin[1]
	distance = lin[2]
	sf = lin[3]
	tx = lin[4]
	nPackets = lin[5]
	n = 0
	rssi = 0
	snr = 0
	for i in range(1, len(ptsplit)):
		try:
			lin = ptsplit[i].split(" ")
			rssi = rssi+float(lin[2])
			snr = snr+float(lin[4])
			n = n+1
		except:
			continue
	try:
		rssi = rssi/n
		snr = snr/n
	except:
		rssi = snr = 0
	vRssi, vSnr = makeVStatistics(ptsplit, rssi, snr, n)
	return rssi, snr, n, nPackets, tx,sf, distance, vRssi, vSnr

testes = []
path = 'testes/20*'
files = glob.glob(path)
Snr = 0
vSnr = 0
Rssi = 0
vRssi = 0
recvPackets = 0
nPackets = 0
TxP = 0
dstc = 0
SF = 0
for name in files:
	try:
		with open(name) as f:
			plaintext = f.read()
		if(len(plaintext)<1000):
			os.remove(name)
			continue
		Rssi,Snr,recvPackets,nPackets, TxP,SF, dstc, vRssi, vSnr = makeStatistics(plaintext)
	except IOError as erro:
		if erro.errno != errno.EISDIR:
			raise
	testes.append([TxP, dstc, Rssi, Snr, recvPackets, nPackets, vRssi, vSnr, SF])
	
i = n = 0
testes.sort(key= lambda x:(float(x[1]),int(x[8]),int(x[0])), reverse=True)
while i<len(testes)-n:
	if(i+1<len(testes)-n):
		if(testes[i][0]==testes[i+1][0] and testes[i][1]==testes[i+1][1]and testes[i][8]==testes[i+1][8]):
			for u in range(2,4):
				testes[i][u] = (float(testes[i][u])*float(testes[i][5]))/(float(testes[i][5])+float(testes[i+1][5])) + (float(testes[i+1][u])*float(testes[i+1][5]))/(float(testes[i][5])+float(testes[i+1][5]))
				testes[i][u+4] = (float(testes[i][u+4])*float(testes[i][5]))/(float(testes[i][5])+float(testes[i+1][5])) + (float(testes[i+1][u+4])*float(testes[i+1][5]))/(float(testes[i][5])+float(testes[i+1][5]))
				testes[i][u+2] = int(testes[i][u+2]) + int(testes[i+1][u+2])
			testes.pop(i+1)
			n = n+1
		else:
			i = i+1
	else:
		i = i+1
n=0
auxDist = -1.0
auxSf = -1
auxTxp = -1
for lt in testes:
	n = n+1
	if(auxDist!=lt[1]):
		print("\n\n\n\n\n\n\n\n-------------------------------------------")
		print("-------------------------------------------")
		print("             || Distance: "+str(lt[1])+" cms ||")
		print("-------------------------------------------")
		print("-------------------------------------------")
		auxDist = lt[1]
		auxSf=-1
		auxTxp=-1
	if(auxSf!=lt[8]):
		print("\n\n\n------------------------------")
		print("     |Spreading Factor "+str(lt[8])+"|")
		print("------------------------------")
		auxSf=lt[8]
	if(auxTxp!=lt[0]):
		print("_____________________")
		print("Tx Power: "+str(lt[0]))
		print("_____________________")
		auxTxp=lt[0]
		
	print("Teste nº "+str(n))
	print("Total RSSI: "+ str(lt[2]))
	print("Standard deviation of RSSI: "+str(math.sqrt(float(lt[6]))))
	print("Total SNR: "+ str(lt[3]))
	print("Standard deviation of SNR: "+str(math.sqrt(float(lt[7]))))
	print("Number of packets received: "+str(lt[4]) +"/"+str(lt[5])+" ("+str(round(int(lt[4])/int(lt[5])*100, 3))+"%)\n")
	
