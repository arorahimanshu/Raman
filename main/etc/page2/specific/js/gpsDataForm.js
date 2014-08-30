fitx.utils.require(['fitx', 'page2', 'newGpsDataForm']);

jQuery(window).load(function () {
    //setupAJAXSubmit('newGpsDataFrom', 'newGpsDataFormAction', setupData, setupConstraints, '.searchButton', null, successFunc);
	//sendAjaxRequest('newGpsDataFormVehicleList',{},allVehicles)

	onLoad_liveTracking()

});
var speedLimit = false;
var maxSpeed = 0;
var unitAnimationSpeed = 10000;
var vehiclesData = {};
var map;
var rawData;
var marker;
var previousPath;
var trackRequestTime = 10000;

function initializeMap() {
    var centre = new google.maps.LatLng(23.25, 77.417);
    var mapOptions = setMapProperties(12, centre, google.maps.MapTypeId.ROADMAP);
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
}

function getColor(vehicleId) {
    switch (vehicleId) {
        case 1:
            return '#FF0000';
        case 2:
            return '#00FF00';
        case 3:
            return '#0000FF';
        case 4:
            return '#000000';
    }
    return '#FFFFFF';
}

function getIcon(vehicleId) {
    switch (vehicleId) {
        case 1:
            return './etc/page2/specific/images/red.jpg'
        case 2:
            return './etc/page2/specific/images/green.jpg'
        case 3:
            return './etc/page2/specific/images/blue.jpg'
        case 4:
            return './etc/page2/specific/images/black.jpg'
    }
    return './etc/page2/specific/images/white.jpg'
}

function successFunc(rawData) {
    rawData = rawData.message;

	if (rawData == undefined || rawData.length == 0)
		return;

    map.setCenter(getPositionObject(rawData[0].position));

    function animatePath(index) {
        if (index < rawData.length) {
            var obj = rawData[index];
            if(obj.found == "yes") {

            var currentId = obj.vehicleId;
            if (jQuery ('.remainingVehicles #' + currentId)) {
            	jQuery ('.remainingVehicles').remove ('#' + currentId)
            }
            var position = getPositionObject(obj.position);

			try {
                vehiclesData[currentId].path.push(position);
                vehiclesData[currentId].previousTime = vehiclesData[currentId].currentTime;
                vehiclesData[currentId].currentTime = obj.time;

                vehiclesData[currentId].previousPosition = vehiclesData[currentId].currentPosition;
                vehiclesData[currentId].currentPosition = position;

                var pathLength = vehiclesData[currentId].path.length;

                if (pathLength > 1) {
                    var time = getTimeDifference(vehiclesData[currentId].previousTime, vehiclesData[currentId].currentTime);
                    var distance = google.maps.geometry.spherical.computeDistanceBetween(vehiclesData[currentId].previousPosition, vehiclesData[currentId].currentPosition);
                    vehiclesData[currentId].totalDistance += convertMToKm(distance);
                    var speed = obj.speed;
                    vehiclesData[currentId].speed = speed;
                    setTimeout(function () {
                        var path = setPath(vehiclesData[currentId].path, vehiclesData[currentId].color);
                        if (vehiclesData[currentId].visible == true) {
                            vehiclesData[currentId].oldFlightPaths.push(path);
                            drawLine(path, map);
                            vehiclesData[currentId].marker.setMap(map);
                            vehiclesData[currentId].marker.setPosition(getPositionObject(obj.position));
                        } else {
                            jQuery.each(vehiclesData[currentId].oldFlightPaths, function (index, p) {
                                p.setMap(null);
                            });
                            vehiclesData[currentId].marker.setMap(null);
                        }
                        animatePath(index + 1);
                        if (speed > vehiclesData[currentId].maxSpeed) {
                            if (vehiclesData[currentId].checkBrokenSpeedLimit == true) {
                                vehiclesData[currentId].brokenSpeedLimit++;
                            }
                            vehiclesData[currentId].checkBrokenSpeedLimit = false;
                            if (index == rawData.length - 1 || currentId != rawData[index + 1].vehicleId) {
                                vehiclesData[currentId].checkBrokenSpeedLimit = true;
                            }
                        } else {
                            vehiclesData[currentId].checkBrokenSpeedLimit = true;
                        }
                    }, 2000);//unitAnimationSpeed / vehiclesData[currentId].speed);
                } else {
                    animatePath(index + 1);
                }
            } catch (err) {

                var name = 'empty';

                var marker = new google.maps.Marker({
                    position: position,
                    icon: getIcon(currentId)
                });
                marker.setMap(map);

                var infoWindowContent = getLiveInfoWindowContent('empty', 'empty', 0, 0, 0);//, 0, 0, 0);
                var infoWindow = new google.maps.InfoWindow({
                    content: infoWindowContent
                });
                infoWindow.open(map, marker);

				/*
                var div = jQuery('<div/>', {
                    'class': 'vehicle' + currentId,
                });

                div.append('<input class="vehicleId" type="checkbox" value="' + currentId + '" checked> vehicle ' + currentId + '</input>')

                jQuery('<span/>', {
                    'class': 'ign',
                    'text': ' IGN' + '-'
                }).appendTo(div);

                jQuery('<span/>', {
                    'class': 'pwr',
                    'text': 'PWR' + '-'
                }).appendTo(div);

                jQuery('<span/>', {
                    'class': 'ac',
                    'text': 'AC' + '-'
                }).appendTo(div);

                jQuery('<span/>', {
                    'class': 'gps',
                    'text': 'GPS' + '-'
                }).appendTo(div);

                jQuery('<span/>', {
                    'class': 'path',
                    'text': 'Show Path' + '-'
                }).appendTo(div);

                jQuery('<span/>', {
                    'class': 'playback',
                    'text': 'Playback' + '-'
                }).appendTo(div);

                div.hide();

                div.appendTo('.delhi');

                jQuery('.delhi .vehicle' + currentId + ' .vehicleId').change(function (evt) {
                    var parent = jQuery(evt.target).parent();
                    var vehicleId = parseInt(parent[0].className.substring(7));
                    vehiclesData[vehicleId].visible = !vehiclesData[vehicleId].visible;
                });
				*/
                vehiclesData[currentId] = {
                    'vehicleName': name,
                    'companyName': name,
                    'totalDistance': 0,
                    'color': getColor(currentId),
                    'marker': marker,
                    'infoWindow': infoWindow,
                    'path': [position],
                    'previousTime': 0,
                    'currentTime': obj.time,
                    'previousPosition': 0,
                    'currentPosition': position,
                    'speed': 0,
                    'maxSpeed': 20,
                    'brokenSpeedLimit': 0,
                    'checkBrokenSpeedLimit': true,
                    'visible': true,
                    'oldFlightPaths': []
                };

                animatePath(index + 1);
            }

            var currentData = vehiclesData[currentId];

            vehiclesData[currentId].infoWindow.setContent(getLiveInfoWindowContent(currentData.vehicleName, currentData.companyName, currentData.speed, currentData.totalDistance, currentData.brokenSpeedLimit));//, 0, 0, 0));
		} else {
			manageVehiclesWithNoTrack (obj);
			animatePath (index+1);
		}
        }
    }

    animatePath(0);
}


google.maps.event.addDomListener(window, 'load', initializeMap);

/*
vehicleIdsWithNoData = []
function allVehicles(result) {
	result = JSON.parse(result)
	jQuery.each (result, function (index, branch){
		var branchName = branch['branchDetails']['branchName']
		var vehicleGroups = branch['vehicleGroups']
		jQuery.each (vehicleGroups, function (i, vehicleGroup){
			var vehicleGroupName = vehicleGroup['vehicleGroupDetails']['vehicleGroupName']
			var vehicles = vehicleGroup['vehicles']
			jQuery.each (vehicles, function (j, vehicle){
				vehicleIdsWithNoData.push(vehicle['value'])
			})
		})
	})
}
*/

function onLoad_liveTracking () {
	//jQuery ('.branch').hide ()
	//jQuery ('.vehicleGroup').hide ()
	//jQuery ('.vehicle').hide ()

	jQuery ('.vehicle').change (function (){
		setupCarsAndTime ();
	});
	setupCarsAndTime ();

}

var carsToTrack = []
var trackRequest;
function setupCarsAndTime () {
	clearInterval(trackRequest)
	carsToTrack = []
	for (var key in vehiclesData) {
		try {
			vehiclesData[key].visible = false;
		} catch (err) {
		}
	}
    jQuery('.vehicle:checked').each(function () {
    	var id = jQuery (this).prop ('value');
        carsToTrack.push(id)
		try {
        	vehiclesData[id].visible = true;
        } catch (err) {
        }
    })
    if (carsToTrack != null && carsToTrack.length!=0) {

        var specific={}
        var curdate = new Date()
        var offset =-1* curdate.getTimezoneOffset()
        specific.gmt=(parseInt(offset/60)*3600)+(offset%60)*60
        specific.carToTracked=carsToTrack

        sendAjaxRequest('newCarSetup', specific, undefined);

        trackRequest=setInterval(function () {
            sendAjaxRequest('newGpsDataFormAction',undefined,successFunc)
        }, trackRequestTime);
    }
}

function manageVehiclesWithNoTrack (obj) {
	var id = obj.vehicleId;
	var remainingVehicles = jQuery ('.remainingVehicles');
	var notFoundId = remainingVehicles.find ("#" + id);
	if(notFoundId == undefined || notFoundId.length == 0) {
		remainingVehicles.append ('<div id="' + id + '"></div>')
	}
	if (obj.found == "old") {
	jQuery ('.remainingVehicles #' + id).text (
		"" + id + " " + getLocation (obj.position) + " at " +
		obj.time.day + "-" + obj.time.month + "-" + obj.time.year + " " +
		obj.time.hour + ":" + obj.time.minute + ":" + obj.time.second
	)
	} else if (objj.found == "no"){
		jQuery ('.remainingVehicles #' + id).text ("No Data")
	}
}

function getLocation (position) {
	return "here";
}