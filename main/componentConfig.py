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
	},

	{
	'name': 'authSettings',
	'urls': ['rbacAuth','rbacAuthAction'],
	'component': 'webUi.page2Components.rbacAuth.RbacAuth',
	'apps': [
		{
		'name': 'securitySettings',
		'displayName': 'Security Settings',
		'url': ['rbacAuth'],
		},
	]
	},
	{

	'name': 'addGps',
	'urls': [
		'newGpsDataForm',
		'newGpsDataFormAction',
	    'newCarSetup',
	    'newDashboardForm',
		'newDashboardFormAction',
		'newGpsDataFormVehicleList',
	],
	'component': 'webUi.page2Components.gpsData.GpsData',
	'apps': [
		{
		'name': 'addGpsDataForm',
		'displayName': 'Track My Vehicle',
		'url': ['newGpsDataForm'],
		}
	],

	},

	{

	'name': 'addPoi',
	'urls': [
		'newPoiForm',
		'newPoiFormAction',
		'getPoiData',
		'generateReport'
	],
	'component': 'webUi.page2Components.poi.Poi',
	'apps': [
		{
		'name': 'addPoiForm',
		'displayName': 'Add POI',
		'url': ['newPoiForm'],
		}
	],

	},

	{

	'name': 'addGeofence',
	'urls': [
		'newGeoFenceForm',
		'newGeoFenceFormAction',
	],
	'component': 'webUi.page2Components.geoFence.GeoFence',
	'apps': [
		{
		'name': 'addGeoFenceForm',
		'displayName': 'Create GeoFence',
		'url': ['newGeoFenceForm'],
		}
	],

	},

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
	]
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
	]
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
	]
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
				'displayName': 'Report 1',
				'url': ['newReport1Form'],
			}
		],

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
				'displayName': 'Report 4',
				'url': ['newReport4Form'],
			}
		],

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

	},
    {

		'name': 'utilUrl',
		'urls': [
			'logoutAction',
		],
		'component': 'webUi.page2Components.utilUrl.UtilUrl',

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

	},
]

PermissionConfig=[
	{
		'name':'AddPayment',
		'appName' : 'paymentReceipt',
	},
	{
		'name':'ManageUser',
		'appName' : 'userManagement',
	},
	{
		'name':'ExpenseReport',
		'appName' : 'expenseReport',
	},
	{
		'name':'TrackVehicle',
		'appName' : 'addGps',
	},

	{
		'name':'AddGeofence',
		'appName' : 'addGeofence',
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
	}
]