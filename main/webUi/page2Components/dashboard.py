from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Dashboard(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)


	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'newDashboardForm':
			return self._newDashboardForm(requestPath)
		elif nextPart == 'newDashboardFormAction':
			return self._newDashboardFormAction(requestPath)
		#

	#



