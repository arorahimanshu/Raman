from appConfig import AppConfig
from component import Component

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import and_, or_, not_
from sqlalchemy import func


class SecurityManager(Component):
	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

	#

	def isSuperuser(self,
	                username,
	                organizationId
	):
		db = self.app.component('dbManager')

		with db.session() as session:
			try:
				role = session.query(
					db.Role
				).filter(and_(
					db.Role.name == db.Facet_Role.role_name,
					db.Role.organization_id == db.Facet_Role.organization_id,

					db.Facet_Role.username == username,
					db.Facet_Role.organization_id == organizationId,
				)).one()
			except (NoResultFound, MultipleResultsFound):
				return False
			#

			if role.name == db.Roles.Superuser:
				return True
			else:
				return False
			#
		#
	#

	def userHasPermission(self,username,organizationId,permissionName):
		db = self.app.component('dbManager')

		with db.session() as session:
			try:
				roles = session.query(
					db.Role
				).filter(and_(
					db.Role.name == db.Facet_Role.role_name,
					db.Role.organization_id == db.Facet_Role.organization_id,

					db.Facet_Role.username == username,
					db.Facet_Role.organization_id == organizationId,
				)).all()
			except (NoResultFound):
				return False
			#

			for role in roles:

				if role.name == db.Roles.Superuser:
					return True
				else:
					permissions = session.query(
						db.Permission
					).filter(and_(
						db.Permission.name == db.Permission_Role.permission_name,
						db.Permission.organization_id == db.Permission_Role.organization_id,

						db.Permission_Role.organization_id == organizationId,
						db.Permission_Role.role_name == role.name
					)).all()

					for permission in permissions:
						if permission.name == permissionName:
							return True
						#
					#
				#
			#
		#
		return False
	#

	def userPermissions(self, username, organizationId):
		db = self.app.component('dbManager')
		with db.session() as session:
			query = session.query(
				db.Permission_Role.permission_name,
			).filter(
				and_(
					db.Facet_Role.organization_id == organizationId,
					db.Facet_Role.username == username,
					db.Facet_Role.role_name == db.Permission_Role.role_name,
					db.Permission_Role.organization_id == organizationId,
				)
			)

			results = []
			for row in query.all():
				results.append(row[0])
			#

			return results
		#
		#

#

