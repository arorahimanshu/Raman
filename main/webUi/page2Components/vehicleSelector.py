from .page2Component import Page2Component
from utils import newUuid

import cherrypy

class VehicleSelector (Page2Component) :
	def __init__ (self, parent, **kwargs) :
		Page2Component.__init__ (self, parent, **kwargs)
	#

	def handler (self, nextPart, requestPath) :
		if nextPart == 'listBranches' :
			self._listBranches (requestPath)
		elif nextPart == 'listVehicleGroups' :
			self._listVehicleGroups (requestPath)
		elif nextPart == 'listVehicles' :
			self._listVehicles (requestPath)

	def render (self, proxy, params, **kwargs) :
		return proxy.render ('vehicleSelector.html')
	#

	def _listBranches (requestPath) :
		branches = [
			{'name' : 'branch1', 'id' : '1'},
			{'name' : 'branch2', 'id' : '2'},
		]

		return self.jsonSuccess ('success', branches = branches)
	#
#

