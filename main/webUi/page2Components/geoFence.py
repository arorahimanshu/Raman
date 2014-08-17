from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class GeoFence(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newGeoFenceForm':
			return self._newGeoFenceForm(requestPath)
		elif nextPart == 'newGeoFenceFormAction':
			return self._newGeoFenceFormAction(requestPath)
		#

	#



	def _newGeoFenceForm(self, requestPath):

		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'geoFenceForm.css')
		)
		params['externalJs'].append("https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=geometry")
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'geoFenceForm.js')
		)
		db = self.app.component('dbHelper')
		db.trial();
		with self.server.session() as session:
			self.username = session['username']
			self.userId = session['userId']
		#

		self.vehicleList = db.returnVehicleList(self.userId)
		self.tableData = []
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Gps_Geofence_Data).filter_by(User_Id=self.userId)
			for obj in query.all():
				self.tableData.append(
					{'Geofence_Name': str(obj.Geofence_Name), 'Vehicle_Id': obj.Vehicle_Id, 'Latitude': obj.Latitude,
					 'Longitude': obj.Longitude})

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('GeoFenceForm.html', vehicleList=self.vehicleList, tableData=self.tableData),
			newTabTitle='Create Geo Fence',
			url=requestPath.allPrevious(),
		)

	#


	def _newGeoFenceFormValidate(self, formData):
		def checkVehicleId(data):
			dbHelper = self.app.component('dbHelper')
			if dbHelper.checkVehicleExists(self.userId, data):
				return None
			else:
				return "Unknown Vehicle"


		def checkDecimalList(data):
			for x in data.split(','):
				result=checkDecimal(x)

				if result:
					return "Invalid Coordinates"

			return None



		def checkDecimal(data):
			try:
				first = data.split('.')[0]
				second = data.split('.')[1]
				int(first)
				int(second)
			except:
				return True
			else:
				return False

		v = Validator(formData)
		vehicleId = v.required('vehicleId')
		vehicleId.validate('custom', checkVehicleId)

		fencename = v.required('fenceName')
		fencename.validate('type', str)

		latitude = v.required('latitudeList')
		latitude.validate('custom', checkDecimalList)

		longitude = v.required('longitudeList')
		longitude.validate('custom', checkDecimalList)
		print(v.errors)
		return v.errors;

	#

	def _newGeoFenceFormAction(self, requestPath):

		formData = json.loads(cherrypy.request.params['formData'])

		errors = self._newGeoFenceFormValidate(formData)
		db = self.app.component('dbManager')

		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		with db.session() as session:
			gps_data = db.Gps_Geofence_Data.newFromParams({
			'Geofence_Id': db.Entity.newUuid(),
			'Geofence_Name': formData['fenceName'],
			'Vehicle_Id': formData['vehicleId'],
			'User_Id': self.userId,
			'Coordinate_Id': db.Entity.newUuid(),
			'Latitude': formData['latitudeList'],
			'Longitude': formData['longitudeList'],
			})
			session.add(gps_data)

		return self.jsonSuccess('Geo Fence Saved !', vehicleId=formData['vehicleId'], fenceName=formData['fenceName'],
		                        latitude=formData['latitudeList'], longitude=formData['longitudeList'])


		#
		#