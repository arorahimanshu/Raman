from appConfig import AppConfig

import json


def task(driver, app, logger, **kwargs):
	driver.get(AppConfig.BrowserConfig.BaseUrl)

	driver.find_element_by_css_selector('.loginForm .username input').send_keys('superuser')
	driver.find_element_by_css_selector('.loginForm .password input').send_keys('superuser')
	driver.find_element_by_css_selector('.loginForm .submit').click()

	appButtons = driver.find_elements_by_css_selector('.primaryTabsContent .appButton')
	for button in appButtons:
		info = json.loads(button.get_attribute('data-info'))
		if info['name'] == 'newEmployeeForm':
			button.click()
			break
		#
		#

#

