fitx.utils.require (['fitx', 'lib1'])

fitx.lib1.MapAnimator = function (config) {
	var _self = this

	_self._mapCanvas = config.canvas
	_self._mapCenter = config.center

	_self._mapZoom   = fitx.utils.getattr (config, "zoom", 14)

	var mapOptions = {
		 center: _self._mapCenter
		,zoom: _self._mapZoom
	}

	_self._map = new google.maps.Map (_self._mapCanvas, mapOptions)

	_self.map = function () {
		return _self._map
	}

	_self._animations = {}

	_self.newAnimation = function (name, config) {
		var animationConfig = {mapAnimator:_self, name:name}
		Object.merge (animationConfig, config)
		var animation = new fitx.lib1.Animation (animationConfig)
		_self._animations[name] = animation
		return animation
	}

	_self.getAnimation = function (name) {
		return _self._animations[name]
	}

	_self._markers = {}

	_self.newMarker = function (name, config) {
		var _config = {
			url:config.url,
			position: new google.maps.LatLng (config.position[0], config.position[1])
		}

		if (Object.has (config, "scale")) {
			_config.scale = new google.maps.Size (config.scale[0], config.scale[1])
		} else {
			_config.scale = null
		}

		if (Object.has (config, "anchor")) {
			_config.anchor = new google.maps.Point (config.anchor[0], config.anchor[1])
		} else {
			_config.anchor = null
		}

		var iconSpec = {url:_config.url}
		if (_config.scale) {
			iconSpec.scaledSize = _config.scale
		}
		if (_config.anchor) {
			iconSpec.anchor = _config.anchor
		}

		var newMarker = new google.maps.Marker ({icon:iconSpec})
		_self._markers[name] = newMarker
		newMarker.setPosition (_config.position)
		newMarker.setMap (_self._map)

		return newMarker
	}

	_self.removeMarker = function (name) {
		var marker = _self._markers[name]
		if (marker) {
			marker.setMap (null)
		}

		delete _self._markers[name]
	}
}

fitx.lib1.Animation = function (config) {
	var _self = this

	_self._mapAnimator = config.mapAnimator
	_self._name = config.name

	_self._steps = config.steps
	_self._timeMultiplier = config.timeMultiplier

	_self._iconSpec = fitx.utils.getattr (config, "iconSpec", null)

	_self._infoContent = fitx.utils.getattr (config, "infoContent", null)

	_self._lineColor = fitx.utils.getattr (config, "lineColor", "#F00")
	_self._lineOpacity = fitx.utils.getattr (config, "lineOpacity", 1.0)
	_self._lineWidth = fitx.utils.getattr (config, "lineWidth", 2)

	_self._path = fitx.utils.getattr (config, "path", [])

	_self._stepCallback = fitx.utils.getattr (config, "stepCallback", null)

	_self.name = function () {
		return _self._name
	}

	_self.steps = function () {
		var args = arguments
		if (args.length == 0) {
			return _self._steps
		} else {
			_self._steps = args[0]
		}
	}

	_self.timeMultiplier = function () {
		var args = arguments
		if (args.length == 0) {
			return _self._timeMultiplier
		} else {
			_self._timeMultiplier = args[0]
		}
	}

	_self.infoContent = function () {
		var args = arguments
		if (args.length == 0) {
			return _self._infoContent
		} else {
			var lastInfoContent = _self._infoContent
			_self._infoContent = "" + args[0]

			if (_self._isVisible) {
				if (lastInfoContent == null) {
					_self._openInfoWindow ()
				} else {
					_self._updateInfoWindow ()
				}
			}
		}
	}

	if (_self._iconSpec != null) {
		var iconSpec = {url:_self._iconSpec.url}
		var scale = fitx.utils.getattr (_self._iconSpec, "scale", null)
		if (scale != null) {
			iconSpec.scaledSize = new google.maps.Size (scale[0], scale[1])
		}
		var anchor = fitx.utils.getattr (_self._iconSpec, "anchor", null)
		if (anchor != null) {
			iconSpec.anchor = new google.maps.Point (anchor[0], anchor[1])
		}

		_self._headerMarker = new google.maps.Marker ({icon:iconSpec})
	} else {
		_self._headerMarker = null
	}

	_self._openInfoWindow = function () {
		if (_self._infoContent != null) {
			_self._infoWindow = new google.maps.InfoWindow ({
				content:_self._infoContent
			})
		} else {
			_self._infoWindow = null
		}

		if (_self._path.length > 0 && _self._headerMarker != null && _self._infoContent != null) {
			_self._infoWindow.open (_self._mapAnimator._map, _self._headerMarker)
		}
	}

	_self._updateInfoWindow = function () {
		_self._infoWindow.setContent (_self._infoContent)
	}

	_self._nextAnimationStep = null
	_self._nextAnimationControl = null

	_self._stepDelay = 250

	_self._isVisible = true
	_self._drawnLines = []

	var resume = function () {
		var args = arguments
		if (args.length > 0) {
			_self._nextAnimationStep = args[0]
		}
		if (_self._nextAnimationStep != null) {
			_self._nextAnimationControl = (function () {
				var animationStep = _self._nextAnimationStep
				_self._nextAnimationStep = null
				_self._nextAnimationControl = null
				animationStep ()
			}).delay (Math.round (_self._stepDelay))
		}
	}

	var pause = function () {
		if (_self._nextAnimationControl != null) {
			_self._nextAnimationControl.cancel ()
			_self._nextAnimationControl = null
		}
	}

	var playSegment = function (pathIndex) {
		if (pathIndex < 0 || pathIndex + 1 >= _self._path.length) {
			_self._nextAnimationControl = function () { playSegment (pathIndex) }
			return
		}

		var p1 = _self._path[pathIndex][0]
		var p2 = _self._path[pathIndex + 1][0]

		var t1 = _self._path[pathIndex][1]
		var t2 = _self._path[pathIndex + 1][1]

		_self._stepDelay = (t2 - t1) * 1000 / _self._timeMultiplier

		if (_self._stepDelay <= 0) {
			_self._stepDelay = 1
		}

		var points = [p1]
		var latStep = (p2.lat() - p1.lat()) / _self._steps
		var lngStep = (p2.lng() - p1.lng()) / _self._steps
		for (var i = 1; i < _self._steps; i++) {
			var latN = p1.lat() + (i*latStep)
			var lngN = p1.lng() + (i*lngStep)
			points.push ({lat:latN, lng:lngN})
		}
		points.push (p2)

		var playPartialSegment = function (partialPathIndex) {
			var n1 = partialPathIndex
			var n2 = partialPathIndex + 1

			if (n2 >= points.length) {
				playSegment (pathIndex + 1)
			} else {

				if (pathIndex == 0 && _self._headerMarker != null) {
					_self._headerMarker.setPosition (_self._path[pathIndex][0])
					_self._headerMarker.setMap (_self._mapAnimator._map)
				}

				var drawnLine = new google.maps.Polyline ({
					path: [points[n1], points[n2]],
					strokeColor: _self._lineColor,
					strokeOpacity: _self._lineOpacity,
					strokeWidth: _self._lineWidth,
				})

				drawnLine.setVisible (_self._isVisible)
				_self._drawnLines.push (drawnLine)

				if (_self._headerMarker != null) {
					_self._headerMarker.setPosition (points[n2])
				}

				if (_self._stepCallback != null) {
					_self._stepCallback (_self, pathIndex)
				}
				drawnLine.setMap (_self._mapAnimator._map)

				if (n2 + 1 >= points.length) {
					playSegment (pathIndex + 1)
				} else {
					resume (function () {playPartialSegment (n2)})
				}
			}
		}

		resume (function () {playPartialSegment (0)})
	}

	_self.reset = function () {
		jQuery.each (_self._drawnLines, function (index, item) {
			item.setMap (null)
		})
		_self._nextAnimationStep = function () { playSegment (0) }
		_self._drawnLines = []
	}

	_self.reset ()

	_self.play = function () {
		resume ()
	}

	_self.pause = function () {
		pause ()
	}

	_self._updateDrawnLinesVisibility = function () {
		jQuery.each (_self._drawnLines, function (index, item) {
			item.setVisible (_self._isVisible)
		})
	}

	_self._updateMarkerVisibility = function () {
		if (_self._headerMarker != null) {
			_self._headerMarker.setVisible (_self._isVisible)
		}
	}

	_self.hide = function () {
		_self._isVisible = false
		_self._updateDrawnLinesVisibility ()
		_self._updateMarkerVisibility ()

		if (_self._infoWindow != null) {
			_self._infoWindow.close ()
			_self._infoWindow = null
		}
	}

	_self.unhide = function () {
		_self._isVisible = true
		_self._updateDrawnLinesVisibility ()
		_self._updateMarkerVisibility ()

		var temp = _self.infoContent ()
		_self._infoContent = null
		_self.infoContent (temp)
	}

	_self.remove = function () {
		_self.pause ()
		jQuery.each (_self._drawnLines, function (index, item) {
			item.setMap (null)
		})

		if (_self._headerMarker != null) {
			_self._headerMarker.setMap (null)
		}

		delete _self._mapAnimator._animations[_self._name]
	}
}

