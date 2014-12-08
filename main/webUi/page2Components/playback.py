from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Playback(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newPlaybackForm':
			return self._newPlaybackForm(requestPath)
		elif nextPart == 'newPlaybackFormAction':
			return self._newPlaybackFormAction(requestPath)

		#

	#



	def _newPlaybackForm(self, requestPath):
		proxy, params = self.newProxy()
		dbHelp = self.app.component('dbHelper')

		params['externalJs'].append('http://maps.googleapis.com/maps/api/js?libraries=geometry&sensor=false')
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'playbackForm.js')
		)
		params['externalJs'].append (
			self.server.appUrl ('etc', 'lib1', 'mapAnimator.js')
		)

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'playback.css')
		)
		#-------------- Code block to implement Vehicle Selector
		vehicleStructure = []
		dataUtils = self.app.component('dataUtils')
		with self.server.session() as serverSession:
			primaryOrganizationId = serverSession['primaryOrganizationId']


		with dataUtils.worker() as worker:
 			vehicleStructure= worker.getVehicleTree(primaryOrganizationId)
		#-------------- Code block to implement Vehicle Selector


		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('playbackForm.html',
				additionalOptions = [
					"<br><br><br><br>",

					proxy.render ('vehicleSelector.html',
						branches = vehicleStructure[0],
						vehicleGroups = vehicleStructure[1],
						vehicles = vehicleStructure[2],
					)
				]
			),
			newTabTitle='Playback',
			url=requestPath.allPrevious(),
		)

	#


	def _newPlaybackFormValidate(self, formData):
		pass

	#

	def _newPlaybackFormAction(self, requestPath):
		
		formData = json.loads(cherrypy.request.params['formData'])
		print(formData)
		db = self.app.component('dbHelper')
		deviceID =0
		#data = db.returnCarsDataByDates(formData['fromDate'],formData['toDate'])
		data = db.returnLiveCarsData(deviceID)
		#errors = self._newPlaybackFormValidate(formData)
		#if errors:
		#	return self.jsonFailure('validation failed', errors=errors)
		#
		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')
		#
	#
