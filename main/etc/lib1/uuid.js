fitx.utils.require(['fitx', 'lib1'])

fitx.lib1._mTwister = new MersenneTwister()

fitx.lib1._uuidRng = function () {
    var result = new Array(16)
    for (var i = 0; i < 16; i++) {
        result[i] = parseInt(fitx.lib1._mTwister.random() * 256)
    }

    return result
}

fitx.lib1.uuid = function () {
    var buffer = new Array(16)
    uuid.v4({rng: fitx.lib1._uuidRng}, buffer)

    var result = ""
    for (var i = 0; i < 16; i++) {
        var hex = buffer[i].toString(16)

        if (hex.length == 1) {
            result += "0" + hex
        } else {
            result += hex
        }
    }

    return result
}

