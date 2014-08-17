fitx.utils.require(['fitx', 'page2', 'newServiceForm']);

jQuery(window).load(function () {
    setupAJAXSubmit('newServiceForm', 'newServiceFormActionUrl', setupData, setupConstraints)
})

function setupData() {
    var specificFormData = {}

    specificFormData.productName = jQuery('#productName').val()
    specificFormData.productType = jQuery('#productType').val()
    specificFormData.unitType = jQuery('#unitType').val()
    specificFormData.baseCost = parseInt(jQuery('#baseCost').val())
    specificFormData.baseUnit = parseInt(jQuery('#baseUnit_Hour').val()) * 60 + parseInt(jQuery('#baseUnit_Minute').val())
    specificFormData.capacity = parseInt(jQuery('#capacity').val())
    specificFormData.status = jQuery('#status').val()
    specificFormData.showOnWebsite = jQuery('#showOnWebsite').is(' :checked')
    specificFormData.canSingle = jQuery('#canSingle').is(' :checked')
    console.log(specificFormData.baseUnit)

    return specificFormData
}

function setupConstraints() {

    var specificFormConstraints = {
        productName: {
            presence: true
        },

        productType: {
            presence: true
        },

        unitType: {
            presence: true
        },

        baseCost: {
            presence: true
        },

        baseUnit: {
            presence: true,
            numericality: {
                message: "Enter Valid Numbers"
            }
        },

        capacity: {
            presence: true
        },

        status: {
            presence: true
        }
    }

    return specificFormConstraints
}