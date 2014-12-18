fitx.utils.require(['fitx', 'page2', 'newPlaybackForm']);
fitx.utils.require(['fitx', 'page2', 'newPlaybackFormAction']);

jQuery(window).load(function() {
	/************************Control Related**********************/
	makeMapAnimator()
	startNewAnimation()
	var dataTimer = 1
	
	function setupData() {
		var curdate = new Date();
		var offset =-1* curdate.getTimezoneOffset();
		var gmtAdjust=offset*60;
		
		var specificFormData = {}
		
		specificFormData['gmtAdjust'] = gmtAdjust
		
        return specificFormData;
	}
	
	jQuery('.vehicleSelector input[type=checkbox]').change(function(){
		hideAnimation()
		jQuery('.vsVehicleId:checked').each (function(){
		    var vehicleId = jQuery (this).data( "details" ).deviceId
			unhideAnimation(vehicleId)
	    })
	})
	
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
				actionUrl : fitx.utils.appUrl('newGpsDataFormAction'),
				actionMethod : 'GET',
				dataFunction : function () {
					return {
						'data' : JSON.stringify(setupData()),
						'id' : id
					}
				},
				successFunction : function (result) {
					var coordinates = result.message[0]
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

						path.push ([point, seconds])
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
							animation.infoContent ('currentIndex: ' + index)
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
