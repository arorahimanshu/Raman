fitx.utils.require(['fitx', 'page2', 'newReport4Form']);

jQuery (window).load (function (){
	setupFlexiGrid('#showReport4', undefined, "Stoppage Summary", undefined, undefined, undefined, undefined, classData);

	setupAJAXSubmit('report4', 'newReport4FormAction', setupData, setupConstraints, '.submit', null, showReport);
	
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
	onLoadReport4();
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
	
	rp = parseInt(jQuery('.pGroup select option:selected').text())
	specificData['rp'] = rp
	
	return specificData;
}

function setupConstraints() {
	return null;
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

function onLoadReport4() {

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
            sendAjaxRequest('newReport4FormAction', auxiPaymentData(pageNo), showReport)
        }
    })
}


function showReport(result) {
	jQuery('#showReport4').flexAddData(result.message.sendData)
    total = result.message.sendData.total
}

var total = 0
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
    sendAjaxRequest('newReport4FormAction', auxi(pageNo), showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('newReport4FormAction', {'pageNo': pageNo}, showReport)
}
function onFirstPageRequest() {
    sendAjaxRequest('newReport4FormAction', {'pageNo': 1}, showReport)
}
function onLastPageRequest() {
	if (!rp)
		rp = 10
    pageNo = parseInt(total / rp) + 1
    sendAjaxRequest('newReport4FormAction', {'pageNo': pageNo}, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('newReport4FormAction', {'pageNo': pageNo}, showReport)
}