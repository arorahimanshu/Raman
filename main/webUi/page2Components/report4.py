from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Report4(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)
	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newReport4Form':
			return self._newReport4Form(requestPath)
		elif nextPart == 'newReport4FormAction':
			return self._newReport4FormAction(requestPath)
		#
	#

	def _newReport4Form(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'report4Form.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'report4Form.js')
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

		self.classData = ['S.No.', 'Vehicle ID', 'Vehicle Name', 'Reg No', 'Vehicle Model', 'Running Duration', 'Distance Travelled', 'Stop Duration',
						  'No of Stops', 'Avg Speed']

		# Vehicle selector Block Starts
		vehicleStructure = []
		dataUtils = self.app.component('dataUtils')
		with self.server.session() as serverSession:
			primaryOrganizationId = serverSession['primaryOrganizationId']

		with dataUtils.worker() as worker:
				vehicleStructure= worker.getVehicleTree(primaryOrganizationId)

		# Vehicle selector Block Ends

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('report4Form.html', classdata=self.classData,
				additionalOptions = [
					proxy.render ('vehicleSelector.html',
						branches = vehicleStructure[0],
						vehicleGroups = vehicleStructure[1],
						vehicles = vehicleStructure[2],
					)
				]
			),
			newTabTitle='Stoppage Summary',
			url=requestPath.allPrevious(),
		)
	#



	def _newReport4FormValidate(self, formData):
		pass

	#

	def _newReport4FormAction(self, requestPath):

		formData = json.loads(cherrypy.request.params['formData'])

		gmtAdjust = formData['gmtAdjust']
		fromDate = formData['fromDate']
		toDate = formData['toDate']

		gpsHelp = self.app.component('gpsHelper')
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		vehiclesListNested = json.loads(self._report4VehicleListNested(requestPath))
		vehicleIds = formData['vehicleList']
		if len(vehicleIds) == 0:
			return self.jsonSuccess('No Vehicle Selected',errors='Yes')

		timeHelp = self.app.component('timeHelper')
		time = timeHelp.getDateAndTime(fromDate[0], fromDate[1], fromDate[2], 0, 0, 0)
		fromTime = timeHelp.getDateAndTime_subtract(gmtAdjust, time)

		time = timeHelp.getDateAndTime(toDate[0], toDate[1], toDate[2], 23, 59, 59)
		toTime = timeHelp.getDateAndTime_subtract(gmtAdjust, time)

		rows = []
		for id in vehicleIds:
			rawCoordinates = dbHelp.getRawCoordinatesForDeviceBetween(id, fromTime, toTime)
			#rawCoordinates = rawCoordinates.order_by(db.gpsDeviceMessage1.timestamp)
			if rawCoordinates.count() == 0:
				continue
			report = gpsHelp.makeReport(rawCoordinates.all(), gmtAdjust)
			vehicleData = dbHelp.getVehicleDetails(vehiclesListNested, id)
			row = {}
			row['cell'] = [len(rows) + 1]
			row['cell'].append(id)
			row['cell'].append(vehicleData['vehicleName'])
			row['cell'].append(vehicleData['regNo'])
			row['cell'].append(vehicleData['vehicleModel'])
			row['cell'].append(str(report['totalRunningDuration']))
			row['cell'].append('{0:.2f}'.format(report['totalRunningDistance']))
			row['cell'].append(str(report['totalStopDuration']))
			row['cell'].append(report['timesStopped'])
			row['cell'].append('{0:.2f}'.format(report['avgSpeed']))
			rows.append(row)

		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])

		rows = dbHelp.getSlicedData(rows, pageNo, self.numOfObj)

		data = {
			'classData': self.classData,
			'sendData': rows,
		}
		if len(rows['rows']) == 0:
			return self.jsonSuccess('No Data Present',errors='Yes')

		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')

		#

	#

	def _report4VehicleListNested(self, requestPath):
		primaryOrganizationId = None
		with self.server.session() as serverSession:
			primaryOrganizationId = serverSession['primaryOrganizationId']
		dbHelp = self.app.component('dbHelper')
		vehiclesListNested = json.dumps(dbHelp.getVehiclesListNested(primaryOrganizationId))
		return vehiclesListNested
	#