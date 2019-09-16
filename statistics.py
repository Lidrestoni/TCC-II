import glob
import errno
import os

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
	for i in range(1, len(ptsplit)):
		try:
			lin = ptsplit[i].split(" ")
			pktId = lin[2]
			rssi = rssi+float(lin[5])
			snr = snr+float(lin[8])
			n = n+1
			if(tx<0):
				tx = lin[3].split(")")[0]
		except:
			continue
	rssi = rssi/n
	snr = snr/n
	return rssi, snr, pktId, n, tx, distance

testes = []
path = 'testes/20*'
files = glob.glob(path)
totSnr = 0
totRssi = 0
lastId = 0
nPackets = 0
TxP = 0
dstc = 0
for name in files:
	totSnr = totRssi = 0
	try:
		with open(name) as f:
			plaintext = f.read()
		if(len(plaintext)<1000):
			os.remove(name)
			continue
		a,b,lastId,nPackets, TxP, dstc = makeStatistics(plaintext)
		totRssi = totRssi + a
		totSnr = totSnr + b
	except IOError as erro:
		if erro.errno != errno.EISDIR:
			raise
	testes.append([TxP, dstc, totRssi, totSnr, nPackets, lastId])
	
n = 0
for lt in testes:
	n = n+1
	print("Teste nº "+str(n))
	print("Tx Power: "+str(lt[0]))
	print("Distance: "+str(lt[1])+" cms")
	print("Total RSSI: "+ str(lt[2]))
	print("Total SNR: "+ str(lt[3]))
	print("Number of packets received: "+str(lt[4]) +"/"+str(lt[5])+" ("+str(round(int(lt[4])/int(lt[5])*100, 3))+"%)")
	print("---------------------")
