###########################################################################
#                                                                         #
#             MetroPY ("Weather" you like this script or not)             #
#                                                                         #
#                                                                         #
#  Copyright (c) 2022, Zackery .R. Smith <zackery.smith@hsdgreenbush.org>.#
#                                                                         #
#  This program is free software: you can redistribute it and/or modify   #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation, either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful,        #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#  GNU General Public License for more details.                           #
#                                                                         #
#  You should have received a copy of the GNU General Public License      #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.   #
#                                                                         #
###########################################################################
####     Huge thanks to mrHeavenli for updated webscraping method!     ####
###########################################################################

from requests import get
from bs4 import BeautifulSoup
from re import sub, match, search, compile
from typing import Optional
from datetime import datetime
from time import sleep

regexes = {
	"tempature" : r"tempValue.*(?P<tempature>\b([0-9]|[1-9][0-9]|1[0-9]{2}|200)°)",
	"windspeed" : r"(?P<windspeed>([0-9]|[1-9][0-9]|100).mph)",
	"humidity" : r"PercentageValue.*(?P<humidity>\d([0-9]|[1-9][0-9]|100)%)",
	"realfeel" : r"feelsLikeTempValue.*(?P<realfeel>\d([0-9]|[1-9][0-9]|1[0-9]{2}|200)°)",
	"weatherob" : r"CurrentConditions--phraseValue--.+?>(?P<weatherob>.+?(?=<))"
}


def log_check():
	with open("Weather Observation.csv") as logfile:
		contents = [x.strip("\n").split(",") for x in logfile.readlines()]
		try:
			userinput = int(input())
			if userinput == 0:
				for entry in contents:
					print(", ".join(entry))
			elif userinput - 1 <= len(contents):
				for i in range(0, len(contents)):
					print(contents[i][userinput - 1])
		except (ValueError, IndexError):
			return


def parse_site(weathersoup: BeautifulSoup) -> list:
	weatherdata = datetime.now().strftime("%m/%d/%Y %H:%M").split(" ") + [""] * 7

	span_string = "".join([str(span) for span in weathersoup.find_all("span")])
	data = [search(regex, span_string) for regex in regexes.values()]

	# Weather Observation
	weatherdata[2] = search(
		r"CurrentConditions--phraseValue--.+?>(?P<weatherob>.+?(?=<))", 
		"".join([str(div) for div in weathersoup.find_all("div")])
	).group("weatherob")
	# Temperature, Windspeed, Humidity, and Realfeel
	for i in range(3, 6+1): 
		weatherdata[i] = data[i-3].group(list(regexes.keys())[i-3])

		# Sunset & Sunrise
		matches = [
			sub(r"[apm\s]", "", i.text)
			for i in weathersoup.find_all("p")
			if match(".*SunriseSunset--dateValue.*", str(i))
		]
		weatherdata[7], weatherdata[8] = matches[0], matches[1]
	
	return weatherdata


def get_zipcode() -> str:
	while True:
		if compile(r"^\d{5}$").search(zipcode := input("What is your zip code?\n: ").strip()) is None:
			print("Hmm.. I don't recognize that as a proper zipcode (example zipcode: 75115)")
			continue
		return zipcode
	

def main(zipcode: Optional[str] = None) -> str:
	# "Basic" Zipcode Check
	if zipcode is None:
		zipcode = get_zipcode()

	# req will request the websites source
	req = get("https://weather.com/weather/today/l/" + zipcode + ":4:US")

	# Check if any errors occurred
	try: 
		req.raise_for_status()
	except Exception as exc: 
		print("There was a problem: " + exc)
		return zipcode

	weathersoup = BeautifulSoup(req.text, features="html.parser")
	weatherdata = parse_site(weathersoup)

	with open("Weather Observation.csv", "a") as log_file: 
		log_file.write(",".join(weatherdata) + "\n")
	
	print("Successfully Collected Data From " + zipcode)
	
	return zipcode


# Menu loop
while True:
	choice = input("\n1:   Check Logs\n2:   Get Data\n: ")
	if choice == "1":
		log_check()
	elif choice == "2":
		zipcode = main()
		if input("Would you like to loop this process? [y, N]").lower() == "y":
			print("Ok, press ctrl+c to cancel")
			while True:
				try:
					main(str(zipcode))
					sleep(60 * 10)
				except:
					sleep(60 * 5)
