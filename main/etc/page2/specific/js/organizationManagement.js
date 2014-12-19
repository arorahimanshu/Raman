fitx.utils.require(['fitx', 'page2', 'organizationManagement'])
jQuery(window).load(function () {

    //setupAJAXSubmit('organizationManagementForm', 'organizationManagementFormAction', setupData, setupConstraints, '.ok', errorFunc, successFunc)
    //setupAJAXSubmit('organizationManagementForm', 'editOrganization', setupData2, setupConstraints, '.editbutton', errorFunc, successFunc)
    setupFlexiGrid('#showOrganization', undefined, "Organization Details", undefined, undefined, undefined, undefined, classData)
    sendAjaxRequest('organizationData', setupDataFlexi(), showReport,errorFunc, successFunc)


    if (typeof jQuery.cookie('userMessageCok') !== 'undefined'){

            jQuery('.userMessage').text(jQuery.cookie("userMessageCok"));
            jQuery.removeCookie("userMessageCok");
    }

    jQuery('.cancel').click(function () {
        console.log('cancel')
        fitx.page2.closeActiveTab()
    })
    jQuery('#addOrganization').hide();
    jQuery('.pPrev.pButton').click(function () {

        onPrevPageRequest()
    })
    jQuery('.pNext').click(function () {
        onNextPageRequest()
    })
    jQuery('.pGroup select').change(function () {
        onRpChange()
    })
    jQuery('.pFirst.pButton').click(function () {
        onFirstPageRequest()
    })
    jQuery('.pLast.pButton').click(function () {
        onLastPageRequest()
    })
    jQuery('.pReload.pButton').click(function () {
        onReload()
    })
    jQuery('.pcontrol input').keypress(function (e) {
        var key = e.which;
        if (key == 13)  // the enter key code
        {
            var pageNo = parseInt(jQuery('.pcontrol input').val())
			if(pageNo>=1 && pageNo<=parseInt(total/rp)+1)
				sendAjaxRequest('organizationData', {'pageNo':pageNo}, showReport)
        }
    })

    jQuery('.add').click(function () {
		resetForm();
        jQuery('#addOrganization').show();
        //jQuery('.flexigrid').hide();
		jQuery('#tablediv').hide();
    })
	
	var ajaxFileUploader = new fitx.lib1.AjaxFileUploader ({
		actionUrl : "organizationManagementFormAction",

		selector : ".fileChooser",

        successFunction : function (result) {
            successFunc(result);
        },

		failureFunction : function (result) {
			console.log ('upload failed')
		},

		onFileChanged : function (name) {
			console.log ('file choosen: ' + name)
		},

		dataFunction : function () {
			return setupData()
		}
	})

	jQuery (".chooseButton").click (function () {
		ajaxFileUploader.openFileDialog ()
	})

	jQuery (".ok").click (function () {
		ajaxFileUploader.fire ()
	})
	
	var editAjaxFileUploader = new fitx.lib1.AjaxFileUploader ({
		actionUrl : "editOrganization",

		selector : ".fileChooserEdit",

		successFunction : function (result) {
			console.log (result.message)
		},

		failureFunction : function (result) {
			console.log ('upload failed')
		},

		onFileChanged : function (name) {
			console.log ('file choosen: ' + name)
		},

		dataFunction : function () {
			return setupData2()
		}
	})
	
	jQuery (".chooseButtonEdit").click (function () {
		editAjaxFileUploader.openFileDialog ()
	})
	
	jQuery (".editButton").click (function () {
		editAjaxFileUploader.fire ()
	})
	
	jQuery('.logoEdit').hide();
	
	hideColumn('GeoFence Id')
	hideColumn('Vehicle Id')
	
})
function successFunc(result) {
     alert(result.message)
     jQuery.cookie("userMessageCok", result.message);

     if(result.data.errors=='Yes'){
         return;
     }
    location.reload();

}

var idToEdit;
var setupData = function () {
    var data = {}

    data.name = jQuery('#name').val()
    data.category = jQuery("#category option:selected").val()
    data.address1 = jQuery('#address1').val()
    data.address2 = jQuery('#address2').val()
    data.city = jQuery('#city').val()
    data.state = jQuery('#state').val()
    data.pincode = jQuery('#pincode').val()

    return data
}
var setupData2 = function () {

    data2 = setupData()
  	data2.id =idToEdit
    console.log(data2)
  	return data2
}

var setupConstraints = function () {

    var constraints = {

        name: {presence: true},
        address1: {presence: true},
        city: {presence: true},
        state: {presence: true},
        pincode: {presence: true,
            numericality: true}
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
    jQuery('input[type=checkbox]:checked').each(function () {
        flag = 0;
    })
    if (flag == 1)
        error = jQuery.extend({}, error, {'Role': 'Please Select a role'})

    return error

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
        width = 1000
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
            {name: 'Edit', bclass: 'edit', onpress: onAddOrDelete},
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

function setupDataFlexi() {
    data = {}
    return data
}

function showReport(result) {
    if (result.message.sendData.rows.length == 0){
              jQuery('.userMessage').text('No Data Present');
              return
        }

    console.log(result.message.sendData)
    jQuery('#showOrganization').flexAddData(result.message.sendData)
    total = result.message.sendData.total
	
	hideColumn('OrgID')
}

var total = 0
var rp = 10
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
	if(pageNo>=1)
		sendAjaxRequest('organizationData', {'pageNo': pageNo}, showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
	if(pageNo<=parseInt(total/rp)+1)
		sendAjaxRequest('organizationData', {'pageNo': pageNo}, showReport)
}
function onFirstPageRequest() {
    sendAjaxRequest('organizationData', {'pageNo': 1}, showReport)
}
function onLastPageRequest() {
    pageNo = parseInt(total / rp) + 1
    sendAjaxRequest('organizationData', {'pageNo': pageNo}, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val())
    sendAjaxRequest('organizationData', {'pageNo': pageNo}, showReport)
}
function onRpChange() {
	rp = parseInt(jQuery('.pGroup select').val())
	sendAjaxRequest('organizationData',{'pageNo':1,'rp':rp}, showReport)
}
function paymentData(pageNo) {
    var data = {}
    data.pageNo = 1
    if (pageNo != undefined)
        data.pageNo = pageNo
    return data
}
function auxiPaymentData(pageNo) {
    return {'formData': paymentData(pageNo)}
}


function onAddOrDelete(com, grid) {
	resetForm();
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
                editFields.push({'name': jQuery('td[abbr="Organization Name"] >div', this).html()})
                editFields.push({'category': jQuery('td[abbr="Category"] >div', this).html()})
                editFields.push({'address1': jQuery('td[abbr="Addrs_line1"] >div', this).html()})
                editFields.push({'address2': jQuery('td[abbr="Addrs_line2"] >div', this).html()})
                editFields.push({'city': jQuery('td[abbr="City"] >div', this).html()})
                editFields.push({'state': jQuery('td[abbr="State"] >div', this).html()})
                editFields.push({'pincode': jQuery('td[abbr="Pincode"] >div', this).html()})
                var div = jQuery('#addOrganization')
                jQuery.each(editFields, function (k, v) {
                    for (var key in v) {
                        var value = v[key];
                        div.find(':input[id=' + key + ']').val(value)

                    }
                })
                idToEdit=jQuery('td[abbr="OrgID"] >div', this).html()

                jQuery("#tableDiv").toggle('showOrHide')
                jQuery('#addOrganization').toggle('showOrHide')
                //div.find('.ok').text('Edit')
                //div.find('.ok').removeClass('ok')
                //    .addClass('editbutton')
				div.find('.ok').hide();
				div.find('.editButton').show();
				
				jQuery('.logoAdd').hide();
				jQuery('.logoEdit').show();

            })
        }
        else {
            alert('select single row to edit')
        }
    }
	else if (com == "Delete") {
        var c = 0
		jQuery('.trSelected', grid).each(function () {
			c += 1
		})
		if (c == 1) {
			jQuery('.trSelected', grid).each(function () {
				var delFields = {}
				delFields.id=jQuery('td[abbr="OrgID"] >div', this).html()
				sendAjaxRequest('delOrganization',delFields,function(){
					jQuery('.userMessage').text('Organization Deleted');
					sendAjaxRequest('organizationData', setupDataFlexi(), showReport)
				})

			})
		}
		else {
			alert('select single row to delete')
		}
    }

}

var resetForm = function() {
	jQuery('.userMessage').text('');
	jQuery('.errorBox').text('');
	jQuery('#addOrganization input').val('');
	//jQuery('#addOrganization select').val('');
}

var hideColumn = function(colName) {
	jQuery('th[abbr="' + colName + '"]').hide()
	jQuery('td[abbr="' + colName + '"]').hide()
}