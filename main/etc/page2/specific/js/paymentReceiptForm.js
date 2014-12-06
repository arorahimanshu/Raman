fitx.utils.require(['fitx', 'page2', 'paymentReceipt']);
jQuery(window).load(function () {
	if (location.pathname == '/paymentReceiptForm') {
		onLoadWorkfunc_paymentReceipt()
	}

	setupAJAXSubmit('paymentReceipt', 'paymentReceiptFormActionFormLoad', paymentData, paymentDataConstraints, '#go_Date', null, showReport);
	setupFlexiGrid('#viewPayment', undefined, "Payment Details", undefined, undefined, undefined, undefined, classData)

	jQuery('.add').click(function () {
		jQuery('#paymentReceipt').show();
		jQuery('#paymentReport').hide();
	})


	jQuery("#fromDate").datepicker({
									   changeMonth: true,
									   changeYear: true,
									   yearRange: '-150:+0',
									   dateFormat: 'DD, dd/MM/yy',
									   onSelect: function (selected) {
										   jQuery("#toDate").datepicker("option", "minDate", selected)
									   }
								   });
	jQuery("#toDate").datepicker({
									 changeMonth: true,
									 changeYear: true,
									 yearRange: '-150:+0',
									 dateFormat: 'DD, dd/MM/yy',
									 onSelect: function (selected) {
										 jQuery("#fromDate").datepicker("option", "maxDate", selected)
									 }
								 });


});
var setupData_payRec = function () {

	var data = {};
	data.id = jQuery('.paymentID').text();
	data.payeeName = jQuery('#payeeName').val();
	data.payment = {};
	if (jQuery('#cashMode').is(':checked')) {
		data.payment.cash = {};
		data["payment"]["cash"]["amount"] = jQuery("#cashAmount").val()
	}
	if (jQuery('#chequeMode').is(':checked')) {
		data.payment.cheque = {};
		data["payment"]["cheque"]["amount"] = jQuery("#chequeAmount").val();
		data["payment"]["cheque"]["bname"] = jQuery("#chequeBName").val();
		data["payment"]["cheque"]["bloc"] = jQuery("#chequeBLocation").val()
	}
	if (jQuery('#onlineMode').is(':checked')) {
		data.payment.online = {};
		data["payment"]["online"]["amount"] = jQuery("#onlineAmount").val();
		data["payment"]["online"]["bname"] = jQuery("#onlineBName").val();
		data["payment"]["online"]["bloc"] = jQuery("#onlineBLocation").val()
	}
	data.date = returnDate('date')
	return data
}
var setupConstraints_payRec = function () {
	var constraints = {
		payeeName: {
			presence: true,
			length: {minimum: 3}
		},
		date: {
			presence: true
		}

	};
	return constraints
}
var customErrorFunc_payRec = function (data, errors) {


	if (jQuery('#cashMode').is(':checked')) {
		if (!(data.payment.cash.amount && isInt(data.payment.cash.amount))) {
			errors = jQuery.extend({}, errors, {'cashMode': ['Please fill cash details properly']})
		}
	}
	if (jQuery('#chequeMode').is(':checked')) {
		if (!(data.payment.cheque.amount && data.payment.cheque.bname && data.payment.cheque.bloc && isInt(data.payment.cheque.amount))) {
			errors = jQuery.extend({}, errors, {'chequeMode': ['Please fill cheque details properly']})
		}
	}
	if (jQuery('#onlineMode').is(':checked')) {
		if (!(data.payment.online.amount && data.payment.online.bname && data.payment.online.bloc && isInt(data.payment.online.amount))) {
			errors = jQuery.extend({}, errors, {'onlineMode': ['Please fill online details properly']})
		}
	}
	if (Object.keys(data.payment).length == 0) {
		errors = jQuery.extend({}, errors, {'paymentMode': ['Please select atleast one payment mode']})
	}
	return errors
}
function onLoadWorkfunc_paymentReceipt() {
	fitx.utils.require(['fitx', 'page2', 'paymentReceipt']);
	setupAJAXSubmit('paymentReceiptForm', 'paymentReceiptFormActionUrl', setupData_payRec, setupConstraints_payRec, '#submit_paymentReceipt', customErrorFunc_payRec)

	jQuery('#date').datepicker({
								   changeMonth: true,
								   changeYear: true,
								   yearRange: '-150:+0',
								   dateFormat: 'DD, dd/MM/yy'
							   });
	jQuery('.paymentID').text(fitx.lib1.uuid());
	/* intially field inactive */
	jQuery('.cashFields').addClass('inactive');
	jQuery('.chequeFields').addClass('inactive');
	jQuery('.onlineFields').addClass('inactive');
	jQuery('.same').addClass('inactive');
	jQuery('#chequeMode').prop('checked', false);
	jQuery('#onlineMode').prop('checked', false);
	jQuery('#cashMode').prop('checked', false);
	jQuery('#sameValues').prop('checked', false);
	/* intially field inactive */
	jQuery('#cashMode, #chequeMode, #onlineMode, #sameValues').click(function () {
		clearMessages()
		var status1 = jQuery('#chequeMode').is(':checked');
		var status2 = jQuery('#onlineMode').is(':checked');
		//var status3 = jQuery('#sameValues').is(':checked');
		var trigId = jQuery(this).prop('id');
		if (trigId != 'sameValues') {
			if (jQuery(this).is(':checked')) {
				jQuery('.' + trigId.replace("Mode", "") + 'Fields').removeClass(
					'inactive');
				if (status1 && status2) {
					jQuery('.same').removeClass('inactive')
				}
			} else {
				jQuery('.' + trigId.replace("Mode", "") + 'Fields').addClass('inactive');
				if (trigId != 'cashMode') {
					jQuery('#onlineBName').removeAttr('disabled').val("");
					jQuery('#onlineBLocation').removeAttr('disabled').val("");
					jQuery('.same').addClass('inactive')
					jQuery('#sameValues').prop('checked', false)
				}
			}
		} else {
			if (jQuery(this).is(':checked')) {
				jQuery('#onlineBName').prop('disabled', true).val(jQuery('#chequeBName')
																	  .val());
				jQuery('#onlineBLocation').prop('disabled', true).val(jQuery(
					'#chequeBLocation').val())
			} else {
				jQuery('#onlineBName').removeAttr('disabled').val("");
				jQuery('#onlineBLocation').removeAttr('disabled').val("")
			}
		}
	});
	jQuery('#chequeBName, #chequeBLocation').keyup(function () {
		if (jQuery('#sameValues').is(':checked')) {
			jQuery('#onlineBName').val(jQuery('#chequeBName').val());
			jQuery('#onlineBLocation').val(jQuery('#chequeBLocation').val())
		}
	});
}

function createColModel(colList) {
	colModel = []
	jQuery.each(colList, function (k, v) {
		console.log(v)
		var dict = {
			display: v,
			name: v,
			width: v.length * 15,
			align: 'center',
			sortable: true
		}
		colModel.push(dict)
	})
	return colModel

}
function setupFlexiGrid(selector, datatype, title, noOfPages, width, height, singleSelect, classData, extraCols) {
	if (datatype == undefined)
		datatype = 'json'
	if (title == undefined)
		title = 'Table'
	if (noOfPages == undefined)
		noOfPages = 10
	if (width == undefined)
		width = 700
	if (height == undefined)
		height = 200
	if (singleSelect == undefined)
		singleSelect = true
	var colData = createColModel(classData)
	for (var items in extraCols) {
		colData.push(items)
	}
	jQuery(selector).flexigrid({
								   dataType: datatype,
								   colModel: colData,
								   usepager: true,
								   buttons: [
									   {name: 'Add', bclass: 'add', onpress: onAddOrDelete},
									   {name: 'Delete', bclass: 'delete', onpress: onAddOrDelete},

									   {separator: true}
								   ],
								   title: title,
								   useRp: true,
								   rp: noOfPages,
								   showTableToggleBtn: true,
								   width: width,
								   height: height,
								   singleSelect: singleSelect


							   })


}

function showReport(result) {

	if (result.message.sendData.rows.length == 0){
              jQuery('.userMessage').text('No Data Found');
              return
        }
	jQuery('#viewPayment').flexAddData(result.message.sendData)
	total = result.message.sendData.total
}

var total = 0

function paymentData(pageNo) {
	var data = {}
	data.pageNo = 1
	if (pageNo != undefined)
		data.pageNo = pageNo
	data.fromDate = returnDate('fromDate')
	data.toDate = returnDate('toDate')
	return data
}
function paymentDataConstraints() {
	var constraints = {
		fromDate: {presence: true},
		toDate: {presence: true}
	}
	return constraints;
}

function auxiPaymentData(pageNo) {
	return {'formData': paymentData(pageNo)}

}


function onAddOrDelete(com, grid) {
	if (com == "Edit") {
		var c = 0
		jQuery('.trSelected', grid).each(function () {
			c += 1
		})
		if (c == 1) {
			//code for geting row data and sending to form
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
	else if (com == "Add") {

	}
	else if (com == "Delete") {
		var c = 0
		jQuery('.trSelected', grid).each(function () {
			c += 1
		})
		if (c == 1) {
			jQuery('.trSelected', grid).each(function () {
				var delFields = {}
				delFields.paymentId=jQuery('td[abbr="paymentId"] >div', this).html()
				delFields.Mode=jQuery('td[abbr="Mode"] >div', this).html()
				sendAjaxRequest('paymentReceiptDelAction',delFields,function(){
					jQuery('#go_Date').trigger('click')
				})

			})
		}
		else {
			alert('select single row to delete')
		}
	}
}