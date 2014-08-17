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

#

