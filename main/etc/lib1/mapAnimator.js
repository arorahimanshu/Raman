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
		var animationConfig = {mapAnimator:_self}
		Object.merge (animationConfig, config)
		var animation = new fitx.lib1.Animation (animationConfig)
		_self._animations[config.name] = animation
		return animation
	}

	_self.getAnimation = function (name) {
		return self._animations[name]
	}
}

fitx.lib1.Animation = function (config) {
	var _self = this

	_self._mapAnimator = config.mapAnimator

	_self._steps = config.steps
	_self._stepDelay = config.stepDelay

	_self._iconSpec = fitx.utils.getattr (config, "iconSpec", null)

	_self._infoContent = fitx.utils.getattr (config, "infoContent", null)

	_self._lineColor = fitx.utils.getattr (config, "lineColor", "#F00")
	_self._lineOpacity = fitx.utils.getattr (config, "lineOpacity", 1.0)
	_self._lineWidth = fitx.utils.getattr (config, "lineWidth", 2)

	_self._path = fitx.utils.getattr (config, "path", [])

	_self._stepCallback = fitx.utils.getattr (config, "stepCallback", null)

	_self.steps = function () {
		var args = arguments
		if (args.length == 0) {
			return _self._steps
		} else {
			_self._steps = args[0]
		}
	}

	_self.stepDelay = function () {
		var args = arguments
		if (args.length == 0) {
			return _self._stepDelay
		} else {
			_self._stepDelay = args[0]
		}
	}

	_self.infoContent = function () {
		var args = arguments
		if (args.length == 0) {
			return _self._infoContent
		} else {
			var lastInfoContent = _self._infoContent
			_self._infoContent = "" + args[0]
			if (lastInfoContent == null) {
				_self._openInfoWindow ()
			} else {
				_self._updateInfoWindow ()
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
			}).delay (_self._stepDelay)
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

		var p1 = _self._path[pathIndex]
		var p2 = _self._path[pathIndex + 1]

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
					_self._headerMarker.setPosition (_self._path[pathIndex])
					_self._headerMarker.setMap (_self._mapAnimator._map)
				}

				var drawnLine = new google.maps.Polyline ({
					path: [points[n1], points[n2]],
					strokeColor: _self._lineColor,
					strokeOpacity: _self._lineOpacity,
					strokeWidth: _self._lineWidth,
				})

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
		_self._nextAnimationStep = function () { playSegment (0) }
	}

	_self.reset ()

	_self.play = function () {
		resume ()
	}

	_self.pause = function () {
		pause ()
	}
}

