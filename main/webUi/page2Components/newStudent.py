from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
from sqlalchemy import func
import json
import datetime
from uuid import uuid4


class Student(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newStudentForm':
			return self._newStudentForm(requestPath)
		elif nextPart == 'newStudentFormAction':
			return self._newStudentFormAction(requestPath)
		elif nextPart == 'newStudentData':
			return self._newStudentData(requestPath)
		elif nextPart == 'editNewStudent':
			return self._editNewStudent(requestPath)
		elif nextPart == 'delNewStudent':
			return self.delNewStudent()
		#

	#

	def delNewStudent(self):
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




	def _newStudentForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'organizationManagement.css')
		)
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'newVehicleForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'newStudent.js')
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
		'newStudentFormAction': requestPath.allPrevious(
			ignore=1,
			additional=['newStudentFormAction'],
		)

		})
		with self.server.session() as session:
			self.userId = session['userId']

		classData = ['Name','Roll No.','Branch', 'Marks']

		dbHelp = self.app.component('dbHelper')
		branchList = dbHelp.returnBranchListForOrg(None)

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('newStudent.html', classdata=classData, userId=self.userId, branchList=branchList,
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

		studentCat = v.required('studentCat')
		studentCat.validate('type', str)



		return v.errors

	#

	def _newStudentFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')

		errors = self._newStudentFormValidate(formData)

		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		'''parentBranchId = formData['nameId']

		del formData['nameId']

		with dataUtils.worker() as worker:
			details = formData
			details['parentOrgId'] = parentBranchId
			newVehicleGroup = worker.createVehicleGroup(details)
			'''




		# this part add data to Info Table
		# TODO Nitin will create a function for adding data to info table





		#

		# iF ERROR is Yes then page will not reload ... and if No the page will reload
		return self.jsonSuccess('Vehicle Group created',errors='No')

	#

	numOfObj = 10

	def _newStudentData(self, requestPath):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData = ['Name','Roll No.','Branch', 'Marks']
		formData = json.loads(cherrypy.request.params['formData'])
		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])
		'''with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				sendData = dbHelp.getVehicleGroupDataForFlexiGrid(pageNo, session, db,
																  serverSession['primaryOrganizationId'], id,
																  self.numOfObj)'''

		sendData=[]
		cell = {}
		cell['cell']=[]
		cell['cell'].append("Anmoll")
		cell['cell'].append(24)
		cell['cell'].append("ECE")
		cell['cell'].append(98)
		sendData.append(cell)
		sendData1 = dbHelp.getSlicedData(sendData,pageNo,self.numOfObj)
		actuallySendData = {
		'classData': classData,
		'sendData': sendData1,

		}

		return self.jsonSuccess(actuallySendData)

	#

	def _editNewStudent(self,requestPath):
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

				},**{'name':formData['Name'],'rollno':formData['rollNo'],'Branch':formData['branch'], 'marks':formData['marks']})



			# iF ERROR is Yes then page will not reload ... and if No the page will reload
			return self.jsonSuccess('New Student Edited',errors='No')

		return self.jsonFailure('Error')
	#