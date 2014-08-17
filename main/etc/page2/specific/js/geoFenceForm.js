fitx.utils.require(['fitx', 'page2', 'newGeoFenceForm']);

jQuery(window).load(function () {


    initialize()
    addToTable();

    setupAJAXSubmit('newGeoFenceForm', 'newGeoFenceFormAction', setupData, setupConstraints, '.save',null,getData);


    var data = {
        path: [],
        vechicleID: []
    }


    jQuery(".start").click(function () {
        jQuery('.Fename').val('');

        map = mapProp(0, 0, 3);
        fence_data(map);
    });


    jQuery(".Cars").on("mouseenter", function () {
        jQuery(".carlist").slideDown("fast");
    });

    jQuery(".carlist").on("click", function () {

        var vech = jQuery(this).text();
        vech = vech.split(' ');
        vechicle(vech[0]);
    });

    jQuery(".Cars").on("mouseleave", function () {
        jQuery(".carlist").slideUp("fast");
    });

    jQuery(".Poly").on("click", function () {
        jQuery(".GeoFence").show();
    });


});

function getData(a)
{
    fdata= a.data
 jQuery('.Details').append("<tr><td>"+fdata['vehicleId']+"</td><td>"+fdata['fenceName']+"</td><td>"+fdata['latitude']+"</td><td>"+fdata['longitude']+"</td></tr>");
    location.reload();
}

function setupData() {

    var specificFormData = {}

    specificFormData.vehicleId = jQuery(".vid option:selected").val()
    specificFormData.fenceName = jQuery('.Fename').val()

    var pa = path.getArray();
    latit=""
    longi=""
    for (var i = 0; i < pa.length-1; i++) {
        latit+=pa[i]['k']+",";
        longi+=pa[i]['B'] + ",";
    }
    latit+=pa[i]['k']
    longi+=pa[i]['B']
    specificFormData.latitudeList = latit
    specificFormData.longitudeList = longi
    return specificFormData
}

function setupConstraints() {

    var specificFormConstraints = {


        fenceName: {presence: true},
        latitudeList: {presence:true},
        longitudeList:{presence:true}

    }
    return specificFormConstraints
}

var deg_path = [];
var path = new google.maps.MVCArray;
var markers = [];
var poly;
var map;


function initialize() {
    map = new google.maps.Map(document.getElementById('googleMap'));
    map.setCenter(new google.maps.LatLng(0, 0));
    map.setZoom(2);
    map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
    addVehicle();
}

function fence_data(map) {
    poly = drawPoly()
    path = new google.maps.MVCArray;
    poly.setMap(map);
    poly.setPaths(new google.maps.MVCArray([path]));
    google.maps.event.addListener(map, 'click', function (event) {
        path.insertAt(path.length, event.latLng);
        var marker = new google.maps.Marker({
            position: event.latLng,
            map: map,
            draggable: true
        });
        markers.push(marker);
        marker.setTitle("#" + path.length);
        google.maps.event.addListener(marker, "click", function (event) {
            marker.setMap(null);
            console.log("Iam inside marker click");
            for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
            markers.splice(i, 1);
            path.removeAt(i);
        });

        google.maps.event.addListener(marker, "dragend", function (event) {
            console.log("Iam inside marker dragend");
            for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
            path.setAt(i, marker.getPosition());
        });
        //drawPoly(deg_path,map);
    });

}

function pathCoordinate(lat, lon) {
    var coordinate = [];
    for (var i = 0; i < lat.length && i < lon.length; i++) {
        coordinate.push(
            new google.maps.LatLng(lat[i], lon[i])
        );
    }
    return coordinate;
}

function sendtocheck(lat, lon, testx, testy) {
    var poly = [];
    var carLatLon = new google.maps.LatLng(testx, testy);
    for (var k = 0; k < lat.length; k++) {
        var polypath = pathCoordinate(lat[k], lon[k]);
        var polyLatLon = new google.maps.Polygon({
            paths: polypath
        });
        if (google.maps.geometry.poly.containsLocation(carLatLon, polyLatLon)) {
            poly.push("Polygon " + k + "=True");
        }
        else {
            poly.push("Polygon " + k + "=False");
        }
    }
    return poly;
}
function vechicle(id) {
    var deg_path = [];
    var lat = getlatitude(id);
    var lon = getlongitude(id);
    var splat = lat[0];
    var splon = lon[0];
    var eplat = lat[lat.length - 1];
    var eplon = lon[lon.length - 1];
    var coordinate = pathCoordinate(lat, lon);
    var roadPath = createPath(coordinate);
    var latlon = selatlon(eplat, eplon);
    var map = mapProp(splat, splon, 13);

    var data = getLocalstorage(id);
    if (data['latitude'].length > 0 && data['longitude'].length > 0) {
        fence(data, map);
    }
    setMarker(latlon, 'flag', map);
    roadPath.setMap(map);
    animateCar(map, coordinate, data);
}
function fence(data, map) {

    path = new google.maps.MVCArray;
    var lat = data['latitude'];
    var lon = data['longitude'];
    console.log(lat[0]);
    var poly = drawPoly();
    poly.setMap(map);
    var latlon = [];
    for (var j = 0; j < lat.length; j++) {
        latlon.push(pathCoordinate(lat[j], lon[j]));
    }
    for (var i = 0; i < latlon.length; i++) {
        var temp = latlon[i];
        for (var j = 0; j < temp.length; j++) {
            path.insertAt(path.length, temp[j]);
            poly.setPaths(new google.maps.MVCArray([path]));
            console.log(path);
        }
    }
}
function drawPoly() {
    //console.log(path);
    var flightPath = new google.maps.Polygon({
        strokeColor: "#0000FF",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#0000FF",
        fillOpacity: 0.4
    });
    return flightPath;
}
function mapProp(lat, lon, level) {
    var gMap = new google.maps.Map(document.getElementById('googleMap'));
    gMap.setCenter(new google.maps.LatLng(lat, lon));
    gMap.setZoom(level);
    gMap.setMapTypeId(google.maps.MapTypeId.ROADMAP);
    return gMap;
}
function setMarker(latlon, ico, gMap) {
    var marker = new google.maps.Marker({
        position: latlon,
        map: gMap,
        icon: ico + '.png'
    });
}
function selatlon(lat, lon) {
    var latlon = new google.maps.LatLng(lat, lon);
    return latlon;
}
function createPath(coordinate) {
    var RoadPath = new google.maps.Polyline({
        path: coordinate,
        geodesic: true,
        strokeColor: "red",
        strokeOpacity: 1.0,
        strokeWeight: 2,
        icons: [
            {
                icon: 'car.png',
                offset: '100%'
            }
        ]
    });
    return RoadPath;
}
function rotate() {

}
function animateCar(gMap, coordinate, data) {
    var i = 0;
    var mark = [];
    var lat = [];
    var lon = [];
    var car = 'car.png';
    mark.push(new google.maps.Marker({
        position: coordinate[i],
        map: gMap,
        title: "Hello World!",
        icon: 'car.png'
    }));
    var lat = data['latitude'];
    var lon = data['longitude'];

    function anim(i) {
        var a = sendtocheck(lat, lon, coordinate[i]['k'], coordinate[i]['B']);
        var infowindow = new google.maps.InfoWindow({
            content: "Inside Poly= " + JSON.stringify(a)
        });
        infowindow.open(gMap, mark[i]);
        if (typeof(mark[i - 1]) !== 'undefined') {
            mark[i - 1].setMap(null);
        }
        mark.push(new google.maps.Marker({
            position: coordinate[i],
            map: gMap,
            icon: car,
            zIndex: 100
        }));
        i++;
        setTimeout(function () {
            if (i < coordinate.length) {
                anim(i);
            }
            else {
                mark = [];
                clearTimeout(anim);
                mark.push(new google.maps.Marker({
                    position: coordinate[i],
                    map: gMap,
                    icon: 'car.png'
                }));
                i = 0;
            }
        }, 20);
    }

    return anim(i);
}

function dmm_dd(deg) {
    var temp = parseInt(deg);
    temp = Math.floor(temp);
    temp = temp.toString();
    if (temp.length === 5) {
        var degrees = parseInt(deg.substring(0, 3));
        var minutes = parseFloat(deg.substring(3, 10));
        return deg = degrees + (minutes / 60);
    }
    else {
        var degrees = parseInt(deg.substring(0, 2));
        var minutes = parseFloat(deg.substring(2, 10));
        return deg = degrees + (minutes / 60);
    }
}
function totalVehicle() {
    var vehiclecount = JSLINQ(jsonObject).Distinct(function (item) {
        return item.vehicleId
    }).ToArray();
    return vehiclecount;
}
function parseData(data) {
    var arr = [];
    var dt = jQuery.each(data, function (index, value) {
        var dt_str = value.toString();
        arr.push(dmm_dd(dt_str));
    });
    return arr;
}
function getvehicledata(id) {
    var vehicledata = JSLINQ(jsonObject).Where(function (item) {
        return item.vehicleId == id;
    });
    return vehicledata;
}
function getlatitude(id) {
    var vehicledata = getvehicledata(id);
    var poslat = vehicledata.Select(function (item) {
        return item.position.latitude
    }).ToArray();
    var latitude = parseData(poslat);
    return latitude;
}

function getlongitude(id) {
    var vehicledata = getvehicledata(id);
    var poslong = vehicledata.Select(function (item) {
        return item.position.longitude
    }).ToArray();
    var longitude = parseData(poslong);
    return longitude;
}
function getHour(id) {
    var vehicledata = getvehicledata(id);
    var hr = vehicledata.Select(function (item) {
        return item.time.hour
    }).ToArray();
    return hr;
}
function getMin(id) {
    var vehicledata = getvehicledata(id);
    var min = vehicledata.Select(function (item) {
        return item.time.minute
    }).ToArray();
    return min;
}
function sec(id) {
    var vehicledata = getvehicledata(id);
    var sec = vehicledata.Select(function (item) {
        return item.time.second
    }).ToArray();
    return sec;
}


(function () {
    JSLINQ = window.JSLINQ = function (dataItems) {
        return new JSLINQ.fn.init(dataItems);
    };
    JSLINQ.fn = JSLINQ.prototype = {
        init: function (dataItems) {
            this.items = dataItems;
        },

        // The current version of JSLINQ being used
        jslinq: "2.10",

        ToArray: function () {
            return this.items;
        },
        Where: function (clause) {
            var item;
            var newArray = new Array();

            // The clause was passed in as a Method that return a Boolean
            for (var index = 0; index < this.items.length; index++) {
                if (clause(this.items[index], index)) {
                    newArray[newArray.length] = this.items[index];
                }
            }
            return new JSLINQ(newArray);
        },
        Select: function (clause) {
            var item;
            var newArray = new Array();

            // The clause was passed in as a Method that returns a Value
            for (var i = 0; i < this.items.length; i++) {
                if (clause(this.items[i])) {
                    newArray[newArray.length] = clause(this.items[i]);
                }
            }
            return new JSLINQ(newArray);
        },
        OrderBy: function (clause) {
            var tempArray = new Array();
            for (var i = 0; i < this.items.length; i++) {
                tempArray[tempArray.length] = this.items[i];
            }
            return new JSLINQ(
                tempArray.sort(function (a, b) {
                    var x = clause(a);
                    var y = clause(b);
                    return ((x < y) ? -1 : ((x > y) ? 1 : 0));
                })
            );
        },
        OrderByDescending: function (clause) {
            var tempArray = new Array();
            for (var i = 0; i < this.items.length; i++) {
                tempArray[tempArray.length] = this.items[i];
            }
            return new JSLINQ(
                tempArray.sort(function (a, b) {
                    var x = clause(b);
                    var y = clause(a);
                    return ((x < y) ? -1 : ((x > y) ? 1 : 0));
                })
            );
        },
        SelectMany: function (clause) {
            var r = new Array();
            for (var i = 0; i < this.items.length; i++) {
                r = r.concat(clause(this.items[i]));
            }
            return new JSLINQ(r);
        },
        Count: function (clause) {
            if (clause == null)
                return this.items.length;
            else
                return this.Where(clause).items.length;
        },
        Distinct: function (clause) {
            var item;
            var dict = new Object();
            var retVal = new Array();
            for (var i = 0; i < this.items.length; i++) {
                item = clause(this.items[i]);
                // TODO - This doens't correctly compare Objects. Need to fix this
                if (dict[item] == null) {
                    dict[item] = true;
                    retVal[retVal.length] = item;
                }
            }
            dict = null;
            return new JSLINQ(retVal);
        },
        Any: function (clause) {
            for (var index = 0; index < this.items.length; index++) {
                if (clause(this.items[index], index)) {
                    return true;
                }
            }
            return false;
        },
        All: function (clause) {
            for (var index = 0; index < this.items.length; index++) {
                if (!clause(this.items[index], index)) {
                    return false;
                }
            }
            return true;
        },
        Reverse: function () {
            var retVal = new Array();
            for (var index = this.items.length - 1; index > -1; index--)
                retVal[retVal.length] = this.items[index];
            return new JSLINQ(retVal);
        },
        First: function (clause) {
            if (clause != null) {
                return this.Where(clause).First();
            }
            else {
                // If no clause was specified, then return the First element in the Array
                if (this.items.length > 0)
                    return this.items[0];
                else
                    return null;
            }
        },
        Last: function (clause) {
            if (clause != null) {
                return this.Where(clause).Last();
            }
            else {
                // If no clause was specified, then return the First element in the Array
                if (this.items.length > 0)
                    return this.items[this.items.length - 1];
                else
                    return null;
            }
        },
        ElementAt: function (index) {
            return this.items[index];
        },
        Concat: function (array) {
            var arr = array.items || array;
            return new JSLINQ(this.items.concat(arr));
        },
        Intersect: function (secondArray, clause) {
            var clauseMethod;
            if (clause != undefined) {
                clauseMethod = clause;
            } else {
                clauseMethod = function (item, index, item2, index2) {
                    return item == item2;
                };
            }

            var sa = secondArray.items || secondArray;

            var result = new Array();
            for (var a = 0; a < this.items.length; a++) {
                for (var b = 0; b < sa.length; b++) {
                    if (clauseMethod(this.items[a], a, sa[b], b)) {
                        result[result.length] = this.items[a];
                    }
                }
            }
            return new JSLINQ(result);
        },
        DefaultIfEmpty: function (defaultValue) {
            if (this.items.length == 0) {
                return defaultValue;
            }
            return this;
        },
        ElementAtOrDefault: function (index, defaultValue) {
            if (index >= 0 && index < this.items.length) {
                return this.items[index];
            }
            return defaultValue;
        },
        FirstOrDefault: function (defaultValue) {
            return this.First() || defaultValue;
        },
        LastOrDefault: function (defaultValue) {
            return this.Last() || defaultValue;
        }
    };
    JSLINQ.fn.init.prototype = JSLINQ.fn;
})();

function clearOverlays() {
    while (markers[0]) {
        markers.pop().setMap(null)
    }
}