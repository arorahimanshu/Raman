from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json
import time
from datetime import datetime, timedelta

class GpsData(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newGpsDataForm':
			return self._newGpsDataForm(requestPath)
		elif nextPart == 'newGpsDataFormAction':
			return self._newGpsDataFormAction(requestPath)
		elif nextPart == 'newCarSetup':
			return self._newCarSetup(requestPath)
		elif nextPart == 'newVehicleList':
			return self._newVehicleList(requestPath)
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
		self.gmtAdjust = 19800
		fromTime = self.getDateAndTime_add ()
		fromTime = self.getDateAndTime_subtract (datetime (fromTime.year, fromTime.month, fromTime.day, 0, 0, 0))
		toTime = self.getGMTDateAndTime()
		data = db.returnCoordinatesForVehiclesBetween(self.carToTracked, fromTime, toTime)
		#data = db.returnLiveCarsData ()
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

		vehiclesList = self._newVehicleList(requestPath)
		vehiclesList = json.loads(vehiclesList)
		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('gpsDataForm.html', vehiclesList = vehiclesList),
			newTabTitle='Track My Vehicle',
			url=requestPath.allPrevious(),
		)

	#


	def _newGpsDataFormValidate(self, formData):
		pass

	#
	def _newCarSetup(self, requestPath):
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
		data = db.returnLiveCarDataForVehicles(self.carToTracked,self.getDateAndTime_add())
		return self.jsonSuccess(data)

		#
	#

	def _newVehicleList(self, requestPath):
		vehiclesList = []
		db = self.app.component('dbHelper')
		orgId = '123'
		branchList = db.returnBranchListForOrg(orgId)

		for branch in branchList:
			vehicleGroupList = db.returnVehicleGroupListForBranch(branch['value'])
			groups = []
			for vehicleGroup in vehicleGroupList:
				vehicleList = db.returnVehicleListForVehicleGroup(vehicleGroup['value'])
				group = {'vehicleGroupDetails':{'vehicleGroupName':vehicleGroup['display'], 'vehicleGroupId':vehicleGroup['value']}, 'vehicles':vehicleList}
				groups.append (group)
			branch = {'branchDetails':{'branchName':branch['display'], 'branchId':branch['value']}, 'vehicleGroups':groups}
			vehiclesList.append(branch)
		vehiclesList = json.dumps(vehiclesList)
		return vehiclesList
	#

	def _newGpsDataFormLastRecord(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		remainingVehicles = formData['remainingVehicles']
		db = self.app.component('dbHelper')
		records = []
		for deviceId in remainingVehicles:
			obj = db.getLastRecordForVehicle(deviceId)
			records.append({"position": {"latitude": str(obj.Latitude), "longitude": str(obj.Longitude)},
								"speed": int(obj.speed),
								"orientation": obj.orientation,
					            "timestamp": str(obj.timestamp), "vehicleId": int(obj.deviceId)})
		return records
	#

	def getDateAndTime_add(self, gt=None):
		if gt == None:
			#gmtime = time.gmtime()
			gt = self.getGMTDateAndTime()
		newTime = gt + timedelta(seconds=self.gmtAdjust)
		return newTime
	#

	def getDateAndTime_subtract(self, gt=None):
		if gt == None:
			#gmtime = time.gmtime()
			gt = self.getGMTDateAndTime()
		newTime = gt - timedelta(seconds=self.gmtAdjust)
		return newTime
	#

	def getGMTDateAndTime(self):
		gmtime = time.gmtime()
		gt = datetime(gmtime.tm_year, gmtime.tm_mon, gmtime.tm_mday, gmtime.tm_hour, gmtime.tm_min, gmtime.tm_sec)
		return gt