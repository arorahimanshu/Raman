from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class TravelReport2(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newTravelReportForm2':
			return self._newTravelReportForm(requestPath)
		elif nextPart == 'newTravelReportFormAction2':
			return self._newTravelReportFormAction(requestPath)
		elif nextPart == 'travelReportVehicleListNested':
			return self._travelReportVehicleListNested(requestPath)
		#

	#



	def _newTravelReportForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'travelReportForm2.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'travelReportForm2.js')
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



		classData = ['S.No.','Company','Branch','Vehicle Information','Driver Information','Start Location',
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
			bodyContent=proxy.render('travelReportForm2.html', classdata=classData, vehicleListNested = json.loads(vehiclesListNested), vehicles = json.dumps(vehiclesListNested)),
			newTabTitle='Travel Report2',
			url=requestPath.allPrevious(),
		)
	#


	def _newTravelReportFormValidate(self, formData):
		pass

	#

	def _newTravelReportFormAction(self, requestPath):

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

	def _travelReportVehicleListNested(self, requestPath):
		primaryOrganizationId = None
		with self.server.session() as serverSession :
			primaryOrganizationId = serverSession['primaryOrganizationId']
		dbHelp = self.app.component('dbHelper')
		vehiclesListNested = json.dumps(dbHelp.getVehiclesListNested (primaryOrganizationId))
		return vehiclesListNested
	#