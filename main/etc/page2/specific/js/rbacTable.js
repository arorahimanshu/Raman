fitx.utils.require(['fitx', 'page2', 'rbacAuth']);

jQuery(window).load(function () {
    setupAJAXSubmit('rbacAuth', 'rbacAuthAction', setupData, setupConstraints,'#save')
    jQuery('#cancel').click(function(){
         fitx.page2.closeActiveTab()
    })

    jQuery('.selectBoxContainer').css('margin-left','auto')
    jQuery('.selectBoxContainer').css('margin-bottom','0')

    jQuery('#role').on('change',function(){
        var role = jQuery(this).val()
        jQuery('.formRow').hide()
        jQuery('#selectRole').show()
        jQuery('.selectBoxContainer').css('margin-left','auto')
        jQuery('.selectBoxContainer').css('margin-bottom','0')
        if(role == 0){
            //jQuery('.formRow').hide()
            //jQuery('.selectBoxContainer').css('margin-left','auto')
            //jQuery('.selectBoxContainer').css('margin-bottom','0')
        }
        else{
            //jQuery('.formRow').hide()
            jQuery('#'+role).show(100,function(){
                jQuery('#actionButtons').show()
                jQuery('#selectRole').show()
                jQuery('#'+jQuery(this).prop('id')+'Heading').show()
                jQuery('.selectBoxContainer').css('margin-left','150px')
                jQuery('.selectBoxContainer').css('margin-bottom','50px')
                //jQuery(this).css('display','table-row')
                //jQuery('.formCell').css('display','table-cell')
            })
        }
    })
})

function setupData() {
    var specificFormData = {}
    specificFormData.Roles=[]
    jQuery('.formRow').each(function(){
        role ={}
        row=jQuery(this)

        role.name=row.children('.role').data('roleName')
        role.description=row.children('.role').text()

        role.users=[]

        row.children('.users').find("input:checked").each(function () {
            role.users.push(jQuery(this).val());
        })

        role.permissions=[]
        row.children('.permissions').find("input:checked").each(function () {
            role.permissions.push(jQuery(this).val());
        })
     specificFormData.Roles.push(role)
    })
    return specificFormData
}

function setupConstraints() {
    var specificFormConstraints={}
    return specificFormConstraints
}