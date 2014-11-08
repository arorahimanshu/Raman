#! /usr/bin/env python3

import componentConfig
import sys, os

if __name__ == '__main__' :
	extraKwargs = dict ()
	if '-t' in sys.argv or '--test' in sys.argv :
		import appConfig
		import testAppConfig

		appConfig.AppConfig = testAppConfig.AppConfig
		extraKwargs['testMode'] = True
	else :
		componentConfig.PrimaryAppComponents.remove (('testComponent', 'testComponent.TestComponent'))
	#

	if '-D' in sys.argv or '--daemon' in sys.argv :
		import daemonize
		from appConfig import AppConfig

		if not os.path.exists (AppConfig.DaemonConfig.ShutdownFifo) :
			raise Exception ('AppConfig.DaemonConfig.ShutdownFifo doesnt exist')
		#

		curdir = os.path.abspath (os.curdir)

		def action () :
			extraKwargs['daemon'] = True
			sys.path.append (curdir)
			from app import App
			app = App (**extraKwargs)
			app.run ()
		#

		daemon = daemonize.Daemonize (
			app = AppConfig.DaemonConfig.Name, 
			pid = AppConfig.DaemonConfig.Pidfile,
			action = action,
		)
		daemon.start ()
	else :
		from app import App

		app = App (**extraKwargs)
		app.run ()
	#
#

