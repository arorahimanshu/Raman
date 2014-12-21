fitx.utils.require(['fitx', 'page2', 'newGeoFenceForm']);

/***************************Global variable***************************************/
var indLat=21.0000;
var indLong=78.0000;
var zoomLevel=5;
var circleCenter;
var infoWindows = [];
var markers = [];
var shapes = [];

jQuery(window).load(function () {
	setupAJAXSubmit('newGeoFenceForm', 'newGeoFenceFormAction', setupData, setupConstraints, '.submit', null, saveSuccess);
	//setupAJAXSubmit('newGeoFenceForm', 'editGeoFence', setupData2, setupConstraints, '.editButton', null, saveSuccess);
	
	setupFlexiGrid('#showGeoFenceReport', undefined, "GeoFence Report", undefined, undefined, undefined, undefined, classData);
	
	sendAjaxRequest('geoFenceData', {}, showReport);
	
	onLoad_GeoFence();
	
	hideColumn('GeoFence Id')
	hideColumn('Vehicle Id')
	if (typeof jQuery.cookie('userMessageCok') !== 'undefined'){

            jQuery('.userMessage').text(jQuery.cookie("userMessageCok"));
            jQuery.removeCookie("userMessageCok");
    }


});

function saveSuccess(result) {
	jQuery.cookie("userMessageCok", result.message);
	//alert('saved');
	location.reload();
}

function setupData() {
	var filter = jQuery('.filter').filter(':visible');
	var name = filter.find('.name').val();
	
	var selectedVehicles = filter.find('.vsVehicleId:checked')
	var idList = []
	jQuery(selectedVehicles).each (function(){
		var vehicleId = jQuery (this).data( "details" ).id

		idList.push (vehicleId)
	})
	
	var type = filter.find('.type').val();
	
	var geometry = []
	var details = {'id':null}
	
	var addresses = filter.find('.address');
	jQuery.each(addresses,function(index, address){
		var add = address.value;
		if(add != '') {
			var parent = jQuery(address).parent ().parent ();
			var lat = parseFloat(parent.find('.lat').text());
			var lng = parseFloat(parent.find('.lng').text());
			geometry.push([lat,lng]);
		}
	});
	
	details['geometry'] = geometry;
	
	var data = {
		'fenceName' : name,
		'vehicleIds' : idList
	};
	
	
	if (type=='CIRCLE') {
		if(geometry.length != 1) {
			alert ('one address required');
		} else {
			details['type'] = 'CIRCLE';
			
			var radius = filter.find('.radius').val();
			
			details['radius'] = parseFloat(radius);
		}
	} else if (type=='POLYGON') {
		if(geometry.length < 3) {
			alert ('minimum three addresses required')
		} else {
			details['type'] = 'POLYGON';
			
			details['radius'] = 'N/A';
		}
	} else if (type=='RECTANGLE') {
		if(geometry.length < 3) {
			alert ('please draw rectangle')
		} else {
			details['type'] = 'RECTANGLE';
			
			details['radius'] = 'N/A';
		}
	}
	
	data['Details'] = JSON.stringify(details);
	
	return data;
}

function setupData2() {
	var data=setupData();
	data.id=idToEdit;
	console.log(data)
	return data;
}

function setupConstraints() {
	return {};
}

function initialize()
{
  var mapOptions = {
    zoom: 12,
    center: new google.maps.LatLng(28.643387, 77.612224),
    mapTypeControl: true,
    mapTypeControlOptions: {
        style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
        position: google.maps.ControlPosition.BOTTOM_CENTER
    },
    panControl: true,
    panControlOptions: {
        position: google.maps.ControlPosition.TOP_RIGHT
    },
    zoomControl: true,
    zoomControlOptions: {
        style: google.maps.ZoomControlStyle.LARGE,
        position: google.maps.ControlPosition.RIGHT_BOTTOM
    },
    scaleControl: true,
    streetViewControl: false,
    streetViewControlOptions: {
        position: google.maps.ControlPosition.RIGHT_CENTER
    },
    mapTypeId:google.maps.MapTypeId.ROADMAP
  }

  var map = new google.maps.Map(document.getElementById('googleMap'),
                                mapOptions);
    return map;
}

function onLoad_GeoFence() {
	
	geocoder = new google.maps.Geocoder();
	
	map=initialize();
	
	jQuery('.pPrev.pButton').click(function () {
        onPrevPageRequest()
    })
    jQuery('.pNext').click(function () {
        onNextPageRequest()
    })
    jQuery('.pGroup select').change(function () {
        onRpChange()
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
			if(pageNo>=1 && pageNo<=parseInt(total/rp)+1)
				sendAjaxRequest('geoFenceData', {'pageNo':pageNo}, showReport)
        }
    })
	
	/*
	var drawingManager = new google.maps.drawing.DrawingManager({
		drawingMode: null,
		drawingControl: true,
		drawingControlOptions: {
		  position: google.maps.ControlPosition.RIGHT_TOP,
		  drawingModes: [null]
		},
		/*
		circleOptions: {
		  fillColor: 'red',
		  fillOpacity: 0.3,
		  strokeWeight: 1,
		  clickable: false,
		  editable: true,
		  zIndex: 1
		}
		
	  });
	  drawingManager.setMap(map);
	  */
	//google.maps.event.addListener(drawingManager,'rectanglecomplete',rectanglecomplete);
	//google.maps.event.addListener(drawingManager,'circlecomplete',circlecomplete);
	var drawingManager = undefined;
	
	google.maps.event.trigger(map, 'resize');

	jQuery('.BACK').click(function() {
		jQuery('#tableDiv').show();

		jQuery('#newGeoFence').hide();
	});
	
	jQuery('.CIRCLE, .RECTANGLE, .POLYGON').click(function (){
		clearMap();
		jQuery('.filter').hide();
	});
	
	jQuery('.CIRCLE').click(function () {
		if(drawingManager!=undefined) {
			drawingManager.setMap(null);
		}
		
		drawingManager = new google.maps.drawing.DrawingManager({
			drawingMode: google.maps.drawing.OverlayType.MARKER,
			drawingControl: true,
			drawingControlOptions: {
				position: google.maps.ControlPosition.RIGHT_TOP,
				drawingModes: [google.maps.drawing.OverlayType.MARKER]
			},
		});
		drawingManager.setMap(map);
		google.maps.event.addListener(drawingManager,'circlecomplete',circlecomplete);
		google.maps.event.addListener(drawingManager,'markercomplete',function(marker){
			markercomplete(marker, '.circle');
		});
		jQuery('.circle').show();
	});
	
	jQuery('.RECTANGLE').click(function () {
		if(drawingManager!=undefined) {
			drawingManager.setMap(null);
		}
		
		drawingManager = new google.maps.drawing.DrawingManager({
			drawingMode: google.maps.drawing.OverlayType.MARKER,
			drawingControl: true,
			drawingControlOptions: {
				position: google.maps.ControlPosition.RIGHT_TOP,
				drawingModes: [google.maps.drawing.OverlayType.MARKER, google.maps.drawing.OverlayType.RECTANGLE]
			},
		});
		drawingManager.setMap(map);
		google.maps.event.addListener(drawingManager,'rectanglecomplete',rectanglecomplete);
		google.maps.event.addListener(drawingManager,'markercomplete',function(marker){
			markercomplete(marker, '.rectangle');
		});
		
		jQuery('.rectangle').show();
	});
	
	jQuery('.POLYGON').click(function () {
		
		jQuery('.polygon').show();
		
		var fields = jQuery('.addresses').children();
		
		while(jQuery('.addresses').children().length > 3) {
			jQuery(jQuery('.removeButton')[3]).trigger('click');
		}
		
	});
	
	jQuery('.addButton').click(function (evt){
		var addresses = jQuery('.addresses');
		var addressField = addresses.children()[0];
		var clone = jQuery(addressField).clone(true)
		clone.find('input').val('');
		addresses.append(clone);
		addresses = jQuery('.addresses').children();
		jQuery.each(addresses, function(index, address){
			var label = jQuery(address).find('label');
			label.text('Address ' + (index+1));
		});
	});
	
	jQuery('.removeButton').click(function (evt) {
		var parentDiv = jQuery(evt.target).parent();
		var addressesDiv = parentDiv.parent();
		var addresses = addressesDiv.children();
		if (addresses.length > 3) {
			clearMap();
			parentDiv.remove();
			addresses = addressesDiv.children();
			jQuery.each(addresses, function(index, address){
				var label = jQuery(address).find('label');
				label.text('Address ' + (index+1));
				jQuery(address).find('.searchButton').trigger('click');
			})
		}
	});
	
	jQuery('.radiusButton').click(function (evt){
		clearOnMap(shapes);
		var div = jQuery(evt.target).parent().parent().parent().parent();
		var address = div.find('.address').val();
		if(address != '') {
			var func = function (latlng) {
				var radius = div.find('.radius').val();
				draw_circle(latlng, radius);
				
				div.find('.lat').text(latlng.lat());
				div.find('.lng').text(latlng.lng());
			}
			manageLatLng(address, func);
		}
	});
	
	jQuery('.searchButton').click(function (evt){
		resetRectangle();
		var div = jQuery(evt.target).parent().parent();
		var address = div.find('.address').val();
		if(address!='') {
			codeAddress(address);
			var func = function (latlng) {
				div.find('.lat').text(latlng.lat());
				div.find('.lng').text(latlng.lng());
			}
			manageLatLng(address, func);
		}
	});
	
	jQuery('.circle .searchButton').click(function(){
		clearMap();
	});
	
	jQuery('.rectangle .searchButton').click(function(){
	});
	
	jQuery('.redraw').click(function(evt){
		var fields = jQuery(evt.target).parent().parent().find('.address');
		var path = []
		
		jQuery.each(fields,function(index, field){
			var address = field.value;
			var func = function(latlng) {
				path.push(latlng);
			}
			if(address != '') {
				geocoder.geocode({ 'address': address}, function (results, status) {
					if (status == google.maps.GeocoderStatus.OK) {
						var latlng = results[0].geometry.location
						path.push(latlng);
						if(path.length >= 3)
							draw_polygon(path);
						var parent=jQuery(field).parent();
						parent.find('.lat').text(latlng.lat());
						parent.find('.lng').text(latlng.lng());
					}
				});
			}
		});
	});
	
	jQuery('.cancel').click(function(){
		clearMap();
		clearFilter();
	});
	
	jQuery('.circle .reset').click(function(){
		resetCircle();
	});
	
	jQuery('.rectangle .reset').click(function(){
		resetRectangle();
	});
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
		buttons: [
            {name: 'Add', bclass: 'add', onpress: onAdd},
            {name: 'Delete', bclass: 'delete', onpress: onDelete},
            //{name: 'Edit', bclass: 'edit', onpress: onEdit},
            {separator: true}
        ],
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

function showReport(result) {


	jQuery('#showGeoFenceReport').flexAddData(result.message.sendData)
    total = result.message.sendData.total
	
	hideColumn('GeoFence Id')
	hideColumn('Vehicle Id')
}

var total = 0
var rp = 10
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
	if(pageNo>=1)
		sendAjaxRequest('geoFenceData', {'pageNo':pageNo}, showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
	if(pageNo<=parseInt(total/rp)+1)
		sendAjaxRequest('geoFenceData', {'pageNo':pageNo}, showReport)
}
function onFirstPageRequest() {
	sendAjaxRequest('geoFenceData', {'pageNo':1}, showReport)
}
function onLastPageRequest() {
	var pageNo = parseInt(total / rp) + 1
	sendAjaxRequest('geoFenceData', {'pageNo':pageNo}, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val())
    sendAjaxRequest('geoFenceData', {'pageNo':pageNo}, showReport)
}
function onRpChange() {
	rp = parseInt(jQuery('.pGroup select').val())
	sendAjaxRequest('geoFenceData',{'pageNo':1,'rp':rp}, showReport)
}
function successFunc(result) {
	jQuery.cookie("userMessageCok", result.message);

	if(result.success == true) {
		setTimeout(function(){location.reload();},200);
	} else {
	}
}

function onAdd() {
	jQuery('.buttons button').removeAttr('disabled');
	
	jQuery('.editButton').removeClass('editButton').addClass('submit')
	
	jQuery('#tableDiv').hide();

	jQuery('#newGeoFence').show();
	jQuery('.userMessage').text('');
    google.maps.event.trigger(map, 'resize');
}

function onDelete(com, grid) {
	var c = 0
	jQuery('.trSelected', grid).each(function () {
		c += 1
	})
	if (c == 1) {
		//code for geting row data and sending to form
		jQuery('.trSelected', grid).each(function () {

			var id = jQuery('td[abbr="GeoFence Id"] >div', this).html();
			var vehicleId = jQuery('td[abbr="Vehicle Id"] >div', this).html();

			var delData =  { geoFenceId: id, vehicleId:vehicleId  }
			sendAjaxRequest('delGeoFence',delData,successFunc);
		})
	} else {
		//alert('Select one row');
		displayUserMessageInCrud('emptyDeleteRow');

	}
}

function onEdit(com, grid) {
	var c = 0
	jQuery('.trSelected', grid).each(function () {
		c += 1
	})
	if (c == 1) {
		//code for geting row data and sending to form
		jQuery('.trSelected', grid).each(function () {
			
			jQuery('.buttons button').attr("disabled","disabled");
			var name = jQuery('td[abbr="GeoFence Name"] >div', this).html();
			idToEdit = jQuery('td[abbr="GeoFence Id"] >div', this).html();
			var type = jQuery('td[abbr="Type"] >div', this).html();
			var vehicleId = jQuery('td[abbr="Vehicle Id"] >div', this).html();
			
			jQuery('.'+type).trigger('click');
			
			var div = jQuery('.'+type.toLowerCase());
			div.find('.name').val(name);
			div.find('.type').val(type);
			div.find('.vehicles').val(vehicleId);
			
			var coordinates = JSON.parse(jQuery('td[abbr="Coordinates"] >div', this).html());
			
			while(div.find('.address').length < coordinates.length) {
				jQuery('.addButton').trigger('click');
			}
			
			var addresses = div.find('.address');
			
			var path = [];
			
			jQuery.each(coordinates, function(index, latlng1){
				var parent = jQuery(addresses[index]).parent();
				parent.find('.lat').text(latlng1[0]);
				parent.find('.lng').text(latlng1[1]);
				
				var latlng = new google.maps.LatLng(latlng1[0],latlng1[1]);
				path.push(latlng);
				
				var func = function(address) {
					jQuery(addresses[index]).val(address);
				}
				
				manageAddress(latlng,func);
				
			})
			
			setTimeout(function(){
				jQuery.each(path,function(index,p){
					codeLatLng(p);
				}
			)},1000);
			if(type=='CIRCLE') {
				var radius = jQuery('td[abbr="Radius"] >div', this).html();
				jQuery('.radius').val(radius);
				draw_circle(path[0],radius);
			} else {
				draw_polygon(path);
			}
			
			map.setZoom(15);
            map.setCenter(path[0]);
			
			jQuery("#tableDiv").hide();
			jQuery('#newGeoFence').show();
			div.find('.submit').text('Update')
			div.find('.submit').removeClass('submit')
				.addClass('editButton')
		})
	} else {
		//alert('Select one row');
		displayUserMessageInCrud('emptyEditRow');
	}	
}

function codeAddress(address) {
    
    geocoder.geocode({ 'address': address}, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            codeLatLng(results[0].geometry.location)

            map.setCenter(results[0].geometry.location);
            map.setZoom(15)
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function codeLatLng(latlng) {
    LatLng = latlng;
    geocoder.geocode({ 'latLng': latlng }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            if (results[1]) {
                map.setZoom(15);
                map.setCenter(latlng);

                //placeMarker(latlng);
				var marker = new google.maps.Marker({
					map: map,
					position: results[0].geometry.location
				});
				markers.push(marker);
				var address = results[1].formatted_address
                var str = '<div id="infoWindow"> Address: ' + address + '</div>';
				var infowindow = new google.maps.InfoWindow();
                infowindow.setContent(str);
                infowindow.open(map, marker);
				infoWindows.push(infowindow);
            } else {
                alert('No results found');
            }
        } else {
            alert('Error');
        }
    });
}

function kmToM(radius) {
	return radius*1000;
}

function mToKm(radius) {
	return radius/1000;
}

function draw_circle(center, radius) {
	clearOnMap(shapes);
	radius = parseFloat(radius);
	var circleOptions = {
                fillColor: 'red',
                fillOpacity: 0.3,
                strokeWeight: 1,
                clickable: false,
                editable: false,
                zIndex: 1,
				map: map,
				center: center,
				radius: radius
            };
	
    var circle = new google.maps.Circle(circleOptions);
	shapes.push(circle);
}

function draw_rectangle() {
	clearOnMap(shapes);
}

function draw_polygon(path) {
	clearOnMap(shapes);
	var polygonOptions = {
                fillColor: 'red',
                fillOpacity: 0.3,
                strokeWeight: 1,
                editable: true,
                zIndex: 1,
                geodesic:true,
                paths: path
            };
	
	var polygon = new google.maps.Polygon(polygonOptions);
	
	polygon.setMap(map);
	shapes.push(polygon);
}

function manageAddress(latlng, func) {
	var address;
	geocoder.geocode({ 'latLng': latlng }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            if (results[1]) {
                address = results[1].formatted_address
				func(address);
            }
		}
    });
}

function manageLatLng(address, func) {
	geocoder.geocode({ 'address': address}, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var latlng = results[0].geometry.location
			func(latlng);
        }
    });
}

function clearMap() {
	clearOnMap(markers);
	clearOnMap(shapes);
	clearOnMap(infoWindows);
}

function clearOnMap(array) {
	jQuery.each(array, function(index, a){
		a.setMap(null);
	});
}

function clearFilter() {
	jQuery('.name').val('');
	jQuery('.address').val('');
	jQuery('.lat').text('');
	jQuery('.lng').text('');
	jQuery('.radius').val('');
}

function circlecomplete(Circle) {
	alert('circle');
}

var rectangle=undefined;
var rectanglecomplete = function (Rectangle){
	
	if(rectangle!=undefined) {
		rectangle.setVisible(false);
	}
	
	rectangle=Rectangle;
	if(Rectangle!=undefined) {
		
		var lats = jQuery('.rectangle .lat');
		var lngs = jQuery('.rectangle .lng');
		
		var ne = Rectangle.bounds.getNorthEast();
		var sw = Rectangle.bounds.getSouthWest();
		
		jQuery(lats[0]).text(ne.lat());
		jQuery(lngs[0]).text(ne.lng());
		
		jQuery(lats[1]).text(sw.lat());
		jQuery(lngs[1]).text(sw.lng());
		
		jQuery(lats[0]).parent().find('.address').val('Address 1');
		jQuery(lats[1]).parent().find('.address').val('Address 2');
	}
}

var locationMarker = undefined;
var markercomplete = function(Marker, selector) {
	resetRectangle();
	var func = function(address) {
		jQuery(selector).find('.markable .address').val(address);
		var str = '<div id="infoWindow"> Address: ' + address + '</div>';
		var infowindow = new google.maps.InfoWindow();
		infowindow.setContent(str);
		infowindow.open(Marker.map, Marker);
	}
	markers.push(Marker);
	if(locationMarker!=undefined)
		locationMarker.setVisible(false);
	
	var latlng = Marker.position;
	jQuery(selector).find('.lat').text(latlng.lat());
	jQuery(selector).find('.lng').text(latlng.lng());
	manageAddress(latlng, func);
	
}

var resetCircle = function() {
	clearMap();
}

var resetRectangle = function() {
	rectanglecomplete(undefined);
	clearMap();
}

var hideColumn = function(colName) {
	jQuery('th[abbr="' + colName + '"]').hide()
	jQuery('td[abbr="' + colName + '"]').hide()
}