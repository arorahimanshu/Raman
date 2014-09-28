fitx.utils.require(['fitx', 'page2', 'newTravelReportForm']);

jQuery(window).load(function() {
    jQuery('.dateSelection input').datepicker();

    //setupAJAXSubmit('newReport1From', 'newReport1FormAction', setupData, setupConstraints, '.dateSelection button', null, successFunc);
    sendAjaxRequest('newTravelReportFormAction', setupData(), successFunc)

    jQuery('.from').datepicker({
        changeMonth: true,
        changeYear: true,
        yearRange: '-150:+0',
        dateFormat: 'DD, dd/MM/yy'
    });

    jQuery('.to').datepicker({
        changeMonth: true,
        changeYear: true,
        yearRange: '-150:+0',
        dateFormat: 'DD, dd/MM/yy'
    });
	
	jQuery('.showHideTableButton').click(function (evt){
		jQuery ('.table').toggle();
		jQuery ('.tableFooter').toggle();
		var target = evt.target;
		var text = target.textContent;
		if(text=="Hide") {
			target.textContent="Show";
		} else {
			target.textContent="Hide";
		}
	});
	
	
})

function setupData() {

    /*
	var from = dateFromDatePicker (jQuery('.from'))
	var to = dateFromDatePicker (jQuery('.to'))

	var specificFormData = {
		'fromDate' : from,
		'toDate' : to,
	}

    return specificFormData*/
    return {}
}

function dateFromDatePicker(element) {

    var date = element.datepicker('getDate');
    if (date) {
        data = [
            parseInt(date.getFullYear()),
            date.getMonth() + 1,
            date.getDate()
        ]
        return data
    }

}


function setupConstraints() {
    var specificFormConstraints = {}
    return specificFormConstraints
}

function getTravelReportRows(rawData) {
    rawData = rawData.message;

    function getRow() {
        runningDuration[runningDurationIndex] --;
        var totalRunningDuration = 0
        jQuery.each(runningDuration, function(index, duration) {
            totalRunningDuration += duration;
        })
        var avgSpeed = distanceTravelled / totalRunningDuration;
        row = {
            'vehicleModel': 'Empty',
            'distanceTravelled': convertDistance(distanceTravelled),
            'totalRunningDuration': convertDuration(totalRunningDuration),
            'totalIdleDuration': convertDuration(totalIdleDuration),
            'totalStopDuration': '0',
            'totalInactiveDuration': '0',
            'maxSpeed': convertMpsToKmph(maxSpeed),
            'avgSpeed': convertMpsToKmph(avgSpeed),
            'alert': 'empty'
        };
        return row;
    }

    function manageDistanceAndMaxSpeed(pathPoints) {
        if (pathPoints.length == 0 || pathPoints.length == 1) {
            return pathPoints;
        }
        var coordinates = [];
        jQuery.each(pathPoints, function(i, v) {
            coordinates[coordinates.length] = getPosition(v.position);
        })
        var distance = getDistanceFromPath(coordinates);
        var time = getTimeDifference(pathPoints[0].time, pathPoints[pathPoints.length - 1].time);
        var speed = distance / time;
        if (maxSpeed < speed) {
            maxSpeed = speed;
        }
        distanceTravelled += distance;
        pathPoints = [pathPoints[pathPoints.length - 1]];
        return pathPoints;
    }

    var currentVehicleId = rawData[0].vehicleId;
    var rows = {};
    rows[currentVehicleId] = {};
    var totalData = rawData.length;
    var minStopDuration = 60;
    var maxSpeedCalculationDuration = 5;
    var vehicleStop = false;
    var runningDurationInADay = 0;
    var runningDurationIndex = 0;
    var runningDuration = [0];
    var distanceTravelled = 0;
    var totalIdleDuration = 0;
    var maxSpeed = 0;
    var pathPoints = [];
    var firstTime = rawData[0].time;
    var lastTime = 0;

    jQuery.each(rawData, function(index, obj) {
        var currentPosition = getPosition(obj.position);
        if (currentVehicleId != obj.vehicleId) {
            manageDistanceAndMaxSpeed(pathPoints);
            var extraTime = getTimeDifference(rawData[index - 1].time, obj.time);
            runningDuration[runningDurationIndex] -= extraTime;
            rows[currentVehicleId] = getRow();
            currentVehicleId = obj.vehicleId;
            vehicleStop = false;
            runningDurationIndex = 0;
            runningDuration = [0];
            distanceTravelled = 0;
            totalIdleDuration = 0;
            maxSpeed = 0;
            pathPoints = [];
        }
        if (vehicleStop == false) {
            if ((index + minStopDuration < totalData) && (currentVehicleId == rawData[index + minStopDuration]) && (obj.position == rawData[index + minStopDuration])) {
                pathPoints = manageDistanceAndMaxSpeed(pathPoints);
                vehicleStop = true;
                totalIdleDuration += getTimeDifference(obj.time, rawData[index + 1].time);
                return true;
            }
            if (obj.time.hour == 0 && obj.time.minute == 0 && obj.time.second == 0) {
                runningDuration[runningDurationIndex] -= getTimeDifference(rawData[index - 1].time, obj.time);
                runningDurationIndex++;
                runningDuration[runningDurationIndex] = 0

            }
            if (index == totalData - 1) {
                return false;
            }
            var nextVehicleId = rawData[index + 1].vehicleId;
            pathPoints[pathPoints.length] = obj;
            runningDuration[runningDurationIndex] += getTimeDifference(obj.time, rawData[index + 1].time);
            if (currentVehicleId == nextVehicleId) {
                if (pathPoints.length % maxSpeedCalculationDuration == 0) {
                    pathPoints = manageDistanceAndMaxSpeed(pathPoints);
                }
            } else {
                pathPoints = manageDistanceAndMaxSpeed(pathPoints);
            }
        } else {
            totalIdleDuration += getTimeDifference(obj.time, rawData[index + 1].time);
            var nextVehicleId = rawData[index + 1].vehicleId;
            if (currentVehicleId != nextVehicleId) {
                vehicleStop = false;
            } else if (obj.position != rawData[index + 1].position) {
                vehicleStop = false;
            }
        }
    })

    pathPoints = manageDistanceAndMaxSpeed(pathPoints);
    rows[currentVehicleId] = getRow();

    return rows;
}


function makeTravelReport(rawData) {
    allRows = getTravelReportRows(rawData);
	rowsPerPage = parseInt(jQuery ('.rowsPerPage')[0].value);
	
	displayableRows = [];
	jQuery.each (allRows,function (key,data){
		data['vehicleId']=key;
		displayableRows.push (data);
	});
	
	jQuery('.currentPage').val(0);
	
	displayRows(displayableRows,1);
	
	jQuery('.rowsPerPage').change(function(evt){
		var target = evt.target;
		rowsPerPage = target.value;
		displayRows(displayableRows,1);
	});
	
	jQuery ('.firstPage').click(function(){
		displayRows(displayableRows,1);
	});
	
	jQuery ('.previousPage').click(function(){
		var currentPage = jQuery('.currentPage')
		var cp = currentPage.val();
		if (cp > 1) {
			cp--;
			displayRows(displayableRows,cp);
		}
	});
	
	jQuery ('.nextPage').click(function(){
		var currentPage = jQuery('.currentPage')
		var totalPages = jQuery ('.totalPages').text();
		var cp = currentPage.val();
		if (cp < totalPages) {
			cp++;
			displayRows(displayableRows,cp);
		}
	});
	
	jQuery ('.lastPage').click(function(){
		var totalPages = jQuery ('.totalPages').text();
		displayRows(displayableRows,totalPages);
	});
	
	jQuery ('.refreshButton').click(function (){
		sendAjaxRequest('newTravelReportFormAction', setupData(), successFunc)
	});
	
}

function displayRows(rows, pageNo) {
	var totalRows = rows.length;
	var totalPages = parseInt(totalRows/rowsPerPage);
	if(totalRows % rowsPerPage != 0)
		totalPages++;
	var firstRow = 0;
	var lastRow = totalRows - 1;
	if (totalRows > rowsPerPage) {
		firstRow = (pageNo-1) * rowsPerPage;
		if (pageNo < totalPages)
			lastRow = firstRow + rowsPerPage - 1;
	}
	rows = rows.slice (firstRow,lastRow+1);
	jQuery ('.currentPage').val (pageNo);
	jQuery ('.totalPages').text (totalPages);
	jQuery ('.firstItem').text (firstRow+1);
	jQuery ('.lastItem').text (lastRow+1);
	jQuery ('.totalItems').text(totalRows);
	
	jQuery('table tbody').remove();
    var table = ''
    jQuery.each(rows, function(index, data) {
        var row = '<tbody><tr>';
        row += '<td>' + 'Demo' + '</td>';
        row += '<td>' + 'Delhi' + '</td>';
        row += '<td>' + data.vehicleModel + '</td>';
        row += '<td>' + 'Driver' + '</td>';
        row += '<td>' + 'Start' + '</td>';
        row += '<td>' + data.distanceTravelled + '</td>';
        row += '<td>' + data.totalRunningDuration + '</td>';
        row += '<td>' + data.totalIdleDuration + '</td>';
        row += '<td>' + data.totalStopDuration + '</td>';
        row += '<td>' + data.totalInactiveDuration + '</td>';
        row += '<td>' + data.avgSpeed + '</td>';
        row += '<td>' + data.maxSpeed + '</td>';
        row += '<td>' + '0' + '</td>';
        row += '<td>' + '0' + '</td>';
        row += '<td>' + data.alert + '</td>';
        row += '<td>' + 'end' + '</td>';
        row += '</tr></tbody>';
        table += row;
    })
    jQuery('table').append(table);
}
function successFunc(rawData) {
    makeTravelReport(rawData);
}