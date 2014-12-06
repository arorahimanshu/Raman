fitx.utils.require (['fitx', 'page2', 'UtilUrl'])

/* By Ravi :
 *
 * Please no global variables !!!
 */
fitx.FLAG_SHOW_CHILDREN = 0
fitx.FLAG_HIDE_CHILDREN = 1

fitx.page2.requestNewTab = function (url) {
	var result = {
		tabMode:'createTab',
		tabId:fitx.lib1.uuid (),
		url:url,
	}

	return result
}

fitx.page2.requestRestoreTab = function (tabId) {
	var result = {
		tabMode:'restoreTab',
		tabId:tabId,
	}

	return result
}


fitx.page2.TabScroller = function (config) {
	var _self = this

	_self.target = jQuery (config.target)
	_self.shiftTarget = jQuery (config.shiftTarget)
	_self.shiftValue = config.shiftValue
	_self.shiftInterval = config.shiftInterval
	//_self.stopIf = config.stopIf

	_self.intervalId = null

	_self.shifter = function () {
		_self.shiftTarget.css ('margin-left',
			(parseInt (_self.shiftTarget.css ('margin-left')) + _self.shiftValue) + 'px'
		)
	}

	_self.clearIntervalId = function () {
		if (_self.intervalId != null) {
			window.clearInterval (_self.intervalId)
			_self.intervalId = null
		}
	}

	_self.startScrolling = function () {
		_self.clearIntervalId ()
		_self.intervalId = window.setInterval (_self.shifter, _self.shiftInterval)
	}

	_self.target.mousedown (_self.startScrolling)
	_self.target.mouseup (_self.clearIntervalId)
	_self.target.mouseleave (_self.clearIntervalId)
}

jQuery (window).load (function () {

	var tabs = []

	jQuery ('.dynamicButtonContainer').each (function (item, element) {
		var tabInfo = jQuery (element).data ('info')
		tabs.push ({
			id:tabInfo['id'],
			title:tabInfo['title'],
			url:tabInfo['url'],
		})
	})

	/* By Ravi
	 *
	 * The idea of using global variables 'flag'
	 * is both bad programming style and incorrect.
	 *
	 * Bad style because global variables should be avoided.
	 *
	 * Incorrect, because flag will be different for each
	 * 'menu'. Global variable makes no sense here. You need to
	 * be able to associate it to the element.
	 *
	 * I have used the simple way of passing it as argument.
	 */
	function childSlider (rawElement, flag) {

		var element = jQuery (rawElement)
		if (element.hasClass ('slideWindow')) {
			var slideWindow = element
		} else {
			var slideWindow = element.parents ('.slideWindow')
		}
		var parentSlideButton = slideWindow.find ('.parentSlideButton')
		var children = slideWindow.find ('.childContainer')

		if (flag == fitx.FLAG_SHOW_CHILDREN) {
			children.removeClass ('childContainerNoHover')
			children.addClass ('childContainerHover')

			parentSlideButton.stop ().fadeTo (400, 0.6)
			children.stop ().fadeTo (800, 1)

		} else if (flag == fitx.FLAG_HIDE_CHILDREN) {
			children.removeClass ('childContainerHover')

			parentSlideButton.stop ().fadeTo (400, 1)
			children.stop ().fadeTo (400, 0, function () {
				children.addClass ('childContainerNoHover')
			})
		}
	}

	/* By Ravi :
	 *
	 * Initialising 'childHandler' data as function
	 * to show/hide children.
	 *
	 * Notice the use of .debounce()
	 */
	jQuery.each (jQuery ('.slideWindow'), function (index, rawElement) {
		var element = jQuery (rawElement)
		element.data ('childHandler', (function (flag) {
			childSlider (element, flag)
		}).debounce (250))
	})

	/* By Ravi :
	 *
	 * Initialising 'opacity' of children, so the
	 * animations play properly when activated
	 * first time. Cannot be done via CSS sheet
	 * because we dont want it to reset.
	 */
	jQuery.each (jQuery ('.childContainer'), function (index, rawElement) {
		var element = jQuery (rawElement)
		element.css ('opacity', '0')
	})

	jQuery  ('.parentSlideButton').mouseenter (function (evt) {
		var element = jQuery (evt.target)
		var slideWindow = element.parents ('.slideWindow')
		slideWindow.data ('childHandler') (fitx.FLAG_SHOW_CHILDREN)
	})

	jQuery  ('.parentSlideButton').mouseout(function (evt) {
		var element = jQuery (evt.target)
		var slideWindow = element.parents ('.slideWindow')
		slideWindow.data ('childHandler') (fitx.FLAG_HIDE_CHILDREN)
	})

	jQuery  ('.childMenuTabButton').mouseenter(function (evt) {
		var slideWindow = jQuery (evt.target).parents ('.slideWindow')
		slideWindow.data ('childHandler') (fitx.FLAG_SHOW_CHILDREN)
	})

	jQuery ('.childMenuTabButton').mouseout (function (evt) {
		var slideWindow = jQuery (evt.target).parents ('.slideWindow')
		slideWindow.data ('childHandler') (fitx.FLAG_HIDE_CHILDREN)
	})

	 jQuery('.logout').click(function () {

        var r = confirm("User will be logged out");
        if (r == false) {
                return
                }

        var b = sendAjaxRequest('logoutAction', null, null)

		//window.location.assign("http://127.0.0.1:8080");
        //myVar = setTimeout(function(){location.reload()},2000)

    })


	fitx.utils.infoCookie (function (cookie) {
		if (! ('tabs' in cookie)) {
			cookie.tabs = []
		}

		jQuery.each (tabs, function (index, tabInfo) {

			var found = false
			jQuery.each (cookie.tabs, function (index, cookieTabInfo) {
				if (cookieTabInfo.id == tabInfo.id) {
					found = true
				}
			})

			if (found == false) {
				cookie.tabs.push ({
					id:tabInfo.id,
					title:tabInfo.title,
					url:tabInfo.url,
				})
			}

		})

	})

	var goHomeUnconditional = function () {
		var url = fitx.utils.appUrl ('home')
		fitx.utils.pageWithParams (
			url,
			fitx.page2.requestRestoreTab ('home')
		)
	}

	var goHome = function () {
		if (jQuery ('.homeTab').hasClass ('activeTab')) {
			console.log ('active clicked')
		} else {
			goHomeUnconditional ()
		}
	}

	fitx.page2.closeActiveTab = function () {
		var tab = jQuery ('.activeTab')
		if (tab.hasClass ('dynamicButtonContainer')) {
			var tabInfo = tab.data ('info')

			fitx.utils.infoCookie (function (cookie) {
				var targetIndex = null;
				jQuery.each (cookie.tabs, function (index, cookieTabInfo) {
					if (tabInfo.id == cookieTabInfo.id) {
						targetIndex = index
					}
				})

				if (targetIndex != null) {
					cookie.tabs.splice (targetIndex, 1)
				}
			})

			goHomeUnconditional ()
		}
	}

	jQuery ('.homeTab').click (goHome)

	jQuery ('.tabCloseButton').click (function () {

		var tab = jQuery (this).parent ('.dynamicButtonContainer')
		var tabInfo = tab.data ('info')

		fitx.utils.infoCookie (function (cookie) {

			var targetIndex = null;
			jQuery.each (cookie.tabs, function (index, cookieTabInfo) {
				if (tabInfo.id == cookieTabInfo.id) {
					targetIndex = index
				}
			})

			if (targetIndex != null) {
				cookie.tabs.splice (targetIndex, 1)
			}
		})

		goHomeUnconditional ()
	})

	jQuery ('.dynamicButton').click (function () {
		var tab = jQuery (this).parent ('.dynamicButtonContainer')

		if (tab.hasClass ('activeTab')) {
			//console.log ('active clicked')
			return
		}

		var tabInfo = tab.data ('info')

		fitx.utils.pageWithParams (
			tabInfo.url,
			fitx.page2.requestRestoreTab (tabInfo.id)
		)
	})

	var shiftValue = 25
	var shiftInterval = 100

	var leftScroller = new fitx.page2.TabScroller ({
		target:'.primaryTabs .scrollLeft',
		shiftTarget:'.primaryTabs .dynamicButtonContainer:first',
		shiftValue:shiftValue,
		shiftInterval:shiftInterval,
		stopIf:function () {
			var tab = jQuery ('.primaryTabs .dynamicButtonContainer:first')
			var x1 = parseInt (tab.css ('margin-right'))
			var x2 = parseInt (jQuery (window).width ())

			return x1 > x2
		}
	})

	var rightScroller = new fitx.page2.TabScroller ({
		target:'.primaryTabs .scrollRight',
		shiftTarget:'.primaryTabs .dynamicButtonContainer:first',
		shiftValue:-shiftValue,
		shiftInterval:shiftInterval,
		stopIf:function () {return false;}
	})

	var dynamicTabContainer = jQuery ('.primaryTabs .dynamicTabContainer')
	var scrollLeft = jQuery ('.primaryTabs .scrollLeft')
	var scrollRight = jQuery ('.scrollRight')

	var align = function (resizeEvt) {
		dynamicTabContainer.width (
			scrollRight.offset ().left - (scrollLeft.offset ().left + scrollLeft.outerWidth ())
		)
	}

	align ()

	jQuery (window).resize (align.debounce (150))

})

