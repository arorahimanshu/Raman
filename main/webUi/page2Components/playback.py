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
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'css', 'jquery.datetimepicker.css')
		)
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'js', 'jquery.datetimepicker.js')
		)
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

		formData = cherrypy.request.params
		data = json.loads(formData['data'])
		deviceId = formData['id']
		db = self.app.component('dbHelper')
		#data = db.returnCarsDataByDates(formData['fromDate'],formData['toDate'])
		timeHelper = self.app.component('timeHelper')
		dateTpe = data['dateType']
		gmtAdjust = data['gmtAdjust']
		if dateTpe == 'Relative':
			now = timeHelper.getGMTDateAndTime()
			now = timeHelper.getDateAndTime_add(gmtAdjust, now)
			fromDate = timeHelper.getDateAndTime(now.year, now.month, now. day, 0, 0, 0)
			if data['relativeDay'] == 'today':
				toDate = now
			elif data['relativeDay'] == 'yesterday':
				toDate = fromDate
				fromDate = timeHelper.goBackInTime(fromDate, days=1)
			elif data['relativeDay'] == 'yesterday1':
				toDate = timeHelper.goBackInTime(fromDate, days=1)
				fromDate = timeHelper.goBackInTime(fromDate, days=2)
		else:
			fromDate = timeHelper.getDateAndTime(data['fromDate'][0:4],data['fromDate'][5:7],data['fromDate'][8:10], data['fromDate'][11:13], data['fromDate'][14:16], 0)
			toDate = timeHelper.getDateAndTime(data['toDate'][0:4],data['toDate'][5:7],data['toDate'][8:10], data['toDate'][11:13], data['toDate'][14:16], 0)
		fromDate = timeHelper.getDateAndTime_subtract(gmtAdjust, fromDate)
		toDate = timeHelper.getDateAndTime_subtract(gmtAdjust, toDate)
		data = db.returnLiveCarsData([deviceId], fromDate, toDate, gmtAdjust)
		#errors = self._newPlaybackFormValidate(formData)
		#if errors:
		#	return self.jsonFailure('validation failed', errors=errors)
		#
		'''
		newData = []
		newData.append([])
		newData.append([])
		for d in data[0]:
			if d['speed'] != 0.0:
				newData[0].append(d)
		newData[1]=data[1]
		data=newData
		'''
		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')
		#
	#
