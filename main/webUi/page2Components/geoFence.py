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
		elif nextPart == 'newGeoVehicle_delData':
			return self._newGeoVehicle_delData(requestPath)
		elif nextPart == 'geoFenceData':
			return self._geoFenceData(requestPath)
		elif nextPart == 'editGeoFence':
			return self._editGeoFence(requestPath)
		elif nextPart == 'delGeoFence':
			return self._delGeoFence(requestPath)
		#
	#



	def _newGeoFenceForm(self, requestPath):

		proxy, params = self.newProxy()

		params['externalJs'].append("https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=geometry&libraries=drawing")

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'geoFenceForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'geoFenceForm.js')
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

		db = self.app.component('dbHelper')
		with self.server.session() as session:
			self.username = session['username']
			self.userId = session['userId']
		#
		self.vehicleList = db.returnVehicleList(self.userId)
		self.classData=['S.No.','GeoFence Id','GeoFence Name','Vehicle Id','Type','Radius','Coordinates']
		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('GeoFenceForm.html',vehicleList=self.vehicleList,classdata=self.classData),
			newTabTitle='Create Geo Fence',
			url=requestPath.allPrevious(),
		)

	#


	def _newGeoFenceFormValidate(self, formData):
		def checkVehicleId(data):
			dbHelper = self.app.component('dbHelper')
			data=[x.strip() for x in data.split(',')]
			for i in data:
				if dbHelper.checkVehicleExists(self.userId, i):
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

		Details = v.required('Details')
		Details.validate('type', str)
		print(v.errors)
		return v.errors;

	#

	def _newGeoFenceFormAction(self, requestPath):

		formData = json.loads(cherrypy.request.params['formData'])
		print("*************************Submitted**********************************")
		print(formData)
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
			'Details': formData['Details'],
			})
			session.add(gps_data)

		return self.jsonSuccess('Geo Fence Saved !')


		#
	#

	def _geoFenceData(self,requestPath):
		tableData = []
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Gps_Geofence_Data).filter_by(User_Id=self.userId)
			for obj in query.all():
				tableData.append(
					{'Geofence_Id': obj.Geofence_Id,'Geofence_Name': str(obj.Geofence_Name), 'Vehicle_Id': obj.Vehicle_Id, 'Details':obj.Details}
					)
		rows=[]
		for data in tableData:
			row={}
			row['cell']=[len(rows)+1]
			row['cell'].append(data['Geofence_Id'])
			row['cell'].append(data['Geofence_Name'])
			row['cell'].append(data['Vehicle_Id'])
			details = json.loads(data['Details'])
			row['cell'].append(details['type'])
			if details['type']=='CIRCLE':
				row['cell'].append(details['radius'])
			else:
				row['cell'].append('N/A')
			row['cell'].append(json.dumps(details['geometry']))
			rows.append(row)

		formData = json.loads(cherrypy.request.params['formData'])
		rp=formData.get('rp',10)
		pageNo=formData.get('pageNo',1)
		dbHelp = self.app.component('dbHelper')
		rows = dbHelp.getSlicedData(rows,pageNo,rp)

		data = {
			'classData': self.classData,
			'sendData': rows
		}

		if data != None:
			return self.jsonSuccess(data)
		else:
			return self.jsonFailure('No Data Found')

		#

	def _editGeoFence(self,requestPath):
		formData = json.loads(cherrypy.request.params['formData'])

		db = self.app.component('dbManager')

		errors = self._newGeoFenceFormValidate(formData)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#


		db.Gps_Geofence_Data.updateFromParams({'Geofence_Id': formData['id']},
                                                          **{'Geofence_Name': formData['fenceName'],
                                                             'Vehicle_Id': formData['vehicleId'],
                                                             'User_Id': self.userId,
                                                             'Coordinate_Id': db.Entity.newUuid(),
                                                             'Details': formData['Details'],
            })

		return self.jsonSuccess('Geo Fence Saved !')

	def _delGeoFence(self,requestPath):
		formData= json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		try:
			with db.session() as session:
				query = session.query(db.Gps_Geofence_Data).filter(db.Gps_Geofence_Data.Geofence_Id == formData)
				session.delete(query.one())
		except:
			return self.jsonFailure()
		return self.jsonSuccess('GeoFence Deleted')

	def _newGeoVehicle_updateData(self,requestPath):
		formData= json.loads(cherrypy.request.params['formData'])
		errors = self._newGeoFenceFormValidate(formData)
		db = self.app.component('dbManager')
		print(formData)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)

		with db.session() as session:
			gps_data = db.Gps_Geofence_Data.newFromParams({
			'Geofence_Name': formData['fenceName'],
			'Vehicle_Id': formData['vehicleId'],
			'Details': formData['Details'],
			})
			session.query(db.Gps_Geofence_Data).filter(db.Gps_Geofence_Data.Geofence_Id == formData['fenceID']).update({gps_data})
			session.commit()