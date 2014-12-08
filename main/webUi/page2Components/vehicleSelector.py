from .page2Component import Page2Component

from utils import Validator

import cherrypy

import json


# this code is not being used to show vehciles instead of this we are using getVehicleTree function in dataUtils.py file
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
		branches = []
		db = self.app.component('dbManager')
		with self.server.session() as serverSession:
			with db.session() as session:
				data = session.query(db.branch)
				data=data.filter_by(parent_id=serverSession['primaryOrganizationId'])
				data=data.all()
				for item in data:
					branchData = {}
					branchData['display']  = item.name
					branchData['id']    = item.id
					branches.append(branchData)
				#
			#
		#
		return self.jsonSuccess (branches = branches)
	#

	def _listVehicleGroups (self, requestPath) :
		data = cherrypy.request.params
		branches = json.loads (data['branches'])

		# VALIDATE HERE
		# ....
		db = self.app.component('dbManager')
		vehicleGroups = []
		for branch in branches :
			with db.session() as session:
				data = session.query(db.VehicleGroup)
				data=data.filter_by(parent_id=branch['id'])
				data=data.all()
				for item in data:
					vehicleGroupData = {}
					vehicleGroupData['display']  = item.name
					vehicleGroupData['id']    = item.id
					vehicleGroups.append(vehicleGroupData)
				#
			#
		#

		return self.jsonSuccess (vehicleGroups = vehicleGroups)
	#

	def _listVehicles (self, requestPath) :
		data = cherrypy.request.params
		vehicleGroups = json.loads (data['vehicleGroups'])

		# VALIDATE HERE
		# ....
		db = self.app.component('dbManager')
		vehicles = []
		for vG in vehicleGroups:
			with db.session() as session:
				data = session.query(db.Gps_Vehicle_Info)
				data=data.filter_by(parent_id=vG['id'])
				data=data.all()
				for item in data:
					vehicleData = {}
					vehicleData['display']  = item.name
					vehicleData['id']    = item.id
					vehicles.append(vehicleData)
				#
			#
		#


		return self.jsonSuccess (vehicles = vehicles)
	#
#

