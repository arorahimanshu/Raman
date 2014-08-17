from mako.lookup import TemplateLookup
from mako.runtime import Context

import sys, os


class TemplateManager:
	def __init__(self, cacheUid, cacheDir, templateDirectory):
		self._cacheUid = 'cache_' + cacheUid
		self._templateLookup = TemplateLookup(
			directories=[templateDirectory],
			module_directory=os.path.join(
				cacheDir, self._cacheUid
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


#

class QueryParams:
	def __init__(self, queryArgs, queryKwargs):
		self._queryArgs = queryArgs
		self._queryKwargs = queryKwargs

	#

	class _ArgsWalker:
		def __init__(self, parent, start):
			self._queryArgs = list(parent._queryArgs)
			self._current = 0

			for i in range(start):
				self.pop()
			#

		#

		def pop(self, default=None):
			if len(self._queryArgs) == self._current:
				return default
			else:
				self._current += 1
				return self._queryArgs[self._current - 1]
			#
			#

	#

	def argsWalker(self, start=0):
		return self._ArgsWalker(self, start)

	#

#

