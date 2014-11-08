from componentConfig import PrimaryAppComponents, MainAppComponent
from component import Container
from utils import importItem, checkWritableDir
from appConfig import AppConfig

import cherrypy

from contextlib import ExitStack, contextmanager
import threading
import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter, StreamHandler
import sys, os

class App (Container) :

	class AccessDenied (Exception) : pass

	def __init__ (self, **kwargs) :
		Container.__init__ (self, **kwargs)

		self._initialComponents = []
		for name, qName in PrimaryAppComponents :
			cls = importItem (qName)
			self._initialComponents.append ((name, cls ()))
		#

		self._requestLock = threading.RLock ()

		self._setupLogging ()

		self._testMode = kwargs.get ('testMode', False)
		self._daemon = kwargs.get ('daemon', False)
	#

	@property
	def testMode (self) :
		return self._testMode
	#

	@property
	def daemon (self) :
		return self._daemon
	#

	def registerComponent (self, name, item) :
		Container.registerComponent (self, name, item)
		item._app = self
		self._exitStack.enter_context (item.asContext ())
	#

	def registerSubComponent (self, item) :
		item._app = self
		self._exitStack.enter_context (item.asContext ())
	#

	def run (self) :
		with ExitStack () as stack :
			self._exitStack = stack
			for name, item in self._initialComponents :
				self.registerComponent (name, item)
			#

			mainAppComponent = self.component (MainAppComponent)
			mainAppComponent.run ()
		#
	#

	@contextmanager
	def requestLock (self) :
		self._requestLock.acquire (timeout = AppConfig.RequestTimeout)
		try :
			yield
		finally :
			self._requestLock.release ()
		#
	#

	@contextmanager
	def requestLockedDbSession (self) :
		with self.requestLock () :
			with self.component ('dbManager').session () as session :
				yield session
			#
		#
	#

	@property
	def logger (self) :
		return self._logger
	#

	@property
	def masterLogger (self) :
		return self._masterLogger
	#

	def _setupLogging (self) :
		self._masterLogger = logging.getLogger ('fitx')
		self._masterLogger.setLevel (logging.DEBUG)

		formatter = Formatter (
			'\n{} {} {}\nTime: {}\nMessage:\n{}\n'.format (
				'-' * 10,
				'%(name)s:%(levelname)s',
				'-' * 10,
				'%(asctime)s',
				'%(message)s',
			)
		)

		if AppConfig.LogToFile :
			checkWritableDir (
				AppConfig.LogFolder,
				'AppConfig.LogFolder is not a valid directory.'
			)

			logFilename = os.path.join (AppConfig.LogFolder, 'app.log')
			fileHandler = RotatingFileHandler (
				logFilename,
				'a',
				2 * 1024 * 1024, # max file size
				10, # backup count
			)

			fileHandler.setLevel (logging.DEBUG)
			fileHandler.setFormatter (formatter)

			self._masterLogger.addHandler (fileHandler)
		#

		if AppConfig.LogToConsole :
			consoleHandler = StreamHandler ()
			consoleHandler.setLevel (logging.DEBUG)
			consoleHandler.setFormatter (formatter)
			self._masterLogger.addHandler (consoleHandler)
		#

		self._logger = self._masterLogger.getChild ('app')
	#
#

#if __name__ == '__main__' :
#	app = App ()
#	app.run ()
#

