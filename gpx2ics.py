import sys
import re

from lxml import etree
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

GPX_NAMESPACE = 'http://www.topografix.com/GPX/1/0'
GROUNDSPEAK_NAMESPACE = 'http://www.groundspeak.com/cache/1/0/1'
GPX_NAMESPACES = { 'gpx': GPX_NAMESPACE }

def concatenate(string1, string2):
	return string1 + '\r\n' + string2

def readable_location(location):

	if location.get('city') == 'Lisboa' or location.get('city') == 'Porto':
		if location.get('neighbourhood') != None:
			return location.get('city') + ' (' + location.get('neighbourhood') + ')'
		if location.get('suburb') != None:
			return location.get('city') + ' (' + location.get('suburb') + ')'
		else:
			return location.get('city') + ' (' + location.get('city_district') + ')'
	if location.get('municipality') == 'Lisboa' or location.get('municipality') == 'Porto':
		if location.get('neighbourhood') != None:
			return location.get('municipality') + ' (' + location.get('neighbourhood') + ')'
		if location.get('suburb') != None:
			return location.get('municipality') + ' (' + location.get('suburb') + ')'
		else:
			return location.get('municipality') + ' (' + location.get('city_district') + ')'
	elif location.get('village') != None:
		if location.get('municipality') != None:
			return location.get('village') + ', ' + location.get('municipality')
		else:
			return location.get('village')
	elif location.get('town') != None:
		return location.get('town')
	elif location.get('city') != None:
		return location.get('city')
	else:
		return location.get('municipality')

def generate_calendar(gpx):
	
	now = datetime.strftime(datetime.now(), '%Y%m%dT%H%M%S')

	xml = etree.parse(gpx)
	nominatim = Nominatim(user_agent='Geocaching Eventos em Portugal by FJSFerreira')
	geocoder = RateLimiter(nominatim.geocode, min_delay_seconds=1, return_value_on_exception=None) 
	
	result = 'BEGIN:VCALENDAR'
	result = concatenate(result, 'PRODID:-//Geocaching Eventos em Portugal by FJSFerreira//NONSGML 1.0//EN')
	result = concatenate(result, 'VERSION:2.0')
	
	for wpt in xml.xpath('//gpx:wpt', namespaces = GPX_NAMESPACES):
		
		short_description = wpt.find('.//{' + GROUNDSPEAK_NAMESPACE + '}short_description').text
		short_description_html = etree.fromstring(short_description).text
		splitted_short_description = re.split(', | - ', short_description_html)
		
		date = datetime.strptime(splitted_short_description[0], '%d %B %Y')
		start_time = datetime.strptime(splitted_short_description[1], '%H:%M')
		end_time = datetime.strptime(splitted_short_description[2], '%H:%M')
		
		start_date = datetime.strftime(date, '%Y%m%dT') + datetime.strftime(start_time, '%H%M%S')
		end_date = datetime.strftime(date, '%Y%m%dT') + datetime.strftime(end_time, '%H%M%S')
		
		gc_code = wpt.find('.//{' + GPX_NAMESPACE + '}name').text
		
		latitude = wpt.attrib['lat']
		longitude = wpt.attrib['lon']
		
		location = nominatim.reverse((latitude, longitude))
		
		name = wpt.find('.//{' + GROUNDSPEAK_NAMESPACE + '}name').text
		
		result = concatenate(result, 'BEGIN:VEVENT')
		
		result = concatenate(result, 'DTSTART:' + start_date)
		result = concatenate(result, 'DTEND:' + end_date)
		result = concatenate(result, 'DTSTAMP:' + now)
		result = concatenate(result, 'UID:' + gc_code)
		result = concatenate(result, 'CREATED:' + now)
		result = concatenate(result, 'LAST-MODIFIED:' + now)
		result = concatenate(result, 'DESCRIPTION:https://coord.info/' + gc_code)
		result = concatenate(result, 'LOCATION:' + latitude + '\, ' + longitude)
		result = concatenate(result, 'SUMMARY:' + readable_location(location.raw['address']) + ' - ' + name)
		
		result = concatenate(result, 'END:VEVENT')
	
	result = concatenate(result, 'END:VCALENDAR')
	
	return result

if len(sys.argv) < 2:
	print('Parameter error! Usage: <gpx>', file=sys.stderr)
else:
	gpx = sys.argv[1]
	print(generate_calendar(gpx))
	#generate_calendar(gpx)