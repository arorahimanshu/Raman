import cherrypy


class Page2Component:
	class UtilityOnlyComponent(Exception):
		pass

	def __init__(self, parent, **kwargs):
		self._parent = parent
		self._server = parent.server
		self._app = parent.app

	#

	@property
	def app(self):
		return self._app

	@property
	def parent(self):
		return self._parent

	@property
	def server(self):
		return self._server

	@property
	def logger(self):
		return self._parent.logger

	@property
	def _renderWithTabs(self):
		return self.parent.component('primaryTabs').renderWithTabs

	#

	def handler(self, nextPart, requestPath):
		raise NotImplementedError()

	#

	# returns if no error
	# raises exception in case of error
	def security(self, appName):
		with self.server.session() as session:
			username = session.get('username', '')
			uid = session.get('uid', '')
			worker = self.app.component('userManager').worker(username, uid)

			# check for superuser
			organizations = worker.organizations()
			requestOrganizationId = cherrypy.request.fitxData['organizationId']

			if requestOrganizationId in organizations:
				organizationId = requestOrganizationId
				if worker.isSuperuser(organizationId):
					return True
				else:
					return self._security(appName, worker, organizationId)

	#

	def _security(self, appName, umWorker, organizationId):
		if umWorker.hasPermission(organizationId, appName):
			return True
		else:
			return False

	#

	def newProxy(self):
		return self._parent.newProxy()

	#

	def jsonSuccess(self, *args, **kwargs):
		return self._parent.jsonSuccess(*args, data=kwargs)

	#

	def jsonFailure(self, *args, **kwargs):
		return self._parent.jsonFailure(*args, data=kwargs)

	#

	def requestParams(self):
		return self._server.requestParams()

	#

	def infoCookie(self):
		return self._server.infoCookie()

	#

#

