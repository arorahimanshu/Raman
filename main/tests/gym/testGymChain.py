from appConfig import AppConfig
from testComponent import Mock
import utils

from unittest import TestCase
import json
import time


class Fixture:
	def __init__(self, app, testComponent):
		self._app = app
		self._parent = testComponent.fixture('basic1',
		                                     config={
		                                     'basic1.superuser.username': 'superuser',
		                                     'basic1.superuser.password': 'superuser',
		                                     }
		)

	#

	@property
	def app(self): return self._app

	def setUp(self):
		self._parent.setUp()

	#

	def tearDown(self):
		self._parent.tearDown()

	#


#

def collectTests(collector, parent, app, logger):
	@collector
	class TestNewGymChain(TestCase):
		def setUp(self):
			self.fixture = Fixture(app, parent)
			self.fixture.setUp()

		#

		def tearDown(self):
			self.fixture.tearDown()

		#

		def test_NewGymChainFormBasic1(self):
			with parent.newBrowser() as driver:
				driver.get(AppConfig.BrowserConfig.BaseUrl)
				driver.find_element_by_css_selector('.loginForm .username input').send_keys('superuser')
				driver.find_element_by_css_selector('.loginForm .password input').send_keys('superuser')
				driver.find_element_by_css_selector('.loginForm .submit').click()

				appButtons = driver.find_elements_by_css_selector('.primaryTabsContent .appButton')
				for button in appButtons:
					info = json.loads(button.get_attribute('data-info'))
					if info['name'] == 'addGymChain':
						button.click()
						break
					#
				#

				driver.find_element_by_css_selector('.newGymChainForm')
				driver.execute_script('''
					var form = fitx.page2.gymChain.newGymChainForm
					form._originalSuccessFunction = form.successFunction
					form.successFunction = function (result) {
						jQuery ('.newGymChainForm').addClass ('testTarget')
						form._successResult = result
					}
				''')

				newGymChain = Mock('gymChain')

				def inputElement(cssClass):
					return driver.find_element_by_css_selector('.newGymChainForm .{} input'.format(cssClass))

				#
				inputElement('name').send_keys(str(newGymChain))
				inputElement('headOfficeAddress').send_keys(str(newGymChain.headOfficeAddress))
				inputElement('website').send_keys(str(newGymChain.website.com))
				inputElement('email').send_keys('email@{}'.format(str(newGymChain.com)))
				inputElement('serviceTaxNumber').send_keys(str(newGymChain.serviceTaxNumber))
				inputElement('createGym').click()
				manager = newGymChain / 'manager'
				inputElement('username').send_keys(str(manager.username))
				inputElement('password').send_keys(str(manager.password))
				inputElement('passwordConfirm').send_keys(str(manager.password))
				inputElement('managerEmail').send_keys('manager@{}'.format(newGymChain.com))

				driver.find_element_by_css_selector('.newGymChainForm .submitButton').click()
				driver.find_element_by_css_selector('.testTarget')

				result = driver.execute_script('''
					var form = fitx.page2.gymChain.newGymChainForm
					return JSON.stringify (form._successResult)
				''')

				result = json.loads(result)
				logger.debug(result)

				driver.execute_script('''
					var form = fitx.page2.gymChain.newGymChainForm
					jQuery ('.newGymChainForm').removeClass ('.testTarget')
					form._originalSuccessFunction (form._successResult)
				''')
			#

			# /test_NewGymChainFormBasic1

			# /TestNewGymChain

#

