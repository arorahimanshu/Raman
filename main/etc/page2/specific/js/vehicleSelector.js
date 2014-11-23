fitx.utils.require (['fitx', 'page2', 'vehicleSelector'])

jQuery (window).load (function () {

	//console.log ('vehicle selector loaded')

	var createNewEntry = function (data, display) {
		return (
			'<div class="vehicleSelectorEntry" data-details="'
			+ escape (JSON.stringify (data))
			+ '">'
			+ '<input type="checkbox" checked="checked">'
			+ escape (display)
			+ '</div>'
		)
	}

	var onBranchSelectionUpdate = function () {
		var elements = jQuery ('.vehicleSelector .branches input:checked')
		var selectedBranches = []
		jQuery.each (elements, function (index, rawElement) {
			var element = jQuery (rawElement).parents ('.vehicleSelectorEntry')
			selectedBranches.push (JSON.parse (unescape (element.data ('details'))))
		})
		vehicleGroupsLoader.fire (selectedBranches)
	}

	var onVehicleGroupSelectionUpdate = function () {
		var elements = jQuery ('.vehicleSelector .vehicleGroups input:checked')
		var selectedVehicleGroups = []
		jQuery.each (elements, function (index, rawElement) {
			var element = jQuery (rawElement).parents ('.vehicleSelectorEntry')
			selectedVehicleGroups.push (JSON.parse (unescape (element.data ('details'))))
		})
		vehiclesLoader.fire (selectedVehicleGroups)
	}

	var listBranches = function (branches) {
		var content = ''
		jQuery.each (branches, function (index, branchDetails) {
			content += createNewEntry (branchDetails, branchDetails.display)
		})

		jQuery ('.vehicleSelector .branches').html (content)

		jQuery ('.vehicleSelector .branches input').change (
			onBranchSelectionUpdate.debounce (2000) // 2 seconds
		)

		onBranchSelectionUpdate ()
	}

	var listVehicleGroups = function (vehicleGroups) {
		var content = ''
		jQuery.each (vehicleGroups, function (index, vgDetails) {
			content += createNewEntry (vgDetails, vgDetails.display)
		})
		jQuery ('.vehicleSelector .vehicleGroups').html (content)

		jQuery ('.vehicleSelector .vehicleGroups input').change (
			onVehicleGroupSelectionUpdate.debounce (2000)
		)

		onVehicleGroupSelectionUpdate ()
	}

	var listVehicles = function (vehicles) {
		var content = ''
		jQuery.each (vehicles, function (index, vehicleDetails) {
			content += createNewEntry (vehicleDetails, vehicleDetails.display)
		})
		jQuery ('.vehicleSelector .vehicles').html (content)
	}

	var branchesLoader = new fitx.lib1.CustomAjax ({
		actionUrl: fitx.utils.appUrl ('vehicleSelector', 'listBranches'),
		successFunction: function (result) {
			var branches = []
			jQuery.each (result.data.branches, function (index, branch) {
				branches.push (branch)
			})
			listBranches (branches)
		},
		failureFunction: function () {
			console.log ('vehicleSelector.branchesLoader: failed')
		}
	})

	branchesLoader.fire ()

	var vehicleGroupsLoader = new fitx.lib1.CustomAjax ({
		actionUrl: fitx.utils.appUrl ('vehicleSelector', 'listVehicleGroups'),
		dataFunction: function (control) {
			return {branches: JSON.stringify (control.args ()[0])}
		},
		successFunction: function (result) {
			var vehicleGroups = []
			jQuery.each (result.data.vehicleGroups, function (index, vehicleGroup) {
				vehicleGroups.push (vehicleGroup)
			})
			listVehicleGroups (vehicleGroups)
		},
		failureFunction: function () {
			console.log ('vehicleSelector.vehicleGroupsLoader: failed')
		}
	})

	var vehiclesLoader = new fitx.lib1.CustomAjax ({
		actionUrl: fitx.utils.appUrl ('vehicleSelector', 'listVehicles'),
		dataFunction: function (control) {
			return {vehicleGroups: JSON.stringify (control.args ()[0])}
		},
		successFunction: function (result) {
			var vehicles = []
			jQuery.each (result.data.vehicles, function (index, vehicle) {
				vehicles.push (vehicle)
			})
			listVehicles (vehicles)
		},
		failureFunction: function () {
			console.log ('vehicleSelector.vehiclesLoader: failed')
		}
	})
})

