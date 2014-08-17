fitx.utils.require(['fitx', 'page2', 'newreport4Form']);

jQuery(window).load(function () {
	jQuery ('.dateSelection input').datepicker ();

    setupAJAXSubmit('newReport4From', 'newReport4FormAction', setupData, setupConstraints, '.dateSelection button', null, successFunc);
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
})

function setupData() {
    
	var from = dateFromDatePicker (jQuery('.from'))
	var to = dateFromDatePicker (jQuery('.to'))

	var specificFormData = {
		'fromDate' : from,
		'toDate' : to,
	}

    return specificFormData
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

function getReport4Rows (rawData) {
	rawData = rawData.message;
	
	function getRow() {
		var avgSpeed = distanceTravelled/runningDuration;
		row = {
			'vehicleName' : 'Empty',
			'vehicleModel' : 'Empty',
			'runningDuration' : convertDuration(runningDuration),
			'distanceTravelled' : convertDistance(distanceTravelled),
			'stopDuration' : convertDuration(stopDuration),
			'noOfStops' : noOfStops,
			'avgSpeed' : convertMpsToKmph(avgSpeed)
		};
		return row;
	}
	
	function manageDistanceAndMaxSpeed (pathPoints) {
		if (pathPoints.length == 0 || pathPoints.length == 1) {
			return pathPoints;
		}
		var coordinates = [];
		jQuery.each (pathPoints,function(i,v){
			coordinates[coordinates.length]=getPosition(v.position);
		})
		var distance = getDistanceFromPath (coordinates);
		var time = getTimeDifference (pathPoints[0].time, pathPoints[pathPoints.length-1].time);
		var speed = distance/time;
		if (maxSpeed < speed) {
			maxSpeed = speed;
		}
		distanceTravelled += distance;
		pathPoints = [pathPoints[pathPoints.length-1]];
		return pathPoints;
	}
	
	function manageDistance (pathPoints) {
		if (pathPoints.length == 0 || pathPoints.length == 1) {
			return pathPoints;
		}
		var distance = getDistanceFromPath (pathPoints);
		distanceTravelled += distance;
		pathPoints = [pathPoints[pathPoints.length-1]];
		return pathPoints;
	}
	
	var currentVehicleId = rawData[0].vehicleId;
	var rows = {};
	rows[currentVehicleId] = {};
	var totalData = rawData.length;
	var minStopDuration = 1;
	var vehicleStop = false;
	var runningDuration = 0;
	var distanceTravelled = 0;
	var stopDuration = 0;
	var noOfStops = 0;
	var pathPoints = [];
	
	jQuery.each (rawData, function (index,obj) {
		var currentPosition = getPosition (obj.position);
		if (currentVehicleId != obj.vehicleId) {
			pathPoints = manageDistanceAndMaxSpeed (pathPoints);
			var extraTime = getTimeDifference (rawData[index-1].time, obj.time);
			runningDuration -= extraTime;
			rows[currentVehicleId] = getRow();
			currentVehicleId = obj.vehicleId;
			vehicleStop = false;
			runningDuration = 0;
			distanceTravelled = 0;
			stopDuration = 0;
			maxSpeed = 0;
			noOfStops = 0;
			pathPoints = [];
		}
		if (index == totalData-1) {
			return false;
		}
		if (vehicleStop == false) {
			if (   (index + minStopDuration < totalData)
			    && (currentVehicleId == rawData[index + minStopDuration])
			    && (obj.position == rawData[index + minStopDuration].position)) {
				pathPoints = manageDistance(pathPoints);
				vehicleStop = true;
				noOfStops++;
				stopDuration += getTimeDifference (obj.time, rawData[index+1].time);
				return true;
			}
			var nextVehicleId = rawData[index+1].vehicleId;
			if (currentVehicleId == nextVehicleId) {
				pathPoints[pathPoints.length] = currentPosition;
				runningDuration += getTimeDifference (obj.time, rawData[index+1].time);
			} else {
				pathPoints = manageDistance (pathPoints);
			}
		} else {
			stopDuration += getTimeDifference (obj.time, rawData[index+1].time);
			var nextVehicleId = rawData[index+1].vehicleId;
			if (currentVehicleId != nextVehicleId) {
				vehicleStop = false;
			}
			else if (obj.position != rawData[index+1].position) {
				vehicleStop = false;
			}
			
		}
	})
	
	pathPoints = manageDistance(pathPoints);
	rows[currentVehicleId] = getRow();
		
	return rows;
}

function makeReport4(rawData) {
	var rows = getReport4Rows (rawData);
	jQuery('table tbody').remove();
	var table = ''
	jQuery.each (rows, function (key, data){
		var row = '<tbody><tr>';
		row += '<td>' + key + '</td>';
		row += '<td>' + data.vehicleName + '</td>';
		row += '<td>' + data.vehicleModel + '</td>';
		var from = jQuery ('.from').val ();
		var to = jQuery ('.to').val ();
		row += '<td>' + from + '-' + to + '</td>';
		row += '<td>' + data.runningDuration + '</td>';
		row += '<td>' + data.distanceTravelled + '</td>';
		row += '<td>' + data.stopDuration + '</td>';
		row += '<td>' + data.noOfStops + '</td>';
		row += '<td>' + data.avgSpeed + '</td>';
		row += '</tr></tbody>';
		table += row;
	})
	jQuery('table').append(table);
}
	
function successFunc (rawData) {
	makeReport4 (rawData);
}
