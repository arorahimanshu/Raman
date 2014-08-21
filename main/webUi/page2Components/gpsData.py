from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json
import time


class GpsData(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newGpsDataForm':
			return self._newGpsDataForm(requestPath)
		elif nextPart == 'newGpsDataFormAction':
			return self._newGpsDataFormAction(requestPath)
		elif nextPart == 'newGpsDataCarSetup':
			return self._newGpsDataCarSetup(requestPath)
		elif nextPart == 'newDashboardForm':
			return self._newDashboardForm(requestPath)
		elif nextPart == 'newDashboardFormAction':
			return self._newDashboardFormAction(requestPath)

		#

	#


	def _newDashboardForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'dashboardForm.css')
		)
		params['externalJs'].append('http://maps.googleapis.com/maps/api/js?libraries=geometry&sensor=false')
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'dashboardForm.js')
		)

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('dashboardForm.html'),
			newTabTitle='Dashboard',
			url=requestPath.allPrevious(),
		)

	#


	def _newDashboardFormValidate(self, formData):
		pass

	#

	def _newDashboardFormAction(self, requestPath):

		#formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbHelper')
		#data = db.returnCarsDataByDates(formData['fromDate'],formData['toDate'])
		data = db.returnLiveCarsData()
		#errors = self._newDashboardFormValidate(formData)
		#if errors:
		#	return self.jsonFailure('validation failed', errors=errors)
		#
		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')
		#
	#


	def _newGpsDataForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalJs'].append('http://maps.googleapis.com/maps/api/js?libraries=geometry&sensor=false')

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'gpsDataForm.css')
		)
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'gpsDataForm.js')
		)
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'basic.js')
		)

		vehicleGroup = [{
		                'value': 'VehicleGroup1',
		                'display': [{'vid': 1, 'name': 'Alfa Romeo'}, {'vid': 2, 'name': 'Ferrari'},
		                            {'vid': 3, 'name': 'Veyron'}]},
		                {
		                'value': 'VehicleGroup2',
		                'display': [{'vid': 33, 'name': 'Alfa Romeo'}, {'vid': 24, 'name': 'Ferrari'},
		                            {'vid': 34, 'name': 'Veyron'}]},
		]
		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('gpsDataForm.html', vehicleGroup=vehicleGroup),
			newTabTitle='Track My Vehicle',
			url=requestPath.allPrevious(),
		)

	#


	def _newGpsDataFormValidate(self, formData):
		pass

	#
	def _newGpsDataCarSetup(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		self.carToTracked = formData['carToTracked']
		self.gmtAdjust = formData['gmt']

	def getTime(self):
		gmtime = time.gmtime()
		self.time = gmtime.tm_hour * 3600 + gmtime.tm_min * 60 + gmtime.tm_sec + self.gmtAdjust
		if self.time // 3600 > 24:
			self.hour = (self.time // 3600) - 24
		else:
			self.hour = self.time // 3600
		self.hour = str(self.hour)
		self.min = str((self.time % 3600) // 60)
		self.sec = str((self.time % 3600) % 60)
		if len(self.hour) == 1:
			self.hour = "0" + self.hour
		if len(self.min) == 1:
			self.min = "0" + self.min
		if len(self.sec) == 1:
			self.sec = "0" + self.sec
		return self.hour + self.min + self.sec
	#

	def _newGpsDataFormAction(self, requestPath):

		db = self.app.component('dbHelper')
		data = db.returnLiveCarData(self.carToTracked,self.getDateAndTime())
		print(data)
		return self.jsonSuccess(data)

		#
	#

	def getDateAndTime(self):
		gmtime = time.gmtime()
		newTime = {}
		seconds = gmtime.tm_hour * 3600 + gmtime.tm_min * 60 + gmtime.tm_sec + self.gmtAdjust
		if seconds // 3600 > 24:
			newTime['hour'] = (seconds // 3600) - 24
			gmtime.tm_mday += 1
			if gmtime.tm_mday == 32:
				gmtime.tm_mday = 1
				gmtime.tm_mon += 1
			elif gmtime.tm_mday == 31:
				month = gmtime.tm_mon
				if (month == 4 or
					month == 6 or
					month == 9 or
					month == 11):
					gmtime.tm_mday = 1
					gmtime.tm_mon += 1
			elif gmtime.tm_mon == 2:
				if ((gmtime.tm_mday == 30 and gmtime.tm_year % 400 == 0) or
					(gmtime.tm_mday == 29 and gmtime.tm_year % 100 == 0) or
					(gmtime.tm_mday == 30 and gmtime.tm_year % 4 == 0)):
					gmtime.tm_mon += 1
					gmtime.tm_mday = 1
			if gmtime.tm_mon == 13:
				gmtime.tm_mon = 1
				gmtime.tm_year += 1
		else:
			newTime['hour'] = seconds // 3600
		newTime['hour'] = str(newTime['hour'])
		newTime['min'] = str((seconds % 3600) // 60)
		newTime['sec'] = str((seconds % 3600) % 60)
		if len(newTime['hour']) == 1:
			newTime['hour'] = "0" + newTime['hour']
		if len(newTime['min']) == 1:
			newTime['min'] = "0" + newTime['min']
		if len(newTime['sec']) == 1:
			newTime['sec'] = "0" + newTime['sec']

		newTime['day'] = str(gmtime.tm_mday)
		newTime['mon'] = str(gmtime.tm_mon)
		newTime['year'] = str(gmtime.tm_year)
		if len(newTime['day']) == 1:
			newTime['day'] = "0" + newTime['day']
		if len(newTime['mon']) == 1:
			newTime['mon'] = "0" + newTime['mon']
		return newTime
	#