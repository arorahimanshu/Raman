fitx.utils.require(['fitx', 'page2', 'vehicleGroupManagement'])
jQuery(window).load(function () {
    jQuery('#addVehicleGroup').hide();
    setupAJAXSubmit('vehicleGroupManagementForm', 'vehicleGroupManagementFormAction', setupData, setupConstraints, '.ok', errorFunc, successFunc)
    setupAJAXSubmit('vehicleGroupManagementForm', 'editVehicleGroup', setupData2, setupConstraints, '.editbutton', errorFunc, successFunc)
    setupFlexiGrid('#showVehicleGroup', undefined, "VehicleGroup Details", undefined, undefined, undefined, undefined, classData)
    sendAjaxRequest('vehicleGroupData', setupDataFlexi(), showReport)


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
            sendAjaxRequest('vehicleGroupData', auxiPaymentData(pageNo), showReport)
        }
    })

    jQuery('.add').click(function () {
        jQuery('#addVehicleGroup').show();
        jQuery('.flexigrid').hide();
    })

})
function successFunc() {
    location.reload()
}

var idToEdit;
var setupData = function () {
    alert('ADD')
    var data = {}

    data.vehicleGroupName = jQuery('#vehicleGroupName').val()
    data.vehicleGroupCat = jQuery('#vehicleGroupCat').val()


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
    console.log(result.message.sendData)
    jQuery('#showVehicleGroup').flexAddData(result.message.sendData)
    total = result.message.sendData.total
}

var total = 0
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
    sendAjaxRequest('vehicleGroupData', auxi(pageNo), showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
}
function onFirstPageRequest() {
    sendAjaxRequest('vehicleGroupData', {'pageNo': 1}, showReport)
}
function onLastPageRequest() {
    pageNo = parseInt(total / 10) + 1
    sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('vehicleGroupData', {'pageNo': pageNo}, showReport)
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
    if (com == "Edit") {
        alert("first")
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
                idToEdit=jQuery('td[abbr="Id"] >div', this).html()

                jQuery("#tableDiv").toggle('showOrHide')
                jQuery('#addVehicleGroup').toggle('showOrHide')
                div.find('.ok').text('Edit')
                div.find('.ok').removeClass('ok')
                    .addClass('editbutton')


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
				delFields.id=jQuery('td[abbr="Id"] >div', this).html()
				alert(delFields.id)
				sendAjaxRequest('delVehicleGroup',delFields,function(){
					sendAjaxRequest('vehicleGroupData', setupDataFlexi(), showReport)
				})

			})
		}
		else {
			alert('select single row to delete')
		}
    }

}