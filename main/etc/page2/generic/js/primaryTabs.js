var flag = 0
fitx.utils.require (['fitx', 'page2', 'UtilUrl'])

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



    function childSlider(flag) {

        if (flag==0) {
            jQuery('.childContainer').addClass('childContainerHover')
            jQuery('.appButton').fadeTo(400,0.6)
            jQuery('.parentAppButton').fadeTo(400,0.6)

            jQuery('.childContainer').stop.fadeTo(800,1)
            flag = 1
        }

    }

	jQuery  ('.parentSlideButton').mouseover(function () {

                jQuery(this).slideDown(650)
                childSlider(flag)


       })

    jQuery  ('.parentSlideButton').mouseout(function () {

                    my_timer = setTimeout(function () {
                        jQuery('.childContainer').hide();
                    }, 4000);
                    jQuery('.appButton').fadeTo(200,1)
                    jQuery('.parentAppButton').fadeTo(200,1)
       })

    jQuery  ('.childContainer').mouseover(function () {

               jQuery('.childContainer').addClass('childContainerHover')
               flag = 0
               childSlider(flag)

       })





	 jQuery('.logout').click(function () {

        console.log('cancel')
     	b = sendAjaxRequest('logoutAction', 'user', 'abc')
        alert("User will be logged out")
        location.reload()
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

