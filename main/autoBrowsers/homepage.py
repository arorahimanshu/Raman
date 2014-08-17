from appConfig import AppConfig


def task(driver, app, logger, **kwargs):
	driver.get(AppConfig.BrowserConfig.BaseUrl)

	driver.find_element_by_css_selector('.loginForm .username input').send_keys('superuser')
	driver.find_element_by_css_selector('.loginForm .password input').send_keys('superuser')

	logger.debug('before js')
	result = driver.execute_script('''
		console.log ('from auto component'
		return 20
	''')
	logger.debug('after js: ' + str(result))

#

