from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json
from sqlalchemy import and_

class Poi(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newPoiForm':
			return self._newPoiForm(requestPath)
		elif nextPart == 'newPoiFormAction':
			return self._newPoiFormAction(requestPath)
		elif nextPart == 'getPoiData':
			return self.getPoiData(requestPath)
		elif nextPart == 'generateReport':
			return self.generateReport(requestPath)
		elif nextPart == 'delPoi':
			return self.delPoi()
		#

	#

	def generateReport(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbHelper')
		# TODO: Himanshu When done with branch of organization just pass the company name and branch too here

		pageNo = int(formData.get('pageNo', '1'))
		if 'pageNo' not in formData:
			self.numOfObj = 10
		if 'rp' in formData and 'pageNo' in formData:
			self.numOfObj = int(formData['rp'])

		with self.server.session() as session:
			#poidata = db.returnPoiReport(session['username'], formData['reportAddressCategory'],self.numOfObj,pageNo)
			poidata = db.returnPoiReport(session['username'],self.numOfObj,pageNo)

		return self.jsonSuccess(poidata)

	def delPoi(self):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbManager')
		dataUtils = self.app.component('dataUtils')

		with db.session() as session:
			vehicleData = session.query(db.Poi_vehicle).filter(db.Poi_vehicle.Poi_Id == formData['poiId'])
			if vehicleData.count() == 1:
				db.Poi_vehicle.delete({
					'Poi_Id':formData['poiId']
				})
				db.Gps_Poi_Data.delete({
					'Poi_Id':formData['poiId']
				})
				db.Gps_Poi_Info.delete({
					'Poi_Id':formData['poiId']
				})


			elif vehicleData.count() > 1:
				query = session.query(db.Poi_vehicle).filter(and_(db.Poi_vehicle.Vehicle_Id == formData['vehicleId'],
																  db.Poi_vehicle.Poi_Id == formData['poiId']))
				session.delete(query.one())

			session.commit()
			#db.Poi_vehicle.delete({
			#	'poi_id':formData['id']
			#	})
			#db.Gps_Poi_Info.delete({
			#	'Poi_Id':formData['id']
			#	})
		return self.jsonSuccess('Poi Deleted')
		#

	def getPoiData(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		db = self.app.component('dbHelper')
		# todo:db query for poi list
		# return self.jsonSuccess(db.returnPoiList(self.userId, formData['userEnteredString']['vehicle']))
		return self.jsonSuccess("done")


	def _newPoiForm(self, requestPath):
		primaryOrganizationId = None
		with self.server.session() as session:
			self.username = session['username']
			self.userId = session['userId']
			primaryOrganizationId = session['primaryOrganizationId']
		#
		proxy, params = self.newProxy()
		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'poiForm.css')
		)
		params['externalJs'].append('http://maps.googleapis.com/maps/api/js?v=3.exp')
		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'poiForm.js')
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

		db = self.app.component('dbHelper')
		vehicleList = db.returnVehicleList(self.userId)

		addresscatfile = open('./dataModel/addCategory.json')
		addressList = json.load(addresscatfile)

		orgList = db.returnOrgList(primaryOrganizationId)
		branchList2 = []
		companyList2 = orgList
		vehicleGroupList2 = []
		vehicleList2 = []
		for org in orgList:
			#if org['value'] != primaryOrganizationId:
			branchList = db.returnBranchListForOrg(org['value'])
			branchList2.extend(branchList)
			for branch in branchList:
				vehicleGroupList = db.returnVehicleGroupListForBranch(branch['value'])
				vehicleGroupList2.extend(vehicleGroupList)
				for vehicleGroup in vehicleGroupList:
					vehicleList = db.returnVehicleListForVehicleGroup(vehicleGroup['value'])
					vehicleList2.extend(vehicleList)
		self.classData = [ 'SNo.','Id', 'Poi Name', 'Address Category','Vehicle Name','Vehicle Reg No','Vehicle Id', 'Street', 'City', 'State']

		# Vehicle selector Block Starts
		vehicleStructure = []
		dataUtils = self.app.component('dataUtils')
		with self.server.session() as serverSession:
			primaryOrganizationId = serverSession['primaryOrganizationId']

		with dataUtils.worker() as worker:
				vehicleStructure= worker.getVehicleTree(primaryOrganizationId)

		# Vehicle selector Block Ends

		return self._renderWithTabs(
			proxy, params,
			bodyContent=proxy.render('poiForm.html', classdata=self.classData, addressList=addressList,
									 branchList=branchList2, companyList=companyList2,
				additionalOptions = [
					proxy.render ('vehicleSelector.html',
						branches = vehicleStructure[0],
						vehicleGroups = vehicleStructure[1],
						vehicles = vehicleStructure[2],
					)
				]
			),
			newTabTitle='Add Poi',
			url=requestPath.allPrevious(),
		)
	#




	def _newPoiFormValidate(self, formData):
		pass


	def _newPoiFormAction(self, requestPath):
		formData = json.loads(cherrypy.request.params['formData'])
		print(formData)
		errors = self._newPoiFormValidate(formData)
		if errors:
			return self.jsonFailure('validation failed', errors=errors)
		#

		db = self.app.component('dbManager')
		vehicleIds=formData['vehicleList']

		with db.session() as session:

				entity = db.Entity.newUnique()
				session.add(entity)

				poi_data = db.Gps_Poi_Info.newFromParams({
					'Poi_Id': entity.id,
					'User_name': self.username,
					'Poi_Name': formData['poiplaceName'],
					'Poi_Latitude': formData['latitude'],
					'Poi_Longitude': formData['longitude'],
					'Category': formData['addressCategory']
				})
				session.add(poi_data)
				session.commit()


				address = formData['street'] + ";" + formData['state'] + ";" + formData['city']

				session.add(db.Info.newFromParams({
					'id': db.Entity.newUuid(),
					'entity_id': entity.id,
					'enumType': db.Info.Type.Address,
					'preference': 0,
					'data': address,
				}))

				for vid in vehicleIds:
					maping_data = db.Poi_vehicle.newFromParams({
						'Poi_Id':entity.id,
						'Vehicle_Id':vid
					})
					session.add(maping_data)

		return self.jsonSuccess('Poi Successfully Saved')


	#
#