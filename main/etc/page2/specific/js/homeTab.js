jQuery(window).load(

    function () {
        var flag=1
        jQuery('#addGpsDataForm').hover(

            function (event) {

                if(flag==1) {
                    flag=0
                    jQuery('#overlay').empty();
                    var s = "" +
                        "<div data-info='{\"url\":\"/newGpsDataForm\"}'  id='liveTracking' class='appButton2 unselectable'>Live Tracking</div>" +
                        "<div data-info='{\"url\":\"/newDashboardForm\"}' id='dashboard'  class='appButton2 unselectable'>Dashboard</div>" +
                        "<div data-info='{\"url\":\"/addGpsDataForm\"}' id='playback'  class='appButton2 unselectable'>Playback</div>"
                    jQuery('#overlay').append(s)

                    jQuery('#overlay').css('left', event.pageX)
                    jQuery('#overlay').css('top', event.pageY)
                    jQuery('.body').css('opacity', '0.4')

                }

            }
        )


        jQuery('body').click(function(){

            jQuery('#overlay').empty();
            jQuery('.body').css('opacity','1')
            flag=1
        })


        jQuery('body').on('click', '.unselectable', function () {
                var _button = jQuery(this)
                var info = _button.data().info

                //fitx.utils.loadPage (info.url)
                fitx.utils.pageWithParams(
                    info.url,
                    fitx.page2.requestNewTab(info.url)
                )
            }
        )
    }


)

