from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
from sqlalchemy import func
import json
import datetime
from mako.template import Template


class PaymentReceipt(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)
		self._setupFieldInfo()

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'paymentReceiptForm':
			return self.paymentReceiptForm(requestPath)
		elif nextPart == 'paymentReceiptFormActionUrl':
			return self._paymentReceiptFormAction(requestPath)
		elif nextPart == 'paymentReceiptFormActionFormLoad':
			return self._paymentReceiptFormActionLoad(requestPath)
		elif nextPart == 'paymentReceiptDelAction':
			return self.paymentReceiptDelAction()

	#

	def paymentReceiptDelAction(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')

		i=db.PaymentDetail.delete({
			'payment_id':formData['paymentId'],
			'preference': db.PaymentDetail.Method[formData['Mode']].value
		})
		if(i==1):
			db.Payment.delete({
			'id':formData['paymentId']
		})






	def _setupFieldInfo(self):
		db = self.app.component('dbManager')

		self._clientFieldInfo = {
		'bankname': {'maxLength': 20},
		'bankloc': {'maxLength': 20},
		'id': {'maxLength': 32},
		'name': {'maxLength': 32},
		}

	#
	#numOfObj = 10
	def _paymentReceiptFormActionLoad(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		dbHelp = self.app.component('dbHelper')
		classData =['S.No','paymentId','UserName','Date','currency','Mode','Amount']
		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		self.numOfObj = int(formData.get('rp', '10'))

		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])
		with self.server.session() as serverSession:
			with db.session() as session:
				sendData = dbHelp.getPaymentDataForFlexiGrid(pageNo,session,db,serverSession['userId'],formData['toDate'],formData['fromDate'],self.numOfObj)

		actuallySendData = {
			'classData': classData,
		    'sendData':sendData
		}
		return self.jsonSuccess(actuallySendData)


	#

	def paymentReceiptForm(self, requestPath):
		proxy, params = self.newProxy()


		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'paymentReceiptForm.js')
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
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'design.css')
		)

		params['config'].update({
		'paymentReceiptFormActionUrl': requestPath.allPrevious(
			ignore=1,
			additional=['paymentReceiptFormAction'],
		),

		'fieldInfo': self._clientFieldInfo,
		})
		classData = ['S.No', 'paymentId', 'UserName', 'Date', 'currency', 'Mode', 'Amount']
		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('paymentReceiptForm.html',classdata=classData),
			newTabTitle='payment details',
			url=requestPath.allPrevious(),
		)

	#

	def _paymentReceiptValidate(self, formData):
		db = self.app.component ('dbManager')
		v = Validator (formData)

		def idExist (data) :
			with db.session () as session :
				id = session.query (db.Payment).filter (db.Payment.id == data).scalar ()
			#

			if id:
				return 'Payment Failed..'
			#
		id = v.required ('id')
		id.validate ('and',
			('type', str),
			('custom', idExist),
		)

		name = v.required ('payeeName')
		name.validate ('and',
			('type', str),
			('maxLength', self._clientFieldInfo['name']['maxLength']),
		)



		date = v.required ('date')
		date.validate ('isDate')

		payment = v.required('payment')
		payment.validate('or',
						('inclusion',{'cash':['amount']}),
						('inclusion',{'cheque':['amount','bname','bloc']}),
						('inclusion',{'online':['amount','bname','bloc']}),
						)

		with db.session() as session:
			payeeId = session.query(db.User).filter(db.User.username==formData['payeeName']).all()
		if(len(payeeId) > 0):
			pass
		#	payeeId = payeeId.entity_id
		else:
			if (v.errors) :
				v.errors['payeeName']='No such username'
			else:
				return {'payeeName':'No such username'}


		return v.errors

	def _paymentReceiptFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		dataUtils = self.app.component('dataUtils')
		db = self.app.component('dbManager')
		#TODO: check permissions
		# userManager = self.app.component ('userManager')
		# with self.server.session () as session :
		# 	username = session['username']
		# 	uid = session['uid']
		# #
		# worker = userManager.worker (username, uid).organizationWorker (
		# 	formData['organizationId']
		# )
		# worker.assertPermission (db.Permissions.CreateUser)

		errors = self._paymentReceiptValidate(formData)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		with db.session() as datasession:
			details = {
			'id': formData['id'],
			'name': formData['payeeName'],
			'date': datetime.date(*formData['date'])
			}
			amount = 0

			queryList = []

			if 'payment' in formData:

				if 'cash' in formData['payment']:
					amount += int(formData['payment']['cash']['amount'])
					paymentDetail = db.PaymentDetail.newFromParams({
					'id': db.Entity.newUuid(),
					'payment_id': details['id'],
					'type': db.PaymentDetail.Type.Amount.value,
					'preference': db.PaymentDetail.Method.Cash.value,
					'data': formData['payment']['cash']['amount']
					})
					queryList.append(paymentDetail)

				if 'cheque' in formData['payment']:
					amount += int(formData['payment']['cheque']['amount'])

					paymentDetail = db.PaymentDetail.newFromParams({
					'id': db.Entity.newUuid(),
					'payment_id': details['id'],
					'type': db.PaymentDetail.Type.Amount.value,
					'preference': db.PaymentDetail.Method.Cheque.value,
					'data': formData['payment']['cheque']['amount']
					})
					queryList.append(paymentDetail)

					paymentDetail = db.PaymentDetail.newFromParams({
					'id': db.Entity.newUuid(),
					'payment_id': details['id'],
					'type': db.PaymentDetail.Type.BankName.value,
					'preference': db.PaymentDetail.Method.Cheque.value,
					'data': formData['payment']['cheque']['bname']
					})
					queryList.append(paymentDetail)

					paymentDetail = db.PaymentDetail.newFromParams({
					'id': db.Entity.newUuid(),
					'payment_id': details['id'],
					'type': db.PaymentDetail.Type.BranchName.value,
					'preference': db.PaymentDetail.Method.Cheque.value,
					'data': formData['payment']['cheque']['bloc']
					})
					queryList.append(paymentDetail)
				if 'online' in formData['payment']:
					amount += int(formData['payment']['online']['amount'])

					paymentDetail = db.PaymentDetail.newFromParams({
					'id': db.Entity.newUuid(),
					'payment_id': details['id'],
					'type': db.PaymentDetail.Type.Amount.value,
					'preference': db.PaymentDetail.Method.Online.value,
					'data': formData['payment']['online']['amount']
					})
					queryList.append(paymentDetail)

					paymentDetail = db.PaymentDetail.newFromParams({
					'id': db.Entity.newUuid(),
					'payment_id': details['id'],
					'type': db.PaymentDetail.Type.BankName.value,
					'preference': db.PaymentDetail.Method.Online.value,
					'data': formData['payment']['online']['bname']
					})
					queryList.append(paymentDetail)

					paymentDetail = db.PaymentDetail.newFromParams({
					'id': db.Entity.newUuid(),
					'payment_id': details['id'],
					'type': db.PaymentDetail.Type.BranchName.value,
					'preference': db.PaymentDetail.Method.Online.value,
					'data': formData['payment']['online']['bloc']
					})
					queryList.append(paymentDetail)

			payeeId = datasession.query(db.User).filter(db.User.username == formData['payeeName']).scalar()
			payeeId = payeeId.entity_id
			with self.server.session() as session:
				payementrec = db.Payment.newFromParams({
				'id': details['id'],
				'payer_id': payeeId,
				'payee_id': session['userId'],
				'amount': amount,
				'when': datetime.date(*formData['date']),
				'currency': 'rs'
				})
				datasession.add(payementrec)
			for item in queryList:
				datasession.add(item)

		return self.jsonSuccess('Payment Success!!!')
		#
		#