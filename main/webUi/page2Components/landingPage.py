from .page2Component import Page2Component
from componentConfig import Page2Config , Page2ConfigChild

import operator
from io import StringIO


class LandingPage(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestPath):
		if nextPart == 'home':
			return self._renderHome()
		#

	#

	def _renderHome(self):
		proxy, params = self.newProxy()

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'homeTab.js')
		)

		params['externalCss'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'css', 'poiform.css')
		)

		return self._renderWithTabs(proxy, params,
		                            self._renderAppButtons(proxy, params),
		                            activeTab='home',
		                            url=self.server.appUrl('home'),
		)

	#

	def _renderAppButtons(self, proxy, params):
		apps = []
		appsChild = []
		for itemChild in Page2ConfigChild:
			for itemChildApp in itemChild.get('apps', []):
				appsChild.append(
							{
							'name': itemChildApp['name'],
							'displayName': itemChildApp['displayName'],
							'url': self.server.appUrl(*itemChildApp['url']),
							'type': itemChild['type'],
							'parent': itemChild['parent']
							}
				)


		for item in Page2Config:
			component = self.parent.component(item['name'])
			for itemApp in item.get('apps', []):
				if component.security(item['name']):
					apps.append(
						{
						'name': itemApp['name'],
						'displayName': itemApp['displayName'],
						'url': self.server.appUrl(*itemApp['url']),
						'type': item['type']
						}
					)

		#

		result = StringIO()
		for appInfo in apps:
			proxy.render('appButton.html',
			             stream=result,
			             appInfo=appInfo,
						 appsChild=appsChild
			)
		#

		return result.getvalue()

	#

#

