fitx.utils.require(['fitx', 'page2', 'userManagementForm'])

var byDetailsButton
var byIdButton

var byDetailsContainer
var byIdContainer

jQuery(window).load(function () {
	byDetailsButton = jQuery('.userManagement .personDataType .byDetails')
	byIdButton = jQuery('.userManagement .personDataType .byId')
	byDetailsContainer = jQuery('.userManagement .byDetailsContainer')
	byIdContainer = jQuery('.userManagement .byIdContainer')

	jQuery('.userManagement .dob').datepicker({
												  changeMonth: true,
												  changeYear: true,
												  yearRange: '-150:+0',
												  dateFormat: 'DD, dd/MM/yy',
											  })

	setupAJAXSubmit('userManagementOk', 'userManagementFormAction', setupData, setupConstraints, '.ok', errorFunc, successFunc)
	onLoadFunc_newEmployee()

	setupFlexiGrid('#showUser', undefined, "Employee Details", undefined, undefined, undefined, undefined, classData, saveSuccess, setupButtonDict(), {'bindUrl': 'generateEmployeeData'})

	setupAJAXSubmit('newEmployeeFormOk', 'editEmployeeFormAction', setupData2, setupConstraints, '.editbutton', errorFunc, successFunc)

	if (typeof jQuery.cookie('userMessageCok') !== 'undefined'){

            jQuery('.userMessage').text(jQuery.cookie("userMessageCok"));
            jQuery.removeCookie("userMessageCok");
     }



	jQuery('#addUser').hide()

	jQuery( ".userCheckbox" ).each(function() {
		//alert(jQuery( this ).attr('id')+"=="+activeOrgId);
		activeOrgId = 'check'+jQuery( "#organizationLog option:selected" ).val();
		if ( jQuery( this ).attr('id') == activeOrgId )
		{
		  jQuery(this).show();
		}
		else{
			jQuery(this).hide();
		}
	});




	jQuery('.cancel').click(function(){
		//jQuery('.flexigrid').show()
		jQuery('#tableDiv').show();
		jQuery('#addUser').hide()
		jQuery('input').each(function(){
			jQuery(this).val('')
		})
	})
	/*
	jQuery ('.check').click (function (evt) {
		var target = evt.target;
		
		if (target.checked == true) {
			jQuery ('.check').prop ("checked", false);
			jQuery(target).prop ("checked", true);
		}
	})
	*/

	jQuery( "#organizationLog" ).change( function () {


		activeOrgId = 'check'+jQuery( "#organizationLog option:selected" ).val();
		//console.log(activeOrgId);
		jQuery('.check').prop('checked', false);

		jQuery( ".userCheckbox" ).each(function() {
				//alert(jQuery( this ).attr('id')+"=="+activeOrgId);
				if ( jQuery( this ).attr('id') == activeOrgId )
				{
				  jQuery(this).show();
				}
				else{
					jQuery(this).hide();
				}

		 });

		// add uncheck here

 	});





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

function saveSuccess(result){

	}

function addButtonClick(com, grid, c, selectedData) {
	resetForm();
	jQuery.cookie("userMessageCok", " ");
	jQuery('#addUser').show();
	//jQuery('.flexigrid').hide();
	jQuery('#tableDiv').hide();
}

function editButtonClick(com, grid, c, selectedData) {
	resetForm();
	if (c == 1) {
		jQuery('.trSelected', grid).each(function () {
			var editFields = Array()
			editFields.push({id: jQuery(this).data('id')})
			editFields.push({'name': jQuery('td[abbr="Name"] >div', this).html()})
			editFields.push({'username': jQuery('td[abbr="UserName"] >div', this).html()})
			editFields.push({'dob': jQuery('td[abbr="DOB"] >div', this).html()})
			editFields.push({'address': jQuery('td[abbr="Address"] >div', this).html()})
			editFields.push({'email': jQuery('td[abbr="email-address"] >div', this).html()})
			editFields.push({'mobile': jQuery('td[abbr="Phone No."] >div', this).html()})
			editFields.push({'personId': jQuery('td[abbr="Uid"] >div', this).html()})
			var div = jQuery('#addUser')
			jQuery.each(editFields, function (k, v) {
				for (var key in v) {
					var value = v[key];
					div.find('.' + key).val(value)

				}
			})
			jQuery('#sex').val(jQuery('td[abbr="Sex"] >div', this).html())
			jQuery.cookie("userMessageCok", " ");
			jQuery("#tableDiv").toggle('showOrHide')
			jQuery('#addUser').toggle('showOrHide')
			div.find('.ok').text('Edit')
			div.find('.ok').removeClass('ok')
				.addClass('editbutton')
			div.find(':input[class=personId]').attr('disabled', 'disabled')

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
			delFields.id = jQuery('td[abbr="Uid"] >div', this).html()
			delFields.name = jQuery('td[abbr="UserName"] >div', this).html()
			sendAjaxRequest('delEmployeeFormAction', delFields, function () {
				//alert(result);
				jQuery('.userMessage').text('User Deleted');
				onReload('generateEmployeeData')
			})

		})
	}
	else {
		alert('select single row to delete')
	}
}


function successFunc(result) {

	jQuery.cookie("userMessageCok", result.message);

	//jQuery('#genericError').text(result.message + '..Page will be reloaded.')
	jQuery('#genericError').removeClass('errorBox')
	jQuery('#genericError').addClass('success');
	setTimeout(function () {
		location.reload()
	}, 100);

}
function setupData2() {
	data2 = setupData()
	console.log(data2)
	data2.id = jQuery('.personId').val()
	return data2
}

var onLoadFunc_newEmployee = function () {


	byDetailsButton.click(function () {
		byDetailsButton.removeClass('inactive')
		byDetailsButton.addClass('active')
		byIdButton.removeClass('acive')
		byIdButton.addClass('inactive')

		byDetailsContainer.removeClass('inactive')
		byIdContainer.addClass('inactive')
	})

	byIdButton.click(function () {
		byIdButton.removeClass('inactive')
		byIdButton.addClass('active')
		byDetailsButton.removeClass('active')
		byDetailsButton.addClass('inactive')

		byIdContainer.removeClass('inactive')
		byDetailsContainer.addClass('inactive')
	})


}


var setupData = function () {
	var data = {}

	if (byDetailsButton.hasClass('active')) {
		data.personDataType = 'byDetails'

		data.name = jQuery('.userManagement .name').val()
		if (data.name.length == 0) {
			delete data.name
		}

		var dob = jQuery('.userManagement .dob').datepicker('getDate')
		if (dob) {
			data.dob = [
				parseInt(dob.getFullYear()),
					dob.getMonth() + 1, // Python interprets January as 1 (instead of 0 in javascript)
				dob.getDate()
			]
		}
		data.organizationLog = jQuery('.userManagement #organizationLog :selected').val()
		alert(data.organizationLog)
		data.sex = jQuery('.userManagement .sex').val()

		data.address = jQuery('.userManagement .address').val()
		if (data.address.length == 0) {
			delete data.address
		}

		data.email = jQuery('.userManagement .email').val()
		if (data.email.length == 0) {
			delete data.email
		}

		data.mobile = jQuery('.userManagement .mobile').val()
		if (data.mobile.length == 0) {
			delete data.mobile
		}
	} else {
		data.personDataType = 'byId'
		data.personId = jQuery('.userManagement .personId').val()
	}

	data.username = jQuery('.userManagement .username').val()
	data.password = jQuery('.userManagement .password').val()
	data.passwordConfirm = jQuery('.userManagement .passwordConfirm').val()

	data.roles = []

	jQuery('#addUser input[type=checkbox]:checked').each(function () {
		data.roles.push(jQuery(this).prop('id'));
	})

	return data
}

var setupConstraints = function () {

	var constraints = {

		username: {
			presence: true,
			length: {maximum: fitx.config.fieldInfo.username.maxLength}
		},
		password: {
			presence: true
		},
		passwordConfirm: {
			presence: true
		}
	}

	if (byDetailsButton.hasClass('active')) {
		constraints.name = {
			presence: true,
			length: {maximum: fitx.config.fieldInfo.name.maxLength}
		}

		constraints.address = {
			presence: true,
			length: {maximum: fitx.config.fieldInfo.address.maxLength}
		}
		constraints.dob = {
			presence: true

		}
		constraints.email = {
			email: true,
			length: {maximum: fitx.config.fieldInfo.email.maxLength}
		}

		constraints.mobile = {
			length: {minimum: fitx.config.fieldInfo.mobile.minLength, maximum: fitx.config.fieldInfo.mobile.maxLength}
		}
	} else {
		constraints.personId = {
			presence: true,
			length: {is: fitx.config.fieldInfo.personId.exactLength}
		}
	}
	return constraints
}
var errorFunc = function (data, error) {
	if (data.password != data.passwordConfirm) {
		error = jQuery.extend({}, error, {'password': 'Passwords dont match'})
	} else {
		delete data.passwordConfirm
	}

	flag = 1;


	jQuery('.check:checked').each(function () {
		flag = 0;
	})

	if (flag == 1) {

		error = jQuery.extend({}, error, {'Role': 'Please Select a role'})

	}
	return error

}

var resetForm = function() {
	jQuery('.message').text('');
	jQuery('#addUser input').val('');
	//jQuery('#addUser select').val('');
	jQuery('.errorBox').text('');
	jQuery('input[type=checkbox]').prop('checked',false);
	jQuery('.userMessage').text('');
}