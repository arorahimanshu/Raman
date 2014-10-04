from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class TravelReport(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newTravelReportForm':
			return self._newTravelReportForm(requestPath)
		elif nextPart == 'newTravelReportFormAction':
			return self._newTravelReportFormAction(requestPath)
		elif nextPart == 'travelReportVehicleListNested':
			return self._travelReportVehicleListNested(requestPath)
		#

	#



	def _newTravelReportForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'travelReportForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'travelReportForm.js')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'js', 'flexigrid.js')
		)
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'js', 'flexigrid.pack.js')
		)
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'css', 'flexigrid.pack.css')
		)
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'css', 'flexigrid.css')
		)



		self.classData = ['S.No.','Company','Branch','Vehicle Information','Driver Information','Start Location',
					 'Total Running(km)','Total Running Duration','Total Idle Duration','Total Stop Duration',
					 'Total Inactive Duration','Avg Duration','Avg Speed','Max Speed','Times Stopped',
					 'Times Idle','Alert','End Location']

		primaryOrganizationId = None
		with self.server.session() as serverSession :
			primaryOrganizationId = serverSession['primaryOrganizationId']
		dbHelp = self.app.component('dbHelper')
		vehiclesListNested = self._travelReportVehicleListNested(requestPath)
		return  self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('travelReportForm.html', classdata=self.classData, vehicleListNested = json.loads(vehiclesListNested), vehicles = json.dumps(vehiclesListNested)),
			newTabTitle='Travel Report',
			url=requestPath.allPrevious(),
		)
	#


	def _newTravelReportFormValidate(self, formData):
		pass

	#

	def _newTravelReportFormAction(self, requestPath):

		formData = json.loads(cherrypy.request.params['formData'])

		gmtAdjust = formData['gmtAdjust']
		fromDate = formData['fromDate']
		toDate = formData['toDate']

		orgId = formData['company']
		branchId = formData['branch']
		vehicleGroupId = formData['vehicleGroup']

		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		vehiclesListNested = json.loads(self._travelReportVehicleListNested(requestPath))
		vehicleIds = dbHelp.filterVehicles(vehiclesListNested, orgId, branchId, vehicleGroupId)

		vehicleDetails = {}
		for id in vehicleIds:
			vehicleDetails[id] = dbHelp.getVehicleDetails(id)

		timeHelp = self.app.component ('timeHelper')
		time = timeHelp.getDateAndTime(fromDate[0], fromDate[1], fromDate[2], 0, 0, 0)
		fromTime = timeHelp.getDateAndTime_subtract(gmtAdjust, time)

		time = timeHelp.getDateAndTime(toDate[0], toDate[1], toDate[2], 23, 59, 59)
		toTime = timeHelp.getDateAndTime_subtract(gmtAdjust, time)

		gpsHelp = self.app.component ('gpsHelper')
		rows = []
		for id in vehicleIds:
			rawCoordinates = dbHelp.getRawCoordinatesForDeviceBetween(id, fromTime, toTime)
			rawCoordinates = rawCoordinates.order_by(db.gpsDeviceMessage1.timestamp)
			#distance = gpsHelp.getDistance (rawCoordinates.all())
			#data = gpsHelp.getReportData (rawCoordinates.all())
			data = self._dummyFunction(id)
			rows.append(data)
			t = 0

		pageNo = int((cherrypy.request.params).get('pageNo', '1'))
		if 'pageNo' not in cherrypy.request.params:
			self.numOfObj = 10
		if 'rp' in cherrypy.request.params and 'pageNo' in cherrypy.request.params:
			self.numOfObj = int(cherrypy.request.params['rp'])

		rows = dbHelp.getSlicedData(rows,pageNo,self.numOfObj)

		data = {
			'classData' : self.classData,
			'sendData' : rows,
		}

		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')

		#
	#

	def _travelReportVehicleListNested(self, requestPath):
		primaryOrganizationId = None
		with self.server.session() as serverSession :
			primaryOrganizationId = serverSession['primaryOrganizationId']
		dbHelp = self.app.component('dbHelper')
		vehiclesListNested = json.dumps(dbHelp.getVehiclesListNested (primaryOrganizationId))
		return vehiclesListNested
	#

	def _dummyFunction(self, id):
		row = {}
		row['cell'] = [1]
		for i in range(0,17):
			row['cell'].append(id)
		return row