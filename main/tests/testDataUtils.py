from appConfig import AppConfig

from unittest import TestCase
import json
from time import sleep


def collectTests(collector, parent, app, logger):
	@collector
	class TestDataUtils(TestCase):
		def setUp(self):
			self.fixture = parent.fixture('basic1', config={
			'basic1.superuser.username': 'superuser',
			'basic1.superuser.password': 'superuser',
			})
			self.fixture.setUp()

		#

		def tearDown(self):
			self.fixture.tearDown()

		#

		def testNewUserLogin(self):
			db = app.component('dbManager')
			dataUtils = app.component('dataUtils')

			with dataUtils.worker() as worker:
				adminOrganization = worker.organizationByName(
					AppConfig.AdminOrganization
				)

				newUser = worker.createUser({
				'username': 'dummyUser1',
				'password': 'dummyPass1',
				})

				newRole = worker.createRole({
				'name': 'employee',
				'organizationId': adminOrganization.id,
				})

				newFacet = worker.createFacet({
				'username': newUser.username,
				'organizationId': adminOrganization.id,
				})

				worker.assignPermissionRole({
				'organizationId': adminOrganization.id,
				'permissionName': db.Permissions.Login,
				'roleName': newRole.name
				})

				worker.assignFacetRole({
				'organizationId': adminOrganization.id,
				'roleName': newRole.name,
				'username': newUser.username
				})
			#

			with parent.newBrowser() as driver:
				driver.get(AppConfig.BrowserConfig.BaseUrl)
				driver.find_element_by_css_selector('.loginForm .username input').send_keys('dummyUser1')
				driver.find_element_by_css_selector('.loginForm .password input').send_keys('dummyPass1')
				driver.find_element_by_css_selector('.loginForm .submit').click()

				elements = driver.find_elements_by_css_selector('.primaryTabsContent')
				sleep(3)
				self.assertGreater(len(elements), 0)
			#
			#
			#

#

