from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator

import cherrypy
from sqlalchemy import func

import json
import datetime


class Vehicle(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)
		self._setupFieldInfo()

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newVehicleForm':
			return self._newVehicleForm(requestPath)
		elif nextPart == 'newVehicleFormAction':
			return self._newVehicleFormAction(requestPath)
		elif nextPart == 'vehicleData':
			return self._VehicleFormActionData()
		elif nextPart == 'delVehicleDataAction':
			return self.delVehicle()
		elif nextPart == 'editVehicleAction':
			return self.editVehicleAction()
		#
	#

	def _setupFieldInfo(self):
		db = self.app.component('dbManager')
		infoLength = 19
		infoLength2 = 15

		self._clientFieldInfo = {
		'vehicleRegNo': {'maxLength': infoLength2},
		'vehicleName': {'maxLength': infoLength},
		'vehicleMake': {'maxLength': infoLength},
		'vehicleType': {'maxLength': infoLength2},
		}

	#

	def _newVehicleForm(self, requestPath):
		proxy, params = self.newProxy()
		with self.server.session() as session:
			self.username = session['username']
			self.userId = session['userId']
		#
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'newVehicleForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'newVehicleForm.js')
		)
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'flexiBasic.js')
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

		params['config'].update({
		'newVehicleFormAction': requestPath.allPrevious(
			ignore=1,
			additional=['newVehicleFormAction'],
		),

		'fieldInfo': self._clientFieldInfo,
		})
		attrNames = ['User_Id', 'Vehicle_Id', 'Vehicle_Name', 'Vehicle_Make', 'Vehicle_Reg_No', 'Vehicle_Type','Vehicle_Model','Group_id','Device_id']
		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('newVehicleForm.html', classdata=attrNames),
			newTabTitle='New Vehicle',
			url=requestPath.allPrevious(),
		)

	#

	def _newVehicleFormValidate(self, formData):

		a = Validator(formData)

		vehicleRegNo = a.required('vehicleRegNo')
		vehicleRegNo.validate('and',
							  ('type', str),
							  ('maxLength', self._clientFieldInfo['vehicleRegNo']['maxLength']))

		vehicleName = a.required('vehicleName')
		vehicleName.validate('and',
							 ('type', str),
							 ('maxLength', self._clientFieldInfo['vehicleName']['maxLength']))

		vehicleMake = a.required('vehicleMake')
		vehicleMake.validate('and',
							 ('type', str),
							 ('maxLength', self._clientFieldInfo['vehicleMake']['maxLength']))

		vehicleType = a.required('vehicleType')
		vehicleType.validate('and',
							 ('type', str),
							 ('maxLength', self._clientFieldInfo['vehicleType']['maxLength']))

		return a.errors


	def _newVehicleFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])

		errors = self._newVehicleFormValidate(formData)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		db = self.app.component('dbManager')

		with db.session() as session:
			vehicle_data = db.Gps_Vehicle_Info.addOrUpdateFromParams('add', {
			'Vehicle_Id': db.Entity.newUuid(),
			'User_Id': self.userId,
			'Vehicle_Reg_No': formData['vehicleRegNo'],
			'Vehicle_Name': formData['vehicleName'],
			'Vehicle_Make': formData['vehicleMake'],
			'Vehicle_Type': formData['vehicleType'],
			})
			session.add(vehicle_data)

		return self.jsonSuccess('Vehicle Added')

	#

	def _VehicleFormActionData(self):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		formData = json.loads(cherrypy.request.params['formData'])
		pageNo = int(formData.get('pageNo', '1'))
		numOfObj = int(formData.get('rp', '10'))

		attrNames = ['User_Id', 'Vehicle_Id', 'Vehicle_Name', 'Vehicle_Make', 'Vehicle_Reg_No', 'Vehicle_Type','Vehicle_Model','Group_id','Device_id']
		with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				queryObj = session.query(db.Gps_Vehicle_Info).filter_by(User_Id=id)
				sendData = dbHelp.getDataForFlexiGrid(pageNo, queryObj, attrNames, numOfObj)
		actuallySendData = {
		'sendData': sendData
		}
		return self.jsonSuccess(actuallySendData)

	#

	def delVehicle(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')

		db.Gps_Vehicle_Info.delete({
		'Vehicle_Id': formData['id'],
		})
		db.Gps_Geofence_Data.delete({
		'Vehicle_Id': formData['id'],
		})
		db.Gps_Coordinate_Data.delete({
		'Vehicle_Id': formData['id'],
		})
		db.Gps_Poi_Data.delete({
		'Vehicle_Id': formData['id'],
		})
		db.Gps_Poi_Info.delete({
		'Vehicle_Id': formData['id'],
		})

	#

	def editVehicleAction(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		with db.session() as session:
			db.Gps_Vehicle_Info.updateFromParams({'Vehicle_Id': formData['id']}, **{
			'Vehicle_Name': formData.get('vehicleName', None),
			'Vehicle_Make': formData.get('vehicleMake', None),
			'Vehicle_Reg_No': formData.get('vehicleRegNo', None),
			'Vehicle_Type': formData.get('vehicleType', None)
			})

		return self.jsonSuccess('Vehicle Edited')
		#