from subprocess import Popen, PIPE
import json
import codecs

def wifiSearch():
	process = Popen(['iwgetid', '-r'], stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	stdout,_ = codecs.escape_decode(stdout, 'hex')
	now = str(stdout,"utf-8").replace("\u0000","").replace("\n","")
	
	process = Popen(['wpa_cli', '-i', 'wlan0', 'scan'], stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	process = Popen(['wpa_cli', '-i', 'wlan0', 'scan_result'], stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	stdout,_ = codecs.escape_decode(stdout, 'hex')
	ret = []
	data = str(stdout,"utf-8").replace("\u0000","").split("\n")
	
	for i in range(1,len(data)):
		sub = data[i].split("\t")
		if len(sub)<5:
			continue
		if sub[4]=="":
			continue
			
		d = dict()
		d["level"]=max(min(int(sub[2])+120,100),0)
		d["ssid"]=sub[4]
		
		if now == d["ssid"]:
			d["connected"]=1
		else:
			d["connected"]=0
		if sub[3].find("WPA2-PSK")==-1 and sub[3].find("WPA-PSK")==-1: #not password
			d["type"]=0
		else:
			d["type"]=1
			
		ret.append(d)
		
	ret = sorted(ret,key =lambda k:k["level"])
	ret = ret[::-1]
		
	repeatCheck = []
	newRet = []
	for r in ret:
		if r["ssid"] not in repeatCheck:
			repeatCheck.append(r["ssid"])
			newRet.append(r)
		
	return newRet
	
def run():
	data = wifiSearch()
	ret = dict()
	ret["wifi"] = data
	return json.dumps(ret, separators=(',', ':'))
	
if __name__ == "__main__":
	print(run())
	
