import glob
import errno

def makeStatistics(pt):
	ptsplit = pt.split()
	data = ptsplit[0]
	baud = ptsplit[1]
	n = 0
	rssi = 0
	snr = 0
	for i in range(3, len(ptsplit))[::11]:
		#ptsplit[i+3].split(')')[0] /id do pacote
		rssi = rssi+float(ptsplit[i+5])
		snr = snr+float(ptsplit[i+10])
		n = n+1
	rssi = rssi/n
	snr = snr/n
	return rssi, snr

path = '20*'
files = glob.glob(path)
totSnr = 0
totRssi = 0
for name in files:
	try:
		with open(name) as f:
			plaintext = f.read()
		a,b = makeStatistics(plaintext)
		totRssi = totRssi + a
		totSnr = totSnr + b
	except IOError as erro:
		if erro.errno != errno.EISDIR:
			raise
print("Total SNR: "+ str(totSnr))
print("Total RSSI: "+ str(totRssi))
