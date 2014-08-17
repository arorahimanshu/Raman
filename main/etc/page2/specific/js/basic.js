var findErrorBox = function (fieldName) {
	if (fieldName.indexOf("_") > -1)
		return jQuery('#' + fieldName.split('_')[0] + 'Error')
	return jQuery('#' + fieldName + 'Error')
}
function isInt(n) {
	return (n) != "" && !isNaN(n) && Math.round(n) == (n);
}
var clearMessages = function () {
	jQuery('.errorBox').text('')
	var errorImg = jQuery('img[src*="/etc/page2/generic/css/images/error.png"]')
    errorImg.prop('src','').css('display','false')
};
function returnDate(id) {

	var date = jQuery('#' + id).datepicker('getDate');
	if (date) {
		data = [
			parseInt(date.getFullYear()),
				date.getMonth() + 1,
			date.getDate()
		]
		return data
	}

}
var sendAjaxRequest = function (url,data,successFunction,errorFunction,datatype,requestType,compFun) {
	var reqData = { formData: JSON.stringify(data)}
	var successFunc = function(result) {}
	if(successFunction != undefined)
	{
		successFunc = successFunction;
	}
	if(data != undefined)
	{

	}
	var errorFunc = function(result) {}
	if(errorFunction != undefined)
	{
		errorFunc = errorFunction;
	}
	var reqType = 'POST'
	if(requestType != undefined)
	{
		reqType = requestType
	}
	var dataType = 'JSON'
	if(dataType != undefined)
	{
		dataType = datatype
	}
	var completeFunction = function (xhr,status) {}
	if(compFun != undefined)
	{
		completeFunction = compFun
	}
	jQuery.ajax({
		url:url,
		data:reqData,
		type: reqType,
		datatype: dataType,
		success:successFunc,
		error:errorFunc,
		complete:completeFunction
	})
	
}
var errorMessage = function (fieldName, msg) {
	var errorImg = jQuery('#'+fieldName+'ErrorImg>img');
    errorImg.prop('src','/etc/page2/generic/css/images/error.png').css('display','true').effect('pulsate');
	var errorBox = findErrorBox(fieldName);
	var genericMessageBox = findErrorBox('generic');
	genericMessageBox.removeClass('success');
	genericMessageBox.addClass('errorBox');
	errorBox.text(msg);
	errorBox.effect('pulsate')
};
var successMessage = function (msg) {
	var genericMessageBox = findErrorBox('generic');
	genericMessageBox.removeClass('errorBox');
	genericMessageBox.addClass('success');
	genericMessageBox.text(msg);

	location.reload();
};
var newFormLoadFunc = function (result, onLoadWorkfun, newFormDivSelector) {
	console.log('inside new form load')

	if (result.success) {
		jQuery(newFormDivSelector).html(result.message)
		jQuery(newFormDivSelector).addClass('overlay')
		onLoadWorkfun()
	}

}
var cancelForm = function(selector)
{
	var choice = confirm("Are you sure you want to close this form?")
	if(choice)
	{
		if(selector.closest('.overlay').length)
		{
			selector.closest('.overlay').remove()
		}
		else
		{
			fitx.closeActiveTab()
		}
	}

}
var setupCancel = function(select,cancelSelector,trigger){
	jQuery(cancelSelector)[trigger](function(){
		cancelForm(cancelSelector)
	})
	jQuery(select).closest('form').keydown(function(e){
		                 if(e.keyCode==27){
			                 cancelForm(select)
		                 }
	                 })
}
var setupAJAXSubmit = function (formName, formActionUrl, setupData, setupConstraints, select, extendError, newFormLoadFunc,cancelSelect,cancelTrig) {
//
//	//TODO:Implement next line properly
//	if(cancelSelect == undefined)
//		cancelSelect = '.cancel'
//	if(cancelTrig == undefined)
//		cancelTrig = 'click'
//
//	setupCancel(select,cancelSelect,cancelTrig)

	fitx.config[formActionUrl] = formActionUrl
	fitx.page2[formName] = new fitx.lib1.AjaxClickable({
           selector: select,
           actionUrl: fitx.config[formActionUrl],

           dataFunction: function () {
               if (setupData != undefined) {
                   return setupData();
               }
               else {
                   return function () {
                       return {}
                   }
               }
           },
           preRequestFunction: function (control) {
               clearMessages();
               var data = control.data()
               var constraints

               if (setupConstraints != undefined) {
                   constraints = setupConstraints()
               }
               else {
                   constraints = {}
               }
               var errors = validate(data, constraints, {fullMessages: false})
               if (extendError != undefined) {
                   errors = extendError(data, errors)
               }
               if (errors) {
                   clearMessages();
                   for (var error in errors) {
                       console.log(error, errors[error])
                       errorMessage(error, errors[error])
                   }
                   control.cancelRequest();
                   return
               }
               control.data({
                                formData: JSON.stringify(data)
                            })
           },
           successFunction: function (result) {

               if (result.success) {
                   if (newFormLoadFunc != undefined) {
                       newFormLoadFunc(result)
                   }
                   else {
                       successMessage(result.message)

                   }
	               //TODO: can be better
	               jQuery(select).closest('.overlay')
		               .trigger('formSubmitted')

               } else {
                   errorMessage('generic', result.message);
                   if ('errors' in result.data) {
                       jQuery.each(result.data.errors, function (key, value) {
                           errorMessage(key, value)
                       })
                   }
               }
           },
           failureFunction: function () {
               errorMessage('generic', 'unknown error')
           }
       })
}
var createNewForm = function (formName, formActionUrl,divSelector,selector,trigger,successFunc,errorFunc) {
	//(url,data,successFunction,errorFunction,datatype,requestType,compFun)
	var thisSuccess = function (result) {

		jQuery(divSelector)
			.html(result)
			.addClass('overlay')
	}
	if(successFunc != undefined)
	{
		thisSuccess = successFunc
	}
	var trig = 'click'
	if(trigger != null)
	{
		trig = trigger
	}
	//TODO: remove after testing
	jQuery(divSelector).on('formSubmitted',function () {
			jQuery(divSelector).remove()
		})
	jQuery(selector)[trig](function (evt) {
		evt.preventDefault()
		sendAjaxRequest(formActionUrl,{'noTabs':'true'},thisSuccess)

	})
}
function createMarker(latlng) {
    marker = new google.maps.Marker({
        position: latlng,
        map: map
    });
    markers.push(marker);
    marker.setAnimation(google.maps.Animation.BOUNCE);
}
function placeMarker(location) {
    clearOverlays();

    createMarker(location)
}
function clearOverlays() {
    while (markers[0]) {
        markers.pop().setMap(null)
    }
}



function getCentre () {
	var centre = new google.maps.LatLng(23.25,77.417);
	return centre;
}

function getPosition (position) {
	var lat = convertToDegree (position.latitude);
	var lng = convertToDegree (position.longitude);
	var latlng = new google.maps.LatLng(lat,lng);
	return latlng;
}

function getDistanceFromPath(pathPoints) {
	var distance = google.maps.geometry.spherical.computeLength (pathPoints);
	return distance;
}

function convertToDegree (coordinates) {
	coordinates = coordinates.toString()
	var index = coordinates.indexOf('.')
	index = index - 2
	var degrees = parseInt(coordinates.substring(0,index))
	var minutes = parseFloat(coordinates.substring(index))
	return deg = degrees + minutes/60
}

function convertDuration (seconds) {
	var minutes = seconds/60;
	var hours = minutes/60;
	minutes = minutes % 60;
	hours = Math.round (hours).toString ();
	minutes = Math.round (minutes). toString ();
	if (hours.length == 1) {
		hours = '0' + hours;
	}
	if (minutes.length == 1) {
		minutes = '0' + minutes;
	}
	var duration = '' + hours + ':' + minutes;
	return duration;
}

function convertDistance(distance) {
	distance = distance / 1000;
	distance = Math.round (distance).toString ();
	return distance;
}

function convertMpsToKmph(speed) {
	speed = speed * 18 / 5;
	speed = Math.round (speed).toString ();
	return speed;
}

function convertMToKm (distance) {
	distance = distance / 1000;
	return distance;
}

function getSecond (time) {
	var minute = time.hour * 60 + time.minute;
	var second = minute * 60 + time.second;
	return second;
}

function getTimeDifference (previous, next) {
	var difference = getSecond (next) - getSecond (previous);
	if (difference < 0) {
		difference = -difference;
	}
	return difference;
}

function convertMpsToKmph(speed) {
	speed = speed * 18 / 5;
	speed = Math.round (speed).toString ();
	return speed;
}

//Map Functions
function setMapProperties(zoom,center,mapTypeId) {
	return {
		zoom: zoom,
		center: center,
		mapTypeId: mapTypeId
	}
}

function setPath(coordinates, color) {
	var flightPath = new google.maps.Polyline({
		path: coordinates,
		geodesic: true,
		strokeColor: color,
		strokeOpacity: 1.0,
		strokeWeight: 3
	})
	return flightPath
}

function drawLine(path,map) {
	path.setMap(map)
}

function getInfoWindowContent (vehicleName, speed, ignition, ac) {
	var content = vehicleName + '<br/>' +
			speed + ' kmph' +'<br/>' +
			'ignition' + '<br/>' +
			'ac';
	return content;
}

function getLiveInfoWindowContent (vehicleName, companyName, speed, distance, speedLimitBroken, field1, others, field2) {
	var content = vehicleName + '<br/>' +
			companyName + '<br/>' +
			speed + ' kmph' +'<br/>' +
			distance + 'km' + '<br/>' +
			speedLimitBroken + '<br/>' +
			field1 + '<br/>' +
			others + '<br/>' +
			field2;
	return content;
}
