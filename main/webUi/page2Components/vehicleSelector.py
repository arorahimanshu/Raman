from .page2Component import Page2Component
from utils import newUuid

import cherrypy

import json

class VehicleSelector (Page2Component) :
	def __init__ (self, parent, **kwargs) :
		Page2Component.__init__ (self, parent, **kwargs)
	#

	def handler (self, nextPart, requestPath) :
		nextPart = requestPath.nextPart ()
		if nextPart == 'listBranches' :
			return self._listBranches (requestPath)
		elif nextPart == 'listVehicleGroups' :
			return self._listVehicleGroups (requestPath)
		elif nextPart == 'listVehicles' :
			return self._listVehicles (requestPath)

	def render (self, proxy, params, **kwargs) :
		return proxy.render ('vehicleSelector.html')
	#

	def _listBranches (self, requestPath) :
		branches = [
			{'display' : 'branch.1', 'id' : '1'},
			{'display' : 'branch.2', 'id' : '2'},
		]

		return self.jsonSuccess (branches = branches)
	#

	def _listVehicleGroups (self, requestPath) :
		data = cherrypy.request.params
		branches = json.loads (data['branches'])

		# VALIDATE HERE
		# ....

		vehicleGroups = []
		for branch in branches :
			for i in range (1, 3) :
				vehicleGroups.append ({
					'display' : 'br.{}/vg.{}'.format (branch['id'], i),
					'id' : '{}.{}'.format (branch['id'], i)
				})
			#
		#

		return self.jsonSuccess (vehicleGroups = vehicleGroups)
	#

	def _listVehicles (self, requestPath) :
		data = cherrypy.request.params
		vehicleGroups = json.loads (data['vehicleGroups'])

		# VALIDATE HERE
		# ....

		vehicles = []
		for vehicleGroup in vehicleGroups :
			for i in range (1, 3) :
				vehicles.append ({
					'display': '{}/v.{}'.format (vehicleGroup['display'], i),
					'id': '{}.{}'.format (vehicleGroup['id'], i)
				})
			#
		#

		return self.jsonSuccess (vehicles = vehicles)
	#
#

