fitx.utils.require(['fitx', 'lib1'])

fitx.lib1.TRIGGER_CUSTOM = 0

fitx.lib1.AjaxControl = function (config, trigger) {

	var _self = this

	if (trigger != fitx.lib1.TRIGGER_CUSTOM) {
		/* REQUIRED unless CUSTOM */
		_self.selector = config.selector
	}

	/* REQUIRED */
	_self.actionUrl = config.actionUrl

	_self.actionMethod = fitx.utils.defaultGet(
			config, 'actionMethod', 'POST'
	)
	_self.dataFunction = fitx.utils.defaultGet(
			config, 'dataFunction', function () {
					return {}
			}
	)

	/* REQUIRED */
	_self.successFunction = config.successFunction

	/* REQUIRED */
	_self.failureFunction = config.failureFunction

	_self.preRequestFunction = fitx.utils.defaultGet(
			config, 'preRequestFunction', function () {
			}
	)

	var fireFunction = function (evt) {

		if (trigger == fitx.lib1.TRIGGER_CUSTOM) {
			var args = arguments
		} else {
			evt.preventDefault()
		}

		var _cancelRequest = false

		var dataControl = {
			cancelRequest: function () {
					_cancelRequest = true
			},
			eventObject: function () {
					return evt
			},
			args: function () {
				return args
			}
		}

		var _dataToSend = _self.dataFunction(dataControl)

		if (_cancelRequest) {
			return;
		}

		var _actionUrl = _self.actionUrl

		if (!('organizationId' in _dataToSend)) {
			_dataToSend['organizationId'] = fitx.utils.defaultGet(
					fitx.config, 'organizationId', null
			)
		}

		var control = {
			data: function () {
				if (arguments.length == 0) {
						return _dataToSend
				} else if (arguments.length == 1) {
						_dataToSend = arguments[0]
				}
			},
			cancelRequest: function () {
				_cancelRequest = true
			},
			actionUrl: function () {
				if (arguments.length == 0) {
						return _actionUrl
				} else if (arguments.length == 1) {
						_actionUrl = arguments[0]
				}
			},
			eventObject: function () {
				return evt
			},
			args: function () {
				return args
			}
		}

		_self.preRequestFunction(control)

		if (!_cancelRequest) {
			jQuery.ajax(
				_actionUrl,
				{
						type: _self.actionMethod,
						data: _dataToSend,
						dataType: 'json',
						success: _self.successFunction,
				}
			).fail(_self.failureFunction)
		}
	}

	if (trigger == fitx.lib1.TRIGGER_CUSTOM) {
		_self.fire = fireFunction
	} else {
		//jQuery (_self.selector)[trigger] (
		jQuery("body").on(trigger, _self.selector, fireFunction)
	}
}

fitx.lib1.Form = function (config) {
    fitx.lib1.AjaxControl.bind(this)(config, 'submit')
}

fitx.lib1.AjaxClickable = function (config) {
    fitx.lib1.AjaxControl.bind(this)(config, 'click')
}

fitx.lib1.CustomAjax = function (config) {
	fitx.lib1.AjaxControl.bind (this) (config, fitx.lib1.TRIGGER_CUSTOM)
}

