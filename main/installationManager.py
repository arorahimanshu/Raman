from appConfig import AppConfig
from component import Component


class InstallationManager(Component):
	class AccessDenied(Exception):
		pass

	class _Worker:
		def __init__(self, manager):
			self.manager = manager

		#

		def createTables(self):
			dbManager = self.manager.app.component('dbManager')
			with dbManager.session() as session:
				dbManager.metadata.create_all()
			#

		#

		def dropTables(self):
			dbManager = self.manager.app.component('dbManager')
			with dbManager.session() as session:
				dbManager.metadata.drop_all()
			#

		#

		def loadInitialData(self, params):
			dbManager = self.manager.app.component('dbManager')
			dbManager.loadInitialData(params)

		#

	#

	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

	#

	def _preCondition(self, username, uid):
		userManager = self.app.component('userManager')
		installerUsername = AppConfig.InstallationConfig.Username
		if username == installerUsername and userManager.isLoggedIn(installerUsername, uid):
			return
		else:
			raise AccessDenied()
		#

	#

	def getWorker(self, username, uid):
		self._preCondition(username, uid)
		return self._Worker(self)

	#

#

