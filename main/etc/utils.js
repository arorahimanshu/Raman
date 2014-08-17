var fitx = {}
fitx.utils = {}

if (!'console' in window) {
    window.console = {
        log: function () {
        },
        trace: function () {
        },
    }
}

fitx.utils.defaultGet = function (container, key, value) {
    if (key in container) {
        return container[key]
    } else {
        return value
    }
}

fitx.utils.join = function (joinLiteral, args) {

    var argsLength = args.length

    if (argsLength == 0) {
        return ''
    } else if (argsLength == 1) {
        return args[0]
    } else {
        var result = args[0]
        jQuery.each(
            args,
            function (index, value) {
                if (index > 0) {
                    result += joinLiteral + value
                }
            }
        )
        return result
    }
}

fitx.utils.chain = function () {
    var result = []
    jQuery.each(
        arguments,
        function (index, value) {
            jQuery.each(
                value,
                function (i, v) {
                    result.push(v)
                }
            )
        }
    )

    return result
}

fitx.utils.deepcopy = function (item) {
    return JSON.parse(JSON.stringify(item))
}

fitx.utils._appUrl = function (argArray) {
    return '/' + fitx.utils.join(
        '/', fitx.utils.chain(
            fitx.config.BaseUri,
            argArray
        )
    )
}

fitx.utils.appUrl = function () {
    return fitx.utils._appUrl(arguments)
}

fitx.utils.require = function (nsArray) {
    var previous = window
    jQuery.each(nsArray,
        function (i, name) {
            if (!(name in previous)) {
                previous[name] = {}
            }
            previous = previous[name]
        }
    )
}

fitx.utils.refreshPage = function () {
    window.location.reload(true)
}

fitx.utils.loadAppPage = function () {
    var url = fitx.utils._appUrl(arguments)
    window.location.href = url
}

fitx.utils.loadPage = function (url) {
    window.location.href = url
}

fitx.utils.appPageWithParams = function (urlArgs, requestParams) {
    var params = fitx.utils.deepcopy(requestParams)
    if (!('organizationId' in params)) {
        params['organizationId'] = fitx.utils.defaultGet(
            fitx.config, 'organizationId', null
        )
    }

    window.location.href = (
        fitx.utils._appUrl(urlArgs)
        + "?requestParams="
        + encodeURIComponent(JSON.stringify(params))
        )
}

fitx.utils.pageWithParams = function (url, requestParams) {
    var params = fitx.utils.deepcopy(requestParams)
    if (!('organizationId' in params)) {
        params['organizationId'] = fitx.utils.defaultGet(
            fitx.config, 'organizationId', null
        )
    }

    window.location.href = (
        url
        + "?requestParams="
        + encodeURIComponent(JSON.stringify(params))
        )
}

fitx.utils.infoCookie = function (process) {
    var cookie = jQuery.cookie('fitxInfo')
    if (typeof cookie === "undefined") {
        jQuery.cookie(
            'fitxInfo',
            JSON.stringify({}),
            {path: '/'}
        )

        cookie = jQuery.cookie('fitxInfo')
    }

    cookie = JSON.parse(cookie)

    process(cookie)

    jQuery.cookie('fitxInfo', JSON.stringify(cookie), {path: '/'})
}

fitx.utils.resetInfoCookie = function () {
    jQuery.cookie('fitxInfo', JSON.stringify({}), {path: '/'})
}

