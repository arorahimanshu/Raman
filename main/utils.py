from appConfig import AppConfig

from passlib.apps import custom_app_context as pwdContext
from mako.lookup import TemplateLookup
from mako.runtime import Context

import os
from itertools import chain
from importlib import import_module
from collections import Iterable
from functools import partial
from uuid import uuid4
import re
import datetime


def passwordEncrypt(raw):
	return pwdContext.encrypt(raw)


#

def passwordVerify(toVerify, storedHash):
	return pwdContext.verify(userInput, storedHash)


#

def fromSameDirectory(_file_, *args):
	return os.path.join(
		os.path.dirname(
			os.path.abspath(_file_)
		), *args
	)


#

def sameDirectory(_file_):
	return os.path.dirname(os.path.abspath(_file_))


#

def checkWritableDir(dirname, excMsg):
	if not os.path.isdir(dirname):
		if not os.access(dirname, os.R_OK | os.W_OK | os.X_OK):
			raise Exception(excMsg)
		#
		#


#

def relativePath(_file_, destination):
	return os.path.join(
		os.path.dirname(
			os.path.abspath(_file_)
		), destination
	)


#

def importItem(qName):
	i = qName.rfind('.')
	moduleName = qName[:i]
	clsName = qName[i + 1:]

	module = import_module(moduleName)
	cls = getattr(module, clsName)

	return cls


#

def importItemFromModule(moduleName, itemName):
	module = import_module(moduleName)
	item = getattr(module, itemName)
	return item


#

def deferredGet(item, key, *args, **kwargs):
	if key in item:
		return item[key]
	else:
		return partial(*args, **kwargs)()
	#


#

class TemplateManager:
	class Proxy:
		def __init__(self, parent, kwargs):
			self._parent = parent
			self._defaultKwargs = kwargs

		#

		def render(self, name, stream=None, **kwargs):
			params = dict(self._defaultKwargs)
			params.update(kwargs)
			return self._parent.render(name, stream, **params)

		#

	#

	def __init__(self, cacheUid, templateDirectory):
		checkWritableDir(
			AppConfig.MakoConfig.CacheDir,
			'AppConfig.MakoConfig.CacheDir is not a valid directory.'
		)
		self._cacheUid = 'cache_' + cacheUid
		self._templateLookup = TemplateLookup(
			directories=[templateDirectory],
			module_directory=os.path.join(
				AppConfig.MakoConfig.CacheDir, self._cacheUid
			)
		)

	#

	def render(self, name, stream=None, **kwargs):
		template = self._templateLookup.get_template(name)
		if stream:
			context = Context(stream, **kwargs)
			template.render_context(context)
		else:
			return template.render(**kwargs)
		#

	#

	def proxy(self, **kwargs):
		return TemplateManager.Proxy(self, kwargs)

	#


#

def callOrDisplay(x):
	if callable(x):
		x()
		return ''
	else:
		return x
	#


#

def newUuid():
	return uuid4().hex


#

class Validator:
	def __init__(self, target):
		self._target = target
		self._errors = dict()
		self._evaluatedTargets = set()

	#

	@property
	def errors(self):
		if len(self._errors) > 0:
			return self._errors
		else:
			return None
		#

	#

	def required(self, name, errorMsg='must be present'):
		if name in self._target:
			return _FieldValidator(self, name)
		else:
			self._errors[name] = errorMsg
			return _FieldValidator(self, None)
		#

	#

	def optional(self, name):
		if name in self._target:
			return _FieldValidator(self, name)
		else:
			return _FieldValidator(self, None)
		#
		#


#

class _ValidatorRegs:
	Email = re.compile(r'[^@]+@[^@]+\.[^@]+')


#

class _FieldValidator:
	def __init__(self, validator, targetName):
		self._validator = validator

		if targetName:
			self._targetName = targetName
			self._target = self._validator._target[targetName]
		else:
			self._targetName = None
			self._target = None
		#

		self._unsetError()

	#

	def _setError(self, depth, message):
		if depth > self._lastErrorDepth:
			self._lastErrorDepth = depth
			self._errorMsg = message
		#

	#

	def _unsetError(self):
		self._lastErrorDepth = -1
		self._errorMsg = None

	#

	@property
	def errorMsg(self):
		return self._errorMsg

	#

	def validate(self, *args, errorMsg=None):
		if self._target:
			if errorMsg:
				self._setError(0, errorMsg)
			#
			result = self._eval(0, args)
			if result:
				self._unsetError()
			else:
				self._validator._errors[self._targetName] = self.errorMsg
			#

	#

	def _eval(self, depth, args, errorMsgValue=False):
		first = args[0]
		errorMsg = 'invalid'

		if first == 'or':
			result = self._or(depth, args[1:])
		elif first == 'and':
			result = self._and(depth, args[1:])
		elif first == 'not':
			result = not self._eval(depth + 1, args[1])
		elif first == 'type':
			result = isinstance(self._target, args[1])
			errorMsg = 'wrong type'
		elif first == 'validateElementByKey':
			result = self._validateElementByKey(depth, args[1:])
			errorMsg = " doesn't satisfy constraints"
		elif first == 'validateForAllInList':
			result = self._validateForAllItems(depth, args[1:])
			errorMsg = "List doesn't satisfy condition"

		# Usage: send args as {'keyName1':['Value1','Value2'],'keyName2':['value3','value4']}
		#result will be true only when each keyname is present and value is present corresponding to its keyname
		#send empty valuename if they are not be validated
		elif first == 'inclusion':
			dict = args[1]
			data = self._target
			result = False
			try:
				for keyName in dict:
					if keyName in data:
						for valueName in dict[keyName]:
							if valueName in data[keyName]:
								pass
							else:
								raise Exception
					else:
						raise Exception
				result = True
			except:
				result = False

		elif first == 'isDate':
			try:
				datetime.date(*self._target)
				result = True
			except (TypeError, ValueError):
				result = False
			#
			errorMsg = 'is not a valid date'
		elif first == 'in':
			result = self._target in args[1]
			errorMsg = 'must be from {}'.format(str(args[1]))
		elif first == 'inRange':
			start = args[1]
			stop = args[2]
			result = self._target in range(start, stop)
			errorMsg = 'must be >={} and <{}'.format(start, stop)
		elif first == 'lengthRange':
			targetLength = len(self._target)
			result = targetLength >= args[1] and targetLength <= args[2]
			errorMsg = 'length must be between {} to {} (inclusive)'.format(
				args[1], args[2]
			)
		elif first == 'exactLength':
			result = len(self._target) == args[1]
			errorMsg = 'length must be exactly {}'.format(args[1])
		elif first == 'maxLength':
			result = len(self._target) <= args[1]
			errorMsg = 'length must be less than or equal to {}'.format(args[1])
		elif first == 'value':
			result = self._target == args[1]
		elif first == 'email':
			result = _ValidatorRegs.Email.fullmatch(self._target) == None
			errorMsg = 'not a valid email address'
		elif first == 'custom':
			errorMsg = args[1](self._target)
			result = not errorMsg
		elif first == 'errorMsg':
			result = errorMsgValue
			self._setError(depth + 1, args[1])
			return result
		else:
			raise Exception('Invalid validator specification')
		#

		if not result:
			self._setError(depth, errorMsg)
		#

		return result

	#

	def _or(self, depth, args):
		for item in args:
			result = self._eval(depth + 1, item, errorMsgValue=False)
			if result:
				return True
			#
		#

		return False

	#
	def _validateElementByKey(self, depth, args):
		incoming = self._target
		self._target = incoming[args[1]]
		result = self._eval(depth + 1, args[0])
		self._target = incoming
		return result

	def _validateForAllItems(self, depth, args):
		incoming = self._target
		for item in incoming:
			self._target = item
			result = self._eval(depth + 1, args[0])
			if not result:
				self._target = incoming
				return False
			#
		#
		self._target = incoming
		return True

	#


	def _and(self, depth, args):
		for item in args:
			result = self._eval(depth + 1, item, errorMsgValue=True)
			if not result:
				return False
			#
		#

		return True

	#

#

