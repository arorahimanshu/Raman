from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
from sqlalchemy import func
import json
import datetime
import os
import traceback
from sqlalchemy import and_

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
		dataUtils = self.app.component('dataUtils')
		worker = dataUtils.worker()

		with db.session () as session:

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


			for data in session.query(db.branch).filter_by(parent_id = formData['id']).all():

				worker.delBranchCascade(data['id'])

			db.Info.delete({
				'entity_id':formData['id'],
			})
			db.Organization.delete({
				'id':formData['id']
			})
			db.Entity.delete({
				'id':formData['id']
			})

		return self.jsonSuccess('Organization deleted',errors='No')


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
		name.validate('type',str )

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
		#formData = json.loads(cherrypy.request.params['formData'])
		formData = cherrypy.request.params
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

			try:
				readHandle = formData['image'].file
				chunkSize = 1<<13 # 2^13
				with db.session () as session :
					newFile = db.logo ()
					newFile.id = db.Entity.newUuid ()
					newFile.fileName = formData['image'].filename
					extension = newFile.fileName[-4:].lower ()
					newFile.extension = extension
					if extension not in ['.jpg','.jpeg','.png']:
						self.jsonFailure('Incompatible Extension')
					session.add (newFile)

					with open (os.path.join (AppConfig.DbAssets, newFile.id + extension),'wb' ) as writeHandle:
						while True :
							data = readHandle.read (chunkSize)
							writeHandle.write (data)
							if not data :
								break
							#
						#
					#
					worker.session.add(db.Info.newFromParams({
						'id': db.Entity.newUuid(),
						'entity_id': newOrganization.id,
						'enumType': db.Info.Type.Image,
						'preference': 0,
						'data': newFile.id,
					}))
			except:
				traceback.print_exc ()
				return self.jsonFailure()
		#
		# iF ERROR is Yes then page will not reload ... and if No the page will reload
		return self.jsonSuccess('Organization created',errors='No')


	#

	numOfObj = 10

	def _organizationData(self, requestPath):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData = ['S.No', 'Organization Name', 'Category', 'Addrs_line1', 'Addrs_line2',
		             'City', 'State', 'Pincode','OrgID']
		formData = json.loads(cherrypy.request.params['formData'])
		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])
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
		#formData = json.loads(cherrypy.request.params['formData'])
		formData = cherrypy.request.params
		# TODO:Checking errors in the database
		# errors = self._userManagementFormValidate(formData)
		return self.addOrEditOrganizationToDatabase('edit', formData)
	#

	def addOrEditOrganizationToDatabase(self, query, formData):
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')
		details = dict()


		with dataUtils.worker() as worker:
			if(query=='edit'):
				db.Organization.updateFromParams({
				'id':formData['id']

				},**{'name':formData['name']})


				address= formData['address1'] + ";" + formData['address2'] + ";" + formData['state'] + ";" + formData[
					'city'] + ";" + formData['pincode']

				db.Info.updateFromParams({
					'entity_id':formData['id'],
					'type':db.Info.Type.Address.value
				},**{'data':address
				})

				try:
					readHandle = formData['image'].file
					chunkSize = 1<<13 # 2^13
					with db.session () as session :
						newFile = db.logo ()
						newFile.id = db.Entity.newUuid ()
						newFile.fileName = formData['image'].filename
						extension = newFile.fileName[-4:].lower ()
						newFile.extension = extension
						if extension not in ['.jpg','.jpeg','.png']:
							self.jsonFailure('Incompatible Extension')
						session.add (newFile)

						with open (os.path.join (AppConfig.DbAssets, newFile.id + extension),'wb' ) as writeHandle:
							while True :
								data = readHandle.read (chunkSize)
								writeHandle.write (data)
								if not data :
									break
								#
							#
						#

						oldFileQuery = session.query(db.Info).filter(and_(db.Info.entity_id==formData['id'], db.Info.type==db.Info.Type.Image.value))
						try:
							oldInfoRow = oldFileQuery.one()
							oldImageId = oldInfoRow.data
							oldLogoRow = session.query(db.logo).filter(db.logo.id==oldImageId).one()
							oldImageName = oldImageId + oldLogoRow.extension
							session.delete(oldLogoRow)
							session.delete(oldInfoRow)
							os.remove(AppConfig.DbAssets, oldImageName)
						except:
							traceback.print_exc()
						worker.session.add(db.Info.newFromParams({
							'id': db.Entity.newUuid(),
							'entity_id': formData['id'],
							'enumType': db.Info.Type.Image,
							'preference': 0,
							'data': newFile.id,
						}))


				except:
					traceback.print_exc ()
					return self.jsonFailure()

				return self.jsonSuccess('Organization Edited',errors='No')

		return self.jsonFailure('Error')
	#
