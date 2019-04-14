#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse
import mechanize
import csv
import urllib
import urllib.robotparser as urobot
from fake_useragent import UserAgent

class CarrerasScraper():

	def __init__(self):
		self.url = "http://www.corriendovoy.com/calendario-carreras"
		self.data = {'Calendario' : {'from_date' : '01/01/2019', 'from_distance' : '0', 'to_distance' : '200'} }
		
	def __get_running_info(self, ul, div_extra):
		# Get <li> childs for general info
		lis = ul.findChildren('li')
		running = {}
		for li in lis:
			if 'cal-date' in li['class']:
				running['Fecha'] = datetime.strptime(li.string, '%d.%m.%Y') # Parse Date
			elif 'cal-name' in li['class']:
				running['Carrera'] = li.string
			elif 'cal-city' in li['class']:
				m = re.match(r"(?P<Ciudad>.+?(?= \()) \((?P<Provincia>.+?(?=\)))\)", li.string)
				running['Ciudad'] = m.group('Ciudad')
				running['Provincia'] = m.group('Provincia')
			elif 'cal-type' in li['class']:
				running['Tipo'] = li.string
			elif 'cal-distance' in li['class']:
				running['Distancia'] = li.string
		
		# Get Extra info
		running['Web'] = div_extra.findChild('a')['href']
		txt_cat_infantil = div_extra.findAll(text=re.compile("infantiles\?:"))[0]
		if txt_cat_infantil.split("infantiles?: ")[1] == "No":
			running['Infantil'] = True
		else:
			running['Infantil'] = False
		
		return running
		
	def __get_runnings_on_page(self, html):
		bs = BeautifulSoup(html, 'html.parser')
		uls = bs.findAll('ul', {'class' : 'calendar-element'})[1:]
		divs_extra = bs.findAll('div', {'class' : 'calendar-element-hide'})
		runnings = []

		for idx,ul in enumerate(uls):
			running = self.__get_running_info(ul, divs_extra[idx])
			runnings.append(running)

		return runnings
	
	# Scrape function
	def scrape(self):
		print("Web Scraping of running events in spain from '" + self.url + "'...")

		print("This process could take 1 or 2 minutes.\n")

		# Start timer
		start_time = time.time()

		# Get robots.txt to check if scraping is permitted
		url = "http://www.corriendovoy.com"
		rp = urobot.RobotFileParser()
		rp.set_url(url + "/robots.txt")
		rp.read()
		# Check the content of robots.txt
		if rp.can_fetch("*", url):
			site = urllib.request.urlopen(url)
			sauce = site.read()
			soup = BeautifulSoup(sauce, "html.parser")
			actual_url = site.geturl()[:site.geturl().rfind('/')]
			
			my_list = soup.find_all("calendario-carreras", href=True)
			for i in my_list:
				# rather than != "#" you can control your list before loop over it
				if i != "#":
					newurl = str(actual_url+"/")
					try:
						if rp.can_fetch("*", newurl):
							site = urllib.request.urlopen(newurl)
							# do what you want on each authorized webpage
					except:
						pass
		else:
			print("Scraping is not allowed")
		
		# Browse with mechanize
		br = mechanize.Browser()
		# Change default user agent. Use fake-useragent to generate random user agents.
		br.addheaders = [('User-Agent', ua.random), ('Accept', '*/*')]
		br.open(self.url)

		# Select search form
		br.form = list(br.forms())[2]
		
		# Fill form fields		
		fdate_ctrl = br.form.find_control('Calendario[from_date]')
		fdate_ctrl.value = '01/01/2019'
		fdistance_ctrl = br.form.find_control('Calendario[from_distance]')
		fdistance_ctrl.readonly = False
		fdistance_ctrl.value = '0'
		tdistance_ctrl = br.form.find_control('Calendario[to_distance]')
		tdistance_ctrl.readonly = False
		tdistance_ctrl.value = '200'
		
		# Get response response from browser
		response = br.submit()
		
		# Initialize runnings result list
		all_runnings = []
		
		# Initialize loop control variable
		end_scrapping = False
			
		# Page reading loop
		while not end_scrapping:
			
			# Parse page and scrap data
			# Read Page and get runnings
			runnings_on_page = self.__get_runnings_on_page(response.read())
			
			# Add to results
			all_runnings.extend(runnings_on_page)
			
			# Continue reading pages checking
			for link in br.links():
				if link.text == '»':
					next_url = link.url
					next_lnk = link
				elif link.text == "Última »":
					last_url = link.url			
			
			if (next_url == last_url):
				# end scrapping
				end_scrapping = True
			else:
				# Get next page
				response = br.follow_link(next_lnk)


		# Export to csv
		fieldnames = ['Fecha','Carrera','Ciudad','Provincia','Tipo','Distancia','Web','Infantil']
		self.export_to_csv('runnings.csv', all_runnings, fieldnames)
		
		# Show elapsed time
		end_time = time.time()
		print("\nelapsed time: " + str(round(((end_time - start_time) / 60) , 2)) + " minutes")

	def export_to_csv(self, filename, data, fieldnames):
		# Overwrite to the specified file.
		# Create it if it does not exist.
		with open(filename, 'w', encoding='utf-8-sig', newline='') as csvfile:
			#fieldnames = ['first_name', 'last_name']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		
			writer.writeheader()
			print (data)
			for row in data:
				print (row, '\n')
				writer.writerow(row)
				
