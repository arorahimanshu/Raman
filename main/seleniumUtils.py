from appConfig import AppConfig

from selenium import webdriver

from functools import partial
import sys, os


class BrowserManager:
	def __init__(self):
		Browser = AppConfig.BrowserConfig.Name

		if Browser == 'Firefox':
			self._setupBrowser = self._setupFirefox
		#

	#

	def createNewBrowser(self):
		_Browser, profile = self._setupBrowser()
		driver = _Browser(profile)
		driver.implicitly_wait(AppConfig.BrowserConfig.ImplicitWait)
		return driver, profile

	#

	def _setupFirefox(self):

		_profile = webdriver.FirefoxProfile()
		_profile.native_events_enabled = True

		Firebug = AppConfig.BrowserConfig.Firefox.Firebug

		if Firebug.Enabled:
			if not os.path.isfile(Firebug.Location):
				raise Exception('Firebug XPI installer not found at : ' + Firebug.Location)
			#

			for key, value in Firebug.Settings.items():
				_profile.set_preference(
					'extensions.firebug.' + key,
					value,
				)
			#

			_profile.add_extension(Firebug.Location)
		#

		_Browser = webdriver.Firefox

		return _Browser, _profile

	#

#

