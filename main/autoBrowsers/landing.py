from appConfig import AppConfig


def task(driver, app, logger, **kwargs):
	driver.get(AppConfig.BrowserConfig.BaseUrl)

	driver.find_element_by_css_selector('.loginForm .username input').send_keys('superuser')
	driver.find_element_by_css_selector('.loginForm .password input').send_keys('superuser')
	driver.find_element_by_css_selector('.loginForm .submit').click()

#

