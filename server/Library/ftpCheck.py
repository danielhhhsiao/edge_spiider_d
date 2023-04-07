import ftplib
import io
import sys

def ftpCheckStatus(ip, proxy, user, passwd):
	print('Hostname: '+ip)
	print('Proxy: '+proxy)
	print('user: '+user)
	print('password: '+passwd)
	print('')
	print('=====Test Result=====')
	fileName = "testFile"
	try:
		ftp = ftplib.FTP(ip, user, passwd, timeout=3)
		print("FTP connect success.")
		ftp.encoding = "utf-8"
	except:
		print("FTP connect failed.")
		return 1
	try:
		try:
			ftp.cwd("/createTest")
		except:
			ftp.mkd("/createTest")
		print("Create dir success.")
	except:
		print("Dir create failed.")
		return 2
	try:
		ftp.rmd("/createTest")
		print("Delete dir success.")
	except:
		print("Dir delete failed.")
		return 3
	try:
		x = "Test String"
		bio = io.BytesIO(bytes(x,encoding='utf8'))
		ftp.storbinary("STOR /" + fileName, bio)
		print("File create success.")
	except:
		print("File create failed.")
		return 4
	try:
		ftp.delete(fileName)
		print("File delete success.")
	except:
		print("File delete failed.")
		return 5
	return 0

if __name__=="__main__":
	ip=str(sys.argv[1])
	user=str(sys.argv[2])
	pwd=str(sys.argv[3])
	
	
	ftpCheckStatus(ip,'1',user,pwd)
