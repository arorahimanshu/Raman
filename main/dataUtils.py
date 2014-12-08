from appConfig import AppConfig
from component import Component

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy import func, and_, or_, not_

from contextlib import contextmanager
 


class DataUtils(Component):
	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

	#

	@contextmanager
	def worker(self):
		db = self.app.component('dbManager')
		with db.session() as session:
			yield _Worker(self, session)
		#
		#


#

class _Worker:
	def __init__(self, parent, session):
		self._parent = parent
		self._app = parent.app
		self._session = session
		self._logger = self.app.masterLogger.getChild('DataUtilsWorker')

	#

	@property
	def app(self):
		return self._app

	@property
	def parent(self):
		return self._parent

	@property
	def session(self):
		return self._session

	@property
	def logger(self):
		return self._logger

	def createPerson(self, details=None):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		if 'entityId' in details:
			entity = self.session.query(db.Entity).filter_by(
				id=details['entityId']
			).one()
		else:
			entity = db.Entity.newUnique()
			self.session.add(entity)
		#

		newPerson = db.Person.newFromParams({
		'name': details.get('name', None),
		'dob': details.get('dob', details.get('dateOfBirth', None)),
		'id': entity.id,
		})
		self.session.add(newPerson)

		if 'sex' in details:
			newPerson.enumSex = details['sex']
		#

		for i, email in enumerate(details.get('emails', [])):
			self.session.add(db.Info.newFromParams({
			'id': db.Entity.newUuid(),
			'entity_id': newPerson.id,
			'enumType': db.Info.Type.Email,
			'preference': i,
			'data': email,
			}))
		#

		for i, address in enumerate(details.get('addresses', [])):
			self.session.add(db.Info.newFromParams({
			'id': db.Entity.newUuid(),
			'entity_id': newPerson.id,
			'enumType': db.Info.Type.Address,
			'preference': i,
			'data': address,
			}))
		#

		for i, mobile in enumerate(details.get('mobiles', [])):
			self.session.add(db.Info.newFromParams({
			'id': db.Entity.newUuid(),
			'entity_id': newPerson.id,
			'enumType': db.Info.Type.Mobile,
			'preference': 0,
			'data': mobile,
			}))
		#

		return newPerson

	#

	def createUser(self, details=None):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		if 'entityId' in details:
			entity = self.session.query(db.Entity).filter_by(
				id=details['entityId']
			).one()
		else:
			entity = db.Entity.newUnique()
			self.session.add(entity)
		#

		newUser = db.User.newFromParams({
		'username': details['username'],
		'rawPassword': details['password'],
		'entity_id': entity.id,
		})
		self.session.add(newUser)

		return newUser

	#

	def createFacet(self, details=None):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		username = details['username']
		organizationId = details['organizationId']
		preference = details.get('preference', None)

		if preference == None:
			preferences = self.session.query(db.Facet.preference).filter(
				and_(
					db.Facet.username == username,
					db.Facet.organization_id == organizationId,
				)
			).order_by(
				db.Facet.preference.desc()
			).all()

			if len(preferences) == 0:
				preference = 0
			else:
				preference = preferences[0] + 1
			#
		#

		facet = db.Facet.newFromParams({
		'username': details['username'],
		'organization_id': details['organizationId'],
		'preference': preference,
		})

		self.session.add(facet)

		return self.session

	#

	def createRole(self, details=None):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		name = details['name']
		organizationId = details['organizationId']
		description = details.get('description', '')

		newRole = db.Role.newFromParams({
		'name': name,
		'organization_id': organizationId,
		'description': description,
		})

		self.session.add(newRole)

		return newRole

	#

	def organizationByName(self, name):
		db = self.app.component('dbManager')
		return self.session.query(
			db.Organization
		).filter_by(
			name=name
		).one()

	#

	def createOrganization(self, details=None):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		parentId = details.get(
			'parentId', None
		)

		if parentId:
			parent = self.session.query(
				db.Organization
			).filter_by(
				id=parentId
			).one()
		else:
			adminOrganization = self.session.query(
				db.Organization
			).filter_by(
				name=AppConfig.AdminOrganization
			).one()

			parent = adminOrganization

		#

		entityId = details.get('entityId', None)
		if entityId == None:
			entity = db.Entity.newUnique()
			self.session.add(entity)

		else:
			entity = self.session.query(
				db.Entity
			).filter_by(
				id=entityId
			).one()
		#
		self.session.commit()
		newOrganization = db.Organization.newFromParams({
		'id': entity.id,
		'parent': parent,
		'name': details['name'],
		})

		self.session.add(newOrganization)

		for name in db.Permissions._asDict().values():
			self.session.add(db.Permission.newFromParams({
			'name': name,
			'organization_id': newOrganization.id,
			}))
		#

		for name in db.Roles._asDict().values():
			self.session.add(db.Role.newFromParams({
			'name': name,
			'organization_id': newOrganization.id,
			}))
		#

		return newOrganization

	#

	def delBranchCascade(self,branchId):
		db = self.app.component('dbManager')
		with db.session () as session:
			for data in session.query(db.VehicleGroup).filter_by(parent_id = branchId).all():
				self.delVehicleGroupCascade(data.id)

			db.Info.delete({
				'entity_id':branchId
			})
			db.branch.delete({
				'id':branchId
			})
			db.Entity.delete({
				'id':branchId
			})

	def delVehicleGroupCascade(self,vehicleGroupId):
		db = self.app.component('dbManager')
		with db.session () as session:
			for data in session.query(db.Gps_Vehicle_Info).filter_by(parent_id = vehicleGroupId).all():
				self.delVehicleCascade(data.id)

			db.VehicleGroup.delete({
				'id':vehicleGroupId
				})
			db.Entity.delete({
				'id':vehicleGroupId
				})


	def delVehicleCascade(self,vehicleId):
		db = self.app.component('dbManager')
		with db.session () as session:

			db.gpsDeviceMessage1.delete({
				'deviceId':vehicleId
				})
			# delete geofence data
			# if only one row is present then delete both geofence & geofence vehicle mapping
			# other wise delete only mapping
			geoFenceData = session.query(db.GeoFence_vehicle).filter_by( Vehicle_id = vehicleId )

			if geoFenceData.count() == 1:
				db.GeoFence_vehicle.delete({
					'Vehicle_id':vehicleId
					})
				db.Gps_Geofence_Data.delete({
					'Geofence_Id':geoFenceData['GeoFence_id']
					})
			if geoFenceData.count() > 1:
					db.GeoFence_vehicle.delete({
					'Vehicle_id':vehicleId
					})
			# delete geoPoi data
			# if only one row is present then delete both POI & POI vehicle mapping data
			# other wise delete only mapping

			poiData = session.query(db.Poi_vehicle).filter_by(Vehicle_Id = vehicleId)
			if poiData.count() == 1:
				db.Poi_vehicle.delete({
					'Vehicle_id':vehicleId
					})
				db.Gps_Poi_Info.delete({
					'Poi_Id':poiData['Poi_Id']
					})
			if poiData.count() > 1:
				db.Poi_vehicle.delete({
					'Vehicle_id':vehicleId
					})

			db.Info.delete({
				'entity_id':vehicleId
			})

			db.Gps_Vehicle_Info.delete({
				'id':vehicleId
			})
			db.Entity.delete({
				'id':vehicleId
			})




	def createBranch(self, details=None):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		branchName = details.get(
			'name', None
		)



		entityId = details.get('entityId', None)
		if entityId == None:
			entity = db.Entity.newUnique()
			self.session.add(entity)

		else:
			entity = self.session.query(
				db.Entity
			).filter_by(
				id=entityId
			).one()
		#

		self.session.commit()
		newBranch = db.branch.newFromParams({
		'id': entity.id,
		'parent_id': details['parentOrgId'],
		'name': details['branchName'],
		})

		self.session.add(newBranch)

		self.session.add(db.Info.newFromParams({
		'id': db.Entity.newUuid(),
		'entity_id': newBranch.id,
		'enumType': db.Info.Type.branchAddLine1,
		'preference': 0,
		'data': details['branchAdd1'],
		}))

		self.session.add(db.Info.newFromParams({
		'id':  db.Entity.newUuid(),
		'entity_id': newBranch.id,
		'enumType': db.Info.Type.branchAddLine2,
		'preference': 0,
		'data': details['branchAdd2'],
		}))

		self.session.add(db.Info.newFromParams({
		'id': db.Entity.newUuid(),
		'entity_id': newBranch.id,
		'enumType': db.Info.Type.branchCity,
		'preference': 0,
		'data': details['branchAdd1'],
		}))

		self.session.add(db.Info.newFromParams({
		'id': db.Entity.newUuid(),
		'entity_id': newBranch.id,
		'enumType': db.Info.Type.branchState,
		'preference': 0,
		'data': details['branchState'],
		}))

		self.session.add(db.Info.newFromParams({
		'id': db.Entity.newUuid(),
		'entity_id': newBranch.id,
		'enumType': db.Info.Type.branchPin,
		'preference': 0,
		'data': details['branchPin'],
		}))


		return newBranch

	#
	def createVehicleGroup(self, details=None):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		branchName = details.get(
			'name', None
		)



		entityId = details.get('entityId', None)
		if entityId == None:
			entity = db.Entity.newUnique()
			self.session.add(entity)

		else:
			entity = self.session.query(
				db.Entity
			).filter_by(
				id=entityId
			).one()
		#

		self.session.commit()
		newVehicleGroup = db.VehicleGroup.newFromParams({
		'id': entity.id,
		'parent_id': details['parentOrgId'],
		'name': details['vehicleGroupName'],
		'category':details['vehicleGroupCat']
		})

		self.session.add(newVehicleGroup)



		return newVehicleGroup

	#

	def assignPermissionRole(self, details):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		organizationId = details['organizationId']
		permissionName = details['permissionName']
		roleName = details['roleName']

		newPermission_Role = db.Permission_Role.newFromParams({
		'permission_name': permissionName,
		'role_name': roleName,
		'organization_id': organizationId,
		})

		self.session.add(newPermission_Role)

		return newPermission_Role

	#

	def assignFacetRole(self, details):
		details = dict() if details == None else details
		db = self.app.component('dbManager')

		organizationId = details['organizationId']
		roleName = details['roleName']
		username = details['username']

		newFacet_Role = db.Facet_Role.newFromParams({
		'role_name': roleName,
		'username': username,
		'organization_id': organizationId,
		})

		self.session.add(newFacet_Role)

		return newFacet_Role

	#

	def _old_getVehicleTree(self,orgId):

		# This function is EXTREMELY inefficient :
		# 1. multiple sessions are not needed, prefer to work
		#    with a single outer session whenever possible.
		#    The whole point of using sessions is to accomplish
		#    lots of task as a single ACID transaction. Using
		#    multiple sessions within one request/one function
		#    defeats the purpose.
		#
		# 2. IN operator of SQL is SUPER INEFFICIENT :
		#    It is created as quick and dirty way to implement
		#    search queries on ad-hoc created tables. Tables
		#    which are properly designed can avoid its usage.
		#
		# I rewrote this function, refer to that and compare.

		branches = []
		db = self.app.component('dbManager')


		with db.session() as session:
				data = session.query(db.branch)
				data=data.filter_by(parent_id=orgId)
				data=data.all()
				for item in data:
					branchData = {}
					branchData['display']  = item.name
					branchData['id']    = item.id
					branches.append(branchData)
				#
			#
		#
		branchList= []

		for item in branches :
			branchList.append(item['id'])

		db = self.app.component('dbManager')
		vehicleGroups = []

		with db.session() as session:
				data = session.query(db.VehicleGroup).order_by(db.VehicleGroup.name)
				data=data.filter(db.VehicleGroup.parent_id.in_(branchList))
				data=data.all()
				for item in data:
					vehicleGroupData = {}
					vehicleGroupData['display']  = item.name
					vehicleGroupData['id']    = item.id
					vehicleGroupData['parentId'] = item.parent_id
					vehicleGroups.append(vehicleGroupData)
				#
			#


		vGroupList = []
		for item in vehicleGroups:
			vGroupList.append(item['id'])

		db = self.app.component('dbManager')
		vehicles = []

		with db.session() as session:
				data = session.query(db.Gps_Vehicle_Info).order_by(db.Gps_Vehicle_Info.name)
				data=data.filter(db.Gps_Vehicle_Info.parent_id.in_(vGroupList))
				data=data.all()
				for item in data:
					vehicleData = {}
					vehicleData['display']  = item.name
					vehicleData['id']    = item.id
					vehicleData['parentId']    = item.parent_id
					vehicles.append(vehicleData)
				#
			#
		#

		treeDict = []
		treeDict.append(branches)
		treeDict.append(vehicleGroups)
		treeDict.append(vehicles)

		return treeDict
	#

	def getVehicleTree (self, orgId) :
		db = self.app.component ('dbManager')
		with db.session () as session :
			branches = []
			for item in session.query (db.branch).filter_by (parent_id = orgId).all () :
				branches.append ({
					"display" : item.name,
					"id" : item.id,
				})
			#

			vehicleGroups = []
			query = session.query (db.VehicleGroup).filter (
				and_ (
					db.VehicleGroup.parent_id == db.branch.id,
					db.branch.parent_id == orgId
				)
			).order_by (db.VehicleGroup.name)

			for item in query.all () :
				vehicleGroups.append ({
					'display' : item.name,
					'id' : item.id,
					'parentId' : item.parent_id
				})
			#

			vehicles = []
			query = session.query (db.Gps_Vehicle_Info).filter (
				and_ (
					db.Gps_Vehicle_Info.parent_id == db.VehicleGroup.id,
					db.VehicleGroup.parent_id == db.branch.id,
					db.branch.parent_id == orgId
				)
			).order_by (db.Gps_Vehicle_Info.name)

			for item in query.all () :
				vehicles.append ({
					'display' : item.name,
					'id' : item.id,
					'parent_id' : item.parent_id,
					'deviceId': item.device_id
				})
			#

			return [branches, vehicleGroups, vehicles]
		#
	#
#

