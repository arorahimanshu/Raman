from appConfig import AppConfig
from db import DbTypes, DbEntity, InfoMixin

from sqlalchemy import Column
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy import Integer, Float, Date
from sqlalchemy.orm import relationship
from bunch import Bunch

from passlib.apps import custom_app_context as pwdContext
import json
import enum
import os

def defineTables (db) :
	
	@db.table (
		'entity',
		Column ('id', DbTypes.Uuid, nullable = False),
		PrimaryKeyConstraint ('id'),
	)
	class Entity (DbEntity) :

		@classmethod
		def newUnique (cls) :
			obj = cls ()
			obj.id = db.Entity.newUuid ()
			return obj
		#
	#

	@db.table (
		'displayable',
		Column ('id', Entity.columnType ('id'), nullable = False),
		Column ('initials', DbTypes.VeryShortString),
		Column ('shortName', DbTypes.ShortString),
		Column ('longName', DbTypes.MediumString),
		Column ('description', DbTypes.LongString),

		PrimaryKeyConstraint ('id'),
		ForeignKeyConstraint (['id'], ['entity.id']),
	)
	@db.mapper (
		properties = {
			'entity' : relationship (Entity, uselist = False),
		}
	)
	class Displayable (DbEntity) : pass

	@db.table (
		'info',
		Column ('id', DbTypes.Uuid, nullable = False),
		Column ('entity_id', Entity.columnType ('id'), nullable = False),
		Column ('type', Integer, nullable = False),
		Column ('preference', Float, nullable = False),
		Column ('data', DbTypes.MediumString),
		PrimaryKeyConstraint ('id'),
		ForeignKeyConstraint (['entity_id'], ['entity.id']),
		UniqueConstraint ('entity_id', 'data', 'type'),
		UniqueConstraint ('entity_id', 'type', 'preference'),
	)
	@db.mapper (
		properties = {
			'entity' : relationship (Entity, uselist = False)
		}
	)
	class Info (DbEntity, InfoMixin) :

		@enum.unique
		class Type (enum.Enum) :
			Email = 1
			Landline = 2
			Address = 3
			Mobile = 4
			Facebook = 5
			Twitter = 6
			Person = 7
			Website = 8
			ServiceTaxNumber = 9
			parentOrganization = 10
			branchAddLine1 = 11
			branchAddLine2 = 12
			branchCity = 13
			branchState = 14
			branchPin = 15
			vehicleRegNo=16
			vehicleMake=17
			vehicleType=18
			speed = 19

		#
	#

	@db.table (
		'person',
		Column ('id', Entity.columnType ('id'), nullable = False),
		Column ('name', DbTypes.ShortString),
		Column ('dob', Date),
		Column ('sex', Integer),

		PrimaryKeyConstraint ('id'),
		ForeignKeyConstraint (['id'], ['entity.id']),
	)
	@db.mapper (
		properties = {
			'entity' : relationship (Entity, uselist = False),
		}
	)
	class Person (DbEntity) :

		@enum.unique
		class Sex (enum.Enum) :
			Male = 1
			Female = 2
		#

		def _get_enumSex (self) :
			return self.Sex (self.sex)
		#

		def _set_enumSex (self, other) :
			self.sex = self.Sex (other).value
		#

		enumSex = property (_get_enumSex, _set_enumSex)
	#

	@db.table (
		'contact',
		Column ('entity_id', Entity.columnType ('id'), nullable = False),
		Column ('contactEntity_id', Entity.columnType ('id'), nullable = False),
		Column ('preference', Float, nullable = False),

		PrimaryKeyConstraint ('entity_id', 'preference'),
		UniqueConstraint ('entity_id', 'contactEntity_id'),
		ForeignKeyConstraint (['entity_id'], ['entity.id']),
		ForeignKeyConstraint (['contactEntity_id'], ['entity.id']),
	)
	@db.mapper (
		properties = {
			'entity' : relationship (db.Entity, uselist = False, foreign_keys = lambda : db.Contact.entity_id),
			'contact' : relationship (db.Entity, uselist = False, foreign_keys = lambda : db.Contact.contactEntity_id),
		}
	)
	class Contact (DbEntity) : pass

	organization = db.rawTable (
		'organization',
		Column ('id', Entity.columnType ('id'), nullable = False),
		Column ('parent_id', Entity.columnType ('id'), nullable = False),
		Column ('name', DbTypes.ShortString, nullable = False),
		Column ('countryCode', DbTypes.VeryShortString),
		Column ('languageCode', DbTypes.VeryShortString),

		PrimaryKeyConstraint ('id'),
		UniqueConstraint ('name'),
		ForeignKeyConstraint (['id'], ['entity.id']),
		ForeignKeyConstraint (['parent_id'], ['organization.id']),
	)
	class Organization (DbEntity) : pass
	db.rawMapper (
		Organization, organization,
		properties = {
			'entity' : relationship (Entity, uselist = False),
			'parent' : relationship (Organization, uselist = False, remote_side = [organization.c.id])
		}
	)

	@db.table (
		'user',
		Column ('username', DbTypes.ShortString, nullable = False),
		Column ('password', DbTypes.Password, nullable = False),
		Column ('entity_id', Entity.columnType ('id'), nullable = False),
		Column ('countryCode', DbTypes.VeryShortString),
		Column ('languageCode', DbTypes.VeryShortString),

		PrimaryKeyConstraint ('username'),
		ForeignKeyConstraint (['entity_id'], ['entity.id']),
	)
	@db.mapper (
		properties = {
			'entity' : relationship (Entity, uselist = False),
		}
	)
	class User (DbEntity) :

		class _PasswordVerifier :
			def __init__ (self, parent) :
				self._parent = parent
			#

			def __eq__ (self, other) :
				return self._parent.passwordVerify (
					other, self._parent.password
				)
			#

			def __ne__ (self, other) :
				return not self._parent.passwordVerify (
					other, self._parent.password
				)
			#
		#

		def _getRawPassword (self) :
			return self._PasswordVerifier (self)
		#

		def _setRawPassword (self, raw) :
			self.password = self.encrypt (raw)
		#

		rawPassword = property (_getRawPassword, _setRawPassword)

		@staticmethod
		def encrypt (raw) :
			return pwdContext.encrypt (raw)
		#

		@staticmethod
		def passwordVerify (toVerify, storedHash) :
			return pwdContext.verify (toVerify, storedHash)
		#
	#

	@db.table (
		'facet',
		Column ('username', User.columnType ('username'), nullable = False),
		Column ('organization_id', Organization.columnType ('id'), nullable = False),
		Column ('preference', Float, nullable = False),

		PrimaryKeyConstraint ('username', 'organization_id'),
		UniqueConstraint ('username', 'preference'),
		ForeignKeyConstraint (['username'], ['user.username']),
		ForeignKeyConstraint (['organization_id'], ['organization.id']),
	)
	@db.mapper (
		properties = {
			'user' : relationship (User, uselist = False),
			'organization' : relationship (Organization, uselist = False),
		}
	)
	class Facet (DbEntity) : pass

	@db.table (
		'role',
		Column ('name', DbTypes.ShortString, nullable = False),
		Column ('organization_id', Organization.columnType ('id'), nullable = False),
		Column ('description', DbTypes.LongString),

		PrimaryKeyConstraint ('name', 'organization_id'),
		ForeignKeyConstraint (['organization_id'], ['organization.id']),
	)
	@db.mapper (
		properties = {
			'organization' : relationship (Organization, uselist = False),
		}
	)
	class Role (DbEntity) : pass

	setupRolesHolder (db)

	db.addRoles (
		Superuser = 'superuser',
	)

	@db.table (
		'permission',
		Column ('name', DbTypes.ShortString, nullable = False),
		Column ('organization_id', Organization.columnType ('id'), nullable = False),
		Column ('description', DbTypes.LongString),

		PrimaryKeyConstraint ('name', 'organization_id'),
		ForeignKeyConstraint (['organization_id'], ['organization.id']),
	)
	@db.mapper (
		properties = {
			'organization' : relationship (Organization, uselist = False),
		}
	)
	class Permission (DbEntity) : pass

	setupPermissionsHolder (db)

	db.addPermissions (
		Login = 'login',
	)

	@db.table (
		'permission_role',
		Column ('permission_name', Permission.columnType ('name'), nullable = False),
		Column ('role_name', Role.columnType ('name'), nullable = False),
		Column ('organization_id', Organization.columnType ('id'), nullable = False),

		PrimaryKeyConstraint ('permission_name', 'role_name', 'organization_id'),
		ForeignKeyConstraint (['permission_name', 'organization_id'], ['permission.name', 'permission.organization_id']),
		ForeignKeyConstraint (['role_name', 'organization_id'], ['role.name', 'role.organization_id']),
	)
	@db.mapper (
		properties = {
			'permission' : relationship (Permission, uselist = False),
			'role' : relationship (Role, uselist = False),
		}
	)
	class Permission_Role (DbEntity) : pass

	@db.table (
		'facet_role',
		Column ('role_name', Role.columnType ('name'), nullable = False),
		Column ('username', Facet.columnType ('username'), nullable = False),
		Column ('organization_id', Facet.columnType ('organization_id'), nullable = False),

		PrimaryKeyConstraint ('role_name', 'username', 'organization_id'),
		ForeignKeyConstraint (['role_name', 'organization_id'], ['role.name', 'role.organization_id']),
		ForeignKeyConstraint (['username', 'organization_id'], ['facet.username', 'facet.organization_id']),
	)
	@db.mapper (
		properties = {
			'role' : relationship (Role, uselist = False),
			'facet' : relationship (Facet, uselist = False),
		}
	)
	class Facet_Role (DbEntity) : pass
#

def loadInitialData (db, params = None) :
	with db.session () as session :
		superuserCredentials = {
			'username' : params['basic1.superuser.username'],
			'password' : params['basic1.superuser.password'],
		}
		superuser = db.User.newFromParams (
			{
				'entity' : db.Entity.newUnique (),
				'username' : superuserCredentials['username'],
			}
		)
		superuser.rawPassword = superuserCredentials['password']
		session.add (superuser)

		adminOrgEntity = db.Entity.newUnique ()
		session.add (adminOrgEntity)

		adminOrg = db.Organization.newFromParams (
			{
				'id' : adminOrgEntity.id,
				'parent_id' : adminOrgEntity.id,
				'name' : AppConfig.AdminOrganization,
			}
		)

		session.add (adminOrg)
		entity = db.Entity.newUnique()
		session.add(entity)

		session.add(db.Info.newFromParams({
		'id': entity.id,
		'entity_id': adminOrgEntity.id,
		'enumType': db.Info.Type.Address,
		'preference': 0,

		}))

		for name in db.Permissions._asDict ().values () :
			session.add (db.Permission.newFromParams ({
				'name' : name,
				'organization' : adminOrg
			}))
		#

		for name in db.Roles._asDict ().values () :
			session.add (db.Role.newFromParams ({
				'name' : name,
				'organization' : adminOrg,
			}))
		#

		superuserFacet = db.Facet.newFromParams (
			{
				'user' : superuser,
				'organization' : adminOrg,
				'preference': 0,
			}
		)

		session.add (superuserFacet)

		session.add (
			db.Facet_Role.newFromParams (
				{
					'role_name' : db.Roles.Superuser,
					'username' : superuser.username,
					'organization_id' : adminOrg.id,
				}
			)
		)
	#
#

def afterCreate (db) :
	if not os.path.isdir (AppConfig.DbAssets) :
		if not os.path.exists (AppConfig.DbAssets) :
			os.makedirs (AppConfig.DbAssets)
		else :
			raise Exception ('DbAssets exists, but not a directory : {}'.format (AppConfig.DbAssets))
		#
	#
#

def beforeDrop (db) :
	pass
	#os.path.rmtree (AppConfig.DbAssets)
#

def setupPermissionsHolder (db) :

	permissions = dict ()

	class Permissions :
		def __init__ (self) :
			raise Exception ('Instantiation not allowed for this class')
		#

		@staticmethod
		def _asDict () :
			return permissions
		#
	#

	def _getPermissions (self) :
		return Permissions
	#
	dbCls = type (db)
	dbCls._getPermissions = _getPermissions
	dbCls.Permissions = property (_getPermissions)

	def addPermissions (**kwargs) :
		for key, value in kwargs.items () :
			if key in permissions :
				raise Exception ('Permission with name : "{}", already exists'.format (value))
			elif hasattr (Permissions, key) :
				raise Exception ('Invalid permission name: "{}"'.format (value))
			else :
				permissions[key] = value
				setattr (Permissions, key, value)
			#
		#
	#

	db.addPermissions = addPermissions
#

def setupRolesHolder (db) :

	roles = dict ()

	class Roles :
		def __init__ (self) :
			raise Exception ('Instantiation not allowed for this class')
		#

		@staticmethod
		def _asDict () :
			return roles
		#
	#

	def _getRoles (self) :
		return Roles
	#

	dbCls = type (db)
	dbCls._getRoles = _getRoles
	dbCls.Roles = property (_getRoles)

	def addRoles (**kwargs) :
		for key, value in kwargs.items () :
			if key in roles :
				raise Exception ('Role with name : "{}", already exists'.format (value))
			elif hasattr (Roles, key) :
				raise Exception ('Invalid role name: "{}"'.format (value))
			else :
				roles[key] = value
				setattr (Roles, key, value)
			#
		#
	#


	db.addRoles = addRoles
#

