jQuery(document).ready(
    function () {

        console.log('fitx admin landing: hello world')

        jQuery('.ptContainer .homeButton').click(
            function (evt) {
                evt.preventDefault()
                fitx.utils.loadPage('/fitxAdmin/tab/home')
            }
        )

        jQuery('.ptContainer .dashboardButton').click(
            function (evt) {
                evt.preventDefault()
                fitx.utils.loadPage('/fitxAdmin/tab/dashboard')
            }
        )

        var newTabWithoutSwitchButton = new fitx.lib1.AjaxClickable(
            {
                selector: '.newTabWithoutSwitchButton',
                actionUrl: '/fitxAdmin/newTab',
                successFunction: function (result) {
                    console.log(result)
                    if (result.success) {
                        fitx.utils.loadPage('/fitxAdmin/tab/home')
                    }
                }
            }
        )

        var newTabWithSwitchButton = new fitx.lib1.AjaxClickable(
            {
                selector: '.newTabWithSwitchButton',
                actionUrl: '/fitxAdmin/newTab',
                successFunction: function (result) {
                    console.log(result)
                    if (result.success) {
                        fitx.utils.loadPage('/fitxAdmin/tab/' + result.newTabId)
                    }
                }
            }
        )

        jQuery('.tabButton').click(
            function (eventObject) {
                eventObject.preventDefault()

                var target = eventObject.target
                var parentId = jQuery(target).parent().attr('id')
                fitx.utils.loadPage('/fitxAdmin/tab/' + parentId)
            }
        )

        var tabCloseButton = new fitx.lib1.AjaxClickable(
            {
                selector: '.tabCloseButton',
                actionUrl: '/fitxAdmin/closeTab',
                dataFunction: function (eventObject) {
                    var parentId = jQuery(eventObject.target).parent().attr('id')
                    return {id: parentId}
                },
                successFunction: function (result) {
                    console.log(result)
                    fitx.utils.loadPage('/fitxAdmin/tab/home')
                }
            }
        )

        /*
         var tabShifter = function (shiftValue) {
         var target = jQuery ('.ptContainer .tabButtonContainer:first-of-type')
         target.css (
         'margin-left',
         parseInt (target.css ('margin-left')) + shiftValue
         )
         }

         var leftScrollIntervalId = null;
         var rightScrollIntervalId = null;

         jQuery ('.ptContainer .scrollLeft').click (marginShifter (10))
         jQuery ('.ptContainer .scrollRight').click (marginShifter (-10))

         jQuery ('.ptContainer .scrollLeft').mouseenter (

         function () {

         if (leftScrollIntervalId != null) {
         window.clearInterval (leftScrollIntervalId)
         leftScrollIntervalId = null
         }

         leftScrollIntervalId = window.setInterval (
         function () {tabShifter (10)},
         500
         )
         }
         )

         jQuery ('.ptContainer .scrollLeft').mouseleave (

         function () {

         if (leftScrollIntervalId != null) {
         window.clearInterval (leftScrollIntervalId)
         leftScrollIntervalId = null
         }
         }
         )
         */

        var Scroller = function (config) {
            var _self = this

            _self.target = jQuery(config.target)
            _self.shiftTarget = jQuery(config.shiftTarget)
            _self.shiftValue = config.shiftValue
            _self.shiftInterval = config.shiftInterval

            _self.intervalId = null

            _self.shifter = function () {
                _self.shiftTarget.css('margin-left',
                        (parseInt(_self.shiftTarget.css('margin-left')) + _self.shiftValue) + 'px'
                )
            }

            _self.clearIntervalId = function () {
                if (_self.intervalId != null) {
                    window.clearInterval(_self.intervalId)
                    _self.intervalId = null
                }
            }

            _self.startScrolling = function () {
                _self.clearIntervalId()
                _self.intervalId = window.setInterval(_self.shifter, _self.shiftInterval)
            }

            _self.target.mousedown(_self.startScrolling)
            _self.target.mouseup(_self.clearIntervalId)
            _self.target.mouseleave(_self.clearIntervalId)
        }

        var shiftValue = 25
        var shiftInterval = 100

        var leftScroller = new Scroller(
            {
                target: '.ptContainer .scrollLeft',
                shiftTarget: '.ptContainer .tabButtonContainer:first-of-type',
                shiftValue: shiftValue,
                shiftInterval: shiftInterval,
            }
        )

        var rightScroller = new Scroller(
            {
                target: '.ptContainer .scrollRight',
                shiftTarget: '.ptContainer .tabButtonContainer:first-of-type',
                shiftValue: -shiftValue,
                shiftInterval: shiftInterval,
            }
        )
    }
)

