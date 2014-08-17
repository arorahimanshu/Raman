jQuery(window).load(
    function () {
        //console.log ('login page javascript')
        jQuery(".loginLogo").effect("bounce", { times: 4 }, "slow");
        jQuery(".username").effect("bounce", { times: 1 }, "slow");
        jQuery(".unselectable").effect("bounce", { times: 2 }, "slow");
        jQuery(".password").effect("bounce", { times: 3 }, "slow");
        jQuery(".loginLogo").effect("bounce", { times: 4 }, "slow");

        jQuery('.loginForm input').keypress(
            function (eventObject) {
                var keycode = eventObject.which
                if (keycode == 10 || keycode == 13) {
                    jQuery('.loginForm form').submit()
                }
            }
        )

        jQuery('.loginForm .username input').focus()
        jQuery('.loginForm .submit').click(
            function () {
                jQuery('.loginForm form').submit()
            }
        )

        var loginForm = new fitx.lib1.Form(
            {
                selector: '.loginForm form',
                actionUrl: fitx.config.loginFormActionUrl,
                dataFunction: function () {
                    return {
                        username: jQuery('.loginForm .username input').val(),
                        password: jQuery('.loginForm .password input').val(),
                    }
                },
                preRequestFunction: function (control) {
                    fitx.utils.resetInfoCookie()
                },
                successFunction: function (result) {
                    if (result.success == true) {
                        fitx.utils.loadPage(fitx.config.loginFormSuccessUrl);
                    } else {
                        console.log(result.message)
                    }
                },
                failureFunction: function () {
                    console.log('... Login Failed')
                },
            }
        )
    }
)

