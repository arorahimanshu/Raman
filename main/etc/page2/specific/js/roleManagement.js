fitx.utils.require(['fitx', 'page2', 'roleManagement'])

jQuery(window).load(function () {
	
	setupAJAXSubmit('roleManagementForm', 'addRole', setupData, setupConstraints, '.ok', errorFunc, successFunc)
	setupAJAXSubmit('roleManagementForm', 'editRole', setupData2, setupConstraints, '.editbutton', errorFunc, successFunc)
	
	setupFlexiGrid('#showRole', undefined, "Role Details", undefined, undefined, undefined, undefined, classData, undefined, setupButtonDict(), {'bindUrl': 'newRoleManagementFormAction'});
	
	onLoad_RoleManagement();
})

function setupButtonDict() {
	var buttons = []
	var addButton = {'name': 'Add', 'class': 'add', 'click': addButtonClick}
	buttons.push(addButton)
	var editButton = {'name': 'Edit', 'class': 'edit', 'click': editButtonClick}
	buttons.push(editButton)
	var deleteButton = {'name': 'Delete', 'class': 'delete', 'click': deleteButtonClick}
	buttons.push(deleteButton)
	return buttons
}

function onLoad_RoleManagement() {
	jQuery('.cancel').click(function(){
		jQuery('.flexigrid').show()
		jQuery('#addRole').hide()
	})
}

function addButtonClick(com, grid, c, selectedData) {
	jQuery('#addRole').show();
	jQuery('.flexigrid').hide();
	
	jQuery('input').val('');
	jQuery('input[type=checkbox]:checked').prop("checked", false);
	
	jQuery('#name').removeAttr("disabled")
	
}

function editButtonClick(com, grid, c, selectedData) {
	if (c == 1) {
		jQuery('.trSelected', grid).each(function () {
			var editFields = Array()
			//editFields.push({id: jQuery(this).data('id')})
			editFields.push({'name': jQuery('td[abbr="Role Name"] >div', this).html()})
			var div = jQuery('#addRole')
			jQuery.each(editFields, function (k, v) {
				for (var key in v) {
					var value = v[key];
					div.find('#' + key).val(value)
				}
			})
			
			div.find('#oldName').val(editFields[0]['name']);
			
			var permissions = jQuery('td[abbr="Permissions"] >div', this).html()
			if (permissions.length != 0 && permissions != '&nbsp;') {
				permissions = permissions.split (', ')
				jQuery.each (permissions, function(index, data){
					div.find('#' + data).prop("checked", true)
				})
			}
			
			jQuery("#tableDiv").toggle('showOrHide')
			jQuery('#addRole').toggle('showOrHide')
			div.find('.ok').text('Update')
			div.find('.ok').removeClass('ok')
				.addClass('editbutton')
				
			jQuery('#name').prop("disabled", "disabled")
		})
	}
	else {
		alert('select single row to edit')
	}
}
function deleteButtonClick(com, grid, c, selectedData) {
	if (c == 1) {
		jQuery('.trSelected', grid).each(function () {
			var delFields = {}
			//delFields.id = jQuery('td[abbr="Uid"] >div', this).html()
			delFields.name = jQuery('td[abbr="Role Name"] >div', this).html()
			sendAjaxRequest('delRole', delFields, function () {
				onReload('newRoleManagementFormAction')
			})
		})
	}
	else {
		alert('select single row to delete')
	}
}

var successFunc = function (result) {
	jQuery('#genericError').text(result.message + '..Page will be reloaded.')
	jQuery('#genericError').removeClass('errorBox')
	jQuery('#genericError').addClass('success');
	setTimeout(function () {
		location.reload()
	}, 2000);

}

var setupData2 = function () {
	var data = setupData ();
	data.oldName = jQuery('#oldName').val ()
	return data
}

var setupData = function () {
	var data = {}
	data.name = jQuery ('.roleManagement #name').val ()
	if (data.name.length == 0) {
		delete data.name
	}
	
	data.permissions = []
	jQuery('#addRole .permissions input[type=checkbox]:checked').each(function () {
		data.permissions.push(jQuery(this).prop('id'));
	})
	
	return data
}

var errorFunc = function () {
	return undefined
}

var setupConstraints = function () {
	var constraints = {
		name: {
			presence: true
		}
	}
	
	return constraints
}