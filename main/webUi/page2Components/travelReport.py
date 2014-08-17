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
		#

	#



	def _newTravelReportForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'travelReportForm.css')
		)
		params['externalJs'].append('http://maps.googleapis.com/maps/api/js?libraries=geometry&sensor=false')
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'travelReportForm.js')
		)

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('travelReportForm.html'),
			newTabTitle='Travel Report',
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
