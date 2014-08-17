from component import Component
from componentConfig import TestComponents
from utils import importItemFromModule

import unittest
from collections import OrderedDict
import re
from contextlib import contextmanager


class _Fixture:
	def __init__(self, parent, config):
		self._app = parent.app
		self._config = config

	#

	@property
	def app(self):
		return self._app

	#

	@property
	def config(self):
		return self._config

	#


#

class Mock:
	def __init__(self, name):
		self._name = name

	#

	def __str__(self):
		return self._name

	#

	def __truediv__(self, s):
		return Mock(self._name + '/' + str(s))

	#

	def __mul__(self, i):
		return [Mock(self._name + str(x)) for x in range(i)]

	#

	def __add__(self, s):
		return Mock(self._name + str(s))

	#

	def __call__(self):
		return Mock(self._name + '(' + str(s) + ')')

	#

	def __getattr__(self, s):
		return Mock(self._name + '.' + str(s))

	#


#

class TestComponent(Component):
	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

		self._tests = OrderedDict()

	#

	def setup(self):
		Component.setup(self)
		self._logger = self.app.masterLogger.getChild('test')

		from seleniumUtils import BrowserManager

		self._browserManager = BrowserManager()

		for qName in TestComponents:
			collectTests = importItemFromModule(qName, 'collectTests')
			collectTests(
				self._collector(qName),
				self,
				self.app,
				self.logger
			)
		#

	#

	@contextmanager
	def newBrowser(self, withProfile=False):
		try:
			driver, profile = self._browserManager.createNewBrowser()
			if withProfile:
				yield (driver, profile)
			else:
				yield driver
			#
		finally:
			driver.quit()

	#

	def _collector(self, moduleName):

		def tempClosure(cls):
			self._tests['{}.{}'.format(moduleName, cls.__name__)] = cls
			return cls

		#

		return tempClosure

	#

	def runTests(self, like=None, listOnly=False):
		if listOnly:
			print()
		#

		suite = unittest.TestSuite()
		for testCase in self._tests.values():
			tests = unittest.defaultTestLoader.loadTestsFromTestCase(testCase)
			for test in tests:
				if listOnly:
					print(test.id())
				elif like != None:
					if re.fullmatch(like.replace('%', '.*'), test.id()):
						suite.addTest(test)
					#
				else:
					suite.addTest(test)
				#
				#
				# suite.addTest (tests)
		#

		runner = unittest.TextTestRunner()
		runner.run(suite)

	#

	def fixture(self, name, config=None):
		if config == None:
			config = dict()
		#
		Cls = getattr(self, '_Fixture_' + name)
		obj = Cls(self, config)
		return obj

	#

	class _Fixture_basic1(_Fixture):

		def setUp(self):
			self.app.reset()

			commandConsole = self.app.component('commandConsole')
			with commandConsole.temporaryVerbosity(commandConsole.Verbosity.Low):
				commandConsole.rawCommand('db -d')
				commandConsole.rawCommand('db -c')
				commandConsole.rawCommand('db -l',
				                          config={
				                          'basic1.superuser.username': self.config.get('basic1.superuser.username',
				                                                                       'superuser'),
				                          'basic1.superuser.password': self.config.get('basic1.superuser.password',
				                                                                       'superuser'),
				                          }
				)
			#

		#

		def tearDown(self):
			commandConsole = self.app.component('commandConsole')
			with commandConsole.temporaryVerbosity(commandConsole.Verbosity.Low):
				commandConsole.rawCommand('db -d')
			#
			#
			#

#

