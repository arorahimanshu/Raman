from appConfig import AppConfig
from db import DbTypes, DbEntity, InfoMixin

from sqlalchemy import Column
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy import Numeric, Integer, Float, DateTime
from sqlalchemy.orm import relationship

import enum

def defineTables (db) :

	payment = db.rawTable (
		'payment',
		Column ('id', DbTypes.Uuid, nullable = False),
		Column ('payer_id', db.Entity.columnType ('id'), nullable = False),
		Column ('payee_id', db.Entity.columnType ('id'), nullable = False),
		Column ('when', DateTime, nullable = False),
		Column ('amount', Numeric (7,2), nullable = False),
		Column ('currency', DbTypes.VeryShortString, nullable = False),

		PrimaryKeyConstraint ('id'),
		ForeignKeyConstraint (['payer_id'], ['entity.id']),
		ForeignKeyConstraint (['payee_id'], ['entity.id']),
	)
	class Payment (DbEntity) : pass
	db.rawMapper (
		Payment, payment,
		properties = {
			'payer' : relationship (db.Entity, uselist = False, foreign_keys = [payment.c.payer_id]),
			'payee' : relationship (db.Entity, uselist = False, foreign_keys = [payment.c.payee_id]),
		}
	)

	@db.table (
		'credit',

		Column ('payment_id', Payment.columnType ('id'), nullable = False),
		Column ('when', DateTime, nullable = False),
		Column ('amount', Numeric (7,2), nullable = False),

		PrimaryKeyConstraint ('payment_id', 'when'),
		ForeignKeyConstraint (['payment_id'], ['payment.id']),
	)
	@db.mapper (
		properties = {
			'payment' : relationship (Payment, uselist = False),
		}
	)
	class Credit (DbEntity) : pass

	@db.table (
		'paymentDetail',
		Column ('id', db.Info.columnType ('id'), nullable = False),
		Column ('payment_id', Payment.columnType ('id'), nullable = False),
		Column ('type', db.Info.columnType ('type'), nullable = False),
		Column ('preference', db.Info.columnType ('preference'), nullable = False),
		Column ('data', db.Info.columnType ('data')),

		PrimaryKeyConstraint ('id'),
		ForeignKeyConstraint (['payment_id'], ['payment.id']),
		UniqueConstraint ('payment_id', 'type', 'data','preference'),
	)
	@db.mapper (
		properties = {
			'payment' : relationship (Payment, uselist = False),
		}
	)
	class PaymentDetail (DbEntity, InfoMixin) :
		@enum.unique
		class Type (enum.Enum) :
			Method = 0
			InstrumentNo = 1
			InstrumentDate = 2
			BankName = 3
			BranchName = 4
			InstrumentExpiry = 5
			CardType = 6
			MachineType = 7
			AuthCode = 8
			Amount = 9
			
		#

		@enum.unique
		class Method (enum.Enum) :
			Cash = 0
			CreditCard = 1
			DebitCard = 2
			Cheque = 3
			Online =4
		#

		@enum.unique
		class CardType (enum.Enum) :
			MasterCard = 0
			Visa = 1
			Maestro = 2
		#

		_registeredEnumTypes = {
			Type.Method: Method,
			Type.CardType: CardType,
		}
	#
#

def loadInitialData (db, params = None) :
	pass
#

