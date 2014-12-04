from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
from sqlalchemy import func
import json
import datetime
from uuid import uuid4


class Branch(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'branchManagementForm':
			return self._branchManagementForm(requestPath)
		elif nextPart == 'branchManagementFormAction':
			return self._branchManagementFormAction(requestPath)
		elif nextPart == 'branchData':
			return self._branchData(requestPath)
		elif nextPart == 'editBranch':
			return self._editBranchData(requestPath)
		elif nextPart == 'delBranch':
			return self.delBranch()
		#

	#

	def delBranch(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		dataUtils = self.app.component('dataUtils')
		with dataUtils.worker() as worker:
			db.Info.delete({
				'entity_id':formData['id']
			})

			db.branch.delete({
				'id':formData['id']
			})
			db.Entity.delete({
				'id':formData['id']
			})
		#




	def _branchManagementForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'organizationManagement.css')
		)
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'newVehicleForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'branchManagement.js')
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
		'branchManagementFormAction': requestPath.allPrevious(
			ignore=1,
			additional=['branchManagementFormAction'],
		)


		})
		with self.server.session() as session:
			self.userId = session['userId']

		classData = ['Sno','Organization_id','branch_name', 'Addrs_line1', 'Addrs_line2',
					 'City', 'State', 'Pincode','BranchId']

		dbHelp = self.app.component('dbHelper')
		orgList = dbHelp.returnOrgList(None)
		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('branchManagement.html', classdata=classData, userId=self.userId, orgList=orgList
								   ),
			newTabTitle='New Branch',
			url=requestPath.allPrevious(),
		)

	#

	def _branchManagementFormValidate(self, formData):
		db = self.app.component('dbManager')
		v = Validator(formData)

		branchName = v.required('branchName')
		branchName.validate('type', str)

		branchAdd1 = v.required('branchAdd1')
		branchAdd1.validate('type', str)

		branchAdd2 = v.required('branchAdd2')
		branchAdd2.validate('type', str)

		branchState = v.required('branchState')
		branchState.validate('type', str)

		branchCity = v.required('branchCity')
		branchCity.validate('type', str)

		branchPin = v.required('branchPin')
		branchPin.validate('type', str)

		return v.errors

	#

	def _branchManagementFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')

		errors = self._branchManagementFormValidate(formData)

		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#
		with self.server.session() as serverSession:
			primaryOrganizationId = serverSession['primaryOrganizationId']

		with dataUtils.worker() as worker:
			details = formData
			details['parentOrgId'] = primaryOrganizationId 

			newBranch = worker.createBranch(details)




		# this part add data to Info Table
		# TODO Nitin will create a function for adding data to info table

		return self.jsonSuccess('Branch created',errors='No')

	#

	numOfObj = 10

	def _branchData(self, requestPath):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData = ['S.No1', 'Organization Name', 'Category', 'Addrs_line1', 'Addrs_line2',
					 'City', 'State', 'Pincode','BranchId']
		pageNo = int((cherrypy.request.params).get('pageNo', '1'))
		if 'pageNo' not in cherrypy.request.params:
			self.numOfObj = 10
		if 'rp' in cherrypy.request.params and 'pageNo' in cherrypy.request.params:
			self.numOfObj = int(cherrypy.request.params['rp'])
		with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				sendData = dbHelp.getBranchDataForFlexiGrid(pageNo, session, db,
																  serverSession['primaryOrganizationId'], id,
																  self.numOfObj)

		actuallySendData = {
		'classData': classData,
		'sendData': sendData,

		}

		return self.jsonSuccess(actuallySendData)

	#

	def _editBranchData(self,requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		# TODO:Checking errors in the database
		# errors = self._userManagementFormValidate(formData)
		return self.addOrEditBranchToDatabase('edit', formData)
	#

	def addOrEditBranchToDatabase(self, query, formData):
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')
		details = dict()
		with self.server.session() as serverSession:
			orgId = serverSession['primaryOrganizationId']
		with dataUtils.worker() as worker:
			if(query=='edit'):
				db.branch.updateFromParams({
				'id':formData['id']

				},**{'name':formData['branchName'], 'parent_id':orgId})

				db.Info.updateFromParams({
				'entity_id':formData['id'],'preference':0,'type':db.Info.Type.branchAddLine1.value
				},**{'data':formData['branchAdd1']})

				db.Info.updateFromParams({
				'entity_id':formData['id'],'preference':0,'type':db.Info.Type.branchAddLine2.value
				},**{'data':formData['branchAdd2']})

				db.Info.updateFromParams({
				'entity_id':formData['id'],'preference':0,'type':db.Info.Type.branchCity.value
				},**{'data':formData['branchCity']})

				db.Info.updateFromParams({
				'entity_id':formData['id'],'preference':0,'type':db.Info.Type.branchPin.value
				},**{'data':formData['branchPin']})

				db.Info.updateFromParams({
				'entity_id':formData['id'],'preference':0,'type': db.Info.Type.branchState.value
				},**{'data':formData['branchState']})

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

				return self.jsonSuccess('Branch Edited',errors='No')

		return self.jsonFailure('Error')
	#