from contextlib import contextmanager


class Component:
	def __init__(self, **kwargs):
		pass

	#

	@property
	def app(self):
		return self._app

	#

	@property
	def logger(self):
		return self._logger

	#

	def setup(self):
		pass

	#

	def reset(self):
		pass

	#

	def run(self):
		pass

	#

	def shutdown(self):
		pass

	#

	@contextmanager
	def asContext(self):
		self.setup()
		try:
			yield self
		finally:
			self.shutdown()
		#
		#


#

class Container:
	def __init__(self, **kwargs):
		self._components = dict()

	#

	def component(self, name):
		return self._components[name]

	#

	def reset(self):
		for item in self._components.values():
			item.reset()
		#

	#

	def registerComponent(self, name, item):
		if name in self._components:
			raise Exception('Component already exists: ' + name)
		else:
			self._components[name] = item
		#
		#

#

