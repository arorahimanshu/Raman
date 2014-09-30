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
        console.log(v)
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
	jQuery ('.filter .company select').change (resetCompany);
	jQuery ('.filter .branch select').change (resetBranch);
	jQuery ('.filter .branch select').change (resetVehicleGroup);
}

function resetCompany () {
	resetBranch();
}

function resetBranch () {
	addOptions ('.branch', '.company');



	/*
	if (company == 'All') {
		var branches1 = originalFilter.find ('.branch select option').clone ();
		branches.append (branches1);
	} else {
		branches.append (originalFilter.find ('.branch select .All').clone ());
		jQuery.each (allVehiclesListNested, function (index1, org) {
			if(org['orgDetails']['orgName'] == company) {
				jQuery.each (org['branches'], function (index2, branch) {
					var id = '#' + branch['branchDetails']['branchId'];
					var options = originalFilter.find ('.branch select .' + company);
					branches.append (options);
				});
			}
		});
		var t = 0;
	}
	*/
	resetVehicleGroup();
}

function resetVehicleGroup () {
	var company = jQuery ('.filter .company select option:selected');
	var branch = jQuery ('.filter .branch select option:selected');
}

function addOptions (currentSelector, parentSelector) {
	var parentString = jQuery ('.filter ' + parentSelector + ' select option:selected').text ();

	var currentIdentifierString = '.filter ' + currentSelector + ' select';
	var currentElement = jQuery (currentIdentifierString);
	currentElement.empty ();

	if (parentString == 'All') {
		var currentSelect1 = originalFilter.find (currentIdentifierString + ' option').clone ();
		currentElement.append (currentSelect1);
	} else {
		currentElement.append (originalFilter.find (currentIdentifierString + ' .All').clone ());
		jQuery.each (allVehiclesListNested, function (index1, org) {
			if (currentSelector != 'org') {

			}
			if(org['orgDetails']['orgName'] == company) {
				jQuery.each (org['branches'], function (index2, branch) {
					var options = originalFilter.find ('.branch select .' + company);
					branches.append (options);
				});
			}
		});
		var t = 0;
	}
}