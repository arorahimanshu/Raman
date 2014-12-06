from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator

import cherrypy
from sqlalchemy import func
from passlib.apps import custom_app_context as pwdContext
import json
import datetime


class UserManagement (Page2Component) :
	def __init__ (self, parent, **kwargs) :
		Page2Component.__init__ (self, parent, **kwargs)
		self._setupFieldInfo ()
	#

	def handler (self, nextPart, requestPath) :
		if nextPart == 'userManagementForm' :
			return self._userManagementForm (requestPath)
		elif nextPart == 'userManagementFormAction' :
			return self._userManagementFormAction (requestPath)
		elif nextPart =='generateEmployeeData':
			return self._employeeData(requestPath)
		elif nextPart == 'editEmployeeFormAction':
			return self._editEmployeeData(requestPath)
		elif nextPart == 'delEmployeeFormAction':
			return self.delEmployeeFormAction()
		#
	#

	def delEmployeeFormAction(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')

		db.Facet_Role.delete({
			'username':formData['name'],
		})
		db.Facet.delete({
			'username':formData['name'],
		})
		db.Info.delete({
			'entity_id':formData['id'],
		})
		db.Person.delete({
			'id':formData['id'],
		})
		db.User.delete({
			'entity_id':formData['id'],
		})


	def _setupFieldInfo (self) :
		db = self.app.component ('dbManager')
		endDiff = 2
		infoLength = db.Info.columnType ('data').length - endDiff

		self._clientFieldInfo = {
			'name' : {'maxLength': infoLength},
			'address' : {'maxLength' : infoLength},
			'email' : {'maxLength' : infoLength},
			'mobile' : {'maxLength' : 10,'minLength':10},
			'personId' : {'exactLength' : db.Entity.columnType ('id').length},
			'username' : {'maxLength' : db.User.columnType ('username').length - endDiff},
		}
	#


	def _editEmployeeData(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		# TODO:Checking errors in the database
		#errors = self._userManagementFormValidate(formData)
		return self.addOrEditUserToDatabase('edit', formData)

	def _userManagementForm (self, requestPath) :
		proxy, params = self.newProxy ()

		params['externalCss'].append (
			self.server.appUrl ('etc', 'page2', 'specific', 'css', 'userManagementForm.css')
		)
		params['externalCss'].append (
			self.server.appUrl ('etc', 'page2', 'specific', 'css', 'design.css')
		)
		params['externalJs'].append (
			self.server.appUrl ('etc', 'page2', 'specific', 'js', 'userManagementForm.js')
		)
		params['externalJs'].append (
			self.server.appUrl ('etc', 'page2', 'specific', 'js', 'flexiBasic.js')
		)
		params['externalJs'].append (
			self.server.appUrl ('etc', 'page2', 'generic', 'js', 'flexigrid.js')
		)
		params['externalJs'].append (
			self.server.appUrl ('etc', 'page2', 'generic', 'js', 'flexigrid.pack.js')
		)
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'css', 'flexigrid.pack.css')
		)
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'css', 'flexigrid.css')
		)

		params['config'].update ({
			'userManagementFormAction' : requestPath.allPrevious (
				ignore = 1,
				additional = ['userManagementFormAction'],
			),

			'fieldInfo' : self._clientFieldInfo,
		})
		db=self.app.component('dbHelper')
		roleList = db.returnRoleList(cherrypy.request.fitxData['organizationId'])
		classData =['S.No','Uid','Name','UserName','DOB','email-address','Phone No.','Address']
		return self._renderWithTabs (
			proxy, params,
			bodyContent = proxy.render ('userManagementForm.html',roleList=roleList,classdata = classData),
			newTabTitle = 'New User',
			url = requestPath.allPrevious (),
		)
	#

	def _userManagementFormValidate (self, formData) :
		db = self.app.component ('dbManager')
		v = Validator (formData)

		paymentId = v.required ('personDataType')
		paymentId.validate ('in', ['byDetails', 'byId'])

		def userExists (data) :
			with db.session () as session :
				numUsers = session.query (func.count ('*')).select_from (db.User).filter (
					db.User.username == data
				).scalar ()
			#

			if numUsers > 0 :
				return 'username already taken'
			#
		#

		username = v.required ('username')
		username.validate ('and',
			('maxLength', self._clientFieldInfo['username']['maxLength']),
			('custom', userExists),
		)

		password = v.required ('password')
		password.validate ('type', str)

		name = v.optional ('name')
		name.validate ('and',
			('type', str),
			('maxLength', self._clientFieldInfo['name']['maxLength'])
		)

		address = v.optional ('address')
		address.validate ('and',
			('type', str),
			('maxLength', self._clientFieldInfo['address']['maxLength'])
		)

		email = v.optional ('email')
		email.validate ('and',
			('type', str),
			('maxLength', self._clientFieldInfo['email']['maxLength'])
		)

		mobile = v.optional ('mobile')
		mobile.validate ('and',
			('type', str),
			('maxLength', self._clientFieldInfo['mobile']['maxLength'])
		)

		dob = v.optional ('dob')
		dob.validate ('isDate')

		if formData['personDataType'] == 'byId' :

			def entityExists (data) :
				with db.session () as session :
					num = session.query (
						func.count ('*')
					).select_from (
						db.Entity
					).filter (
						db.Entity.id == data
					).scalar ()
				#

				if num < 1 :
					return 'doesnt exist'
				#
			#

			personId = v.required ('personId')
			personId.validate ('and',
				('type', str),
				('exactLength', self._clientFieldInfo['personId']['exactLength']),
				('custom', entityExists),
			)
		#

		return v.errors
	#

	def _userManagementFormAction (self, requestPath) :
		formData = json.loads (cherrypy.request.params['formData'])
		dataUtils = self.app.component ('dataUtils')
		db = self.app.component ('dbManager')

		userManager = self.app.component ('userManager')
		with self.server.session () as session :
			username = session['username']
			uid = session['uid']
		#
		worker = userManager.worker (username, uid).organizationWorker (
			formData['organizationId']
		)
		worker.assertPermission (db.Permissions.ManageUser)

		errors = self._userManagementFormValidate (formData)

		if errors :
			return self.jsonFailure ('validation failed', errors = errors)
		#

		with dataUtils.worker () as worker :
			if formData['personDataType'] == 'byDetails' :
				details = {
					'name' : formData.get ('name', None),
					'sex' : db.Person.Sex.Female if formData.get ('sex', 'male') else db.Person.Sex.Male
				}

				if 'dob' in formData :
					details['dob'] = datetime.date (*formData['dob'])
				#

				if 'email' in formData :
					details['emails'] = [formData['email']]
				#

				if 'address' in formData :
					details['addresses'] = [formData['address']]
				#

				if 'mobile' in formData :
					details['mobiles'] = [formData['mobile']]
				#

				newPerson = worker.createPerson (details)
				personId = newPerson.id
			else :
				personId = formData['personId']
			#

			newUser = worker.createUser ({
				'username' : formData['username'],
				'password' : formData['password'],
				'entityId' : newPerson.id,
			})

			newFacet = worker.createFacet ({
				'username' : newUser.username,
				'organizationId' : formData['organizationId'],
			})

			for role in formData['roles'] :
				newFacetRole = worker.assignFacetRole({
					'roleName' : role,
					'username' :  newUser.username,
					'organizationId' : formData['organizationId']
				})


		#
		return self.jsonSuccess ('User Created')
	#


	def _employeeData(self,requestPath):
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData =['S.No','Name','UserName','DOB','email-address','Phone No.','Address']
		#todo:remove print
		formData = json.loads(cherrypy.request.params['formData'])
		print(formData)
		pageNo = int(formData.get('pageNo','1'))
		numOfObj = int(formData.get('rp','10'))
		with self.server.session() as serverSession:
			with db.session() as session:
				id = serverSession['userId']
				sendData = dbHelp.getEmployeeDataForFlexiGrid(pageNo,session,db,serverSession['primaryOrganizationId'],id,numOfObj)

		actuallySendData = {
			'classData': classData,
		    'sendData':sendData
		}
		return self.jsonSuccess(actuallySendData)
	#

	def addOrEditUserToDatabase(self,query,formData):
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')
		details = dict()
		newPerson = None
		with dataUtils.worker() as worker:
			if formData['personDataType'] == 'byDetails':
				details = {
					'name': formData.get('name', None),
					'sex': 1 if formData['sex']=='Male' else 2
				}

				if 'dob' in formData:
					details['dob'] = datetime.date(*formData['dob'])
				#

				if 'email' in formData:
					details['emails'] = [formData['email']]
				#

				if 'address' in formData:
					details['addresses'] = [formData['address']]
				#

				if 'mobile' in formData:
					details['mobiles'] = [formData['mobile']]
				#

				if query=='add':
					newPerson = worker.createPerson(details)
					personId = newPerson.id
			else:
				if query == 'add':
					personId = formData['personId']
			#
			if query=='add':
				newUser = worker.createUser({
					'username': formData['username'],
					'password': formData['password'],
					'entityId': newPerson.id,
				})

				newFacet = worker.createFacet({
					'username': newUser.username,
					'organizationId': formData['organizationId'],
				})

				newFacetRole = worker.assignFacetRole({
					'roleName': 'superuser',
					'username': newUser.username,
					'organizationId': formData['organizationId']
				})
				return self.jsonSuccess('user created')
			else:
				db = self.app.component('dbManager')
				db.User.updateFromParams({'entity_id':formData['id']},**{
					'password': pwdContext.encrypt(formData['password']),
				})
				db.Person.updateFromParams ({'id':formData['id']},**{
					'name' : details.get ('name', None),
					'dob' : details.get ('dob', details.get ('dateOfBirth', None)),
				    'sex':details['sex']
				})


				#

				for i, email in enumerate (details.get ('emails', [])) :
					db.Info.updateFromParams ({'entity_id':formData['id'],'type' : db.Info.Type.Email.value,},**{
						'preference' : i,
						'data' : email,
					})
				#

				for i, address in enumerate (details.get ('addresses', [])) :
					db.Info.updateFromParams ({'entity_id':formData['id'],'type' : db.Info.Type.Address.value},**{
						'preference' : i,
						'data' : address,
					})

				for i, mobile in enumerate (details.get ('mobiles', [])) :
					db.Info.updateFromParams ({'entity_id':formData['id'],'type' : db.Info.Type.Mobile.value},**{
						'preference' : 0,
						'data' : mobile,
					})
				return self.jsonSuccess('User Information Edited')



		#
#