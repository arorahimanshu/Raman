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
		infoLength3 = 10

		self._clientFieldInfo = {
		'vehicleRegNo': {'maxLength': infoLength2},
		'vehicleName': {'maxLength': infoLength},
		'vehicleMake': {'maxLength': infoLength},
		'vehicleDevId': {'maxLength': infoLength3},
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
		attrNames = ['S.No',  'Vehicle_Id', 'Vehicle_Name','Device_Id',  'Vehicle_Make', 'Vehicle_Reg_No', 'Vehicle_Type', 'Speed Limit', 'Vehicle Group Id']

		dbHelp = self.app.component('dbHelper')
		vehicleGroupList = dbHelp.returnVehicleGroupListForBranch(None)

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('newVehicleForm.html', classdata=attrNames, vehicleGroupList=vehicleGroupList),
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
		vehicleDevId = a.required('vehicleDevId')
		vehicleDevId.validate('and',
							 ('type', str),
							 ('maxLength', self._clientFieldInfo['vehicleDevId']['maxLength']))
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
			newVehicleID = db.Entity.newUnique()
			session.add(newVehicleID)
			session.commit()

			vehicle_data = db.Gps_Vehicle_Info.addOrUpdateFromParams('add', {
			'id': newVehicleID.id,
			'parent_id': formData['vehicleGroupId'],
			'name': formData['vehicleName'],
			'device_id':formData['vehicleDevId']
			})
			session.add(vehicle_data)

			session.add(db.Info.newFromParams({
				'id': db.Entity.newUuid(),
				'entity_id': newVehicleID.id,
				'enumType': db.Info.Type.vehicleRegNo,
				'preference': 0,
				'data': formData['vehicleRegNo'],
			}))

			session.add(db.Info.newFromParams({
				'id': db.Entity.newUuid(),
				'entity_id': newVehicleID.id,
				'enumType': db.Info.Type.vehicleMake,
				'preference': 0,
				'data': formData['vehicleMake'],
			}))
			session.add(db.Info.newFromParams({
				'id': db.Entity.newUuid(),
				'entity_id': newVehicleID.id,
				'enumType': db.Info.Type.vehicleType,
				'preference': 0,
				'data': formData['vehicleType'],
			}))
			session.add(db.Info.newFromParams({
				'id': db.Entity.newUuid(),
				'entity_id': newVehicleID.id,
				'enumType': db.Info.Type.speed,
				'preference': 0,
				'data': formData['speedLimit'],
			}))

			return self.jsonSuccess('Vehicle Added',errors='No')


	#

	def _VehicleFormActionData(self):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')

		classData = [  'Vehicle_Id', 'Vehicle_Name','Device_Id', 'Vehicle_Make', 'Vehicle_Reg_No', 'Vehicle_Type', 'Speed Limit', 'Vehicle Group Id']

		formData = json.loads(cherrypy.request.params['formData'])
		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])

		with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				sendData = dbHelp.getVehicleDataForFlexiGrid(pageNo, session, db,
																  serverSession['primaryOrganizationId'], id,
																  self.numOfObj)

		actuallySendData = {
		'classData': classData,
		'sendData': sendData,

		}

		return self.jsonSuccess(actuallySendData)

	#

	def delVehicle(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		dataUtils = self.app.component('dataUtils')
		with dataUtils.worker() as worker:
			worker.delVehicleCascade(formData['id'])


	#

	def editVehicleAction(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		with db.session() as session:
			db.Gps_Vehicle_Info.updateFromParams({'id': formData['id']}, **{
			'name': formData.get('vehicleName', None),
 			'parent_id': formData.get('vehicleGroupId', None),
			'device_id': formData.get('vehicleDevId', None),

			})
			db.Info.updateFromParams({
			'entity_id':formData['id'],'preference':0,'type':db.Info.Type.vehicleRegNo.value
			},**{'data':formData['vehicleRegNo']})

			db.Info.updateFromParams({
			'entity_id':formData['id'],'preference':0,'type':db.Info.Type.vehicleMake.value
			},**{'data':formData['vehicleMake']})

			db.Info.updateFromParams({
			'entity_id':formData['id'],'preference':0,'type':db.Info.Type.vehicleType.value
			},**{'data':formData['vehicleType']})

			db.Info.updateFromParams({
			'entity_id':formData['id'],'preference':0,'type':db.Info.Type.speed.value
			},**{'data':formData['speedLimit']})


		return self.jsonSuccess('Vehicle Edited',errors='No')

		#



