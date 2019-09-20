import glob
import errno
import os
import math

def makeVStatistics(ptsplit, rssi, snr, n):
	vRssi = vSnr = 0
	for i in range(1, len(ptsplit)):
		try:
			lin = ptsplit[i].split(" ")
			vRssi = vRssi+ (float(lin[5])-float(rssi))**2
			vSnr = vSnr+ (float(lin[8])-float(snr))**2
		except:
			continue
	return vRssi/int(n), vSnr/int(n)	

def makeStatistics(pt):
	ptsplit = pt.splitlines()
	lin = ptsplit[0].split(" ")
	data = lin[0]
	baud = lin[1]
	distance = lin[2]
	n = 0
	rssi = 0
	snr = 0
	pktId = 0
	tx = -1
	sf = -1
	for i in range(1, len(ptsplit)):
		try:
			lin = ptsplit[i].split(" ")
			pktId = lin[2] if lin[2].isdigit() else pktId
			rssi = rssi+float(lin[5])
			snr = snr+float(lin[8])
			n = n+1
			if(tx<0):
				tx = lin[3].split(")")[0]
			if(sf<0):
				sf = lin[1]
		except:
			continue
	rssi = rssi/n
	snr = snr/n
	vRssi, vSnr = makeVStatistics(ptsplit, rssi, snr, n)
	return rssi, snr, pktId, n, tx,sf, distance, vRssi, vSnr

testes = []
path = 'testes/20*'
files = glob.glob(path)
Snr = 0
vSnr = 0
Rssi = 0
vRssi = 0
lastId = 0
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
		Rssi,Snr,lastId,nPackets, TxP,SF, dstc, vRssi, vSnr = makeStatistics(plaintext)
	except IOError as erro:
		if erro.errno != errno.EISDIR:
			raise
	testes.append([TxP, dstc, Rssi, Snr, nPackets, lastId, vRssi, vSnr, SF])
	
i = n = 0
testes.sort(key= lambda x:(int(x[8]),int(x[0]),float(x[1])), reverse=True)
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
for lt in testes:
	n = n+1
	print("Teste nº "+str(n))
	print("Spreading Factor "+str(lt[8]))
	print("Tx Power: "+str(lt[0]))
	print("Distance: "+str(lt[1])+" cms")
	print("Total RSSI: "+ str(lt[2]))
	print("Standard deviation of RSSI: "+str(math.sqrt(float(lt[6]))))
	print("Total SNR: "+ str(lt[3]))
	print("Standard deviation of SNR: "+str(math.sqrt(float(lt[7]))))
	print("Number of packets received: "+str(lt[4]) +"/"+str(lt[5])+" ("+str(round(int(lt[4])/int(lt[5])*100, 3))+"%)")
	print("---------------------")
