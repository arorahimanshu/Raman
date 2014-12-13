from appConfig import AppConfig
from componentConfig import Page2Config , Page2ConfigChild
from component import Component
from utils import TemplateManager, relativePath, importItem

import cherrypy

from io import StringIO
import operator
import sys, os
import json
import traceback
from collections import OrderedDict


class PageNotFound(Exception):
	def __init__(self, path):
		Exception.__init__(self, 'Page not found: {}'.format(path))

	#


#

class Page2(Component):
	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

		self.templateManager = TemplateManager(
			'6ef7a637ac8943cb86531b30bd15f051',
			relativePath(__file__, 'page2Templates'),
		)

	#


	def setup(self):
		self.server = self.app.component('httpServer')

		jsScripts = [  # ('lib', 'js', 'jquery.js'),
					   ('lib', 'js', 'jquery2.js'),
					   ('etc', 'jquery_init.js'),
					   ('lib', 'js', 'jquery_ui.js'),
					   ('lib', 'js', 'sugar.js'),
					   ('lib', 'js', 'jquery_cookie.js'),
						 ('lib', 'js', 'jquery.iframe-transport.js'),
						 ('lib', 'js', 'jquery.fileupload.js'),
					   ('lib', 'js', 'mersenne_twister.js'),
					   ('lib', 'js', 'uuid.js'),
					   ('lib', 'js', 'xdate.js'),
					   ('lib', 'js', 'validate.js'),  #('lib', 'js', 'yuibuild', 'yui', 'yui-min.js'),
					   ('etc', 'utils.js'),
					   ('etc', 'lib1', 'ajax.js'),
					   ('etc', 'lib1', 'uuid.js'),
					   ('etc', 'page2', 'specific', 'js', 'basic.js')
		]

		cssSheets = [
			('lib', 'css', 'jquery_theme', 'jquery_ui.css'),
		    ('etc', 'page2', 'generic', 'css', 'basic.css')

		]

		self._jsScripts = []
		for item in jsScripts:
			self._jsScripts.append(self.server.appUrl(*item))
		#
		self._internalJs = ''

		self._cssSheets = []
		for item in cssSheets:
			self._cssSheets.append(self.server.appUrl(*item))
		self._internalCss = ''

		self._logger = self.app.masterLogger.getChild('webUi.page2')
		self._assetsPath = AppConfig.WebserverConfig.StaticUris[('assets',)]

		self._components = OrderedDict()
		# for name, parts, qName in Page2Config :
		#TODO for ravi check whether the child logic nitin added is correct or not
		for item in Page2ConfigChild:
			name = item['name']
			parts = item['urls']
			qName = item['component']
			Cls = importItem(qName)
			self._components[name] = (frozenset(parts), Cls(self))


		for item in Page2Config:
			name = item['name']
			parts = item['urls']
			qName = item['component']
			Cls = importItem(qName)
			self._components[name] = (frozenset(parts), Cls(self))

			if 'defaultLanding' in item:
				self._defaultLandingUrlPart = item['defaultLanding']
			#
			#

	#

	@property
	def assetsPath(self):
		return self._assetsPath

	def newProxy(self):
		params = {
		'externalJs': list(self._jsScripts),
		'externalCss': list(self._cssSheets),
		'internalJs': str(self._internalJs),
		'internalCss': str(self._internalCss),
		'appUrl' : self.server.appUrl,
		'config': {
		'BaseUri': list(AppConfig.WebserverConfig.BaseUri),
		'organizationId': cherrypy.request.fitxData['organizationId'],
		},
		}

		return self.templateManager.proxy(params=params), params

	#

	@cherrypy.expose
	def default(self, *args, **kwargs):
		requestPath = self.server.requestPath()

		try:
			return self.handler()
		except PageNotFound as ex:
			self.handleError(ex)
			return 'Page Not Found'
		except Exception as ex:
			self.handleError(ex)
			return 'Unknown Server Error'
		#

	#

	def handleError(self, ex=None, msg='Server Error: '):
		self.logger.error(
			msg + (str(ex.args) if ex != None else ''),
			exc_info=(ex != None)
		)

	#

	def handler(self):
		cherrypy.request.fitxData = {
		'organizationId': self.organizationId()
		}

		requestPath = self.server.requestPath()
		nextPart = requestPath.nextPart()

		if nextPart == 'loginAjaxAction':
			return self._loginAjaxAction()
		else:
			if self.isLoggedIn():
				return self.handleViaComponent(nextPart, requestPath)
			else:
				return self._renderLoginPage()
			#
		#
		raise PageNotFound(requestPath.allPrevious())

	#

	def handleViaComponent(self, nextPart, requestPath):
		for parts, handler in self._components.values():
			if nextPart in parts:
				if nextPart == 'home' or handler.security(self._returnAppName(nextPart)):
					return handler.handler(nextPart, requestPath)
				#
				#
		#

		if nextPart in ['loginAjaxAction', None]:
			return self._redirectToDefaultLanding(requestPath)
		#
		# Todo : remove print statement
		print(requestPath._parts)
		raise PageNotFound(requestPath.allPrevious())

	#

	def organizationId(self):
		with self.server.session() as session:
			return self.server.requestParams().get(
				'organizationId',
				session.get('primaryOrganizationId', None)
			)
		#

	#

	def component(self, name):
		return self._components[name][1]

	#

	def isLoggedIn(self):
		with self.server.session() as session:
			if 'username' not in session:
				return False
			else:
				userManager = self.app.component('userManager')
				return userManager.isLoggedIn(session['username'], session['uid'])
			#
			#

	#

	def jsonSuccess(self, msg='', data=None):
		return self.server.jsonResult(
			{
			'success': True,
			'message': msg,
			'data': data,
			}
		)

	#

	def jsonFailure(self, msg='Internal Server Error', data=None):
		return self.server.jsonResult(
			{
			'success': False,
			'message': msg,
			'data': data,
			}
		)

	#

	def _loginAjaxAction(self):
		data = cherrypy.request.params
		userManager = self.app.component('userManager')

		with self.server.session() as session:
			uid = session['uid']
			username = data.get('username', '')
			password = data.get('password', '')

			try:
				organizationId = userManager.attemptLogin(username, uid, password)
				session['username'] = username
				session['primaryOrganizationId'] = organizationId
				db = self.app.component('dbHelper')
				session['userId'] = db.returnUid(username)
				return self.jsonSuccess()
			except userManager.LoginFailed:
				return self.jsonFailure('Login Failed')
			#
			#

	#

	def _redirectToDefaultLanding(self, requestPath):
		defaultLandingUrl = requestPath.allPrevious(
			ignore=1,
			additional=[self._defaultLandingUrlPart],
		)

		proxy, params = self.newProxy()

		params['internalJs'] += '''
			fitx.utils.loadPage ({})
		'''.format(json.dumps(defaultLandingUrl))

		return proxy.render('base1.html')

	#

	def _renderLoginPage(self):
		proxy, params = self.newProxy()
		subdomain = self.server.requestSubdomain()
		db = self.app.component('dbManager')

		params['config']['loginFormActionUrl'] = self.server.appUrl('loginAjaxAction')
		params['config']['loginFormSuccessUrl'] = self.server.appUrl('home')

		with db.session() as session:
			result = session.query(db.Organization.id).filter_by(
				name=subdomain
			).first()

			logoImgUrl = None
			if result != None:
				imgName = 'logo_{}.png'.format(result[0])
				if os.path.isfile(os.path.join(self.assetsPath, imgName)):
					logoImgUrl = self.server.appUrl('assets', imgName)
				#
			#

			if logoImgUrl == None:
				logoImgUrl = self.server.appUrl('assets', 'logo_default.png')
			#
		#

		params['externalCss'].extend(
			[
				self.server.appUrl('etc', 'page2', 'generic', 'css', 'base1.css'),
				self.server.appUrl('etc', 'page2', 'generic', 'css', 'basic.css'),
				self.server.appUrl('etc', 'page2', 'generic', 'css', 'layout1.css'),
				self.server.appUrl('etc', 'page2', 'specific', 'css', 'loginPage.css'),
			]
		)

		params['externalJs'].append(
			self.server.appUrl('etc', 'page2', 'specific', 'js', 'loginPage.js'),
		)

		return proxy.render('base1.html',
							bodyContent=proxy.render('layout1.html',
													 bodyContent=operator.add(
														 proxy.render('img.html', imgUrl=logoImgUrl,
																	  imgClass='loginLogo'),
														 proxy.render('loginForm.html')
													 )
							)
		)

	#

	def _returnAppName(self, url):
		for item in Page2Config:
			if url in (item['urls']):
				return item['name']

#

