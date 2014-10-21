from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
from sqlalchemy import func
import json
import datetime
from uuid import uuid4


class vehicleGroup(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'vehicleGroupManagementForm':
			return self._vehicleGroupManagementForm(requestPath)
		elif nextPart == 'vehicleGroupManagementFormAction':
			return self._vehicleGroupManagementFormAction(requestPath)
		elif nextPart == 'vehicleGroupData':
			return self._vehicleGroupData(requestPath)
		elif nextPart == 'editVehicleGroup':
			return self._editVehicleGroupData(requestPath)
		elif nextPart == 'delVehicleGroup':
			return self.delVehicleGroup()
		#

	#

	def delVehicleGroup(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		dataUtils = self.app.component('dataUtils')
		with dataUtils.worker() as worker:

			db.VehicleGroup.delete({
				'id':formData['id']
			})
			db.Entity.delete({
				'id':formData['id']
			})

		#




	def _vehicleGroupManagementForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'organizationManagement.css')
		)
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'newVehicleForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'vehicleGroupManagement.js')
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
		'vehicleGroupManagementFormAction': requestPath.allPrevious(
			ignore=1,
			additional=['vehicleGroupManagementFormAction'],
		)


		})
		with self.server.session() as session:
			self.userId = session['userId']

		classData = ['Sno','Branch_id','Vehicle_Group_Name', 'Category','Id']

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('vehicleGroupManagement.html', classdata=classData, userId=self.userId,
								   ),
			newTabTitle='New VehicleGroup',
			url=requestPath.allPrevious(),
		)

	#

	def _vehicleGroupManagementFormValidate(self, formData):
		db = self.app.component('dbManager')
		v = Validator(formData)

		vehicleGroupName = v.required('vehicleGroupName')
		vehicleGroupName.validate('type', str)

		vehicleGroupCat = v.required('vehicleGroupCat')
		vehicleGroupCat.validate('type', str)



		return v.errors

	#

	def _vehicleGroupManagementFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')

		errors = self._vehicleGroupManagementFormValidate(formData)

		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#
		with self.server.session() as serverSession :
			parentOrganizationId = serverSession['primaryOrganizationId']

		with dataUtils.worker() as worker:
			details = formData
			details['parentOrgId'] = parentOrganizationId
			newVehicleGroup = worker.createVehicleGroup(details)




		# this part add data to Info Table
		# TODO Nitin will create a function for adding data to info table





		#

		return self.jsonSuccess('VehicleGroup created')

	#

	numOfObj = 10

	def _vehicleGroupData(self, requestPath):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData = ['Sno','Branch_id','Vehicle_Group_Name', 'Category']
		pageNo = int((cherrypy.request.params).get('pageNo', '1'))
		if 'pageNo' not in cherrypy.request.params:
			self.numOfObj = 10
		if 'rp' in cherrypy.request.params and 'pageNo' in cherrypy.request.params:
			self.numOfObj = int(cherrypy.request.params['rp'])
		with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				sendData = dbHelp.getVehicleGroupDataForFlexiGrid(pageNo, session, db,
																  serverSession['primaryOrganizationId'], id,
																  self.numOfObj)

		actuallySendData = {
		'classData': classData,
		'sendData': sendData,

		}

		return self.jsonSuccess(actuallySendData)

	#

	def _editVehicleGroupData(self,requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		# TODO:Checking errors in the database
		# errors = self._userManagementFormValidate(formData)
		return self.addOrEditVehicleGroupToDatabase('edit', formData)
	#

	def addOrEditVehicleGroupToDatabase(self, query, formData):
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')
		details = dict()
		print(formData)

		with dataUtils.worker() as worker:
			if(query=='edit'):
				db.VehicleGroup.updateFromParams({
				'id':formData['id']

				},**{'name':formData['vehicleGroupName'],'category':formData['vehicleGroupCat']})

			#
			#	address= formData['address1'] + ";" + formData['address2'] + ";" + formData['state'] + ";" + formData[
			#		'city'] + ";" + formData['pincode']
			#
			#	db.Info.updateFromParams({
			#		'entity_id':formData['id']
			#
			#	},**{'data':address
			#	})
			#

				return self.jsonSuccess('user information edited')

		return self.jsonFailure('Error')
	#