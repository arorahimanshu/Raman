from component import Component
from appConfig import AppConfig
from componentConfig import AutoBrowserComponents
from utils import importItemFromModule

from functools import partial
import sys, os


class AutoBrowserComponent(Component):
	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)
		self._openedTasks = dict()
		self._availableTasks = dict()
		self._browserManager = None

	#

	def setup(self):
		Component.setup(self)
		self._logger = self.app.masterLogger.getChild('autoBrowser')

		for name, qName in AutoBrowserComponents.items():
			taskFunction = importItemFromModule(qName, 'task')
			self._availableTasks[name] = taskFunction
		#

	def reset(self):
		Component.reset(self)
		self._closeAllTasks()

	#

	def listTasks(self):
		return [name for name in self._availableTasks.keys()]

	#

	def _closeAllTasks(self):
		tasks = []
		for name, browser in self._openedTasks.items():
			tasks.append(name)
			browser.quit()
		#

		for name in tasks:
			self._openedTasks.pop(name)
		#

	#

	def shutdown(self):
		self._closeAllTasks()

	#

	@property
	def browserManager(self):
		if self._browserManager == None:
			from seleniumUtils import BrowserManager

			self._browserManager = BrowserManager()
		#

		return self._browserManager

	#

	class TaskAlreadyRunning(Exception):
		pass

	def startTask(self, name):
		if name in self._openedTasks:
			raise self.TaskAlreadyRunning(name)
		#

		browser, profile = self.browserManager.createNewBrowser()
		self._openedTasks[name] = browser
		self._availableTasks[name](browser, self.app, self.logger)

	#

	def restartTask(self, name):
		if name in self._openedTasks:
			self._openedTasks.pop(name).quit()
		#

		browser, profile = self.browserManager.createNewBrowser()
		self._availableTasks[name](browser, self.app)
		self._openedTasks[name] = browser

	#

	class TaskNotRunning(Exception):
		pass

	def stopTask(self, name):
		if name in self._openedTasks:
			self._openedTasks.pop(name).quit()
		else:
			raise self.TaskNotRunning(Exception)
		#
		#

#

