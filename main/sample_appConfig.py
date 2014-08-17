class AppConfig:
	DbEngine = 'postgres'
	RequestTimeout = -1

	LogToConsole = True
	LogToFile = False
	LogFolder = r'PATH'

	AdminOrganization = 'fitx'
	MaxPasswordLength = 150

	DbAssets = r'PATH'

	class PostgresConfig:
		Host = '127.0.0.1'
		Port = 5432
		Username = 'testuser'
		Password = 'testpass'
		Database = 'testdb'

	#

	class MysqlConfig:
		Host = '127.0.0.1'
		Port = 3306
		Username = 'testuser'
		Password = 'testpass'
		Database = 'testdb'

	#

	class WebserverConfig:
		BaseUri = tuple()
		StaticUris = {
		('etc',): ('MODULE_DIR', 'etc'),
		('lib',): r'PATH',
		('assets',): r'PATH',
		('dbassets',): ('CALLABLE', lambda: AppConfig.DbAssets),
		}
		LogFolder = r'PATH'

		Host = '127.0.0.1'
		Port = 8080

		Favicon = r'PATH_TO_ANY_IMAGE_TO_SERVE_AS_SITE_ICON'

	#

	class MakoConfig:
		CacheDir = r'PATH'

	#

	class InstallationConfig:
		Enabled = True
		Username = 'installer'
		Password = 'installer'

	#

	class UserManagerConfig:
		# in seconds
		LoginTimeout = 10

	#

	class BrowserConfig:
		Name = 'Firefox'
		ImplicitWait = 5
		BaseUrl = 'localhost:8080'

		class Firefox:
			class Firebug:
				Enabled = True
				Location = r'PATH'
				Settings = {
				'currentVersion': '1.12.7',
				'console.enableSites': True,
				'delayLoad': False,
				'allPagesActivation': 'on',
				'defaultPanelName': 'console',
				'framePosition': 'bottom',
				}
			#
			#
			#

#

