from appConfig import AppConfig
from component import Component
from sqlalchemy import func
from sqlalchemy import and_
from utils import Validator
import datetime
import time
from sqlalchemy.sql.sqltypes import DateTime
from datetime import timedelta, datetime


class DbHelper(Component):

	def checkExists(self,table,key,data):
		"""
		:param table: Name of the Table from which data has to be queried
		:param key:  Name of the column from which data has to be matched
		:param data: Actual data to be matched
		:return: True if data is found else false
		"""

		db=self.app.component('dbManager')
		with db.session () as session :
				num = session.query (func.count ('*')).select_from (getattr(db,table)).filter (
					getattr(getattr(db,table),key) == data
				).scalar ()
		#

		if num > 0 :
			return True
		else:
			return False
		#
	#
	def returnClassData(self, className):
		db = self.app.component('dbManager')
		classDataList = []
		members = []
		table = getattr(db, className)
		return (table().get_dict())
	#
	def getPaymentDataForFlexiGrid(self,pageNo,session,db,userId,toDate,fromDate,numOfObj=10):

		attrNames =self.returnClassData('Payment')

		sessionQueryObj = session.query(db.Payment).filter(and_(db.Payment.payee_id == userId,db.Payment.when >=datetime(*fromDate),db.Payment.when <= datetime(*toDate)))
		count = 0
		dataSend = {
			'total':count,
		    'page':pageNo,
		    'rows':[]
		}
		rows = []
		i=(pageNo-1)*numOfObj + 1
		s = i
		for data in sessionQueryObj.slice((pageNo-1)*numOfObj,pageNo*numOfObj):
			id = data.id
			queryObj2 = session.query(db.PaymentDetail).filter(and_(db.PaymentDetail.payment_id == id,db.PaymentDetail.type == db.PaymentDetail.Type.Amount.value))
			for data2 in queryObj2.all():
				cell = {}
				cell['cell'] = []
				cell['cell'].append(i)
				for name in attrNames:
					if name == 'amount' or name == 'payee_id':
						continue
					if(name == 'payer_id'):
						cell['cell'].append(self.returnUserName(getattr(data,name)))
					else:
						cell['cell'].append(str(getattr(data,name)))
				cell['cell'].append(db.PaymentDetail.Method(int(data2.preference)).name)
				cell['cell'].append(data2.data)

				cell['id'] = i
				i+=1
				rows.append(cell)
		i = i - s
		dataSend['total'] = i
		dataSend['rows'] = rows
		return dataSend
	#
	def getDataForFlexiGrid(self,pageNo,sessionQueryObj,attrNames,numOfObj=10):
		#pageNo starts from 1
		i = 1
		rows = []
		for data in sessionQueryObj.all():
			cell = {}
			cell['cell'] = []
			for name in attrNames:
				cell['cell'].append(str(getattr(data,name)))
			cell['id'] = i
			i+=1
			rows.append(cell)
		return self.getSlicedData(rows,pageNo,numOfObj)
	#
	def returnUid(self, username):

		uid = ""
		db = self.app.component('dbManager')
		with db.session() as session:
			uid = session.query(db.User).filter_by(username=username).one().entity_id

		return uid
	#
	def returnUserName(self,uid):
		userName = ''
		db = self.app.component('dbManager')
		with db.session() as session:
			userName = session.query(db.User).filter_by(entity_id=uid).one().username
		return userName
	#
	def returnRoleData(self,orgId):
		roles=[]
		users=[]
		permissions=[]

		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Permission).filter(db.Permission.organization_id==orgId)

			for x in query.all():
				perm ={}
				perm['name']=x.name
				#todo : change to description
				perm['description']=x.name
				permissions.append(perm)


			query = session.query(db.Facet).filter(db.Facet.organization_id==orgId)
			for x in query.all():
				user ={}
				user['username']=x.username
				users.append(user)

			query = session.query(db.Role).filter(db.Role.organization_id==orgId)
			for x in query.all():
				role ={}
				role['name']=x.name
				#todo : change to description
				role['description']=x.name
				role['users']=[]
				query1 = session.query(db.Facet_Role).filter(and_(db.Facet_Role.role_name==role['name'],
																  db.Facet_Role.organization_id==orgId))
				for x in query1.all():
					role['users'].append(x.username)
				role['permissions']	=[]
				query2 = session.query(db.Permission_Role).filter(and_(db.Permission_Role.role_name==role['name'],
																  db.Permission_Role.organization_id==orgId))
				for x in query2.all():
					role['permissions'].append(x.permission_name)

				roles.append(role)


		tableData={}
		tableData['roles']=roles
		tableData['users']=users
		tableData['permissions']=permissions
		return tableData
	#
	def returnVehicleList(self, uid):

		vehicleList = []
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Gps_Vehicle_Info)#.filter_by(User_Id=uid)
			for x in query.all():
				vehicleList.append({'value': x.id, 'display': x.name})

		return vehicleList
	#
	def checkVehicleExists(self, uid, vehicleId):

		for x in self.returnVehicleList(uid):
			if (vehicleId in x['value']):
				return True

		return False
	#
	def returnCoordinates(self, vehicleId, date1):
		num = []
		dated = str(date1[0]) + "-" + str(date1[1]) + "-" + str(date1[2])
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Gps_Coordinate_Data).filter_by(Vehicle_Id=vehicleId, Date=dated)
			for obj in query.all():
				num.append({'Latitude': str(obj.Latitude), 'Longitude': str(obj.Longitude)})
		#
		return num


	def returnCarsData(self,vids,time):
		num = []

		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Gps_Coordinate_Data)
			for obj in query.all():
				num.append({"position": {"latitude": str(obj.Latitude), "longitude": str(obj.Longitude)},
							"time": {"hour": int(obj.Time[0:2]), "minute": int(obj.Time[2:4]),
									 "second": int(obj.Time[4:6])}, "vehicleId": int(obj.Vehicle_Id)})

			return num
	#
	def returnPoiList(self, uid, vehicleId):

		poiList = []
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Gps_Poi_Info).filter_by(User_Id=uid, Vehicle_Id=vehicleId)
			for x in query.all():
				poiList.append({'value': x.Poi_Id, 'display': x.Poi_Name})

		return poiList
	#
	def returnPoiReport(self,uid,category,numOfObj=10,pageNo=1):
		# pageNo starts from 1

		dataSend={}
		rows = []
		i=1
		db=self.app.component('dbManager');
		with db.session() as session:
			query=session.query(db.Gps_Poi_Info).filter(and_(db.Gps_Poi_Info.User_name==uid,db.Gps_Poi_Info.Category==category))
			for data in query.all():
				for vehicleDataAll in  session.query(db.Poi_vehicle).filter_by(Poi_Id=data.Poi_Id).all():

					vehicleData= session.query(db.Gps_Vehicle_Info).filter_by(id=vehicleDataAll.Vehicle_Id ).one()
					vehicleDataInfo=session.query(db.Info).filter(and_(db.Info.entity_id==vehicleDataAll.Vehicle_Id,
				  	db.Info.type==db.Info.Type.vehicleRegNo.value,db.Info.preference== 0)).one()

					cell = {}
					cell['cell'] = []
					cell['cell'].append(i)
					cell['cell'].append(data.Poi_Id)
					cell['cell'].append(data.Poi_Name)
					cell['cell'].append(data.Category)
					cell['cell'].append(vehicleData.name)
					cell['cell'].append(vehicleDataInfo.data)
					cell['cell'].append(vehicleDataAll.Vehicle_Id)
					query2=session.query(db.Info).filter(db.Info.entity_id==data.Poi_Id)
					data2=query2.one()
					#print(data2.data)
					data3=data2.data.split(';')

					cell['cell'].append(data3[0])
					cell['cell'].append(data3[2])
					cell['cell'].append(data3[1])
					cell['id'] = i
					i += 1
					rows.append(cell)
		#dataSend['rows'] = rows
		#dataSend['total']=i-1
		#dataSend['page']=1
		return self.getSlicedData(rows,pageNo,numOfObj)
	#
	def returnRoleList(self, orgId):
		roleList = []
	# Old function modified by NV  to handle multiple organization
	#	db = self.app.component('dbManager')
	#	with db.session() as session:
	#		query = session.query(db.Role).filter(db.Role.organization_id == orgId)
	#		for x in query.all():
	#			roleList.append(x.name)

		db = self.app.component('dbManager')
		with db.session() as session:
			for item in orgId:
				query = session.query(db.Role).filter(db.Role.organization_id == item['id']).order_by(db.Role.name)
				for x in query.all():
					roleList.append({
						"id":x.organization_id,
						"name":x.name
					})

		return roleList



	#
	def updateRolePermissions(self, roleName, permList, orgId):
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Permission_Role).filter(and_ (db.Permission_Role.role_name == roleName,
																   db.Permission_Role.organization_id == orgId ))
			for x in query.all():
				session.delete(x)

			for perm in permList:
				session.add(db.Permission_Role.newFromParams(
					permission_name=perm,
					role_name=roleName,
					organization_id=orgId
				))
	#
	def updateRoleFacet(self, roleName, userList, orgId):
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Facet_Role).filter(db.Facet_Role.role_name == roleName)
			for x in query.all():
				session.delete(x)

			for user in userList:
				session.add(db.Facet_Role.newFromParams(
					username=user,
					role_name=roleName,
					organization_id=orgId
				))
	#
	def getEmployeeDataForFlexiGrid(self,pageNo,session,db,orgId,curId,numOfObj=10):
		orgList = []
		dbNew = self.app.component ('dbManager')
		with dbNew.session () as session :

			objOrg = session.query (dbNew.Organization).filter_by (id = orgId).one ()
			orgList.append({
				"id":objOrg.id,
				"display":objOrg.name
			})

			for item in session.query (dbNew.Organization).filter_by (parent_id = orgId).all () :

				if {"id" : item.id,"display":item.name} not in orgList:
						orgList.append ({
						"id" : item.id,
						"display":item.name
					})

		i=1
		rows = []
		for orgItem in orgList:

			sessionQueryObj = session.query(db.Facet).filter(db.Facet.organization_id == orgItem['id'])


			for data in sessionQueryObj.all():
				id = self.returnUid(data.username)

				if id == curId :
					continue

				queryObj2 = session.query(db.Info).filter((db.Info.entity_id == id))
				queryObj3 = session.query(db.Person).filter(db.Person.id == id)
				cell = {}
				cell['cell'] = []
				cell['cell'].append(i)
				cell['cell'].append(id)
				data2 = queryObj3.one()
				cell['cell'].append(data2.name)
				cell['cell'].append(orgItem['display'])
				cell['cell'].append(data.username)
				cell['cell'].append(str(data2.dob))
				queryObj4 = queryObj2.filter(db.Info.type ==db.Info.Type.Email.value)
				data3 = queryObj4.one()
				cell['cell'].append(data3.data)
				queryObj4 = queryObj2.filter(db.Info.type ==db.Info.Type.Mobile.value)
				data3 = queryObj4.one()
				cell['cell'].append(data3.data)
				queryObj4 = queryObj2.filter(db.Info.type ==db.Info.Type.Address.value)
				data3 = queryObj4.one()
				cell['cell'].append(data3.data)
				cell['cell'].append(data2.enumSex.name.lower())
				cell['id'] = i
				i+=1
				rows.append(cell)

		return self.getSlicedData(rows,pageNo,numOfObj)
	#
	def getOrganizationDataForFlexiGrid(self,pageNo,session,db,orgId,curId,numOfObj=10):
		sessionQueryObj = session.query(db.Organization)

		rows = []
		i = 1

		for data in sessionQueryObj.all():

			cell = {}
			cell['cell'] = []
			cell['cell'].append(i)
			cell['cell'].append(data.name)
			queryObj2 = session.query(db.Info).filter(and_(db.Info.entity_id == data.id, db.Info.type == db.Info.Type.Address.value))
			try:
				data2 = queryObj2.one()
				address=data2.data
				parts=address.split(';')
				cell['cell'].append('')
				cell['cell'].append(parts[0])
				cell['cell'].append(parts[1])
				cell['cell'].append(parts[2])
				cell['cell'].append(parts[3])
				cell['cell'].append(parts[4])
				cell['id'] = i



			except:
				cell['cell'].append('')
				cell['cell'].append('')
				cell['cell'].append('')
				cell['cell'].append('')
				cell['cell'].append('')
				cell['cell'].append('')
				pass
			finally:


				cell['cell'].append(data.id)
				i += 1
				rows.append(cell)

		return self.getSlicedData(rows,pageNo,numOfObj)
	#

	def getBranchDataForFlexiGrid(self,pageNo,session,db,orgId,curId,numOfObj=10, branchFields=None):
		sessionQueryObj = session.query(db.branch)

		rows = []
		#i = (pageNo - 1) * numOfObj + 1
		i = 1
		for data in sessionQueryObj.all():

			cell = {}
			cell['cell'] = []
			cell['cell'].append(i)
			cell['cell'].append(data.parent_id)
			cell['cell'].append(data.name)
			# Clear off old values
			branchFields1 = {'first': 'NA'}
			branchFields1['add1'] = 'NA'
			branchFields1['add2'] = 'NA'
			branchFields1['city'] = 'NA'
			branchFields1['state'] = 'NA'
			branchFields1['pinCode'] = 'NA'


			queryObj2 = session.query(db.Info).filter((db.Info.entity_id == data.id))


			for  data2 in 	queryObj2.all():

					if data2.type == db.Info.Type.branchAddLine1.value:
						branchFields1['add1'] = data2.data
					elif data2.type == db.Info.Type.branchAddLine2.value:
						branchFields1['add2'] = data2.data
					elif data2.type == db.Info.Type.branchCity.value  :
						branchFields1['city'] = data2.data
					elif data2.type == db.Info.Type.branchState.value:
						branchFields1['state'] = data2.data
					elif data2.type == db.Info.Type.branchPin.value:
						branchFields1['pinCode'] = data2.data

				 

			cell['cell'].append(branchFields1['add1'])
			cell['cell'].append(branchFields1['add2'])
			cell['cell'].append(branchFields1['city'])
			cell['cell'].append(branchFields1['state'])
			cell['cell'].append(branchFields1['pinCode'])
			cell['cell'].append(data.id)
			cell['id'] = i


			i += 1
			rows.append(cell)

		return self.getSlicedData(rows,pageNo,numOfObj)
	#

	def getVehicleGroupDataForFlexiGrid(self,pageNo,session,db,orgId,curId,numOfObj=10, branchFields=None):
		sessionQueryObj = session.query(db.VehicleGroup)

		rows = []
		i = 1



		for data in sessionQueryObj.all():

			cell = {}
			cell['cell'] = []
			cell['cell'].append(i)
			cell['cell'].append(data.parent_id)
			cell['cell'].append(data.name)
			cell['cell'].append(data.category)

			cell['cell'].append(data.id)
			cell['id'] = i


			i += 1
			rows.append(cell)

		return self.getSlicedData(rows,pageNo,numOfObj)
	#

	def getVehicleDataForFlexiGrid(self,pageNo,session,db,orgId,curId,numOfObj=10, branchFields=None):
		sessionQueryObj = session.query(db.Gps_Vehicle_Info)

		rows = []
		i = 1



		for data in sessionQueryObj.all():

			cell = {}
			cell['cell'] = []
			cell['cell'].append(i)

			cell['cell'].append(data.id)
			cell['cell'].append(data.name)
			cell['cell'].append(data.device_id)

			# Clear off old values
			vehicleFields1 = {'first': 'NA'}
			vehicleFields1['regNo'] = 'NA'
			vehicleFields1['make'] = 'NA'
			vehicleFields1['type'] = 'NA'



			queryObj2 = session.query(db.Info).filter((db.Info.entity_id == data.id))


			for  data2 in 	queryObj2.all():
				if data2.type == db.Info.Type.vehicleRegNo.value:
					vehicleFields1['regNo'] = data2.data
				elif data2.type == db.Info.Type.vehicleMake.value:
					vehicleFields1['make'] = data2.data
				elif data2.type == db.Info.Type.vehicleType.value:
					vehicleFields1['type'] = data2.data
				elif data2.type == db.Info.Type.speed.value:
					vehicleFields1['speedLimit'] = data2.data



			cell['cell'].append(vehicleFields1['make'])
			cell['cell'].append(vehicleFields1['regNo'])
			cell['cell'].append(vehicleFields1['type'])
			cell['cell'].append(vehicleFields1['speedLimit'])
			cell['cell'].append(data.parent_id)

			cell['cell'].append(data.id)
			cell['id'] = i


			i += 1
			rows.append(cell)

		return self.getSlicedData(rows,pageNo,numOfObj)
	#

	def returnLiveCarsData(self,deviceId, fromDate=None, toDate=None, gmtAdjust = None):
		num = []
		status = []
		db = self.app.component('dbManager')
		timeHelper = self.app.component('timeHelper')
		with db.session() as session:
			# add time filter here
			# TODO  Discuss the number of  variable returned from here
			for deviceNum in deviceId:
				vehicleQuery = session.query(db.Gps_Vehicle_Info).filter(db.Gps_Vehicle_Info.device_id == deviceNum)
				vehicleId = vehicleQuery.one().id
				vehicleName = vehicleQuery.one().name
				vehicleInfoQuery = session.query(db.Info).filter(db.Info.entity_id == vehicleId)
				vehicleRegNo = vehicleInfoQuery.filter(db.Info.type == db.Info.Type.vehicleRegNo.value).one().data

				query = session.query(db.gpsDeviceMessage1).filter( and_ (db.gpsDeviceMessage1.deviceId == '00'+deviceNum,
																		  db.gpsDeviceMessage1.timestamp >= fromDate,
																		  db.gpsDeviceMessage1.timestamp < toDate,
																		  db.gpsDeviceMessage1.messageType == "BR00")).order_by(db.gpsDeviceMessage1.timestamp)

				if query.count() == 0:
					status.append({"deviceId":deviceNum,"dataPresent":0})
				elif query.count() > 0:
					status.append({"deviceId":deviceNum,"dataPresent":1})

				status[len(status)-1]["name"] = vehicleName
				status[len(status)-1]["regNo"] = vehicleRegNo


				for obj in query.all():
					timeDetail = obj.timestamp
					if gmtAdjust != None:
						timeDetail = timeHelper.getDateAndTime_add(gmtAdjust, timeDetail)
					num.append({"position": {"latitude": str(obj.latitude), "longitude": str(obj.longitude)},
					            "time": {"hour": timeDetail.hour, "minute": timeDetail.minute,
					            "second":  timeDetail.second, "year": timeDetail.year, "month": timeDetail.month, "day": timeDetail.day} ,
								"speed" : obj.speed,
								"deviceId" : obj.deviceId,
								"timestamp" : str(timeDetail),
								})
		return num,status
	#
	def returnCarsDataByDates(self, fromDate, toDate):
		num = []
		fromDate = str(fromDate[0]) + "-" + str(fromDate[1]) + "-" + str(fromDate[2])
		toDate = str(toDate[0]) + "-" + str(toDate[1]) + "-" + str(toDate[2])

		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Gps_Coordinate_Data).filter(
				and_(db.Gps_Coordinate_Data.Date >= fromDate, db.Gps_Coordinate_Data.Date <= toDate))
			for obj in query.all():
				num.append({"position": {"latitude": str(obj.Latitude), "longitude": str(obj.Longitude)},
				            "time": {"hour": int(obj.Time[0:2]), "minute": int(obj.Time[2:4]),
				                     "second": int(obj.Time[4:6])}, "vehicleId": int(obj.Vehicle_Id)})
		#
		return num
	#

	def getSlicedData(self,rows,pageNo,numOfObj):
		if pageNo < 1:
			pageNo=1

		dataSend = {
		'total': len(rows),
		'page': pageNo,
		'rows': rows[(pageNo - 1) * numOfObj: pageNo * numOfObj]
		}
		return dataSend

	def returnLiveCarData(self, vehicleIds, time):
		num = []
		db = self.app.component('dbManager')
		with db.session() as session:
			for item in vehicleIds:
				# todo:change the date and get the server date and adjust gmt also for date
				query = session.query(db.Gps_Coordinate_Data).filter(
					and_(db.Gps_Coordinate_Data.Vehicle_Id == item, db.Gps_Coordinate_Data.Time == time,
					     db.Gps_Coordinate_Data.Date == '2004-07-15'))
				try:
					obj = query.one()
					num.append({"position": {"latitude": str(obj.Latitude), "longitude": str(obj.Longitude)},
					            "time": {"hour": int(obj.Time[0:2]), "minute": int(obj.Time[2:4]),
					                     "second": int(obj.Time[4:6])}, "vehicleId": int(obj.Vehicle_Id)})
				except:
					pass

		return num
	#

	def returnLiveCarDataForVehicles(self, deviceIds, dateTime):
		#date = dateTime['year'] + '-' + dateTime['mon'] + '-' + dateTime['day']
		#time = dateTime['hour'] + ':' + dateTime['min'] + ':' + dateTime['sec']
		#timestamp = date + ' ' + time
		num = []
		trackTime = 5
		db = self.app.component('dbManager')
		with db.session() as session:
			for item in deviceIds:
				query = session.query(db.gpsDeviceMessage1).filter(
					and_(db.gpsDeviceMessage1.deviceId == item.split()[0], db.gpsDeviceMessage1.timestamp >= dateTime - timedelta(minutes=trackTime), db.gpsDeviceMessage1.timestamp <= dateTime)).order_by(
					db.gpsDeviceMessage1.timestamp.desc())
				try:
					obj = query.all()[0]
					num.append({"found": "yes",
								"position": {"latitude": str(obj.latitude), "longitude": str(obj.longitude)},
								"speed": int(obj.speed),
								"orientation": obj.orientation,
					            "time": {"hour": obj.timestamp.hour, "minute": obj.timestamp.minute,
										 "second": obj.timestamp.second, "day": obj.timestamp.day,
										 "month": obj.timestamp.month, "year": obj.timestamp.year},
								"vehicleId": int(obj.deviceId)})
				except:
					query = session.query(db.gpsDeviceMessage1).filter(
						and_(db.gpsDeviceMessage1.deviceId == item.split()[0]), db.gpsDeviceMessage1.timestamp <= dateTime).order_by(
						db.gpsDeviceMessage1.timestamp.desc())
					try:
						obj2 = query.all()[0]
						num.append({"found": "old",
								"position": {"latitude": str(obj2.latitude), "longitude": str(obj2.longitude)},
								"speed": int(obj2.speed),
								"orientation": obj2.orientation,
					            "time": {"hour": obj2.timestamp.hour, "minute": obj2.timestamp.minute,
										 "second": obj2.timestamp.second, "day": obj2.timestamp.day,
										 "month": obj2.timestamp.month, "year": obj2.timestamp.year},
								"vehicleId": int(obj2.deviceId)})
					except:
						num.append({"found": "no", "vehicleId": int(obj2.deviceId)})
			#
		#
		return num
	#

	def returnOrgList(self,orgId):
		db = self.app.component('dbManager')
		orgList = []
		with db.session() as session:
			data = session.query(db.Organization)
			if orgId != None:
				data=data.filter_by(parent_id=orgId)
			data=data.all()
			for item in data:
				org = {}
				org['display']  = item.name
				org['value'] = item.id
				orgList.append(org)
		#
		return orgList

	def returnVehicleListForVehicleGroup(self,groupId):
		db = self.app.component('dbManager')
		vehicleList = []
		with db.session() as session:
			data = session.query(db.Gps_Vehicle_Info)
			if groupId != None:
				data=data.filter_by(parent_id=groupId)
			data=data.all()
			for item in data:
				vehicle = {}
				vehicle['display']  = item.name
				vehicle['value'] = item.id
				vehicleList.append(vehicle)
		#
		return vehicleList
	#

	def returnVehicleGroupListForBranch(self,branchId):
		db = self.app.component('dbManager')
		groupList = []
		with db.session() as session:
			data = session.query(db.VehicleGroup)
			if branchId != None:
				data=data.filter_by(parent_id=branchId)
			data=data.all()
			for item in data:
				group = {}
				group['display']  = item.name
				group['value'] = item.id
				groupList.append(group)
		#
		return groupList
	#

	def returnBranchListForOrg(self,orgId):
		db = self.app.component('dbManager')
		branchList = []
		with db.session() as session:
			data = session.query(db.branch)
			if orgId != None:
				data=data.filter_by(parent_id=orgId)
			data=data.all()
			for item in data:
				branch = {}
				branch['display']  = item.name
				branch['value'] = item.id
				branchList.append(branch)
		#
		return branchList
	#

	def getCoordinatesForVehicle(self, deviceId, order=None):
		db = self.app.component('dbManager')
		data = None
		with db.session() as session:
			data = session.query(db.gpsDeviceMessage1).filter_by(db.gpsDeviceMessage1.deviceId == deviceId)
			if order == 'desc' :
				data = data.order_by(db.gpsDeviceMessage1.timestamp.desc)
		return data
	#

	def returnCoordinatesForVehiclesBetween(self, deviceIds, fromTime, toTime):
		num = []
		db = self.app.component('dbManager')
		with db.session() as session:
			for item in deviceIds:
				query = session.query(db.gpsDeviceMessage1).filter(
					and_(db.gpsDeviceMessage1.deviceId == item.split()[0], db.gpsDeviceMessage1.timestamp >= fromTime, db.gpsDeviceMessage1.timestamp <= toTime)).order_by(
					db.gpsDeviceMessage1.timestamp)
				objs = query.all()
				for obj in objs:
					num.append({"position": {"latitude": str(obj.latitude), "longitude": str(obj.longitude)},
								"speed": int(obj.speed),
								"orientation": obj.orientation,
					            "time": {"hour": obj.timestamp.hour, "minute": obj.timestamp.minute,
										 "second": obj.timestamp.second, "day": obj.timestamp.day,
										 "month": obj.timestamp.month, "year": obj.timestamp.year},
								"vehicleId": int(obj.deviceId)})
				#
			#
		#
		return num
	#

	def getVehiclesListNested(self, primaryOrganizationId):
		vehiclesList = []
		orgList = self.returnOrgList (primaryOrganizationId)

		for org in orgList:
			#if org['value'] != primaryOrganizationId:
			branchList = self.returnBranchListForOrg(org['value'])
			branches = []
			for branch in branchList:
				vehicleGroupList = self.returnVehicleGroupListForBranch(branch['value'])
				groups = []
				for vehicleGroup in vehicleGroupList:
					vehicleList = self.returnVehicleListForVehicleGroup(vehicleGroup['value'])
					group = {'vehicleGroupDetails':{'vehicleGroupName':vehicleGroup['display'], 'vehicleGroupId':vehicleGroup['value']}, 'vehicles':vehicleList}
					groups.append (group)
				#
				branch = {'branchDetails':{'branchName':branch['display'], 'branchId':branch['value']}, 'vehicleGroups':groups}
				branches.append (branch)
			#
			org = {'orgDetails':{'orgName':org['display'], 'orgId':org['value']}, 'branches':branches}
			vehiclesList.append(org)
			#
		#
		return vehiclesList

	def filterVehicles(self, vehiclesListNested, orgId, branchId, vehicleGroupId):
		vehicleIds = []
		for org in vehiclesListNested:
			if orgId == 'All' or org['orgDetails']['orgId'] == orgId:
				for branch in org['branches']:
					if branchId == 'All' or branch['branchDetails']['branchId'] == branchId:
						for vehicleGroup in branch['vehicleGroups']:
							if vehicleGroupId == 'All' or vehicleGroup['vehicleGroupDetails']['vehicleGroupId'] == vehicleGroupId:
								for vehicle in vehicleGroup['vehicles']:
									vehicleIds.append(vehicle['value'])
		#
		return vehicleIds

	def getRawCoordinatesForDeviceBetween(self, vehicleId, fromTime=None, toTime=None):

		db = self.app.component('dbManager')

		with db.session() as session:
			deviceId=session.query(db.Gps_Vehicle_Info).filter(db.Gps_Vehicle_Info.id==vehicleId).one().device_id


		query = None
		with db.session() as session:
			query = session.query(db.gpsDeviceMessage1).filter(db.gpsDeviceMessage1.deviceId == '00' + deviceId)
			if (fromTime != None):
				query = query.filter (db.gpsDeviceMessage1.timestamp >= fromTime)
			if (toTime != None):
				query = query.filter (db.gpsDeviceMessage1.timestamp <= toTime)
		#
		return query
	#

	def getVehicleDetails(self, vehiclesListNested, vehicleId):
		obj = {
			'company' : 'company',
			'branch' : 'branch',
			'vehicleInfo' : 'empty',
			'driverInfo' : '',
            'vehicleName' : 'empty',
            'vehicleModel' : 'empty',
			'regNo' : 'empty',
			'vehicleMake' : 'empty',
			'vehicleType' : 'empty',
			'speedLimit' : 'empty',
			'deviceId' : 0,
		}

		db = self.app.component('dbManager')

		for org in vehiclesListNested:
			for branch in org['branches']:
				for vehicleGroup in branch['vehicleGroups']:
					for vehicle in vehicleGroup['vehicles']:
						if vehicle['value'] == vehicleId:
							obj['company'] = org['orgDetails']['orgName']
							obj['branch'] = branch['branchDetails']['branchName']
							obj['vehicleName'] = vehicle['display']
							with db.session() as session:
								try:
									query = session.query(db.Info).filter(db.Info.entity_id == vehicleId)
									obj['regNo'] = query.filter(db.Info.type == db.Info.Type.vehicleRegNo.value).one().data
									obj['vehicleMake'] = query.filter(db.Info.type == db.Info.Type.vehicleMake.value).one().data
									obj['vehicleType'] = query.filter(db.Info.type == db.Info.Type.vehicleType.value).one().data
									obj['speedLimit'] = query.filter(db.Info.type == db.Info.Type.speed.value).one().data

									query = session.query(db.Gps_Vehicle_Info).filter(db.Gps_Vehicle_Info.id == vehicleId)
									obj['deviceId'] = query.one().device_id

								except:
									pass
		return obj
	#

	def correctDeviceId(self, deviceId):
		return deviceId.split()[0]
	#

	def createNewRole(self, roleName, orgId):
		db = self.app.component('dbManager')
		with db.session() as session:
			session.add(db.Role.newFromParams(
				name=roleName,
				description=roleName,
				organization_id=orgId
			))
	#

	def deleteRole(self, roleName):
		db = self.app.component('dbManager')

		db.Permission_Role.delete({
			'role_name':roleName
		})

		db.Role.delete({
			'name':roleName
		})

	#
	def updateRoleFacetForUser(self, userName, roleList, orgId):
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(db.Facet_Role).filter(db.Facet_Role.username == userName)
			for x in query.all():
				session.delete(x)

			for role in roleList:
				session.add(db.Facet_Role.newFromParams(
					username=userName,
					role_name=role,
					organization_id=orgId
				))
	#

