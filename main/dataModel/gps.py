from appConfig import AppConfig
from db import DbTypes, DbEntity, InfoMixin
import json
from sqlalchemy import Column
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy import Integer, Float, Date, Numeric, String, CHAR, DateTime
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
	'branch',
		Column('id', DbTypes.Uuid, nullable=False),
   		Column('parent_id', db.Organization.columnType ('id'), nullable=False),
 	   	Column('name',  DbTypes.VeryLongString, nullable=False),

		ForeignKeyConstraint (['id'], ['entity.id']),
		ForeignKeyConstraint (['parent_id'], ['organization.id']),
		PrimaryKeyConstraint('id')

	)
	class branch(DbEntity): pass

	@db.table(
	'VehicleGroup',
		Column('id', DbTypes.Uuid, nullable=False),
  		Column('parent_id', branch.columnType ('id'), nullable=False),
    	Column('name',  DbTypes.VeryLongString, nullable=False),
		Column('category', Integer, nullable=False),

		ForeignKeyConstraint (['id'], ['entity.id']),
		ForeignKeyConstraint (['parent_id'], ['branch.id']),
		PrimaryKeyConstraint('id'),

	)
	class VehicleGroup(DbEntity): pass

	@db.table(
		'Gps_Vehicle_Info',
		Column('id', DbTypes.Uuid, nullable=False),
		Column('parent_id', DbTypes.Uuid, nullable=False),
   		Column('name',  DbTypes.VeryLongString, nullable=False),
		Column('device_id', String(10), nullable=False),

		PrimaryKeyConstraint('id'),
		ForeignKeyConstraint (['id'], ['entity.id']),
		ForeignKeyConstraint (['parent_id'], ['entity.id']),
 		#UniqueConstraint('id')

	)
	class Gps_Vehicle_Info(DbEntity): pass



	@db.table(
		'Gps_Geofence_Data',
		Column('Geofence_Id', DbTypes.Uuid, nullable=False),
		Column('Geofence_Name', String(20), nullable=False),
		#Column('Vehicle_Id', DbTypes.Uuid, nullable=False),
		Column ('User_name', DbTypes.ShortString, nullable = False),
		Column('Coordinate_Id', DbTypes.Uuid, nullable=False),
		Column('Details', String(1024), nullable=False),
		#Column('Longitude', String(1024), nullable=False),

		PrimaryKeyConstraint('Geofence_Id'),
		ForeignKeyConstraint (['User_name'], ['user.username']),


	)
	class Gps_Geofence_Data(DbEntity): pass

	@db.table(
		'GeoFence_vehicle',
		Column('GeoFence_id', DbTypes.Uuid, nullable=False),
		Column('Vehicle_id', DbTypes.Uuid, nullable=False),

		PrimaryKeyConstraint('GeoFence_id','Vehicle_id'),
		ForeignKeyConstraint (['GeoFence_id'], ['Gps_Geofence_Data.Geofence_Id']),
		ForeignKeyConstraint (['Vehicle_id'], ['Gps_Vehicle_Info.id']),
 		#UniqueConstraint('GeoFence_id','Vehicle_id')

	)
	class GeoFence_vehicle(DbEntity): pass
	@db.table(
		'Gps_Poi_Info',
		Column('Poi_Id', DbTypes.Uuid, nullable=False),
		Column ('User_name', DbTypes.ShortString, nullable = False),
		#Column('Vehicle_Id', DbTypes.Uuid, nullable=False),
		Column('Poi_Name', DbTypes.VeryLongString, nullable=False),
		Column('Poi_Latitude', Numeric(20, 15), nullable=False),
		Column('Poi_Longitude', Numeric(20, 15), nullable=False),
		Column('Category', String(20)),

		PrimaryKeyConstraint('Poi_Id'),
		ForeignKeyConstraint (['User_name'], ['user.username']),

	)
	class Gps_Poi_Info(DbEntity): pass


	@db.table(
		'Gps_Poi_Data',
		Column('Id', Integer, nullable=False),
		Column('Poi_Id', DbTypes.Uuid, nullable=False),
		Column('Time', DbTypes.VeryShortString, nullable=False),
		Column('Date', Date, nullable=False),

		PrimaryKeyConstraint('Id'),
		ForeignKeyConstraint (['Poi_Id'], ['Gps_Poi_Info.Poi_Id']),

	)
	class Gps_Poi_Data(DbEntity): pass

	@db.table(
		'Poi_vehicle',

		Column('Poi_Id', DbTypes.Uuid, nullable=False),
		Column('Vehicle_Id', DbTypes.Uuid, nullable=False),

		PrimaryKeyConstraint('Poi_Id','Vehicle_Id'),
		ForeignKeyConstraint (['Poi_Id'], ['Gps_Poi_Info.Poi_Id']),
		ForeignKeyConstraint (['Vehicle_Id'], ['Gps_Vehicle_Info.id']),

	)
	class Poi_vehicle(DbEntity): pass



	@db.table(
		'gpsDeviceMessage1',
		Column('deviceId', String(32), nullable=False),
		Column('messageType', CHAR(4), nullable=False),
		Column('latitude', Float, nullable=False),
		Column('longitude', Float, nullable=False),
		Column('timestamp', DateTime(timezone=False), nullable=False),
		Column('speed', Float, nullable=False),
		Column('orientation', Float, nullable=False),

		PrimaryKeyConstraint('deviceId', 'timestamp'),

	)
	class gpsDeviceMessage1(DbEntity): pass

	@db.table(
		'logo',
		Column('id', DbTypes.Uuid, nullable=False),
		Column('fileName', DbTypes.VeryLongString, nullable=False),

		PrimaryKeyConstraint('id'),

	)
	class logo(DbEntity): pass


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
