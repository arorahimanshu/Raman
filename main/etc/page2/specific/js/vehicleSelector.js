fitx.utils.require (['fitx', 'page2', 'vehicleSelector'])

jQuery (window).load (function () {

	//console.log ('vehicle selector loaded')

	var listBranches = function (branches) {
		var content = ''
		jQuery.each (branches, function (index, branchDetails) {
			content += (
				'<div data-details="'
				+ escape (JSON.stringify (branchDetails))
				+ '">'
				+ '<input type="checkbox">'
				+ escape (branchDetails.name)
				+ '</div>'
			)
		})

		jQuery ('.vehicleSelector .branches').html (content)
	}

	listBranches ([
		{name:'branch1', id:1},
		{name:'branch2', id:2},
	])

})

