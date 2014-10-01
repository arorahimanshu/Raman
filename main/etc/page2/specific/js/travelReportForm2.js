fitx.utils.require(['fitx', 'page2', 'newTravelReportForm2']);

jQuery (window).load (function (){
	setupFlexiGrid('#showTravelReport', undefined, "Travel Report", undefined, 1650, undefined, undefined, classData);

	sendAjaxRequest('travelReportVehicleListNested', {}, setupVehicles);

	onLoadTravelReport();
});

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

var originalFilter = 0;
var allVehiclesListNested = 0;

function setupVehicles(data) {
	allVehiclesListNested = JSON.parse(data);
	originalFilter = jQuery('.filter').clone();
	print (originalFilter);
}

function onLoadTravelReport() {
	jQuery ('.filter .company select').change (resetBranch);
	jQuery ('.filter .branch select').change (resetVehicleGroup);
}

function resetBranch () {
	filterOptions ('.branch', '.company');
	resetVehicleGroup();
}

function resetVehicleGroup () {
	filterOptions ('.vehicleGroup', '.branch');
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