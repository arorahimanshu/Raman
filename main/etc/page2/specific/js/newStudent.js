fitx.utils.require(['fitx', 'page2', 'newStudent'])
jQuery(window).load(function () {
    jQuery('#addStudent').hide();
    setupAJAXSubmit('unnecessary', 'newStudentFormAction', setupData, setupConstraints, '.ok', errorFunc, successFunc)
    setupAJAXSubmit('newStudentForm', 'editStudent', setupData2, setupConstraints, '.editbutton', errorFunc, successFunc)
    setupFlexiGrid('#student', undefined, "Welcome", undefined, undefined, undefined, undefined, classData)
    sendAjaxRequest('newStudentData', setupDataFlexi(), showReport)

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
				sendAjaxRequest('newStudentData', {'pageNo': pageNo}, showReport)
        }
    })

    jQuery('.add').click(function () {
		resetForm();
        jQuery('.userMessage').text(" ");
        jQuery('#newStudent').show();
        jQuery('.flexigrid').hide();
    })


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

    data.name = jQuery('#name').val()
    data.rno = jQuery('#rno').val()
    data.branch = jQuery('#branch :selected').val()
    data.marks = jQuery('#marks').val()

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

        name : {presence: true},

        marks: {presence: true,
            numericality: true}

    }
    return constraints
}
var errorFunc = function (data, error) {
   /*
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
     */

    return error

}

function createColModel(colList) {
    colModel = []
    jQuery.each(colList, function (k, v) {
        console.log(v)
        var dict = {
            display: v,
            name: v,
            width: 180,
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
    jQuery('#student').flexAddData(result.message.sendData)
    total = result.message.sendData.total


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
                editFields.push({'name': jQuery('td[abbr="Name"] >div', this).html()})
                editFields.push({'rno': jQuery('td[abbr="Roll No."] >div', this).html()})
                editFields.push({'branch': jQuery('td[abbr="Branch"] >div', this).html()})
                editFields.push({'marks': jQuery('td[abbr="Marks"] >div', this).html()})

                var div = jQuery('.newStudentForm')
                jQuery.each(editFields, function (k, v) {
                    for (var key in v) {
                        var value = v[key];
                        div.find(':input[id=' + key + ']').val(value)

                    }


                    })

                jQuery('.userMessage').text(" ");
                jQuery("#tablediv").toggle('showOrHide')
                jQuery('#newStudent').toggle('showOrHide')
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