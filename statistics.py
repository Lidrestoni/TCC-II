import glob
import errno
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from datetime import date

def makeVStatistics(ptsplit, rssi, snr):
	vRssi = vSnr = vRssiCount = vSnrCount = 0
	firstVal = secondVal = 0
	for i in range(1, len(ptsplit)):
		try:
			lin = ptsplit[i].split(" ")
			if(len(lin[1])>2 and lin[1][:3]=="BRK"):
				firstVal = 3
				secondVal = 4
			else:
				firstVal = 1
				secondVal = 2
			vRssi += (float(lin[firstVal])-float(rssi))**2
			vRssiCount += 1
			vSnr += (float(lin[secondVal])-float(snr))**2
			vSnrCount+=1
		except:
			continue
	vRssi = 0 if vRssiCount==0 else vRssi/vRssiCount
	vSnr = 0 if vSnrCount==0 else vSnr/vSnrCount
		
	vRssi = 0 if vRssiCount==0 else math.sqrt(vRssi)/math.sqrt(vRssiCount)
	vSnrD = 0 if vSnrCount==0 else math.sqrt(vSnr)/math.sqrt(vSnrCount)
	
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
	brkPackages=0
	for i in range(1, len(ptsplit)):
		try:
			lin = ptsplit[i].split(" ")
			if(len(lin[1])>2 and lin[1][:3]=="BRK"):
				brkPackages+=1
				n = n+1
				rssi+=float(lin[3])
				snr+=float(lin[4])
				
			else:
				rssi +=float(lin[1])
				snr += float(lin[2])
				n = n+1
		except:
			brkPackages+=1
			continue
	try:
		rssi = rssi/n
		snr = snr/n
	except:
		rssi = -100
		snr = 0
	vRssi, vSnr = makeVStatistics(ptsplit, rssi, snr)
	return rssi, snr, n, nPackets, tx,sf, distance, vRssi, vSnr, brkPackages

testes = []
path = 'testes/20*'
files = glob.glob(path)
files = [x for x in files if date.today().strftime("%Y-%m-%d") not in x]
Snr = 0
vSnr = 0
Rssi = 0
vRssi = 0
recvPackets = 0
brkPackages = 0
nPackets = 0
TxP = 0
dstc = 0
SF = 0
for name in files:
	try:
		with open(name) as f:
			plaintext = f.read()
		Rssi,Snr,recvPackets,nPackets, TxP,SF, dstc, vRssi, vSnr, brkPackages = makeStatistics(plaintext)
	except IOError as erro:
		if erro.errno != errno.EISDIR:
			raise
	testes.append([TxP, dstc, Rssi, Snr, recvPackets, nPackets, vRssi, vSnr, SF, brkPackages])
	
i = n = 0
testes.sort(key= lambda x:(float(x[1]),int(x[8]),int(x[0])))
while i<len(testes)-n:
	if(i+1<len(testes)-n):
		if(testes[i][0]==testes[i+1][0] and testes[i][1]==testes[i+1][1]and testes[i][8]==testes[i+1][8]):
			for u in range(2,4):
				testes[i][u] = (float(testes[i][u])*float(testes[i][5]))/(float(testes[i][5])+float(testes[i+1][5])) + (float(testes[i+1][u])*float(testes[i+1][5]))/(float(testes[i][5])+float(testes[i+1][5]))
				testes[i][u+4] = (float(testes[i][u+4])*float(testes[i][5]))/(float(testes[i][5])+float(testes[i+1][5])) + (float(testes[i+1][u+4])*float(testes[i+1][5]))/(float(testes[i][5])+float(testes[i+1][5]))
				testes[i][u+2] = int(testes[i][u+2]) + int(testes[i+1][u+2])
			testes[i][9] +=testes[i+1][9]
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
with open("../TCC-II-logs/test_output", "w+") as f:
	for lt in testes:
		n = n+1
		if(auxDist!=lt[1]):
			f.write("\n\n\n\n\n\n\n\n-------------------------------------------\n")
			f.write("-------------------------------------------\n")
			f.write("             || Distance: "+str(lt[1])+" cms ||\n")
			f.write("-------------------------------------------\n")
			f.write("-------------------------------------------\n")
			auxDist = lt[1]
			auxSf=-1
			auxTxp=-1
		if(auxSf!=lt[8]):
			f.write("\n\n\n------------------------------\n")
			f.write("     |Spreading Factor "+str(lt[8])+"|\n")
			f.write("------------------------------\n")
			auxSf=lt[8]
		if(auxTxp!=lt[0]):
			f.write("_____________________\n")
			f.write("Tx Power: "+str(lt[0])+"\n")
			f.write("_____________________\n")
			auxTxp=lt[0]
		
		f.write("Teste nº "+str(n)+"\n")
		f.write("Total RSSI: "+ str(lt[2])+"\n")
		f.write("Standard error of RSSI: "+str(float(lt[6]))+"\n")
		f.write("Total SNR: "+ str(lt[3])+"\n")
		f.write("Standard error of SNR: "+str(float(lt[7]))+"\n")
		f.write("Number of packets received: "+str(lt[4]) +"/"+str(lt[5])+" ("+str(round(int(lt[4])/int(lt[5])*100, 3))+"%)\n")
		f.write("Broken packets: "+str(lt[9])+"\n\n")
print("Os testes foram concluídos com sucesso! Estão escritos no arquivo de log test_output")
	
filePath = "../TCC-II-figures/"
files = glob.glob(filePath+"*")
fileN = len(files)

nDistances = set(item[1] for item in testes)
SFColors = ["NULL","NULL","NULL","NULL","NULL","NULL","NULL", 'b', 'g', 'r', 'k', 'm', 'y']

prm = [[2, "Received Signal Strength Indicator", 20, 6],[3, "Signal to Noise Ratio", 8, 7], [9, "Packet Delivery Ratio", 20, -1]]
for x in nDistances:
	for tim in prm:
		plt.clf()
		for xsf in range(7,13):
			eixoX = []
			eixoY = []
			errorBars = []
			fds = []
			for item in testes:
				if(item[1]==str(x) and item[8]==str(xsf)):
					eixoX.append(item[0])
					if(tim[3]!=-1):
						errorBars.append(float(item[tim[3]])/2)
					if(tim[0]==9):
						eixoY.append(100.0-(((int(item[5])-int(item[4]))+(int(item[tim[0]])))/int(item[5]))*100.0)
						plt.gca().yaxis.set_major_formatter(PercentFormatter())
					else:
						eixoY.append(item[tim[0]])
					plt.locator_params(axis='y', nbins=tim[2])
			if(len(eixoX)>0 and len(eixoY)>0):
				plt.plot(eixoX, eixoY, color = SFColors[xsf], label = str(xsf), marker = "x")
				if(tim[3]!=-1):
					plt.errorbar(eixoX, eixoY, color = SFColors[xsf], yerr=errorBars, ls="None", marker = "_", uplims=True, lolims=True)
		plt.ylabel(tim[1], labelpad=5)
		plt.xlabel("Transmission Power")
		plt.title("Distance: "+str(x)+" cms")
		leg = plt.legend(bbox_to_anchor = (1.05, 0.5),bbox_transform = plt.gcf().transFigure,  title = "SF")
		leg.get_frame().set_alpha(0.5)
		plt.savefig(filePath+str(fileN)+".png", bbox_inches="tight")
		fileN+=1
