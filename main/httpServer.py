from component import Component
from appConfig import AppConfig
from componentConfig import HttpServerRootComponent
from utils import importItem, relativePath, checkWritableDir

import cherrypy
from cherrypy import _cperror

from contextlib import contextmanager
from itertools import chain
from io import StringIO
from uuid import uuid4
import json
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import sys, os
import re
from urllib.parse import quote_plus, unquote_plus


class RequestPath:
	def __init__(self):
		pathInfo = cherrypy.request.path_info
		self._parts = [
			unquote_plus(x) for x in
			filter(
				(lambda x: len(x) > 0),
				pathInfo.split('/')
			)
		]

		self._currentIndex = 0
		self._numberOfParts = len(self._parts)

	#

	def nextPart(self, default=None):
		if self._currentIndex < self._numberOfParts:
			self._currentIndex += 1
			return self._parts[self._currentIndex - 1]
		else:
			return default
		#

	#

	def allPrevious(self, ignore=0, additional=[]):
		return '/' + '/'.join(self._parts[:self._currentIndex - ignore] + additional)

	#


#

class ErrorHandler:
	def __init__(self, server):
		self.server = server

	#

	def genericError(self, *args, **kwargs):
		# print (args)
		#print (kwargs)
		print(_cperror.format_exc())
		return 'damn...'

	#


#

def _removeStreamHandlers(logger):
	targetHandlers = []
	for handler in logger.handlers:
		if isinstance(handler, StreamHandler):
			targetHandlers.append(handler)
		#
	#

	for handler in targetHandlers:
		logger.removeHandler(handler)
	#


#

def _setupLogManager(log):
	_removeStreamHandlers(log.error_log)
	_removeStreamHandlers(log.access_log)

	log.error_file = ''
	log.access_file = ''

	maxBytes = getattr(log, 'rot_maxBytes', 10000000)
	backupCount = getattr(log, 'rot_backupCount', 10)

	checkWritableDir(
		AppConfig.WebserverConfig.LogFolder,
		'AppConfig.WebserverConfig.LogFolder is not a valid directory.'
	)

	errorLogFilename = os.path.join(AppConfig.WebserverConfig.LogFolder, 'error.log')
	accessLogFilename = os.path.join(AppConfig.WebserverConfig.LogFolder, 'access.log')

	errorLogHandler = RotatingFileHandler(errorLogFilename, 'a', maxBytes, backupCount)
	accessLogHandler = RotatingFileHandler(accessLogFilename, 'a', maxBytes, backupCount)

	errorLogHandler.setLevel(logging.DEBUG)
	errorLogHandler.setFormatter(cherrypy._cplogging.logfmt)
	accessLogHandler.setLevel(logging.DEBUG)
	accessLogHandler.setFormatter(cherrypy._cplogging.logfmt)

	log.error_log.addHandler(errorLogHandler)
	log.access_log.addHandler(accessLogHandler)


#

class Server(Component):
	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

		cherrypy.config.update(
			{
			'engine.autoreload.on': False,
			'tools.sessions.on': True,
			'tools.sessions.timeout': 60,
			'tools.sessions.locking': 'explicit',
			'server.socket_host': AppConfig.WebserverConfig.Host,
			'server.socket_port': AppConfig.WebserverConfig.Port,
			}
		)

		self._config = {}
		for key, value in AppConfig.WebserverConfig.StaticUris.items():
			url = self.formUrl(*key)

			_value = None
			if isinstance(value, str):
				_value = value
			else:
				hint, param = value
				if hint == 'MODULE_DIR':
					_value = relativePath(__file__, param)
				elif hint == 'CALLABLE':
					_value = param()
				#
			#

			if not os.path.isdir(_value):
				raise Exception(
					'Invalid value for AppConfig.WebserverConfig.StaticUris[{}]: {}'.format(
						key, _value
					)
				)
			#

			self._config[url] = {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': _value,
			}
		#

		faviconFilename = getattr(AppConfig.WebserverConfig, 'Favicon', None)
		if (not faviconFilename) or (not os.path.isfile(faviconFilename)):
			raise Exception('Please set AppConfig.WebserverConfig.Favicon to a valid file')
		#

		self._config['/favicon.ico'] = {
		'tools.staticfile.on': True,
		'tools.staticfile.filename': AppConfig.WebserverConfig.Favicon,
		}

		# self._root = Root (self)
		self._errorHandler = ErrorHandler(self)

		cherrypy.config.update(
			{
			'error_page.default': self._errorHandler.genericError,
			}
		)

	#

	@contextmanager
	def session(self):
		with self.app.requestLock():
			cherrypy.session.acquire_lock()
			try:
				if 'uid' not in cherrypy.session:
					cherrypy.session['uid'] = uuid4().hex
				#
				yield cherrypy.session
			finally:
				cherrypy.session.release_lock()
			#
			#

	#

	def expireSession(self, session):
		with self.app.requestLock():
			cherrypy.lib.sessions.expire()
		#

	#

	@staticmethod
	def appUrl(*path):
		return '/' + '/'.join(
			[
				quote_plus(x) for x in
				chain(AppConfig.WebserverConfig.BaseUri, path)
			]
		)

	#

	@staticmethod
	def formUrl(*path):
		return '/' + '/'.join(
			[quote_plus(x) for x in path]
		)

	#

	def setup(self):
		Component.setup(self)
		cls = importItem(HttpServerRootComponent)
		self._root = cls()
		self.app.registerSubComponent(self._root)

		_setupLogManager(cherrypy.log)

		app = cherrypy.tree.mount(self._root, self.appUrl(), self._config)
		cherrypy.engine.start()

		self._logger = self.app.masterLogger.getChild('httpServer')

	#

	# def run (self) :
	#Component.run (self)
	#input ()
	#

	def shutdown(self):
		cherrypy.engine.stop()
		cherrypy.engine.exit()
		Component.shutdown(self)

	#

	def requestPath(self):
		return RequestPath()

	#

	def requestParams(self):
		return json.loads(
			cherrypy.request.params.get(
				'requestParams',
				'{}',
			)
		)

	#

	def infoCookie(self):
		if 'fitxInfo' in cherrypy.request.cookie:
			rawCookie = cherrypy.request.cookie['fitxInfo']
			return json.loads(unquote_plus(rawCookie.value))
		else:
			return dict()
		#

	#

	def requestSubdomain(self):
		return re.search(
			r'(www\.)?(.*?)([:\.]|$)',
			cherrypy.request.headers.get('host', '')
		).groups()[1]

	#

	def jsonResult(self, item):
		cherrypy.response.headers['Content-Type'] = 'application/json'
		return json.dumps(item).encode()

	#

	def javascriptContent(self, content):
		cherrypy.response.headers['Content-Type'] = 'text/javascript'
		return content

	#

#

