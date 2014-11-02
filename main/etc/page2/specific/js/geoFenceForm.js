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
	
	setupFlexiGrid('#showGeoFenceReport', undefined, "GeoFence Report", undefined, undefined, undefined, undefined, classData);
	
	sendAjaxRequest('geoFenceData', {}, showReport);
	
	rp = parseInt(jQuery('.pGroup select option:selected').text())
	
	onLoad_GeoFence();
});

function saveSuccess(result) {
	alert('saved');
	location.reload();
}

function setupData(res) {
	var filter = jQuery('.filter').filter(':visible');
	var name = filter.find('.name').val();
	var vehicleId = filter.find('.vehicles :selected')[0].value;
	var type = filter.find('.type').val();
	
	var geometry = []
	var details = {'id':null}
	
	var addresses = filter.find('.address');
	jQuery.each(addresses,function(index, address){
		var add = address.value;
		if(add != '') {
			var parent = jQuery(address).parent ();
			var lat = parseFloat(parent.find('.lat').text());
			var lng = parseFloat(parent.find('.lng').text());
			geometry.push([lat,lng]);
		}
	});
	
	details['geometry'] = geometry;
	
	var data = {
		'fenceName' : name,
		'vehicleId' : vehicleId
	};
	
	if (type=='Circle') {
		if(geometry.length != 1) {
			alert ('one address required');
		} else {
			details['type'] = 'CIRCLE';
			
			var radius = filter.find('.radius').val();
			
			details['radius'] = parseFloat(radius);
		}
	} else if (type=='Polygon') {
		if(geometry.length < 3) {
			alert ('minimum three addresses required')
		} else {
			details['type'] = 'POLYGON';
			
			details['radius'] = 'N/A';
		}
	}
	
	data['Details'] = JSON.stringify(details);
	
	return data;
}

function setupConstraints() {
	return {};
}

function initialize()
{
    var map=new google.maps.Map(document.getElementById('googleMap'));
    map.setCenter(new google.maps.LatLng(indLat,indLong));
    map.setZoom(zoomLevel);
    return map;
}

function onLoad_GeoFence() {
	
	geocoder = new google.maps.Geocoder();
	
	map=initialize();
	
	jQuery('.BACK').click(function() {
		jQuery('#tablediv').show();
		jQuery('#newGeoFence').hide();
	});
	
	jQuery('.CIRCLE, .RECTANGLE, .POLYGON').click(function (){
		clearMap();
		jQuery('.filter').hide();
	});
	
	jQuery('.CIRCLE').click(function () {
		jQuery('.circle').show();
	});
	
	jQuery('.RECTANGLE').click(function () {
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
		var div = jQuery(evt.target).parent().parent();
		var address = div.find('.address').val();
		if(address != '') {
			var func = function (latlng) {
				var radius = div.find('.radius').val();
				draw_circle(latlng, parseFloat(radius));
				
				div.find('.lat').text(latlng.lat());
				div.find('.lng').text(latlng.lng());
			}
			manageLatLng(address, func);
		}
	});
	
	jQuery('.searchButton').click(function (evt){
		var div = jQuery(evt.target).parent();
		var address = div.find('.address').val();
		if(address!='')
			codeAddress(address);
	});
	
	jQuery('.circle .searchButton').click(function(){
		clearMap();
	});
	
	jQuery('.rectangle .searchButton').click(function(){
	});
	
	jQuery('.redraw').click(function(){
		var fields = jQuery('.polygon .address');
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
            {name: 'Edit', bclass: 'edit', onpress: onEdit},
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
}

var total = 0
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
    sendAjaxRequest('geoFenceData', auxi(pageNo), showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('geoFenceData', {'pageNo': pageNo}, showReport)
}
function onFirstPageRequest() {
    sendAjaxRequest('geoFenceData', {'pageNo': 1}, showReport)
}
function onLastPageRequest() {
	if (!rp)
		rp = 10
    pageNo = parseInt(total / rp) + 1
    sendAjaxRequest('geoFenceData', {'pageNo': pageNo}, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
    sendAjaxRequest('geoFenceData', {'pageNo': pageNo}, showReport)
}

function onAdd() {
	jQuery('#tablediv').hide();
	jQuery('#newGeoFence').show();
}

function onDelete() {
}

function onEdit() {
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
	var circleOptions = {
                fillColor: 'red',
                fillOpacity: 0.3,
                strokeWeight: 1,
                clickable: false,
                editable: true,
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
	return undefined;
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
