fitx.utils.require(['fitx', 'page2', 'newreport1Form']);

jQuery(window).load(function () {
	jQuery ('.dateSelection input').datepicker ();

    setupAJAXSubmit('newReport1From', 'newReport1FormAction', setupData, setupConstraints, '.dateSelection button', null, successFunc);
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

function getReport1Rows (rawData) {
	rawData=rawData.message;
	function getRow() {
		runningDuration[runningDurationIndex]--;
		var totalRunningDuration = 0
		jQuery.each (runningDuration, function (index, duration) {
			totalRunningDuration += duration;
		})
		var avgSpeed = distanceTravelled/totalRunningDuration;
		var runningDurationInADay = totalRunningDuration/runningDuration.length;
		row = {
			'vehicleName' : 'Empty',
			'vehicleModel' : 'Empty',
			'runningDurationInADay' : convertDuration(runningDurationInADay),
			'distanceTravelled' : convertDistance(distanceTravelled),
			'totalIdleDuration' : convertDuration(totalIdleDuration),
			'maxSpeed' : convertMpsToKmph(maxSpeed),
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
	
	jQuery.each (rawData, function (index,obj) {
		var currentPosition = getPosition (obj.position);
		if (currentVehicleId != obj.vehicleId) {
			manageDistanceAndMaxSpeed (pathPoints);
			var extraTime = getTimeDifference (rawData[index-1].time, obj.time);
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
			if (   (index + minStopDuration < totalData)
			    && (currentVehicleId == rawData[index + minStopDuration])
			    && (obj.position == rawData[index + minStopDuration])) {
				pathPoints = manageDistanceAndMaxSpeed (pathPoints);
				vehicleStop = true;
				totalIdleDuration += getTimeDifference (obj.time, rawData[index+1].time);
				return true;
			}
			if (   obj.time.hour==0 
				&& obj.time.minute==0 
				&& obj.time.second==0) {
				runningDuration[runningDurationIndex]-= getTimeDifference (rawData[index-1].time, obj.time);
				runningDurationIndex++;
				runningDuration[runningDurationIndex]=0

				}
			if (index == totalData-1) {
				return false;
			}
			var nextVehicleId = rawData[index+1].vehicleId;
			pathPoints[pathPoints.length] = obj;
			runningDuration[runningDurationIndex] += getTimeDifference (obj.time, rawData[index+1].time);
			if (currentVehicleId == nextVehicleId) {
				if (pathPoints.length % maxSpeedCalculationDuration == 0) {
					pathPoints = manageDistanceAndMaxSpeed (pathPoints);
				}
			} else {
				pathPoints = manageDistanceAndMaxSpeed (pathPoints);
			}
		} else {
			totalIdleDuration += getTimeDifference (obj.time, rawData[index+1].time);
			var nextVehicleId = rawData[index+1].vehicleId;
			if (currentVehicleId != nextVehicleId) {
				vehicleStop = false;
			} else if (obj.position != rawData[index+1].position) {
				vehicleStop = false;
			}
		}
	})
		
	pathPoints = manageDistanceAndMaxSpeed (pathPoints);
	rows[currentVehicleId] = getRow();
		
	return rows;
}

function makeReport1(rawData) {
		var rows = getReport1Rows (rawData);
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
			row += '<td>' + data.runningDurationInADay + '</td>';
			row += '<td>' + data.distanceTravelled + '</td>';
			row += '<td>' + data.totalIdleDuration + '</td>';
			row += '<td>' + data.maxSpeed + '</td>';
			row += '<td>' + data.avgSpeed + '</td>';
			row += '</tr></tbody>';
			table += row;
		})
		jQuery('table').append(table);
	}
	
	function successFunc (rawData) {
		makeReport1 (rawData);
	}


