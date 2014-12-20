fitx.utils.require(['fitx', 'page2', 'newPlaybackForm']);
fitx.utils.require(['fitx', 'page2', 'newPlaybackFormAction']);

jQuery(window).load(function() {
	/**********************Hide/Show in Beginning******************/
	jQuery('.typeFix').hide()
	
	/************************Control Related**********************/
	var mapLoaded = false
	
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
	
	function setupData() {
		var curdate = new Date();
		var offset =-1* curdate.getTimezoneOffset();
		var gmtAdjust=offset*60;

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
		
		specificFormData['gmtAdjust'] = gmtAdjust
		
        return specificFormData;
	}
	
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
	
	jQuery('#loadMap').click (function (){
		makeMapAnimator()
		
		mapLoaded = true
	})
	
	jQuery('.resetMap').click (function (){
		makeMapAnimator()
		
		mapLoaded = true
	})
	
	jQuery('.start').click(function () {
		if (mapLoaded == true) {
			removeAnimation()
			startNewAnimation()
			
			jQuery(this).hide()
			jQuery('.pause').show()
			jQuery('.restart').show()
		}
	})
	
	jQuery('.restart').click(function () {
		removeAnimation()
		startNewAnimation()
		
		jQuery('.pause').show()
		jQuery('.resume').hide()
	})
	
	jQuery('.pause').click(function () {
		pauseAnimation()
		
		jQuery(this).hide()
		jQuery('.resume').show()
	})
	
	jQuery('.resume').click(function () {
		playAnimation()
		
		jQuery(this).hide()
		jQuery('.pause').show()
	})
	
	jQuery('.vehicleSelector input[type=checkbox]').change(function(){
		hideAnimation()
		jQuery('.vsVehicleId:checked').each (function(){
		    var vehicleId = jQuery (this).data( "details" ).deviceId
			unhideAnimation(vehicleId)
	    })
	})
	
	jQuery('.increaseAnimationSpeed').click(function(){
		changeAnimationSpeed('increase')
	})
	
	jQuery('.decreaseAnimationSpeed').click(function(){
		changeAnimationSpeed('decrease')
	})
	
	jQuery('Input[name=type]').change(function(evt) {
					var value = jQuery(evt.target).val();
					if (value == 'Relative') {
									jQuery('.typeRelative').show();
									jQuery('.typeFix').hide();
					} else if (value == 'Fix') {
									jQuery('.typeRelative').hide();
									jQuery('.typeFix').show();
					}
	});
	
	/*************************Animation Related******************/
	var mapAnimator, map;
	var epoch = new Date (1970, 0, 1, 0, 0, 0)
	
	function makeMapAnimator () {
		mapAnimator = new fitx.lib1.MapAnimator ({
			canvas:jQuery ('#map')[0],
			center: new google.maps.LatLng (23.25, 77.417)
		})
		map = mapAnimator.map ()
	}
	
	var animations = {}
	function startNewAnimation() {
		
		var idList = []
        var vehicleId
        jQuery('.vsVehicleId:checked').each (function(){
		    vehicleId = jQuery (this).data( "details" ).deviceId
            idList.push (vehicleId)
	    })
		
		jQuery.each(idList, function(index, id) {
			var ajaxReq = new fitx.lib1.CustomAjax ({
				actionUrl : fitx.utils.appUrl('newPlaybackFormAction'),
				actionMethod : 'GET',
				dataFunction : function () {
					return {
						'data' : JSON.stringify (setupData()),
						'id' : id
					}
				},
				successFunction : function (result) {
					var coordinates = result.message[0]
					var status = result.message[1][0]
					var path = []
					jQuery.each (coordinates, function (index, item) {
						var lat = parseFloat(item.position.latitude)
						var lng = parseFloat(item.position.longitude)
						var point = new google.maps.LatLng (lat, lng)
						var time = new Date (
							item.time.year, item.time.month, item.time.day,
							item.time.hour, item.time.minute, item.time.second
						)
						var seconds = time.secondsSince (epoch)

						//console.log (item[0] + ", " + item[1] + ", " + seconds)
						
						var extraData = {'name':status.name, 'regNo':status.regNo, 'timestamp':item.timestamp, 'speed':item.speed}
						path.push ([point, seconds, extraData])
					})

					var animation1 = mapAnimator.newAnimation ('animation1', {
						steps: 2,
						timeMultiplier: 40,
						path: path,
						iconSpec: {
							url: fitx.utils.appUrl ("assets", "car1.png"),
							scale: [20, 20],
							anchor: [10, 10],
						},
						stepCallback: function (animation, index) {
							var pointData = animation.path()[index][2]
							var infoWindowDiv = '<div class="vehicleInfoWindow">\
									Vehicle Name : ' + pointData.name + '<br/>\
									Reg No : ' + pointData.regNo + '<br/>\
									Speed : ' + pointData.speed + '<br/>\
									Time : ' + pointData.timestamp + '\
								</div>'
								
							animation.infoContent (infoWindowDiv)
						},
					})

					map.setZoom (13)
					map.setCenter (path[0][0])
					animation1.play ()
					animations[result.message[1][0].deviceId] = animation1
				},
				failureFunction : function () {
					console.log ('failed...')
				},
			})
			ajaxReq.fire ()
		})
	}
	
	function removeAnimation (id) {
		if (id != undefined) {
			if (id in animations) {
				animations[id].remove ()
				delete animations[id]
			}
		} else {
			jQuery.each (animations, function (id, animation){
				animation.remove ()
			})
		}
	}
	
	function hideAnimation (id) {
		if (id != undefined) {
			if (id in animations) {
				animations[id].hide ()
			}
		} else {
			jQuery.each (animations, function (id, animation){
				animation.hide ()
			})
		}
	}
	
	function unhideAnimation (id) {
		if (id != undefined) {
			if (id in animations) {
				animations[id].unhide ()
			}
		} else {
			jQuery.each (animations, function (id, animation){
				animation.unhide ()
			})
		}
	}
	
	function pauseAnimation (id) {
		if (id != undefined) {
			if (id in animations) {
				animations[id].pause ()
			}
		} else {
			jQuery.each (animations, function (id, animation){
				animation.pause ()
			})
		}
	}
	
	function playAnimation (id) {
		if (id != undefined) {
			if (id in animations) {
				animations[id].play ()
			}
		} else {
			jQuery.each (animations, function (id, animation){
				animation.play ()
			})
		}
	}
	
	function changeAnimationSpeed(task, id) {
		var multiplier = 1.5
		if (id != undefined) {
			if (id in animations) {
				if(task == 'increase') {
					animations[id].timeMultiplier(animations[id].timeMultiplier() * multiplier)
				} else if(task=='decrease') {
					animations[id].timeMultiplier(animations[id].timeMultiplier() / multiplier)
				}
			}
		} else {
			jQuery.each (animations, function (id, animation){
				if(task == 'increase') {
					animation.timeMultiplier(animation.timeMultiplier() * multiplier)
				} else if(task=='decrease') {
					animation.timeMultiplier(animation.timeMultiplier() / multiplier)
				}
			})
		}
	}
})
