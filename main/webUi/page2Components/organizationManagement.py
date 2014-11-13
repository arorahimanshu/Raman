from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
from sqlalchemy import func
import json
import datetime


class Organization(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'organizationManagementForm':
			return self._organizationManagementForm(requestPath)
		elif nextPart == 'organizationManagementFormAction':
			return self._organizationManagementFormAction(requestPath)
		elif nextPart == 'organizationData':
			return self._organizationData(requestPath)
		elif nextPart == 'editOrganization':
			return self._editOrganizationData(requestPath)
		elif nextPart == 'delOrganization':
			return self.delOrganization()
		#

	#

	def delOrganization(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')

		db.Info.delete({
			'entity_id':formData['id'],
		})
		db.Facet_Role.delete({
			'organization_id':formData['id']
		})
		db.Facet.delete({
			'organization_id':formData['id']
		})
		db.Permission.delete({
			'organization_id':formData['id']
		})
		db.Permission_Role.delete({
			'organization_id':formData['id']
		})
		db.Role.delete({
			'organization_id':formData['id']
		})
		db.Organization.delete({
			'id':formData['id']
		})
		db.Entity.delete({
			'id':formData['id']
		})


	def _organizationManagementForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'organizationManagement.css')
		)
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'organizationManagement.js')
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
		'organizationManagementFormAction': requestPath.allPrevious(
			ignore=1,
			additional=['organizationManagementFormAction'],
		)


		})
		with self.server.session() as session:
			self.userId = session['userId']

		classData = ['S.No', 'Organization Name', 'Category', 'Addrs_line1', 'Addrs_line2',
		             'City', 'State', 'Pincode','OrgID']
		category = [{'value': 1, 'display': 'cat1'}, {'value': 2, 'display': 'cat2'}]
		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('organizationManagement.html', classdata=classData, userId=self.userId,
			                         category=category),
			newTabTitle='New Organization',
			url=requestPath.allPrevious(),
		)

	#

	def _organizationManagementFormValidate(self, formData):
		db = self.app.component('dbManager')
		v = Validator(formData)

		name = v.required('name')
		name.validate('type', str)

		category=v.required('category')
		category.validate('type',str)

		address1 = v.required('address1')
		address1.validate('type', str)

		address2 = v.required('address2')
		address2.validate('type', str)

		state = v.required('state')
		state.validate('type', str)

		city = v.required('city')
		city.validate('type', str)

		pincode = v.required('pincode')
		pincode.validate('type', str)

		return v.errors

	#

	def _organizationManagementFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')

		errors = self._organizationManagementFormValidate(formData)

		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		with dataUtils.worker() as worker:
			details = {
			'name': formData['name']
			}

			newOrganization = worker.createOrganization(details)

			address = formData['address1'] + ";" + formData['address2'] + ";" + formData['state'] + ";" + formData[
			'city'] + ";" + formData['pincode']

			worker.session.add(db.Info.newFromParams({
			'id': db.Entity.newUuid(),
			'entity_id': newOrganization.id,
			'enumType': db.Info.Type.Address,
			'preference': 0,
			'data': address,
			}))
		#
		return self.jsonSuccess('Organization created')

	#

	numOfObj = 10

	def _organizationData(self, requestPath):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData = ['S.No', 'Organization Name', 'Category', 'Addrs_line1', 'Addrs_line2',
		             'City', 'State', 'Pincode','OrgID']
		pageNo = int((cherrypy.request.params).get('pageNo', '1'))
		if 'pageNo' not in cherrypy.request.params:
			self.numOfObj = 10
		if 'rp' in cherrypy.request.params and 'pageNo' in cherrypy.request.params:
			self.numOfObj = int(cherrypy.request.params['rp'])
		with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				sendData = dbHelp.getOrganizationDataForFlexiGrid(pageNo, session, db,
				                                                  serverSession['primaryOrganizationId'], id,
				                                                  self.numOfObj)

		actuallySendData = {
		'classData': classData,
		'sendData': sendData,

		}

		return self.jsonSuccess(actuallySendData)

	#

	def _editOrganizationData(self,requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		# TODO:Checking errors in the database
		# errors = self._userManagementFormValidate(formData)
		return self.addOrEditOrganizationToDatabase('edit', formData)
	#

	def addOrEditOrganizationToDatabase(self, query, formData):
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')
		details = dict()
		print(formData)

		with dataUtils.worker() as worker:
			if(query=='edit'):
				db.Organization.updateFromParams({
				'id':formData['id']

				},**{'name':formData['name']})


				address= formData['address1'] + ";" + formData['address2'] + ";" + formData['state'] + ";" + formData[
					'city'] + ";" + formData['pincode']

				db.Info.updateFromParams({
					'entity_id':formData['id']

				},**{'data':address
				})

				return self.jsonSuccess('user information edited')

		return self.jsonFailure('Error')
	#
