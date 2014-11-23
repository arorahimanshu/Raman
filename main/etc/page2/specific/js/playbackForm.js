fitx.utils.require(['fitx', 'page2', 'newPlaybackForm']);

jQuery(window).load(function() {
        //setupAJAXSubmit('newPlaybackFrom', 'newPlaybackFormAction', setupData, setupConstraints, '.start', null, successFunc);

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

        jQuery('.increaseAnimationSpeed').click(function(evt) {
                unitAnimationSpeed /= 2;
        });

        jQuery('.decreaseAnimationSpeed').click(function(evt) {
                unitAnimationSpeed *= 2;
        });

        jQuery('.toggleFilter').click(function() {
                jQuery('.filterSettings').toggle();
        });


        jQuery('Input[name=type]').change(function(evt) {
                var value = jQuery(evt.target).val();
                if (value == 'Relative') {
                        jQuery('.typeRelative').show();
                        jQuery('.typeFix').hide();
                } else if (value == 'Fix') {
                        jQuery('.typeRelative').hide();
                        jQuery('.typeFix').show();
                }
                sendAjaxRequest('newPlaybackFormAction', setupData(), successFunc);
        });

        jQuery('Input[name=vehicle]').change(function(evt) {
                var value = jQuery(evt.target).val();
                if (value == 'Type') {
                        jQuery('.typeVehicle').show();
                        jQuery('.groupvehicle').hide();
                } else if (value == 'Group') {
                        jQuery('.typeVehicle').hide();
                        jQuery('.groupVehicle').show();
                }
                sendAjaxRequest('newPlaybackFormAction', setupData(), successFunc);
        });

        jQuery('.groupVehicle').hide();

        jQuery('Input[name=relative]').change(function(evt) {
                sendAjaxRequest('newPlaybackFormAction', setupData(), successFunc);
        });

        jQuery('.all').click(function() {
                jQuery('.typeAll').show();
                jQuery('.typeFilter').hide();
        });

        jQuery('.filter').click(function() {
                jQuery('.typeAll').hide();
                jQuery('.typeFilter').show();
        });

        function initialSetup() {
                jQuery('.toggleGeofence').attr('disabled', 'disabled');

                jQuery('.pause').hide();

                jQuery('Input[name=type]')[0].checked = true;
                jQuery('Input[name=relative]')[0].checked = true;

                jQuery('.typeRelative').show();
                jQuery('.typeFix').hide();

                jQuery('.typeAll').show();
                jQuery('.typeFilter').hide();



                allFilterSettings();

                //sendAjaxRequest ('newPlaybackFormAction', setupData (), successFunc);
        }

        initialSetup();

        //to be changed after database changes like branch etc
        function allFilterSettings() {
                jQuery('.hide').hide();
                jQuery('.delhi').hide();
                jQuery('.show').click(function(evt) {
                        var target = evt.target;
                        var parent = jQuery(target).parent();
                        parent.children().toggle();
                });

                jQuery('.hide').click(function(evt) {
                        var target = evt.target;
                        var parent = jQuery(target).parent();
                        parent.children().toggle();
                });

        }

        var loadMap = document.getElementById('loadMap');
        google.maps.event.addDomListener(loadMap, 'click', initializeMap);
})

function setupData() {

        var dateType = jQuery('Input[name=type]:radio:checked').val();

        var specificFormData = {
                'dateType': dateType
        };

        if (dateType == 'Relative') {
                var relativeDay = jQuery('Input[name=relative]:radio:checked').val();
                specificFormData['relativeDay'] = relativeDay;
        } else {
                var from = dateFromDatePicker(jQuery('.from'));
                var to = dateFromDatePicker(jQuery('.to'));

                specificFormData['fromDate'] = from;
                specificFormData['toDate'] = to;
        }

        return specificFormData;
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

var speedLimit = false;
var maxSpeed = 0;
var unitAnimationSpeed = 10000;
var vehiclesData = {};
var map;
var rawData;
var marker;
var controlAnimation = 0;
var dateToday;

function initializeMap() {
        var centre = new google.maps.LatLng(23.25, 77.417);
        var mapOptions = setMapProperties(6, centre, google.maps.MapTypeId.ROADMAP);
        map = new google.maps.Map(document.getElementById('map'), mapOptions)
        //sendAjaxRequest('newPlaybackFormAction', {}, successFunc);
}

function manageDateAndTime(datetime) {
        console.log(datetime);
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
	
        jQuery('.start').click(function() {
                jQuery('.pause').show();
                jQuery('.start').hide();
                controlAnimation = 1;
                animatePath(0);
        });

        jQuery('.pause').click(function() {
                jQuery('.pause').hide();
                jQuery('.start').show();
                controlAnimation = 0;
                animatePath(0);
        });
	
        rawData = rawData.message;
        map.setZoom(12);
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
                                        var speed = distance / time;
                                        speed = convertMpsToKmph(speed);
                                        vehiclesData[currentId].speed = speed;
                                        setTimeout(function() {
                                                var path = setPath(vehiclesData[currentId].path, vehiclesData[currentId].color);
                                                drawLine(path, map);
                                                vehiclesData[currentId].marker.setPosition(getPosition(obj.position));
                                                animatePath(index + 1);
                                                jQuery('.vehicle' + currentId + ' .speed').text(speed + ' kmph');
                                                if (speedLimit == true) {
                                                        if (speed > maxSpeed) {
                                                                jQuery('.vehicle' + currentId).toggle();
                                                                if (index == rawData.length - 1 || currentId != rawData[index + 1].vehicleId) {
                                                                        jQuery('.vehicle' + currentId).show();
                                                                }
                                                        } else {
                                                                jQuery('.vehicle' + currentId).show();
                                                        }
                                                }
                                        }, controlanimation * unitAnimationSpeed / vehiclesData[currentId].speed);
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

                                var infoWindowContent = getInfoWindowContent('empty', 0, 0, 0);
                                var infoWindow = new google.maps.InfoWindow({
                                        content: infoWindowContent
                                });
                                infoWindow.open(map, marker);

                                var div = jQuery('<div/>', {
                                        'class': 'vehicle' + currentId,
                                });

                                jQuery('<span/>', {
                                        'class': 'vehicleId',
                                        'text': currentId + '---'
                                }).appendTo(div);

                                jQuery('<span/>', {
                                        'class': 'vehicleName',
                                        'text': name + '---'
                                }).appendTo(div);

                                jQuery('<span/>', {
                                        'class': 'speed',
                                        'text': 0
                                }).appendTo(div);

                                div.appendTo('.speedDetails');

                                vehiclesData[currentId] = {
                                        'vehicleName': name,
                                        'color': getColor(currentId),
                                        'marker': marker,
                                        'infoWindow': infoWindow,
                                        'path': [position],
                                        'previousTime': 0,
                                        'currentTime': obj.time,
                                        'previousPosition': 0,
                                        'currentPosition': position,
                                        'speed': 0
                                };

                                animatePath(index + 1);
                        }

                        vehiclesData[currentId].infoWindow.setContent(getInfoWindowContent(vehiclesData[currentId].vehicleName, vehiclesData[currentId].speed, 0, 0));

                }
        }

        animatePath(0);
}

//google.maps.event.addDomListener(window, 'load', initializeMap);
