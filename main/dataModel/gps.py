from appConfig import AppConfig
from db import DbTypes, DbEntity, InfoMixin
import json
from sqlalchemy import Column
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy import Integer, Float, Date, Numeric, String
from sqlalchemy.orm import relationship
from componentConfig import PermissionConfig
import os, sys
import enum


def defineTables(db):
	db.addRoles(
		Administrator='administrator',
		MainUser='mainUser',
		SubUser='subUser'
	)

	loadPermission(db)


	@db.table(
		'Gps_Coordinate_Data',
		Column('Vehicle_Id', DbTypes.Uuid, nullable=False),
		Column('Time', DbTypes.VeryShortString, nullable=False),
		Column('Date', Date, nullable=False),
		Column('Latitude', Numeric(20, 15), nullable=False),
		Column('Longitude', Numeric(20, 15), nullable=False),
		Column('Field1', String(16)),
		Column('Field2', String(16)),
		PrimaryKeyConstraint('Vehicle_Id', 'Time', 'Date')

	)
	class Gps_Coordinate_Data(DbEntity): pass

	@db.table(
		'Gps_Vehicle_Info',
		Column('User_Id', DbTypes.Uuid, nullable=False),
		Column('Vehicle_Id', DbTypes.Uuid, nullable=False),
		Column('Vehicle_Name', String(20), nullable=False),
		Column('Vehicle_Make', String(20), nullable=False),
		Column('Vehicle_Reg_No', String(16)),
		Column('Vehicle_Type', String(16)),
		Column('Vehicle_Model', String(16)),
		Column('Group_id', DbTypes.Uuid),
		Column('Device_id', Numeric(16, 0)),

		PrimaryKeyConstraint('Vehicle_Id'),

		UniqueConstraint('User_Id', 'Vehicle_Id')

	)
	class Gps_Vehicle_Info(DbEntity): pass



	@db.table(
		'Gps_Geofence_Data',
		Column('Geofence_Id', DbTypes.Uuid, nullable=False),
		Column('Geofence_Name', String(20), nullable=False),
		Column('Vehicle_Id', DbTypes.Uuid, nullable=False),
		Column('User_Id', DbTypes.Uuid, nullable=False),
		Column('Coordinate_Id', DbTypes.Uuid, nullable=False),
		Column('Latitude', String(1024), nullable=False),
		Column('Longitude', String(1024), nullable=False),

		PrimaryKeyConstraint('Geofence_Id', 'User_Id', 'Vehicle_Id'),

	)
	class Gps_Geofence_Data(DbEntity): pass


	@db.table(
		'Gps_Poi_Info',
		Column('Poi_Id', DbTypes.Uuid, nullable=False),
		Column('User_Id', DbTypes.Uuid, nullable=False),
		Column('Vehicle_Id', DbTypes.Uuid, nullable=False),
		Column('Poi_Name', DbTypes.VeryLongString, nullable=False),
		Column('Poi_Latitude', Numeric(20, 15), nullable=False),
		Column('Poi_Longitude', Numeric(20, 15), nullable=False),
		Column('Category', String(20)),

		PrimaryKeyConstraint('Poi_Id')

	)
	class Gps_Poi_Info(DbEntity): pass


	@db.table(
		'Gps_Poi_Data',
		Column('Id', Integer, nullable=False),
		Column('Poi_Id', DbTypes.Uuid, nullable=False),
		Column('Time', DbTypes.VeryShortString, nullable=False),
		Column('Date', Date, nullable=False),

		PrimaryKeyConstraint('Id')

	)
	class Gps_Poi_Data(DbEntity): pass


def loadInitialData(db, params=None):
	with db.session() as session:

		adminOrgId = session.query(db.Organization.id).filter_by(
			name=AppConfig.AdminOrganization
		).one()

		jsonFile = open('./dataModel/data.json')
		jsonObject = json.load(jsonFile)
		date = ['2014-07-15', '2014-07-16', '2014-07-17']
		# '2014-07-02', '2014-07-03', '2014-07-20', '2014-07-22', '2014-07-24', '2014-07-28']
		for d in date:
			for obj in jsonObject:
				coordinate_data = db.Gps_Coordinate_Data.newFromParams({
				'Longitude': obj['position']['longitude'],
				'Latitude': obj['position']['latitude'],
				'Vehicle_Id': obj['vehicleId'],
				'Time': str(obj['time']['hour']) + str(obj['time']['minute']) + str(obj['time']['second']),
				'Date': d
				})

				session.add(coordinate_data)
		#

		jsonFile2 = open('./dataModel/data2.json')
		jsonObject2 = json.load(jsonFile2)
		i=0
		for obj in jsonObject2:
			if obj['vehicleId'] == 22 or obj['vehicleId'] == 23:
				d = '2014-07-20'
			elif obj['vehicleId'] == 24:
				d = '2014-07-22'
			elif obj['vehicleId'] == 33:
				d = '2014-07-24'
			elif obj['vehicleId'] == 34:
				d = '2014-07-28'
			elif obj['vehicleId'] == 55:
				d = '2014-07-02'
			elif obj['vehicleId'] == 56:
				d = '2014-07-03'
			try:
				coordinate_data = db.Gps_Coordinate_Data.newFromParams({
				'Longitude': obj['position']['longitude'],
				'Latitude': obj['position']['latitude'],
				'Vehicle_Id': obj['vehicleId'],
				'Time': str(obj['time']['hour']) + str(obj['time']['minute']) + str(obj['time']['second']),
				'Date': d
				})
				i+=1
				session.add(coordinate_data)
			except:
				print(i)

#

def loadPermission(db):
	for item in PermissionConfig:
		if (item['appName'] != ''):
			db.addPermissions(**{item['name']: item['appName']})


