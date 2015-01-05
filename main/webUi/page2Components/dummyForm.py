from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
from sqlalchemy import func
import json
import datetime
from uuid import uuid4


class DummyForm(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'displayDummyForm':
			return self._displayDummyForm(requestPath)
		elif nextPart == 'newStudentFormAction':
			return self._newStudentFormAction(requestPath)
		elif nextPart == 'studentData':
			return self._studentData(requestPath)
		elif nextPart == 'editStudent':
			return self._editStudentData(requestPath)
		"""elif nextPart == 'delVehicleGroup':
			return self.delVehicleGroup()
		"""#

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




	def _displayDummyForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'dummyForm.js')
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


		classData = ['Sno','Student Name','Section', 'Date','Sex']
		sectionList1=['Cse','Ece','IT']

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('dummyform.html', classdata=classData, sectionList=sectionList1,
								   ),
			newTabTitle='New Student',
			url=requestPath.allPrevious(),
		)

	#

	def _newStudentFormValidate(self, formData):
		db = self.app.component('dbManager')
		v = Validator(formData)

		studentName = v.required('studentName')
		studentName.validate('type', str)

		section = v.required('section')
		section.validate('type', str)

		date = v.required('date')
		date.validate('type', str)

		sex = v.required('sex')
		sex.validate('type', str)




		return v.errors

	#

	def _newStudentFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		#dataUtils = self.app.component('dataUtils')
		#db = self.app.component('dbManager')
		print(formData)
		errors = self._newStudentFormValidate(formData)
		print(errors)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		'''parentBranchId = formData['branchId']

		del formData['branchId']

		with dataUtils.worker() as worker:
			details = formData
			details['parentOrgId'] = parentBranchId
			newVehicleGroup = worker.createVehicleGroup(details)


'''




		#

		# iF ERROR is Yes then page will not reload ... and if No the page will reload
		return self.jsonSuccess('Student record created',errors='No')

	#

	numOfObj = 10

	def _studentData(self, requestPath):
		#db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData = ['Sno','Student Name','Section', 'Date','Sex']
		formData = json.loads(cherrypy.request.params['formData'])
		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])
		'''
		with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				sendData = dbHelp.getVehicleGroupDataForFlexiGrid(pageNo, session, db,
																  serverSession['primaryOrganizationId'], id,
																  self.numOfObj)
		'''
		sendData=[]
		cell = {}
		cell['cell']=[]
		cell['cell'].append(1)
		cell['cell'].append("raman")
		cell['cell'].append("IT")
		cell['cell'].append(4)
		cell['cell'].append("Male")
		sendData.append(cell)

		sendData1 = dbHelp.getSlicedData(sendData,pageNo,self.numOfObj)
		actuallySendData = {
		'classData': classData,
		'sendData': sendData1,

		}

		return self.jsonSuccess(actuallySendData)

	#

	def _editStudentData(self,requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		# TODO:Checking errors in the database
		# errors = self._userManagementFormValidate(formData)
		print(formData)
		#return self.addOrEditVehicleGroupToDatabase('edit', formData)
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