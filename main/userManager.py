from appConfig import AppConfig
from component import Component

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_, or_, not_

import time


class UserManager(Component):
	class LoginFailed(Exception):
		pass

	class NotLoggedIn(Exception):
		pass

	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

		self._loggedInUsers = {}

	#

	def setup(self):
		self._logger = self.app.masterLogger.getChild('userManager')

	#

	def reset(self):
		Component.reset(self)
		self._loggedInUsers = {}

	#

	def attemptLogin(self, username, uid, password):
		if self._isInstallation(username, uid, password):
			return
		#

		db = self.app.component('dbManager')
		securityManager = self.app.component('securityManager')

		organizationId = None
		with db.session() as session:
			try:
				user = session.query(db.User).filter_by(username=username).one()
				if user.rawPassword == password:
					facets = session.query(db.Facet
					).filter_by(username=username
					).order_by(db.Facet.preference
					).all()

					for facet in facets:
						if securityManager.userHasPermission(
								username,
								facet.organization_id,
								db.Permissions.Login,
						):
							organizationId = facet.organization_id
						#
						#
						#
			except NoResultFound:
				pass
			#
		#

		if organizationId != None:
			self._login(username, uid)
			return organizationId
		#

		raise self.LoginFailed(username)

	#

	def isLoggedIn(self, username, uid):
		if self._isInstallation(username, uid):
			return True
		else:
			return self._isLoggedIn(username, uid)
		#
	#

	def logout(self, username, uid):
		if self._isInstallation(username, uid):
			self._installationUid = None
		else:
			self._logout(username, uid)
		#
	#

	def _login(self, username, uid):
		with self.app.requestLock():
			self._loggedInUsers[username] = uid
		#
	#

	def _isLoggedIn(self, username, uid):
		with self.app.requestLock():
			if self._loggedInUsers.get(username, '') == uid:
				return True
			else:
				return False
			#
		#
	#

	def _logout(self, username, uid):
		with self.app.requestLock():
			if self._loggedInUsers.get(username, '') == uid:
				self._loggedInUsers.pop(username)
			else:
				raise self.NotLoggedIn((username, uid))
			#
		#
	#

	def _isInstallation(self, username, uid, password=None):
		InstallationConfig = AppConfig.InstallationConfig
		if InstallationConfig.Enabled:
			if password != None:
				if (
						InstallationConfig.Username == username and
						InstallationConfig.Password == password
				):
					self._installationUid = uid
					return True
				#
			else:
				if (
						InstallationConfig.Username == username and
						self._installationUid == uid
				):
					return True
				#
			#
		#

		return False
	#

	def worker(self, username, uid):
		if self._isLoggedIn(username, uid):
			return self._Worker(self, username)
		else:
			raise self.NotLoggedIn((username, uid))
		#
	#

	class _Worker:

		def __init__(self, parent, username):
			self._app = parent.app
			self._username = username
			self._parent = parent
		#

		@property
		def app(self):
			return self._app

		@property
		def username(self):
			return self._username

		@property
		def parent(self):
			return self._parent

		def organizations(self, name=True):
			db = self.app.component('dbManager')
			result = set()
			with db.session() as session:
				query = session.query(
					db.Organization
				).filter(
					and_(
						db.Organization.id == db.Facet.organization_id,
						db.Facet.username == self.username
					)
				)

				for row in query.all():
					result.add(row.id)
					#
				#
			#

			return result
		#

		def organizationWorker(self, organizationId):
			if organizationId in self.organizations(name=False):
				return self.parent._OrganizationWorker(
					self.parent,
					self.username,
					organizationId,
				)
			#

		#

		def isSuperuser(self, organizationId):
			return self.app.component('securityManager').isSuperuser(
				self.username, organizationId
			)

		#

		def permissions(self, organizationId):
			return self.app.component('securityManager').userPermissions(
				self.username, organizationId
			)

		#

		def hasPermission(self, organizationId, permission):
			return self.app.component('securityManager').userHasPermission(
				self.username, organizationId, permission
			)

		#

		def assertPermission(self, organizationId, permission):
			if not self.app.component('securityManager').userHasPermission(
					self.username, organizationId, permission
			):
				return 'permission denied'
			#
			#

	#

	class _OrganizationWorker:
		def __init__(self, parent, username, organizationId):
			self._app = parent.app
			self._parent = parent
			self._username = username
			self._organizationId = organizationId

		#

		@property
		def app(self): return self._app

		@property
		def parent(self): return self._parent

		@property
		def username(self): return self._username

		@property
		def organizationId(self): return self._organizationId

		def isSuperuser(self):
			return self.app.component('securityManager').isSuperuser(
				self.username, self.organizationId
			)

		#

		def permissions(self):
			return self.app.component('securityManager').userPermissions(
				self.username, self.organizationId
			)

		#

		def hasPermission(self, permission):
			return self.app.component('securityManager').userHasPermission(
				self.username, self.organizationId, permission
			)

		#

		def assertPermission(self, permission):
			if not self.app.component('securityManager').userHasPermission(
					self.username, self.organizationId, permission
			):
				return self.App.AccessDenied()
			#
			#
			#

#

