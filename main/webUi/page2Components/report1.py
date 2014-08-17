from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Report1(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newReport1Form':
			return self._newReport1Form(requestPath)
		elif nextPart == 'newReport1FormAction':
			return self._newReport1FormAction(requestPath)
		#

	#



	def _newReport1Form(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'report_1_4_form.css')
		)
		params['externalJs'].append('http://maps.googleapis.com/maps/api/js?libraries=geometry&sensor=false')
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'report1Form.js')
		)

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('report1Form.html'),
			newTabTitle='Report 1',
			url=requestPath.allPrevious(),
		)

	#


	def _newReport1FormValidate(self, formData):
		pass

	#

	def _newReport1FormAction(self, requestPath):

		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbHelper')
		data = db.returnCarsDataByDates(formData['fromDate'],formData['toDate'])
		
		errors = self._newReport1FormValidate(formData)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#
		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')
		#
	#
