from utils import TemplateManager, QueryParams

import cherrypy

import pprint
import json
import sys, os
import io
from collections import OrderedDict


def respondJs(content):
	cherrypy.response.headers['Content-Type'] = 'text/javascript'
	return content


#

def respondJson(item):
	cherrypy.response.headers['Content-Type'] = 'application/json'
	return json.dumps(item).encode()


#

def sessionInit():
	# cherrypy.lib.sessions.expire ()
	cherrypy.session['fitx'] = {
	'tabs': OrderedDict(),
	}


#

def app(*args, **kwargs):
	if 'fitx' not in cherrypy.session:
		sessionInit()
	#

	if args == ('config.js',):
		return respondJs(
			'fitx.config = {}'.format(
				json.dumps({'appUrl': []})
			)
		)
	#

	templateManager = TemplateManager(
		'fitxui_a1',
		'/home/hallofrks/rks_temp/testMakoCache',
		os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
	)

	params = {
	'js': [
		'/lib/js/jquery.js',
		'/etc2/init.js',
		'/lib/js/jquery_ui.js',
		'/lib/js/yuibuild/yui/yui-min.js',
		'/etc/utils.js',
		'/etc/lib1/ajaxClickable.js',
		'/etc/lib1/form.js',
		'/config.js',
	],
	'css': [
		'/lib/css/jquery_theme/jquery-ui-1.10.3.custom.min.css',
	],
	}

	proxy = templateManager.proxy(params=params)

	queryParams = QueryParams(args, kwargs)

	argsWalker = queryParams.argsWalker()
	nextArg = argsWalker.pop()

	if nextArg == 'login':

		params['css'].append('/etc2/loginPage.css')
		params['js'].append('/etc2/loginPage.js')

		return proxy.render('base.html',
		                    bodyContent=proxy.render('layout1.html',
		                                             layoutClass='outerLayout',
		                                             headerContent='',
		                                             bodyContent=proxy.render('img.html',
		                                                                      imgClass='loginLogo',
		                                                                      imgUrl='/assets/test_logo_image.jpg',
		                                             ) + proxy.render('loginForm.html',
		                                                              formClass='loginForm',
		                                             ),
		                                             footerContent='',
		                    )
		)
	elif nextArg == 'resetSession':
		cherrypy.lib.sessions.expire()
	elif nextArg == 'fitxAdmin':

		params['css'].append('/etc2/fitxAdmin.css')
		params['js'].append('/etc2/fitxAdmin.js')

		tabs = cherrypy.session['fitx']['tabs']
		isTab = argsWalker.pop()
		showHome = False
		activeTab = None

		if isTab == 'tab':
			tabId = argsWalker.pop(default='home')

			if tabId == 'home':
				showHome = True
			elif tabId == 'dashboard':
				activeTab = tabId
				tabBodyContent = 'Dashboard'
			else:
				if tabId in tabs:
					activeTab = tabId
					tabBodyContent = 'content in {}'.format(tabs[tabId]['title'])
				else:
					tabBodyContent = 'unknown tab'
				#
				#
		elif isTab == 'newTab':
			n = 0
			while True:
				if 'pt{}'.format(n) not in tabs:
					break
				else:
					n += 1
				#
			#
			newTabId = 'pt{}'.format(n)
			newTabTitle = 'Tab {}'.format(n)
			tabs[newTabId] = {
			'title': newTabTitle
			}

			result = {'success': True, 'newTabId': newTabId}
			return respondJson(result)
		elif isTab == 'closeTab':
			result = {
			'success': False,
			'message': 'Unkown Server Error',
			}

			if 'id' not in kwargs:
				result['message'] = 'Provide "id" attribute in POST request'
			else:
				tabId = kwargs['id']
				if tabId not in tabs:
					result['message'] = 'Invalid tab id'
				else:
					tabs.pop(tabId)
					result['success'] = True
				#
			#
			return respondJson(result)
		elif isTab == None:
			showHome = True
		else:
			showHome = True
			tabBodyContent = 'not implemented'
		#

		if showHome:
			activeTab = 'home'
			stream = io.StringIO()
			stream.write(
				'<a class="newTabWithoutSwitchButton" href="/fitxAdmin/newTab">New Tab</a></br>'
				'<a class="newTabWithSwitchButton" href="/fitxAdmin/newTab">New Tab and Switch</a></br>'
			)
			tabBodyContent = stream.getvalue()
		#

		return proxy.render('base.html',
		                    bodyContent=proxy.render('layout1.html',
		                                             layoutClass='outerLayout',
		                                             headerContent='',
		                                             bodyContent=proxy.render('primaryTabArea.html',
		                                                                      containerClass='ptContainer',
		                                                                      tabs=[
			                                                                      {'id': k, 'title': v['title']}
			                                                                      for k, v in tabs.items()
		                                                                      ],
		                                                                      activeTab=activeTab,
		                                             ) + tabBodyContent,
		                                             footerContent='',
		                    )
		)
	elif nextArg == 'roles':
		params['css'].append('/etc2/rolesTable.css')
		params['js'].append('/etc2/rolesTable.js')

		return proxy.render('base.html',
		                    bodyContent=proxy.render('layout1.html',
		                                             layoutClass='outerLayout',
		                                             headerContent='',
		                                             bodyContent=proxy.render('rolesTable.html',
		                                                                      tableClass='rolesTable',
		                                                                      tableData=OrderedDict(
			                                                                      [
				                                                                      ('role1',
				                                                                       {
				                                                                       'shortName': 'Designation 1',
				                                                                       'description': 'Designation 1 Description',
				                                                                       'permissionDescriptions': [
					                                                                       'Permission 1 Description',
					                                                                       'Permission 2 Description',
				                                                                       ],
				                                                                       }
				                                                                      ),  # /role1

				                                                                      ('role2',
				                                                                       {
				                                                                       'shortName': 'Designation 2',
				                                                                       'description': 'Designation 2 Description',
				                                                                       'permissionDescriptions': [
					                                                                       'Permission 1 Description',
					                                                                       'Permission 3 Description',
				                                                                       ],
				                                                                       }
				                                                                      ),  #/role2

				                                                                      ('role3',
				                                                                       {
				                                                                       'shortName': 'Designation 3',
				                                                                       'description': 'Designation 3 Description',
				                                                                       'permissionDescriptions': [
					                                                                       'Permission 2 Description',
					                                                                       'Permission 3 Description',
				                                                                       ],
				                                                                       }
				                                                                      ),  #/role3
			                                                                      ]
		                                                                      ),  # /tableData = OrderedDict
		                                             ),  # /bodyContent = proxy.render ...'rolesTable.html'
		                                             footerContent='',
		                    ),  # /bodyContent = proxy.render ...'layout1.html'
		),  # /return proxy.render ...'base.html'

	elif nextArg == 'testForm':
		params['css'].append('/etc2/form.css')
		params['js'].append('/etc2/form.js')

		return proxy.render('base.html',
		                    bodyContent=proxy.render('layout1.html',
		                                             layoutClass='outerLayout',
		                                             headerContent='',
		                                             footerContent='',
		                                             bodyContent=proxy.render('form.html',
		                                                                      formClass='testForm',
		                                                                      formInputs=[
			                                                                      {
			                                                                      'class': 'textInput',
			                                                                      'label': 'text input label',
			                                                                      'error': 'test error message',
			                                                                      'widget': '<input>',
			                                                                      },

			                                                                      {
			                                                                      'class': 'passwordInput',
			                                                                      'label': 'password input label',
			                                                                      'error': 'password input error',
			                                                                      'widget': '<input type="password">',
			                                                                      },
		                                                                      ]
		                                             )
		                    )
		)
	#

	links = [
		('Login Page', '/login'),
		('Fitx Admin Landing Page', '/fitxAdmin'),
		('Reset Session', '/resetSession'),
		('Role Management', '/roles'),
		('Test Form', '/testForm'),
	]

	bodyContent = []
	for title, href in links:
		bodyContent.append(
			'<a href="{}">{}</a><br>'.format(
				href, title
			)
		)
	#

	return proxy.render('base.html',  # bodyContent = pprint.pformat ([args, kwargs]),
	                    bodyContent=''.join(bodyContent)
	)

#

