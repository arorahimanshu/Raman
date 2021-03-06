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
			worker.delVehicleGroupCascade(formData['id'])
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

		dbHelp = self.app.component('dbHelper')
		branchList = dbHelp.returnBranchListForOrg(None)

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('vehicleGroupManagement.html', classdata=classData, userId=self.userId, branchList=branchList,
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

		parentBranchId = formData['branchId']

		del formData['branchId']

		with dataUtils.worker() as worker:
			details = formData
			details['parentOrgId'] = parentBranchId
			newVehicleGroup = worker.createVehicleGroup(details)




		# this part add data to Info Table
		# TODO Nitin will create a function for adding data to info table





		#

		# iF ERROR is Yes then page will not reload ... and if No the page will reload
		return self.jsonSuccess('Vehicle Group created',errors='No')

	#

	numOfObj = 10

	def _vehicleGroupData(self, requestPath):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData = ['Sno','Branch_id','Vehicle_Group_Name', 'Category']
		formData = json.loads(cherrypy.request.params['formData'])
		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])
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

				},**{'name':formData['vehicleGroupName'],'category':formData['vehicleGroupCat'],'parent_id':formData['branchId']})



			# iF ERROR is Yes then page will not reload ... and if No the page will reload
			return self.jsonSuccess('Vehicle Group Edited',errors='No')

		return self.jsonFailure('Error')
	#