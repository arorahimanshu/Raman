fitx.utils.require(['fitx', 'page2', 'newDashboardForm']);

jQuery (window).load (function (){
	setupFlexiGrid('#showDashboard', undefined, "Dashboard", undefined, 1300, undefined, undefined, classData);

	sendAjaxRequest('dashboardVehicleListNested', {}, setupVehicles);
	
	setupAJAXSubmit('dashboard', 'newDashboardFormAction', setupData2, setupConstraints, '.submit', errorFunc,showReport);

	
	setupData();
	sendAjaxRequest('newDashboardFormAction', setupData2(), showReport);
	
	var requestTime = 60000;			//in milliseconds
	
	trackRequest=setInterval(function () {
            sendAjaxRequest('newDashboardFormAction', setupData2(), showReport)
        }, requestTime);

	rp = parseInt(jQuery('.pGroup select option:selected').text())
	onLoadDashboard();
	hideColumn('Vehicle Information')
});

function setupData() {
	var curdate = new Date();
    var offset =-1* curdate.getTimezoneOffset();
    gmtAdjust=offset*60;
}

function setupData2() {
    var curdate = new Date();
    var offset =-1* curdate.getTimezoneOffset();
    var gmtAdjust=offset*60;

	var specificData = {
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

    return
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
            //width: v.length *6,
            width:125,
            align: 'center',
            sortable: true
        }
        colModel.push(dict)
    })
    return colModel

}

var originalFilter = 0;
var allVehiclesListNested = 0;

function setupVehicles(data) {
	allVehiclesListNested = JSON.parse(data);
	originalFilter = jQuery('.filter').clone();
}

function onLoadDashboard() {
	jQuery ('.filter .company select').change (resetBranch);
	jQuery ('.filter .branch select').change (resetVehicleGroup);
	
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
			var data = setupData2()
			data.pageNo = pageNo
			if(pageNo>=1 && pageNo<=parseInt(total/rp)+1)
				sendAjaxRequest('newDashboardFormAction', data, showReport)
        }
    })
}

function resetBranch () {
	filterOptions ('.branch', '.company');
	resetVehicleGroup();
}

function resetVehicleGroup () {
	filterOptions ('.vehicleGroup', '.branch');
	
	setupData();
}

function filterOptions (currentSelector, parentSelector) {
	var parentString = jQuery ('.filter ' + parentSelector + ' select option:selected').text ();

	var currentIdentifier = currentSelector + ' select';
	var currentElement = jQuery ('.filter ' + currentIdentifier);
	currentElement.empty ();

	if (parentString == 'All') {
		currentElement.append (originalFilter.find (currentIdentifier + ' option').clone ());
	} else {
		currentElement.append (originalFilter.find (currentIdentifier + ' .All').clone ());
		var options = originalFilter.find (currentIdentifier + ' .' + parentString).clone ();
		currentElement.append (options);
	}
}

function showReport(result) {


    console.log(result.data);
    if (result.message.sendData.rows.length == 0){
              jQuery('.userMessage').text('No Data Present');
              return
        }
	jQuery('#showDashboard').flexAddData(result.message.sendData)
    total = result.message.sendData.total

	hideColumn('Vehicle Information')
}

var total = 0
var rp = 10
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
	var data = setupData2()
	data.pageNo = pageNo
	if(pageNo>=1)
		sendAjaxRequest('newDashboardFormAction', data, showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
	var data = setupData2()
	data.pageNo = pageNo
	if(pageNo<=parseInt(total/rp)+1)
		sendAjaxRequest('newDashboardFormAction', data, showReport)
}
function onFirstPageRequest() {
	var data = setupData2()
	data.pageNo = 1
    sendAjaxRequest('newDashboardFormAction', data, showReport)
}
function onLastPageRequest() {
	var pageNo = parseInt(total / rp) + 1
	var data = setupData2()
	data.pageNo = pageNo
    sendAjaxRequest('newDashboardFormAction', data, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val())
	var data = setupData2()
	data.pageNo = pageNo
    sendAjaxRequest('newDashboardFormAction', data, showReport)
}
function onRpChange() {
	rp = parseInt(jQuery('.pGroup select').val())
	var data = setupData2()
	data.pageNo = 1
	data.rp=rp
    sendAjaxRequest('newDashboardFormAction', data, showReport)
}


var errorFunc = function (data, error) {

	return error;
}

function successFunc(result) {
     //alert('b');
     if(result.data.errors=='Yes'){
        jQuery('.userMessage').text(result.message);
         return;
     }

    location.reload()
}

var hideColumn = function(colName) {
	jQuery('th[abbr="' + colName + '"]').hide()
	jQuery('td[abbr="' + colName + '"]').hide()
}
