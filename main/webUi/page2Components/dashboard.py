from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Dashboard(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newDashboardForm':
			return self._newDashboardForm(requestPath)
		elif nextPart == 'newDashboardFormAction':
			return self._newDashboardFormAction(requestPath)
		elif nextPart == 'dashboardVehicleListNested':
			return self._dashboardVehicleListNested(requestPath)
		#

	#



	def _newDashboardForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'dashboardForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'dashboardForm.js')
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

		self.classData = ['S.No.', 'Status', 'Vehicle Information', 'Total Running(km)', 'Total Running Duration', 'Total Idle Duration', 'Total Stop Duration',
						  'Total Inactive Duration', 'Speed', 'Odometer', 'Location', 'Alert', 'Last Updated Time', 'IGN', 'PWR', 'AC', 'GPS']

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
			bodyContent=proxy.render('dashboardForm.html', classdata=self.classData,
				additionalOptions = [
					proxy.render ('vehicleSelector.html',
						branches = vehicleStructure[0],
						vehicleGroups = vehicleStructure[1],
						vehicles = vehicleStructure[2],
					)
				]
			),
			newTabTitle='Dashboard',
			url=requestPath.allPrevious(),
		)
	#





	def _newDashboardFormValidate(self, formData):
		pass

	#

	def _newDashboardFormAction(self, requestPath):

		formData = json.loads(cherrypy.request.params['formData'])

		if not hasattr(self,'gmtAdjust'):
			self.gmtAdjust = formData['gmtAdjust']
		gmtAdjust=self.gmtAdjust


		gpsHelp = self.app.component('gpsHelper')
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		timeHelp = self.app.component('timeHelper')

		gmtTime = timeHelp.getGMTDateAndTime()
		fromTime = timeHelp.getDateAndTime(gmtTime.year, gmtTime.month, gmtTime.day, 0, 0, 0)
		fromTime = timeHelp.getDateAndTime_subtract(gmtAdjust, fromTime)
		toTime = timeHelp.getDateAndTime(gmtTime.year, gmtTime.month, gmtTime.day, 23, 59, 59)
		toTime = timeHelp.getDateAndTime_subtract(gmtAdjust, toTime)

		curTime = timeHelp.getDateAndTime_add(gmtAdjust, gmtTime)

		vehiclesListNested = json.loads(self._dashboardVehicleListNested(requestPath))
		vehicleIds = formData['vehicleList']

		if len(vehicleIds) == 0:
			return self.jsonSuccess('No Vehicle Selected',errors='Yes')

		data = None
		try:
			rows = []
			for id in vehicleIds:
				rawCoordinates = dbHelp.getRawCoordinatesForDeviceBetween(id, fromTime, toTime)
				rawCoordinates = rawCoordinates.order_by(db.gpsDeviceMessage1.timestamp)

				if rawCoordinates.count() == 0:
					continue
				report = gpsHelp.makeReport(rawCoordinates.all())
				vehicleData = dbHelp.getVehicleDetails(vehiclesListNested, id)
				row = {}
				row['cell'] = [len(rows) + 1]
				row['cell'].append('empty')
				row['cell'].append(vehicleData['vehicleInfo'])
				row['cell'].append('{0:.2f}'.format(report['totalRunningDistance']))
				row['cell'].append(str(report['totalRunningDuration']))
				row['cell'].append(str(report['totalIdleDuration']))
				row['cell'].append(str(report['totalStopDuration']))
				row['cell'].append(str(report['totalInactiveDuration']))
				row['cell'].append('empty')
				row['cell'].append('empty')
				row['cell'].append(report['endLocation'])
				row['cell'].append(report['alert'])
				row['cell'].append(str(curTime))
				row['cell'].append('empty')
				row['cell'].append('empty')
				row['cell'].append('empty')
				row['cell'].append('empty')
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
		except:
			pass



		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')

		return

		#

	#

	def _dashboardVehicleListNested(self, requestPath):
		primaryOrganizationId = None
		with self.server.session() as serverSession:
			primaryOrganizationId = serverSession['primaryOrganizationId']
		dbHelp = self.app.component('dbHelper')
		vehiclesListNested = json.dumps(dbHelp.getVehiclesListNested(primaryOrganizationId))
		return vehiclesListNested

	#
