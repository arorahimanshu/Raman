from component import Component
from datetime import timedelta, datetime
import time

class TimeHelper(Component):

	def getDateAndTime_add(self, gmtAdjust, gt=None):
		if gt == None:
			gt = self.getGMTDateAndTime()
		newTime = gt + timedelta(seconds=gmtAdjust)
		return newTime
	#

	def getDateAndTime_subtract(self, gmtAdjust, gt=None):
		if gt == None:
			gt = self.getGMTDateAndTime()
		newTime = gt - timedelta(seconds=gmtAdjust)
		return newTime
	#

	def getGMTDateAndTime(self):
		gmtime = time.gmtime()
		gt = datetime(gmtime.tm_year, gmtime.tm_mon, gmtime.tm_mday, gmtime.tm_hour, gmtime.tm_min, gmtime.tm_sec)
		return gt

	def getDateAndTime(self, year, mon, day, hour, min, sec):
		gt = datetime(year,mon,day,hour,min,sec)
		return gt

	def getTimeDifferenceInSeconds (self, timestamp1, timestamp2):
		timeDifference = self.getTimeDifference(timestamp1, timestamp2)
		difference = timeDifference.days * 24 * 3600 + timeDifference.seconds
		return difference
	#

	def isDayDifferent (self, timestamp1, timestamp2):
		if timestamp1.date() == timestamp2.date():
			return False
		else:
			return True

	def getTimeDifference(self, timestamp1, timestamp2):
		if timestamp2 >= timestamp1:
			timeDifference = timestamp2 - timestamp1
		else:
			timeDifference = timestamp1 - timestamp2
		return timeDifference