fitx.utils.require(['fitx', 'page2', 'vehicle']);
var VId;
jQuery(window).load(function () {
	onLoadFunc_newVehicle ()

});

var onLoadFunc_newVehicle = function () {

	jQuery('.vehicleTable').show();
	jQuery('.newVehicleForm').hide();
	
	setupAJAXSubmit('newVehicleForm','newVehicleFormAction',setupData,setupConstraints,'#submit');
	setupFlexiGrid('#vehicleTable', undefined, "Vehicle Details", undefined, undefined, undefined, undefined, classData, undefined, setupButtonDict(), {'bindUrl': 'vehicleData'});
	setupAJAXSubmit('newVehicleForm', 'editVehicleAction', setupData2, setupConstraints, '#edit');

	jQuery('#cancel').click(function(){
		jQuery('.vehicleTable').show();
		jQuery('.newVehicleForm').hide();
		jQuery('input').each(function(){
			jQuery(this).val('')
		})
	})
};

var setupData = function () {
	var data = {};
	
	data.vehicleRegNo = jQuery ('#vehicleRegNo').val ();
	data.vehicleName = jQuery ('#vehicleName').val ();
	data.vehicleMake = jQuery ('#vehicleMake').val ();
	data.vehicleType = jQuery ('#vehicleType').val ();
	
	data.vehicleGroupId = jQuery('#vehicleGroup :selected').val();
	
	return data
};
function setupData2(){
	var data=setupData();
	data.id=VId;
	return data;
}

var setupConstraints = function () {

	return {

		vehicleRegNo: {
			presence: true
		},
		vehicleName: {
			presence: true
		},
		vehicleMake: {
			presence: true
		},
		vehicleType: {
			presence: true
		}
	};
	

};
function setupButtonDict() {
	var buttons = [];
	buttons.push({'name': 'Add', 'class': 'add', 'click': addButtonClick});
	buttons.push({'name': 'Edit', 'class': 'edit', 'click': editButtonClick});
	buttons.push({'name': 'Delete', 'class': 'delete', 'click': deleteButtonClick});
	return buttons

}

function addButtonClick(com, grid, c, selectedData) {
	jQuery('.newVehicleForm').show();
	jQuery('.vehicleTable').hide();
}

function editButtonClick(com, grid, c, selectedData) {
	if (c == 1) {
		jQuery('.trSelected', grid).each(function () {
			var editFields = [];
			VId=jQuery('td[abbr="Vehicle_Id"] >div', this).html();
			editFields.push({'id': VId});
			editFields.push({'vehicleName': jQuery('td[abbr="Vehicle_Name"] >div', this).html()});
			editFields.push({'vehicleMake': jQuery('td[abbr="Vehicle_Make"] >div', this).html()});
			editFields.push({'vehicleRegNo': jQuery('td[abbr="Vehicle_Reg_No"] >div', this).html()});
			editFields.push({'vehicleType': jQuery('td[abbr="Vehicle_Type"] >div', this).html()});
			var div = jQuery('.newVehicleForm');
			jQuery.each(editFields, function (k, v) {
				for (var key in v) {
					var value = v[key];
					div.find('#' + key).val(value)

				}
			});

			var vehicleGroupId = jQuery('td[abbr="Vehicle_Group_Id"] >div', this).html ();
			div.find('#vehicleGroup').val(vehicleGroupId);
				
			jQuery(".newVehicleForm").show();
			jQuery('.vehicleTable').hide();
			div.find('#submit').text('Edit');
			div.find('#submit').prop('id','edit')

		})
	}
	else {
		alert('select single row to edit')
	}
}

function deleteButtonClick(com, grid, c, selectedData) {
	if (c == 1) {
		jQuery('.trSelected', grid).each(function () {
			var delFields = {};
			delFields.id = jQuery('td[abbr="Vehicle_Id"] >div', this).html();
			sendAjaxRequest('delVehicleDataAction', delFields, function () {
				onReload('vehicleData')
			})

		})
	}
	else {
		alert('select single row to delete')
	}
}
