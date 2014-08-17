#! /usr/bin/env python3

import componentConfig
import sys, os

if __name__ == '__main__':
	extraKwargs = dict()
	if '-t' in sys.argv or '--test' in sys.argv:
		import appConfig
		import testAppConfig

		appConfig.AppConfig = testAppConfig.AppConfig
		extraKwargs['testMode'] = True
	else:
		componentConfig.PrimaryAppComponents.remove(('testComponent', 'testComponent.TestComponent'))
	#

	from app import App

	app = App(**extraKwargs)
	app.run()

