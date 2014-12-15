DataModules = [
    'dataModel.basic1',
    'dataModel.gps',
    'dataModel.basic2'

]

PrimaryAppComponents = [
    ('dbManager', 'db.Db'),
    ('dataUtils', 'dataUtils.DataUtils'),
    ('securityManager', 'securityManager.SecurityManager'),
    ('userManager', 'userManager.UserManager'),
    ('installationManager', 'installationManager.InstallationManager'),
    ('httpServer', 'httpServer.Server'),
    ('autoBrowser', 'autoBrowserComponent.AutoBrowserComponent'),
    ('commandConsole', 'commandConsole.CommandConsole'),
    ('testComponent', 'testComponent.TestComponent'),
    ('dbHelper', 'dbHelper.DbHelper'),
    ('gpsHelper', 'gpsHelper.GpsHelper'),
    ('timeHelper', 'timeHelper.TimeHelper')
]

MainAppComponent = 'commandConsole'

HttpServerRootComponent = 'webUi.page2.Page2'

TestComponents = [
    'tests.testUserManager',
    'tests.testDataUtils',
    'tests.gym.testGymChain',
    'tests.testUtils',
]

AutoBrowserComponents = {
    'homepage': 'autoBrowsers.homepage',
    'landing': 'autoBrowsers.landing',
    'rbac': 'autoBrowsers.rbacAuth',
    'newGymChain': 'autoBrowsers.newGymChainForm',
    'nemp': 'autoBrowsers.newEmployeeForm',
}

Page2Config = [
    {
        'name': 'primaryTabs',
        'urls': [],
        'component': 'webUi.page2Components.primaryTabs.PrimaryTabs',
    },

    {
        'name': 'landingPage',
        'urls': [
            'home',
            'dashboard'
        ],
        'component': 'webUi.page2Components.landingPage.LandingPage',
        'defaultLanding': 'home',
		'type':'child',
    },

	    {

        'name': 'addGps',
        'urls': [
            'newGpsDataForm',
            'newGpsDataFormAction',
            'newCarSetup',
            '''newDashboardForm',
            'newDashboardFormAction',
            'newGpsDataFormVehicleList','''
        ],
        'component': 'webUi.page2Components.gpsData.GpsData',
        'apps': [
            {
                'name': 'addGpsDataForm',
                'displayName': 'Live Tracking',
                'url': ['newGpsDataForm'],
            }
        ],
		'type':'child',

    },

	    {

        'name': 'playback',
        'urls': [
            'newPlaybackForm',
            'newPlaybackFormAction',
        ],
        'component': 'webUi.page2Components.playback.Playback',
        'apps': [
            {
                'name': 'addPlaybackForm',
                'displayName': 'Playback',
                'url': ['newPlaybackForm'],
            }
        ],
		'type':'child',

    },

		{

        'name': 'dashboard',
        'urls': [
            'newDashboardForm',
            'newDashboardFormAction',
            'dashboardVehicleListNested',
        ],
        'component': 'webUi.page2Components.dashboard.Dashboard',
        'apps': [
            {
                'name': 'addDashboardForm',
                'displayName': 'Dashboard',
                'url': ['newDashboardForm'],
            }
        ],
		'type':'child',

    },

	    {

        'name': 'addGeofence',
        'urls': [
            'newGeoFenceForm',
            'newGeoFenceFormAction',
            'geoFenceData',
            'editGeoFence',
            'delGeoFence'
        ],
        'component': 'webUi.page2Components.geoFence.GeoFence',
        'apps': [
            {
                'name': 'addGeoFenceForm',
                'displayName': 'Create GeoFence',
                'url': ['newGeoFenceForm'],
            }
        ],
		'type':'child',

    },

 	{
        'name': 'reportParent',
        'urls': [],
         'component': 'webUi.page2Components.report1.Report1',
        'apps': [
            {
                'name': 'reportParent',
                'displayName': 'Report',
                'url': ['reportParent'],
            },
        ],
		'type':'parent',

    },

	{
        'name': 'userManagementParent',
        'urls': [],
        'component': 'webUi.page2Components.userManagement.UserManagement',
        'apps': [
            {
                'name': 'userManagementParent',
                'displayName': 'User Management',
                'url': ['userManagement'],
            },
        ],
		'type':'parent',

    },



	{
        'name': 'organizationManagementParent',
        'urls': [],
		'component': 'webUi.page2Components.organizationManagement.Organization',
        'apps': [
            {
                'name': 'organizationManagementParent',
                'displayName': 'Organization Hierarchy',
                'url': ['organizationManagement'],
            },
        ],
		'type':'parent',

    },


		{
        'name': 'vehicleGroupManagementParent',
        'urls': [],
        'component': 'webUi.page2Components.vehicleGroupManagement.vehicleGroup',
        'apps': [
            {
                'name': 'vehicleGroupManagementParent',
                'displayName': 'Manage Vehicle',
                'url': ['vehicleGroupManagement'],
            },
        ],
		'type':'parent',

    },

	    {

        'name': 'addPoi',
        'urls': [
            'newPoiForm',
            'newPoiFormAction',
            'getPoiData',
            'generateReport',
            'delPoi'
        ],
        'component': 'webUi.page2Components.poi.Poi',
        'apps': [
            {
                'name': 'addPoiForm',
                'displayName': 'Add POI',
                'url': ['newPoiForm'],
            }
        ],
		'type':'child',

    },




	    {

        'name': 'paymentReceipt',
        'urls': [
            'paymentReceiptForm',
            'paymentReceiptFormActionUrl',
            'paymentReceiptFormActionFormLoad',
            'paymentReceiptDelAction'
        ],
        'component': 'webUi.page2Components.paymentReceipt.PaymentReceipt',
        'apps': [
            {
                'name': 'paymentReceiptForm',
                'displayName': 'Manage Payment',
                'url': ['paymentReceiptForm'],
            }
        ],
		'type':'child',

    },

    {

        'name': 'utilUrl',
        'urls': [
            'logoutAction',
        ],
        'component': 'webUi.page2Components.utilUrl.UtilUrl',
		'type':'child',

    },

	{
		'name' : 'vehicleSelector',
		'urls' : [
			#'vehicleSelector', # <- Not needed anymore since vehicle selector is preloading from template
		],
		'component' : 'webUi.page2Components.vehicleSelector.VehicleSelector',
	}
]


Page2ConfigChild = [


		    {
        'name': 'userManagement',
        'urls': [
            'userManagementForm',
            'userManagementFormAction',
            'generateEmployeeData',
            'editEmployeeFormAction',
            'delEmployeeFormAction',
        ],
        'component': 'webUi.page2Components.userManagement.UserManagement',
        'apps': [
            {
                'name': 'userManagementForm',
                'displayName': 'Manage Users',
                'url': ['userManagementForm'],
            }
        ],
		'type':'child',
		'parent':'userManagementParent',
 	   },

		{
        'name': 'securitySettings',
        'urls': ['securitySettings', 'securitySettingsAction', 'userSecuritySettings', 'roleSecuritySettings'],
        'component': 'webUi.page2Components.securitySettings.SecuritySettings',
        'apps': [
            {
                'name': 'securitySettings',
                'displayName': 'Security Settings',
                'url': ['securitySettings'],
            },
        ],
		'type':'child',
		'parent':'userManagementParent',

   		 },


		{

        'name': 'roleManagement',
        'urls': [
            'newRoleManagementForm',
            'newRoleManagementFormAction',
            'addRole',
            'editRole',
            'delRole',
        ],
        'component': 'webUi.page2Components.roleManagement.RoleManagement',
        'apps': [
            {
                'name': 'addRoleManagement',
                'displayName': 'Role Management',
                'url': ['newRoleManagementForm'],
            }
        ],
		'type':'child',
		'parent':'userManagementParent',

  	  },

		{
	'name': 'organizationManagement',
	'urls': [
		'organizationManagementForm',
		'organizationManagementFormAction',
		'organizationData',
	    'editOrganization',
		'delOrganization'
	],
	'component': 'webUi.page2Components.organizationManagement.Organization',
	'apps': [
		{
		'name': 'organizationManagement',
		'displayName': 'Manage Organization',
		'url': ['organizationManagementForm'],
		}
		],
		'type':'child',
		'parent':'organizationManagementParent',
	},

    {
	'name': 'branchManagement',
	'urls': [
		'branchManagementForm',
		'branchManagementFormAction',
		'branchData',
	    'editBranch',
		'delBranch'
	],
	'component': 'webUi.page2Components.branchManagement.Branch',
	'apps': [
		{
		'name': 'branchManagement',
		'displayName': 'Manage Branch',
		'url': ['branchManagementForm'],
		}
	],
	'type':'child',
	'parent':'organizationManagementParent',
	},

		{
	'name': 'vehicleGroupManagement',
	'urls': [
		'vehicleGroupManagementForm',
		'vehicleGroupManagementFormAction',
		'vehicleGroupData',
	    'editVehicleGroup',
		'delVehicleGroup'
	],
	'component': 'webUi.page2Components.vehicleGroupManagement.vehicleGroup',
	'apps': [
		{
		'name': 'vehicleGroupManagement',
		'displayName': 'Manage Vehicle Group',
		'url': ['vehicleGroupManagementForm'],
		}
	],
	'type':'child',
	'parent':'vehicleGroupManagementParent',
	},

	{
	'name': 'newVehicle',
	'urls': [
		'newVehicleForm',
		'newVehicleFormAction',
		'vehicleData',
		'delVehicleDataAction',
		'editVehicleAction',
	],
	'component': 'webUi.page2Components.newVehicle.Vehicle',
	'apps': [
		{
		'name': 'newVehicle',
		'displayName': 'Manage Vehicle',
		'url': ['newVehicleForm'],
		}
	],
	'type':'child',
	'parent':'vehicleGroupManagementParent',
	},
	{

        'name': 'report1',
        'urls': [
            'newReport1Form',
            'newReport1FormAction',
        ],
        'component': 'webUi.page2Components.report1.Report1',
        'apps': [
            {
                'name': 'addReport1Form',
                'displayName': 'Speed Report',
                'url': ['newReport1Form'],
            }
        ],
		'type':'child',
		'parent':'reportParent',

    },

    {
        'name': 'report4',
        'urls': [
            'newReport4Form',
            'newReport4FormAction',
        ],
        'component': 'webUi.page2Components.report4.Report4',
        'apps': [
            {
                'name': 'addReport4Form',
                'displayName': 'Stoppage Summary',
                'url': ['newReport4Form'],
            }
        ],
		'type':'child',
		'parent':'reportParent',

    },

	    {

        'name': 'travelReport',
        'urls': [
            'newTravelReportForm',
            'newTravelReportFormAction',
            'travelReportVehicleListNested',
        ],
        'component': 'webUi.page2Components.travelReport.TravelReport',
        'apps': [
            {
                'name': 'addTravelReportForm',
                'displayName': 'Travel Report',
                'url': ['newTravelReportForm'],
            }
        ],
		'type':'child',
		'parent':'reportParent',

    },

]



PermissionConfig = [
    {
        'name': 'AddPayment',
        'appName': 'paymentReceipt',
    },
    {
        'name': 'ManageUser',
        'appName': 'userManagement',
    },
    {
        'name': 'ExpenseReport',
        'appName': 'expenseReport',
    },
    {
        'name': 'TrackVehicle',
        'appName': 'addGps',
    },

    {
        'name': 'AddGeofence',
        'appName': 'addGeofence',
    },

    {
        'name': 'VehicleManagement',
        'appName': 'newVehicle',
    },

    {
        'name': 'ConfigureSystem',
        'appName': '',
    },

    {
        'name': 'Alerts',
        'appName': '',
    },
    {
        'name': 'POI',
        'appName': 'addPoi',
    },
    {
        'name': 'playBack',
        'appName': 'playback',
    },
    {
        'name': 'dashboard',
        'appName': 'dashboard',
    },
    {
        'name': 'securitySettings',
        'appName': 'securitySettings',
    },
    {
        'name': 'roleManagement',
        'appName': 'roleManagement',
    },
    {
        'name': 'organizationManagement',
        'appName': 'organizationManagement',
    },
    {
        'name': 'branchManagement',
        'appName': 'branchManagement',
    },
    {
        'name': 'vehicleGroupManagement',
        'appName': 'vehicleGroupManagement',
    },
    {
        'name': 'report1',
        'appName': 'report1',
    },
    {
        'name': 'report4',
        'appName': 'report4',
    },
    {
        'name': 'travelReport',
        'appName': 'travelReport',
    },
    {
        'name': 'reportParent',
        'appName': 'reportParent',
    },
    {
        'name': 'userManagementParent',
        'appName': 'userManagementParent',
    },
    {
        'name': 'organizationManagementParent',
        'appName': 'organizationManagementParent',
    },
    {
        'name': 'vehicleGroupManagementParent',
        'appName': 'vehicleGroupManagementParent',
    },

    {
        'name': 'utilUrl',
        'appName': 'utilUrl',
    },




]
