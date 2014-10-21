fitx.utils.require(['fitx', 'page2', 'rbacAuth']);

jQuery(window).load(function () {
    setupAJAXSubmit('securitySettings', 'securitySettingsAction', setupData, setupConstraints,'#save')
    jQuery('#cancel').click(function(){
         fitx.page2.closeActiveTab()
    })

	jQuery ('#user').val ('0')
	
    jQuery('#user').on('change',function(){
        var user = jQuery(this).val()
        
        if(user == '0'){
			jQuery('.permissionDataContainer').hide ()
			jQuery ('.role').prop ("checked", false)
			jQuery ('.permission').prop ("checked", false)
        }
        else{
			sendAjaxRequest('userSecuritySettings',user,function(data){
				data = data.message
				jQuery.each (data, function (k, v) {
					jQuery ('.role[value=' + k + ']').prop ("checked", true)
					jQuery.each (v, function (i, p) {
						jQuery ('.permission[value=' + p + ']').prop ("checked", true)
					})
				})
				jQuery('.permissionDataContainer').show()
			})
        }
    })
	
	jQuery('.role').on('change',function(){
		var roles = []
		jQuery ('.role:checked').each(function (){
			var role = jQuery(this).val ();
			roles.push(role)
		})
		sendAjaxRequest('roleSecuritySettings',roles,function(data){
			data = data.message
			jQuery ('.permission').prop ("checked", false)
			jQuery.each (data, function (i, p){
				jQuery('.permission[value=' + p +']').prop ("checked", true)
			})
		})
	})
})

function setupData() {
    var specificFormData = {}
    var user = jQuery('#user').val ()
	var roles = []
	jQuery('.role:checked').each (function(){
		var role = jQuery (this).val ()
		roles.push (role)
	})
	
	specificFormData['users'] = {
		'h':roles
	}
    return specificFormData
}

function setupConstraints() {
    var specificFormConstraints={}
    return specificFormConstraints
}