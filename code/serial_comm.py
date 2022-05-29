import serial
import time
import requests


def main():
	print("Running. Press CTRL-C to exit.")
	with serial.Serial("/dev/ttyUSB0", 9600, timeout=1) as arduino:
		time.sleep(0.1)
		if arduino.isOpen():
			print("{} connected!".format(arduino.port))
			try:
				while True:
					while arduino.inWaiting() > 0: 
						answer=arduino.readline()
						k = str(answer.decode()).replace("\n", "").replace("\r","")
						if len(k) > 4:
							try:
								dic = conversion(k)
							except Exception as e:
								continue
							else:
								r = requests.post("http://127.0.0.1:1815/api/data", json={
									"temperature" : dic["temp"],
									"humidity" : dic["humidity"],
									"wind" : dic["windspeedmph"] / 2.237 ,
									"luminosity": dic["luminosity"]
								})
								print("Data sent")
								print("Status Code:" + str(r.status_code))

						
			except KeyboardInterrupt:
				print("Exit...")
				
def conversion(s):
	""" string de la forme "##nom1=valeur1,nom2=valeur2,nom3=valeur3,etc...##"
	les noms ne doivent pas contenir de nombres, points ou # """
	for i in [0,1,-1,-2]:
		if s[i] != "#":
			raise ValueError
		dico = {}
		nom = ""
		valeur = ""
		for i in range(2,len(s)-2):
			if s[i] == '=':
				True
			elif s[i] == ",":
				dico[nom] = float(valeur)
				nom = "" ; valeur = ""
			elif s[i] in ['0','1','2','3','4','5','6','7','8','9','.']:
				valeur += s[i]
			else : nom += s[i]
	dico[nom] = float(valeur)
	return dico

def test():
	assert conversion("Il faut beau aujourd'hui") == ValueError
	assert conversion("##luminosity=485.00,light_lvl=2.09,temp=28.97,humidity=56.77,windspeedmph=0.0,batt_lvl=6.52") == ValueError
	assert conversion("#luminosity=485.00,light_lvl=2.09,temp=28.97,humidity=56.77,windspeedmph=0.0,batt_lvl=6.52##") == ValueError
	assert conversion("##luminosity=485.00,light_lvl=2.09,temp=28.97,humidity=56.77,windspeedmph=0.0,batt_lvl=6.52##") == {'luminosity': '485.00', 'light_lvl': '2.09', 'temp': '28.97', 'humidity': '56.77', 'windspeedmph': '0.0', 'batt_lvl' : '6.52'}
	print("ok")

main()
