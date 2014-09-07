from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Report111(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newReport111Form':
			return self._newReport111Form(requestPath)
		elif nextPart == 'newReport111FormAction':
			return self._newReport111FormAction(requestPath)
		#

	#



	def _newReport111Form(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'report_111_form.css')
		)
		params['externalJs'].append('http://maps.googleapis.com/maps/api/js?libraries=geometry&sensor=false')
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'report111Form.js')
		)

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('report111Form.html'),
			newTabTitle='Report 111',
			url=requestPath.allPrevious(),
		)

	#


	def _newReport111FormValidate(self, formData):
		pass

	#

	def _newReport111FormAction(self, requestPath):

		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbHelper')
		data = db.returnCarsDataByDates111(formData['fromDate'],formData['toDate'])

		errors = self._newReport111FormValidate(formData)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#
		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')
		#
	#
