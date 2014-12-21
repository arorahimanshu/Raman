fitx.utils.require(['fitx', 'page2', 'vehicleGroupManagement'])
jQuery(window).load(function () {
    jQuery('#addVehicleGroup').hide();
    setupAJAXSubmit('vehicleGroupManagementForm', 'vehicleGroupManagementFormAction', setupData, setupConstraints, '.ok', errorFunc, successFunc)
    setupAJAXSubmit('vehicleGroupManagementForm', 'editVehicleGroup', setupData2, setupConstraints, '.editbutton', errorFunc, successFunc)
    setupFlexiGrid('#showVehicleGroup', undefined, "VehicleGroup Details", undefined, undefined, undefined, undefined, classData)
    sendAjaxRequest('vehicleGroupData', setupDataFlexi(), showReport)

    if (typeof jQuery.cookie('userMessageCok') !== 'undefined'){

            jQuery('.userMessage').text(jQuery.cookie("userMessageCok"));
            jQuery.removeCookie("userMessageCok");
    }

    jQuery('.cancel').click(function () {
        console.log('cancel')
        fitx.page2.closeActiveTab()
    })

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
				sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
        }
    })

    jQuery('.add').click(function () {
		resetForm();
        jQuery('.userMessage').text(" ");
        jQuery('#addVehicleGroup').show();
        jQuery('.flexigrid').hide();
    })
	
	hideColumn('Branch_id')
	hideColumn('Id')

})
function successFunc(result) {

     jQuery.cookie("userMessageCok", result.message);

     if(result.data.errors=='Yes'){

         return;
     }
    location.reload();

}

var idToEdit;
var setupData = function () {

    var data = {}

    data.vehicleGroupName = jQuery('#vehicleGroupName').val()
    data.vehicleGroupCat = jQuery('#vehicleGroupCat').val()
	data.branchId = jQuery('#branch :selected').val();
	
    return data
}
var setupData2 = function () {
    alert("edit");
    data2 = setupData()
  	data2.id =idToEdit
    console.log(data2)
  	return data2
}

var setupConstraints = function () {

    var constraints = {

        vehicleGroupName : {presence: true},

        vehicleGroupCat: {presence: true,
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
    jQuery('#showVehicleGroup').flexAddData(result.message.sendData)
    total = result.message.sendData.total
	
	hideColumn('Branch_id')
	hideColumn('Id')
}

var total = 0
var rp = 10
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
	if(pageNo>=1)
		sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
	if(pageNo<=parseInt(total/rp)+1)
		sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
}
function onFirstPageRequest() {
    sendAjaxRequest('vehicleGroupData', {'pageNo': 1}, showReport)
}
function onLastPageRequest() {
    pageNo = parseInt(total / rp) + 1
    sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val())
    sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
}
function onRpChange() {
	rp = parseInt(jQuery('.pGroup select').val())
	sendAjaxRequest('vehicleGroupData',{'pageNo':1,'rp':rp}, showReport)
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
        //alert("first")
        jQuery('.flexigrid').hide();
        var c = 0
        jQuery('.trSelected', grid).each(function () {
            c += 1
        })
        if (c == 1) {
            //code for geting row data and sending to form
            jQuery('.trSelected', grid).each(function () {
                var editFields = Array()
                editFields.push({id: jQuery(this).data('id')})
                editFields.push({'vehicleGroupName': jQuery('td[abbr="Vehicle_Group_Name"] >div', this).html()})

                editFields.push({'vehicleGroupCat': jQuery('td[abbr="Category"] >div', this).html()})

                var div = jQuery('#addVehicleGroup')
                jQuery.each(editFields, function (k, v) {
                    for (var key in v) {
                        var value = v[key];
                        div.find(':input[id=' + key + ']').val(value)

                    }
                })
				
				var branchId = jQuery('td[abbr="Branch_id"] >div', this).html ();
				div.find('#branch').val(branchId);
				
                idToEdit=jQuery('td[abbr="Id"] >div', this).html()
                jQuery('.userMessage').text(" ");
                jQuery("#tableDiv").toggle('showOrHide')
                jQuery('#addVehicleGroup').toggle('showOrHide')
                div.find('.ok').text('Edit')
                div.find('.ok').removeClass('ok')
                    .addClass('editbutton')


            })
        }
        else {
            //alert('select single row to edit')
            displayUserMessageInCrud('emptyEditRow');
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
				delFields.id=jQuery('td[abbr="Id"] >div', this).html()
				//alert(delFields.id)
				sendAjaxRequest('delVehicleGroup',delFields,function(){
					jQuery('.userMessage').text('Vehicle Group Deleted');
					sendAjaxRequest('vehicleGroupData', setupDataFlexi(), showReport)
				})

			})
		}
		else {
			//alert('select single row to delete')
            displayUserMessageInCrud('emptyDeleteRow');
		}
    }

}

var resetForm = function() {
	jQuery('.error').text('');
	jQuery('#addVehicleGroup select').val('');
	jQuery('#addVehicleGroup input').val('');
	jQuery('.userMessage').text('');
}

var hideColumn = function(colName) {
	jQuery('th[abbr="' + colName + '"]').hide()
	jQuery('td[abbr="' + colName + '"]').hide()
}