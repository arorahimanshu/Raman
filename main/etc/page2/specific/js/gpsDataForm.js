fitx.utils.require(['fitx', 'page2', 'newGpsDataForm']);

jQuery(window).load(function () {
    //setupAJAXSubmit('newGpsDataFrom', 'newGpsDataFormAction', setupData, setupConstraints, '.searchButton', null, successFunc);




    jQuery('#trackNow').click(function () {
        var carToTracked=[]
        clearInterval(abc)
        jQuery('.vehicleSelection:checked').each(function () {
           carToTracked.push(jQuery(this).prop('id').split('_')[1])
        })
        if (carToTracked != null) {

            var specific={}
            var curdate = new Date()
            var offset =-1* curdate.getTimezoneOffset()
            specific.gmt=(parseInt(offset/60)*3600)+(offset%60)*60
            specific.carToTracked=carToTracked

            sendAjaxRequest('newGpsDataCarSetup', specific, undefined);

            abc=setInterval(function () {
                sendAjaxRequest('newGpsDataFormAction',undefined,successFunc)
            }, 2000);
        }


    })


});
var speedLimit = false;
var maxSpeed = 0;
var unitAnimationSpeed = 10000;
var vehiclesData = {};
var map;
var rawData;
var marker;
var previousPath;

var abc;
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

    map.setCenter(getPosition(rawData[0].position));

    function animatePath(index) {
        if (index < rawData.length) {
            var obj = rawData[index];
            var currentId = obj.vehicleId;
            var position = getPosition(obj.position);

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
                    var speed = distance / time;
                    speed = convertMpsToKmph(speed);
                    vehiclesData[currentId].speed = speed;
                    setTimeout(function () {
                        var path = setPath(vehiclesData[currentId].path, vehiclesData[currentId].color);
                        if (vehiclesData[currentId].visible == true) {
                            vehiclesData[currentId].oldFlightPaths.push(path);
                            drawLine(path, map);
                            vehiclesData[currentId].marker.setMap(map);
                            vehiclesData[currentId].marker.setPosition(getPosition(obj.position));
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
                    }, unitAnimationSpeed / vehiclesData[currentId].speed);
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

                var infoWindowContent = getLiveInfoWindowContent('empty', 'empty', 0, 0, 0, 0, 0, 0);
                var infoWindow = new google.maps.InfoWindow({
                    content: infoWindowContent
                });
                infoWindow.open(map, marker);

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

            vehiclesData[currentId].infoWindow.setContent(getLiveInfoWindowContent(currentData.vehicleName, currentData.companyName, currentData.speed, currentData.totalDistance, currentData.brokenSpeedLimit, 0, 0, 0));

        }
    }

    animatePath(0);
}


google.maps.event.addDomListener(window, 'load', initializeMap);
	

