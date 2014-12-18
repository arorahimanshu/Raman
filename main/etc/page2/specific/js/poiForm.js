fitx.utils.require(['fitx', 'page2', 'newPoiForm']);

jQuery(window).load(function () {
    setupAJAXSubmit('newPoiForm', 'newPoiFormAction', setupData, setupConstraints, '#save', null, saveSuccess);
    //setupAJAXSubmit('newPoiForm', 'generateReport', PoiData, null, '#show', null, showReport);
    setupFlexiGrid('#showTable', undefined, "POI Details", undefined, undefined, undefined, undefined, classData)
	sendAjaxRequest('generateReport', {}, showReport)

    if (typeof jQuery.cookie('userMessageCok') !== 'undefined'){

            jQuery('.userMessage').text(jQuery.cookie("userMessageCok"));
            jQuery.removeCookie("userMessageCok");
    }

    jQuery('#addPoiButton').click(function () {

        jQuery('#primary').hide();
        jQuery('#secondary').show();
        initialize()

    })

    jQuery('.add').click(function () {

        jQuery('#primary').hide();
        jQuery('#secondary').show();
        initialize()
    })
    jQuery('#searchButtonImg').click(function () {
        codeAddress()
    })

    jQuery("#cancel").click(function () {
        jQuery('#primary').show();
        jQuery('#secondary').hide();
    })


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
			var data = PoiData()
			data.pageNo = pageNo
			if(pageNo>=1 && pageNo<=parseInt(total/rp)+1)
				sendAjaxRequest('generateReport', data, showReport)
        }
    })
	
	hideColumn(1)
	hideColumn(6)
})


function addToPoiTable(list) {

    jQuery('#poiData').prop('hidden', false);

    var data = "<label>Select POI : </label><select id='PoiDataId'>"
    if (list != "") {
        jQuery.each(list, function (key, value) {
            data += "<option value='" + value.value + "'>" + value.display + "</option>"
        })
    }
    else {
        data += "<option value=''>Empty</option>"
    }
    data += "</select>"

    jQuery('#poiData').html(data);


}
function saveSuccess(result) {


    alert(result.message);
    jQuery.cookie("userMessageCok", result.message);
    //console.log(result);
   // console.log("The json startdate is " + response.startdate); //prints undefined
    alert('POI Saved');
    location.reload();
}


function setData(result) {
    //alert('a');
    addToPoiTable(result.message)

}

function PoiData() {
    var data = {}

    data.reportCompany = jQuery("#reportCompany option:selected").val()
    data.reportBranch = jQuery("#reportBranch option:selected").val()
    data.reportAddressCategory = jQuery("#reportAddressCategory option:selected").val()


    return data
}

function setupData() {

    var specificFormData = {}


    specificFormData.company = jQuery("#poiCompany option:selected").val()
    specificFormData.branch = jQuery("#poiBranch option:selected").val()
    specificFormData.vehicleID = jQuery("#PoiVehicleList option:selected").val()
    specificFormData.poiplaceName = jQuery("#poiplaceName").val()
    specificFormData.addressCategory = jQuery("#addressCategory option:selected").val()
    specificFormData.street = jQuery("#street").val()
    specificFormData.city = jQuery("#city").val()
    specificFormData.state = jQuery("#state").val()
    specificFormData.latitude = jQuery('#lat').val()
    specificFormData.longitude = jQuery('#lng').val()

    // Vehicle Selector > vehicle id Picker
    var idList = []
	jQuery('.vsVehicleId:checked').each (function(){
		var vehicleId = jQuery (this).data( "details" ).id

		idList.push (vehicleId)
	})
    specificFormData['vehicleList']=idList
    //-------------------------------------



    return specificFormData
}

function setupConstraints() {

    var specificFormConstraints = {
        poiplaceName: {presence: true},
        street: {presence: true},
        city: {presence: true},
        state: {presence: true}
    }

    return specificFormConstraints
}


function setupFlexiGrid(selector, datatype, title, noOfPages, width, height, singleSelect, classData, extraCols) {
    if (datatype == undefined)
        datatype = 'json'
    if (title == undefined)
        title = 'Table'
    if (noOfPages == undefined)
        noOfPages = 10
    if (width == undefined)
        width = 800
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
            {name: 'Add', bclass: 'add', onpress: onAddOrDelete},
            {name: 'Delete', bclass: 'delete', onpress: onAddOrDelete},
            //{name: 'Edit', bclass: 'edit', onpress: onAddOrDelete},
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
            width:180,
            align: 'center'
        }
        colModel.push(dict)
    })
    return colModel

}

function onAddOrDelete(com, grid) {
    if (com == "Add") {
            jQuery('.userMessage').text(' ');
        jQuery('#primary').hide();
        jQuery('#secondary').show();
        initialize()
    }
    else if (com == "Delete") {
		var c = 0
		jQuery('.trSelected', grid).each(function () {
			c += 1
		})
		if (c == 1) {
			jQuery('.trSelected', grid).each(function (index, data) {
				var delFields = {}
				//delFields.id=jQuery('td[abbr="Id"] >div', this).html()
				delFields.poiId=data.cells[1].textContent
                delFields.vehicleId=data.cells[6].textContent

				sendAjaxRequest('delPoi',delFields,function(){
					jQuery('.userMessage').text('POI Deleted');
					sendAjaxRequest('generateReport', setupDataFlexi(), showReport)
				})
			})
		}
		else {
			alert('select single row to delete')
		}
    }
    else {

    }
}
function setupDataFlexi() {
    data = {}
    return data
}

function showReport(result) {

    jQuery('#showTable').flexAddData(result.message)
    jQuery('.userMessage').text(' ');
    if (result.message.rows.length == 0){
              jQuery('.userMessage').text('No Data Present');
              return
        }
    total = result.message.total
	
	hideColumn(1)
	hideColumn(6)
}

var total = 0
var rp = 10
function onPrevPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) - 1
	var data = PoiData()
	data.pageNo = pageNo
	if(pageNo>=1)
		sendAjaxRequest('generateReport', data, showReport)
}
function onNextPageRequest() {
    var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
	var data = PoiData()
	data.pageNo = pageNo
	if(pageNo<=parseInt(total/rp)+1)
		sendAjaxRequest('generateReport', data, showReport)
}
function onFirstPageRequest() {
	var data = PoiData()
	data.pageNo = 1
    sendAjaxRequest('generateReport', data, showReport)
}
function onLastPageRequest() {
	var pageNo = parseInt(total / rp) + 1
	var data = PoiData()
	data.pageNo = pageNo
    sendAjaxRequest('generateReport', data, showReport)
}
function onReload() {
    var pageNo = parseInt(jQuery('.pcontrol input').val())
	var data = PoiData()
	data.pageNo = pageNo
    sendAjaxRequest('generateReport', data, showReport)
}
function onRpChange() {
	rp = parseInt(jQuery('.pGroup select').val())
	var data = PoiData()
	data.pageNo = 1
	data.rp=rp
    sendAjaxRequest('generateReport', data, showReport)
}

function paymentData(pageNo) {
    var data = {}
    data.pageNo = 1
    if (pageNo != undefined)
        data.pageNo = pageNo
    return data
}
function auxiPaymentData(pageNo) {
    return {'formData': paymentData(pageNo)}

}


var map;
var marker;
var markers = []
var infowindow;
var geocoder;
var sno = 1;
var latlng, address;


function initialize() {
    infowindow = new google.maps.InfoWindow()
    geocoder = new google.maps.Geocoder();
    var mapOptions = {
        zoom: 10,
        center: new google.maps.LatLng(28.2759332899999, 77.029633320000003)
    };

    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    google.maps.event.addListener(map, 'click', function (event) {
        codeLatLng(event.latLng);


    });
}


function codeAddress() {
    var address = document.getElementById('placeName').value;
    geocoder.geocode({ 'address': address}, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            codeLatLng(results[0].geometry.location)

            map.setCenter(results[0].geometry.location);
            map.setZoom(15)

            marker = new google.maps.Marker({
                map: map,
                position: results[0].geometry.location

            });
            markers.push(marker);


        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function getAddress(latlng) {

    geocoder = new google.maps.Geocoder()

    geocoder.geocode({ 'latLng': latlng }, function (results, status) {

        if (status == google.maps.GeocoderStatus.OK) {
            if (results[1]) {

                address = results[1].formatted_address
                var fields = []


                y = ''
                x = fields.slice(0, fields.length - 3)
                for (i = 0; i < x.length; i++) {
                    y += x[i]
                }
                r.state = fields[fields.length - 2]
                r.city = fields[fields.length - 3]
                r.street = y
                a = 1;

            }
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

                placeMarker(latlng);
                address = results[1].formatted_address
                var str = '<div id="infoWindow"> Address: ' + address + '</div>';
                infowindow.setContent(str);
                infowindow.open(map, marker);
                {

                    var fields = address.split(',')
                    jQuery('#state').val(fields[fields.length - 2])
                    jQuery('#city').val(fields[fields.length - 3])
                    jQuery('#street').val(fields.slice(0, fields.length - 3))
                    jQuery('#lat').val(latlng.lat())
                    jQuery('#lng').val(latlng.lng())
                }
            } else {
                alert('No results found');
            }
        } else {
            alert('Error');
        }
    });
}

var hideColumn = function(colNo) {
	jQuery('th[axis="col' + colNo + '"]').hide()
	var rows = jQuery('tr[id]')
	jQuery.each(rows, function(index, tr) {
		var td = jQuery(tr).find('td')[colNo]
		jQuery(td).hide()
	})
}

