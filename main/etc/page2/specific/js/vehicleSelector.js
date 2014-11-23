fitx.utils.require (['fitx', 'page2', 'vehicleSelector'])

fitx.page2.vehicleSelector.UpdateDelay = 1500 // in milliseconds

jQuery (window).load (function () {

	//console.log ('vehicle selector loaded')

	var onBranchSelectionUpdate = function () {
		var elements = jQuery ('.vehicleSelector .branches input:checked')
		var selectedBranches = []
		jQuery.each (elements, function (index, rawElement) {
			var element = jQuery (rawElement).parents ('.vehicleSelectorEntry')
			//var branchData = JSON.parse (unescape (element.data ('details')))
			var branchData = element.data ('details')
			selectedBranches.push (branchData['id'])
		})

		var vehicleGroupElements = jQuery ('.vehicleSelector .vehicleGroups input')
		jQuery.each (vehicleGroupElements, function (index, rawElement) {
			var vehicleGroupElement = jQuery (rawElement)
			var parentDiv = jQuery (vehicleGroupElement.parents ('.vehicleSelectorEntry'))
			//var vehicleGroupData = JSON.parse (unescape (parentDiv.data ('details')))
			var vehicleGroupData = parentDiv.data ('details')
			if (selectedBranches.find (vehicleGroupData["parentId"])) {
				vehicleGroupElement.prop ('checked', true)
			} else {
				vehicleGroupElement.prop ('checked', false)
			}
		})

		onVehicleGroupSelectionUpdate ()
	}

	var onVehicleGroupSelectionUpdate = function () {
		var elements = jQuery ('.vehicleSelector .vehicleGroups input:checked')
		var selectedVehicleGroups = []
		jQuery.each (elements, function (index, rawElement) {
			var element = jQuery (rawElement).parents ('.vehicleSelectorEntry')
			//var vehicleGroupData = JSON.parse (unescape (element.data ('details')))
			var vehicleGroupData = element.data ('details')
			selectedVehicleGroups.push (vehicleGroupData['id'])
		})

		var vehicleElements = jQuery ('.vehicleSelector .vehicles input')
		jQuery.each (vehicleElements, function (index, rawElement) {
			var vehicleElement = jQuery (rawElement)
			var parentDiv = jQuery (vehicleElement.parents ('.vehicleSelectorEntry'))
			//var vehicleData = JSON.parse (unescape (parentDiv.data ('details')))
			var vehicleData = parentDiv.data ('details')
			if (selectedVehicleGroups.find (vehicleData["parentId"])) {
				vehicleElement.prop ('checked', true)
			} else {
				vehicleElement.prop ('checked', false)
			}
		})
	}

	jQuery ('.vehicleSelector .branches input').change (
		onBranchSelectionUpdate.debounce (fitx.page2.vehicleSelector.UpdateDelay)
	)

	jQuery ('.vehicleSelector .vehicleGroups input').change (
		onVehicleGroupSelectionUpdate.debounce (fitx.page2.vehicleSelector.UpdateDelay)
	)

})

