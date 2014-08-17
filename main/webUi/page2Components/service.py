from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Service(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)
		self._setupFieldInfo()

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newServiceForm':
			return self._newServiceForm(requestPath)
		elif nextPart == 'newServiceFormAction':
			return self._newServiceFormAction(requestPath)
		#

	#

	def _setupFieldInfo(self):
		db = self.app.component('dbManager')
		endDiff = 2
		infoLength = db.Info.columnType('data').length - endDiff

		self._clientFieldInfo = {
		'productName': {'maxLength': infoLength},
		'productType': {'maxLength': infoLength},
		'unitType': {'maxLength': infoLength},
		'baseCostPerUnit': {'maxLength': infoLength},
		'baseUnit': {'exactLength': infoLength},
		'capacity': {'maxLength': infoLength},
		'status': {'maxLength': infoLength},

		}

	#

	def _newServiceForm(self, requestPath):
		proxy, params = self.newProxy()

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'newServiceForm.css')
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'newServiceForm.js')
		)

		params['config'].update({
		'newServiceFormActionUrl': requestPath.allPrevious(
			ignore=1,
			additional=['newServiceFormAction'],
		),

		'fieldInfo': self._clientFieldInfo,
		})

		# TODO: Get these list from database
		productType = [{'value': 1, 'display': 'GymFloor'}, {'value': 2, 'display': 'Spa'}]
		unitType = [{'value': 1, 'display': 'Days'}, {'value': 2, 'display': 'Months'}]
		# baseUnit=[{'value':1,'display':'NA'},{'value':2,'display':'x Hours'}]

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('newServiceForm.html', productTypeList=productType, unitTypeList=unitType),
			newTabTitle='New Service',
			url=requestPath.allPrevious(),
		)


	#


	def _newServiceFormValidate(self, formData):
		db = self.app.component('dbManager')
		v = Validator(formData)

		# TODO : replace flags with just above statements filling correct data
		# for eg : flag for userexist will be set to true if usertocheck exists in db
		#flag=self.app.component('dbHelper').checkExists('User','username','usertocheck')

		productName = v.required('productName')
		#flag=self.app.component('dbHelper').checkExists('entityname in dbmanager','key',formData['productName'])
		flag = True
		productName.validate('and',
		                     ('maxLength', self._clientFieldInfo['productName']['maxLength']),
		                     ('custom', lambda x: 'Product Name doesn\'t exists' if not flag else None)
		)

		productType = v.required('productType')
		#flag=self.app.component('dbHelper').checkExists('entityname in dbmanager','key',formData['productType'])
		flag = True
		productType.validate('and',
		                     ('type', str),
		                     ('custom', lambda x: 'Product Type doesn\'t exists' if not flag else None))

		unitType = v.required('unitType')
		#flag=self.app.component('dbHelper').checkExists('entityname in dbmanager','key',formData['unitType'])
		flag = True
		unitType.validate('and',
		                  ('type', str),
		                  ('custom', lambda x: 'Unit Type doesn\'t exists' if not flag else None))

		baseCost = v.required('baseCost')
		#flag=self.app.component('dbHelper').checkExists('entityname in dbmanager','key',formData['baseCost'])
		flag = True
		baseCost.validate('and',
		                  ('type', int),
		                  ('custom', lambda x: 'Base cost doesn\'t exists' if not flag else None))

		baseUnitPerSitting = v.required('baseUnit')
		baseUnitPerSitting.validate('type', int)

		capacity = v.required('capacity')
		capacity.validate('type', int)

		status = v.required('status')
		status.validate('type', str)

		canSingle = v.required('canSingle')
		canSingle.validate('type', bool)

		showOnWebSite = v.required('showOnWebsite')
		showOnWebSite.validate('type', bool)

		print(v.errors)
		return v.errors

	#

	def _newServiceFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		print(formData)
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')

		# TODO: check if user has service creation permission
		# userManager = self.app.component ('userManager')
		# with self.server.session () as session :
		# username = session['username']
		#  uid = session['uid']
		# #
		# worker = userManager.worker (username, uid).organizationWorker (
		#  formData['organizationId']
		# )
		# worker.assertPermission (db.Permissions.CreateUser)

		errors = self._newServiceFormValidate(formData)

		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		#TODO : enter service data into db

		return self.jsonSuccess('Service Created')
		#
		#
		#
		#