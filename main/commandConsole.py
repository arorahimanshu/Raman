from component import Component
from utils import deferredGet

from traceback import print_exc
import shlex
from cmd import Cmd
from argparse import ArgumentParser
from getpass import getpass
import os
from contextlib import contextmanager


class _CustomArgumentParser(ArgumentParser):
	class _CommandTerminated(Exception): pass

	def exit(self, status=0, message=None):
		if message:
			print(message)
		#

		raise self._CommandTerminated()

	#

	def error(self, message):
		print('Error:', message)

		raise self._CommandTerminated()

	#


#

class _CustomCmd(Cmd):
	Continue = False
	Halt = True

	def __init__(self, parent):
		Cmd.__init__(self)
		self.prompt = 'fitx> '
		self._parent = parent

	#

	def postcmd(self, stop, line):
		return self._parent.rawCommand(
			line,
			haltValue=self.Halt,
			continueValue=self.Continue
		)

	#

	def default(self, line):
		pass

	#

	def do_help(self, *args, **kwargs):
		pass

	#


#

class CommandConsole(Component):
	class Verbosity:
		Low = 0
		Normal = 1
		High = 2

	#

	def __init__(self, **kwargs):
		Component.__init__(self, **kwargs)

		self._cmd = _CustomCmd(self)
		self._setupParsers()

		self._verbosity = self.Verbosity.Normal

	#

	@contextmanager
	def temporaryVerbosity(self, newVerbosityLevel):
		oldVerbosity = self._verbosity
		self._verbosity = newVerbosityLevel
		try:
			yield
		finally:
			self._verbosity = oldVerbosity
		#

	#

	def normalPrint(self, *args, **kwargs):
		if self._verbosity >= self.Verbosity.Normal:
			print(*args, **kwargs)
		#

	#

	def run(self):
		Component.run(self)
		self.normalPrint('Welcome to FitX command console, type \'help\' for basic list of commands.')
		self._cmd.cmdloop()

	#

	def rawCommand(self, line, haltValue=None, continueValue=None, config=None):
		tokens = shlex.split(line)

		if len(tokens) > 0:
			cmd = tokens[0].lower().strip()
			args = tokens[1:]

			if cmd in ['quit', 'exit']:
				return haltValue
			elif cmd == 'help':
				self.normalPrint('Basic commands :')
				self.normalPrint('  help: print this help message')
				self.normalPrint('  list: list all operational commands')
				self.normalPrint('  !cmd: run \'cmd\' on shell')
				self.normalPrint('  exit: exists console and shutdown server')
				self.normalPrint('  quit: same as exit')
			elif cmd == 'list':
				self.listCommands()
			elif cmd.startswith('!'):
				self.runInShell(line[1:])
			else:
				try:
					self.command(cmd, args, config=config)
				except SystemExit:
					raise
				except _CustomArgumentParser._CommandTerminated:
					return continueValue
				except:
					print_exc()
				#
				#
		#

		return continueValue

	#

	def command(self, cmd, args, config=None):
		if cmd not in self._parsers:
			# raise Exception ('Invalid command:', cmd)
			print('Command not recognized, type \'help\' for basic list of commands.')
		else:
			if config == None:
				config = dict()
			#
			parser = self._parsers[cmd][0]
			handler = self._parsers[cmd][1]
			handler(parser.parse_args(args), config)
		#

	#

	def listCommands(self):
		self.normalPrint('Following operational commands are available.')
		self.normalPrint('Type <cmd> -h, for more help on individual command.')
		for key in sorted(self._parsers.keys()):
			self.normalPrint('  {}:'.format(key), self._parsers[key][2])
		#

	#

	def runInShell(self, cmd):
		result = os.system(cmd)
		print()
		print('shell returned:', result)

	#

	def _setupParsers(self):
		self._parsers = dict()
		self._parsers['db'] = (self._setupDbParser(), self._handleDbCommand, 'database management')
		self._parsers['test'] = (self._setupTestParser(), self._handleTestCommand, 'testing')
		self._parsers['auto'] = (self._setupAutoBrowserParser(), self._handleAutoBrowserCommand, 'auto browsing')

	#

	def _setupAutoBrowserParser(self):
		parser = _CustomArgumentParser('auto', 'Auto Browser')
		browserAction = parser.add_mutually_exclusive_group()

		browserAction.add_argument(
			'-s', '--start',
			dest='start', metavar='TASK'
		)

		browserAction.add_argument(
			'-t', '--stop',
			dest='stop', metavar='TASK'
		)

		browserAction.add_argument(
			'-r', '--restart',
			dest='restart', metavar='TASK'
		)

		browserAction.add_argument(
			'-l', '--list',
			dest='list',
			action='store_const',
			default=False,
			const=True
		)

		return parser

	#

	def _handleAutoBrowserCommand(self, cmd, config=None):
		autoBrowser = self.app.component('autoBrowser')

		if cmd.start or 'start' in config:
			autoBrowser.startTask(
				deferredGet(config, 'start',
				            getattr, cmd, 'start'
				)
			)
		elif cmd.restart or 'restart' in config:
			autoBrowser.restartTask(
				deferredGet(config, 'restart',
				            getattr, cmd, 'restart'
				)
			)
		elif cmd.stop or 'stop' in config:
			autoBrowser.stopTask(
				deferredGet(config, 'stop',
				            getattr, cmd, 'stop',
				)
			)
		elif cmd.list:
			tasks = autoBrowser.listTasks()
			for name in tasks:
				print('  -', name)
			#
			#

	def _setupTestParser(self):
		parser = _CustomArgumentParser('test', 'Testing Application')

		testOperation = parser.add_mutually_exclusive_group()

		testOperation.add_argument(
			'-l', '--like',
			dest='like',
			help='primitive string matching using %%',
		)

		testOperation.add_argument(
			'-L', '--list',
			dest='listOnly',
			action='store_const',
			default=False,
			const=True,
		)

		return parser

	#

	def _handleTestCommand(self, cmd, config):
		if self.app.testMode:
			testComponent = self.app.component('testComponent')
			testComponent.runTests(listOnly=cmd.listOnly, like=cmd.like)
		else:
			print('Error: App is not running in test mode.')
		#

	#

	def _setupDbParser(self):
		parser = _CustomArgumentParser('db', 'Database Operations')
		tableOperation = parser.add_mutually_exclusive_group()
		tableOperation.add_argument(
			'-d', '--dropTables',
			action='store_true', dest='dropTables'
		)
		tableOperation.add_argument(
			'-c', '--createTables',
			action='store_true', dest='createTables'
		)
		tableOperation.add_argument(
			'-l', '--loadInitialData',
			action='store_true', dest='loadInitialData'
		)

		return parser

	#

	def _handleDbCommand(self, cmd, config):
		dbManager = self.app.component('dbManager')

		if cmd.dropTables:
			dbManager.dropTables()
			self.normalPrint('tables dropped...')
		elif cmd.createTables:
			dbManager.createTables()
			self.normalPrint('tables created...')
		elif cmd.loadInitialData:
			params = dict()
			params['basic1.superuser.username'] = deferredGet(
				config, 'basic1.superuser.username',
				input, 'superuser username: ',
			)
			params['basic1.superuser.password'] = deferredGet(
				config, 'basic1.superuser.password',
				getpass, 'superuser password: ',
			)
			confirm = deferredGet(
				config, 'basic1.superuser.password',
				getpass, 'again: ',
			)
			if confirm != params['basic1.superuser.password']:
				raise Exception('passwords dont match !')
			#
			dbManager.loadInitialData(params)
			self.normalPrint('initial data loaded...')
		#
		#

#


