import json
from .page2Component import Page2Component
import cherrypy


class UtilUrl(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'logoutAction':
			return self._logOutSuccess(requestPath)
		#

	#

	def _logOutSuccess(self,requestPath):
		userManag = self.app.component('userManager')

		with self.server.session() as serverSession:
			id = serverSession['uid']
			userName = serverSession['username']
			userManag.logout(userName,id)
			return self.jsonSuccess("Successfully Logged Out")
	#
