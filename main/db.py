from appConfig import AppConfig
from componentConfig import DataModules
from component import Component
import utils
from sqlalchemy.orm import class_mapper

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
from sqlalchemy.orm import mapper
from sqlalchemy import String
from sqlalchemy import CHAR

from contextlib import contextmanager
from importlib import import_module
from uuid import uuid4
import json


class DbEntity:
	@property
	def table(self):
		return self._db_table

	#

	@classmethod
	def columnType(cls, columnName):
		return getattr(cls._db_table.c, columnName).type

	#

	@classmethod
	def newFromParams(cls, *dictArgs, **params):
		allParams = dict()
		for dictArg in dictArgs:
			allParams.update(dictArg)
		#
		allParams.update(params)

		newObj = cls()
		for key, value in allParams.items():
			setattr(newObj, key, value)
		#

		return newObj

	#

	@classmethod
	def updateFromParams(cls, keyDict, **params):
		db = Db()
		allParams = dict()
		allParams.update(params)

		with db.session() as session:
			getRows = session.query(cls).filter_by(**keyDict).one()
			for key, value in allParams.items():
				setattr(getRows, key, value)
			#
			session.add(getRows)

	@classmethod
	def addOrUpdateFromParams(cls,cmd, *keyDict, **params):
		if(cmd.lower()=='edit'):
			cls.updateFromParams(keyDict, **params)
		else:
			return cls.newFromParams(*keyDict,**params)



	@classmethod
	def delete(cls, keyDict):
		db = Db()
		i = 0
		try:
			with db.session() as session:
				getRows = session.query(cls).filter_by(**keyDict).all()
				for row in getRows:
					i += 1
					session.delete(row)
			return i
		except:
			return None


	@staticmethod
	def newUuid():
		return utils.newUuid()

	#
	@classmethod


	def _get_keys(cls):
		return class_mapper(cls).c.keys()


	def get_dict(self):
		d = []
		for k in self._get_keys():
			d.append(k)
		return d


	#

class DbTypes:
	Uuid = CHAR(32)

	VeryShortString = String(16)
	ShortString = String(64)
	MediumString = String(128)
	LongString = String(512)
	VeryLongString = String(1024)

	DataString = LongString

	Password = String(128)


#

class Db(Component):
	_ConnectionStringFormat = '{engine}+{driver}://{username}:{password}@{host}:{port}/{database}'

	def __init__(self, **kwargs):

		self._config = kwargs.get('config', dict())

		if self._config.get('generateScript', False):
			additionalEngineKwargs = {
			'strategy': 'mock',
			'executor': self._scriptGeneratorCallback,
			}
		else:
			additionalEngineKwargs = dict()
		#

		if AppConfig.DbEngine == 'postgres':
			self._engine = create_engine(
				Db._ConnectionStringFormat.format(
					engine='postgresql',
					driver='psycopg2',
					username=AppConfig.PostgresConfig.Username,
					password=AppConfig.PostgresConfig.Password,
					host=AppConfig.PostgresConfig.Host,
					port=AppConfig.PostgresConfig.Port,
					database=AppConfig.PostgresConfig.Database,
				),
				**additionalEngineKwargs
			)
		elif AppConfig.DbEngine == 'mysql':
			self._engine = create_engine(
				Db._ConnectionStringFormat.format(
					engine='mysql',
					driver='pymysql',
					username=AppConfig.MysqlConfig.Username,
					password=AppConfig.MysqlConfig.Password,
					host=AppConfig.MysqlConfig.Host,
					port=AppConfig.MysqlConfig.Port,
					database=AppConfig.PostgresConfig.Database,
				),
				**additionalEngineKwargs
			)
		else:
			raise Exception('Unsupported Database Engine: ' + AppConfig.DbEngine)
		#

		self._metadata = MetaData(bind=self.engine)
		self._Session = sessionmaker(bind=self.engine)

		self._dataModules = []

		for name in DataModules:
			module = import_module(name)
			self._dataModules.append(module)
			module.defineTables(self)
		#

	#

	def _addTable(self, classDecl):
		name = classDecl.__name__
		if hasattr(self, name):
			raise Exception('db already contains a table with name: ' + name)
		else:
			setattr(self, name, classDecl)
		#

		# return classDecl

	#

	def mapper(self, *args, **kwargs):
		def tempClosure(classDecl):
			classDecl._db_mapper = (args, kwargs)
			return classDecl

		#

		return tempClosure

	#

	def rawTable(self, tableName, *args, **kwargs):
		return Table(tableName, self.metadata, *args, **kwargs)

	#

	def rawMapper(self, classDecl, table, *args, **kwargs):
		classDecl._db_table = table
		mapper(classDecl, table, *args, **kwargs)
		self._addTable(classDecl)

	#

	def table(self, tableName, *args, **kwargs):

		def tempClosure(classDecl):
			mapperArgs, mapperKwargs = getattr(
				classDecl, '_db_mapper',
				(tuple(), dict())
			)

			table = Table(
				tableName, self.metadata,
				*args, **kwargs
			)

			classDecl._db_table = table

			mapper(
				classDecl, table,
				*mapperArgs, **mapperKwargs
			)

			self._addTable(classDecl)

			return classDecl

		#

		return tempClosure

	#

	@property
	def engine(self):
		return self._engine

	@property
	def metadata(self):
		return self._metadata

	@contextmanager
	def session(self):
		_session = self._Session()
		try:
			yield _session
		except:
			_session.rollback()
			_session.close()
			raise
		else:
			_session.commit()
			_session.close()
		#

	#

	def _scriptGeneratorCallback(self, sql):
		self._config['scriptHandler'](
			str(sql.compile(dialect=self.engine.dialect))
		)

	#

	def loadInitialData(self, params=None):
		for module in self._dataModules:
			if hasattr(module, 'loadInitialData'):
				module.loadInitialData(self, params)
			#
			#

	#

	def loadTestData(self):
		for module in self._dataModules:
			if hasattr(module, 'loadTestData'):
				module.loadTestData(self)
			#
			#

	#

	def createTables(self):
		self.metadata.create_all()
		for module in self._dataModules:
			if hasattr(module, 'afterCreate'):
				module.afterCreate(self)
			#
			#

	#

	def dropTables(self):
		for module in self._dataModules:
			if hasattr(module, 'beforeDrop'):
				module.beforeDrop(self)
			#
		#
		self.metadata.drop_all()

	#

	def shutdown(self):
		if not self._config.get('generateScript', False):
			self.engine.dispose()
		#

	#

	def setup(self):
		self._logger = self.app.masterLogger.getChild('db')

	#


#

class InfoMixin:
	'''
	requires
	self._registeredEnumTypes to return a dict of
	{enumType=>enumClass}
	'''

	_registeredEnumTypes = dict()

	def __get_enumType(self):
		return self.Type(self.type)

	#

	def __set_enumType(self, other):
		self.type = self.Type(other).value

	#

	enumType = property(__get_enumType, __set_enumType)

	def __get_jsonData(self):
		data = json.loads(self.data)
		if self.enumType in self._registeredEnumTypes:
			return self._registeredEnumTypes[self.enumType](data)
		else:
			return data
		#

	#

	def __set_jsonData(self, other):
		if self.enumType in self._registeredEnumTypes:
			self.data = json.dumps(self._registeredEnumTypes[self.enumType](other).value)
		else:
			self.data = json.dumps(other)
		#

	#

	jsonData = property(__get_jsonData, __set_jsonData)

#

if __name__ == '__main__':
	def callback(sql):
		print(sql)

	#
	db = Db(
		config={
		'generateScript': True,
		'scriptHandler': callback
		}
	)
	# db.metadata.drop_all ()
	db.metadata.create_all()
# db.loadInitialData ()
#db.engine.dispose ()
#

