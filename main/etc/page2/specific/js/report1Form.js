fitx.utils.require(['fitx', 'page2', 'newReport1Form']);

jQuery (window).load (function (){
	setupFlexiGrid('#showReport1', undefined, "Speed Report", undefined, undefined, undefined, undefined, classData);

	setupAJAXSubmit('report1', 'newReport1FormAction', setupData, setupConstraints, '.submit', errorFunc,successFunc,showReport);



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
	rp = parseInt(jQuery('.pGroup select option:selected').text())
	onLoadReport1();
});

function setupData() {

	var curdate = new Date();
    var offset =-1* curdate.getTimezoneOffset();
    var gmtAdjust=offset*60;
		
	var fromDate = returnDate ('fromDate');
	var toDate = returnDate ('toDate');

	var specificData = {
		'fromDate' : fromDate,
		'toDate' : toDate,
		'gmtAdjust' : gmtAdjust
	};
    // Vehicle Selector > vehicle id Picker
    var idList = []
	jQuery('.vsVehicleId:checked').each (function(){
		var vehicleId = jQuery (this).data( "details" ).id

		idList.push (vehicleId)
	})
    specificData['vehicleList']=idList

    //-------------------------------------
	rp = parseInt(jQuery('.pGroup select option:selected').text())
	specificData['rp'] = rp

	return specificData;
}

var setupConstraints = function () {

    var constraints = {

        fromDate : {presence: true},
        toDate: {presence: true},
    }

    var flag =1;
	jQuery('.vsVehicleId:checked').each(function () {
		flag = 0;
	})

	if (flag == 1) {
	   var message={}
	   message = { "message":"Vehicle Not Selected",
	               "data":{"errors":"Yes"}
	             }


       successFunc(message)
       return;
	}

    return constraints
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
        title: title,
        useRp: true,
        rp: noOfPages,
        showTableToggleBtn: true,
        width: width,
        height: height,
        singleSelect: singleSelect
    })
}

function createColModel(colList) {
    colModel = []
    jQuery.each(colList, function (k, v) {
        var dict = {
            display: v,
            name: v,
            width: v.length * 6,
            align: 'center',
            sortable: true
        }
        colModel.push(dict)
    })
    return colModel

}

function onLoadReport1() {

	jQuery('.pPrev.pButton').click(function () {
        onPrevPageRequest()
    })
    jQuery('.pNext').click(function () {
        onNextPageRequest()
    })
    jQuery('.pGroup select').change(function () {
        //onRpChange()
		rp = parseInt(jQuery('.pGroup select option:selected').text())
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
            sendAjaxRequest('newReport1FormAction', auxiPaymentData(pageNo), showReport)
        }
    })
}


function showReport(result) {
	jQuery('#showReport1').flexAddData(result.message.sendData)
    total = result.message.sendData.total
}

var total = 0
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
    sendAjaxRequest('newReport1FormAction', auxi(pageNo), showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('newReport1FormAction', {'pageNo': pageNo}, showReport)
}
function onFirstPageRequest() {
    sendAjaxRequest('newReport1FormAction', {'pageNo': 1}, showReport)
}
function onLastPageRequest() {
	if (!rp)
		rp = 10
    pageNo = parseInt(total / rp) + 1
    sendAjaxRequest('newReport1FormAction', {'pageNo': pageNo}, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('newReport1FormAction', {'pageNo': pageNo}, showReport)
}


var errorFunc = function (data, error) {


	return error;

}

function successFunc(result) {

     if(result.data.errors=='Yes'){
        jQuery('.userMessage').text(result.message);
         return;
     }

    location.reload()
    }
