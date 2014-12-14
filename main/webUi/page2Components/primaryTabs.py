from .page2Component import Page2Component
from utils import newUuid
from sqlalchemy import and_

import cherrypy


class PrimaryTabs(Page2Component):
	def __init__(self, parent, **kwargs):
		Page2Component.__init__(self, parent, **kwargs)

	#

	def handler(self, nextPart, requestpath):
		raise self.UtilityOnlyComponent()

	#

	def renderWithTabs(self, proxy, params, bodyContent, **kwargs):
		params['externalCss'].extend(
			[
				self.server.appUrl('etc', 'page2', 'generic', 'css', 'base1.css'),
				self.server.appUrl('etc', 'page2', 'generic', 'css', 'layout1.css'),
				self.server.appUrl('etc', 'page2', 'generic', 'css', 'primaryTabs.css'),
			]
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'generic', 'js', 'primaryTabs.js'),
		)

		tabs = []
		tabIds = set()
		for item in self.infoCookie().get('tabs', []):
			tabs.append(
				{
				'id': item['id'],
				'title': item['title'],
				'url': item['url'],
				}
			)
			tabIds.add(item['id'])
		#
		with self.server.session() as session:
			userName=session['username']

		requestParams = self.requestParams()
		mode = requestParams.get('tabMode', '')
		params['config']['tabMode'] = mode

		if mode == 'createTab':
			tabId = requestParams.get('tabId', '')
			if tabId in tabIds:
				activeTab = tabId
			else:
				newTabInfo = {
				'id': tabId,
				'title': kwargs.get('newTabTitle', 'New Tab'),
				'url': kwargs['url'],
				}
				tabs.append(newTabInfo)
				activeTab = newTabInfo['id']
			#
		elif mode == 'restoreTab':
			activeTab = requestParams['tabId']
		else:
			activeTab = kwargs.get('activeTab', 'home')
		#

		clientLogoUrl = None
		orgId = params['config']['organizationId']
		db = self.app.component('dbManager')
		with db.session() as session:
			orgName = session.query(db.Organization).filter(db.Organization.id==orgId).one().name
			logoId = session.query(db.Info).filter(and_(db.Info.entity_id==orgId, db.Info.type==db.Info.Type.Image.value, db.Info.preference==0))
			try:
				logoId = logoId.one().data
				extension = session.query(db.logo).filter(db.logo.id==logoId).one().extension
			except:
				logoId = None
		if logoId:
			clientLogoUrl = self.server.appUrl('dbassets',logoId+extension)
		return proxy.render('base1.html',
		                    bodyContent=proxy.render('layout1.html',
		                                             bodyContent=proxy.render('primaryTabs.html',
		                                                                      activeTab=activeTab,
		                                                                      tabs=tabs,
																			  userName=userName,
		                                                                      bodyContent=bodyContent,
																			  clientLogo=clientLogoUrl,
																			  orgName=orgName,
		                                             )
		                    )
		)

	#

#

