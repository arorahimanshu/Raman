from component import Component
from geopy.distance import  vincenty

class GpsHelper(Component):

	def convertCoordinates(self, coordinates):
		pass


	def getDistance(self, coordinates):
		if len(coordinates) <= 1:
			return 0
		else:
			length = len (coordinates)
			distance = 0
			prevCoordinates = (coordinates[0].latitude, coordinates[0].longitude)
			for i in range (1, length):
				currentCoordinates = (coordinates[i].latitude, coordinates[i].longitude)
				distance += vincenty(prevCoordinates, currentCoordinates).kilometers
				prevCoordinates = currentCoordinates
			return distance

	def getReportData(self, coordinates):
		def nextDay(modePath, dayIndex):
			modePath.append([])
			modePath[dayIndex].append([])
			return 0

		def nextEntry(modePath, dayIndex, count, coordinate):
			modePath[dayIndex][count].append(coordinate)
			return count + 1

		def nextCount(modePath, dayIndex):
			modePath[dayIndex].append([])
			return 0

		timeHelp = self.app.component ('timeHelper')

		idleTime = 300				#in seconds
		stopTime = 1800				#in seconds

		prevMode = 'running'
		currentMode = prevMode
		dayIndex = 0

		runningPathInDay = []
		runCount = nextDay(runningPathInDay, dayIndex)

		stopPathInDay = []
		stopCount = nextDay(stopPathInDay, dayIndex)

		idlePathInDay = []
		idleCount = nextDay(idlePathInDay, dayIndex)

		length = len(coordinates)

		i=0
		while i < length-1:
			if coordinates[i].latitude == coordinates[i+1].latitude and coordinates[i].longitude == coordinates[i+1].longitude:
				currentMode = 'stopped'
				if i!=0 and prevMode == 'running':
					runCount = nextEntry(runningPathInDay, dayIndex, runCount, coordinates[i])
					runCount = nextCount(runningPathInDay,dayIndex)
				else:
					j = i
					while j < length-1:
						if (coordinates[j].latitude != coordinates[j+1].latitude) or (
							coordinates[j].longitude != coordinates[j+1].longitude) or (
							timeHelp.isDayDifferent (coordinates[j].timestamp, coordinates[j+1].timestamp)):
							break
						j += 1
					#
					timeDifference = timeHelp.getTimeDifferenceInSeconds(coordinates[i].timestamp, coordinates[j].timestamp)
					if timeDifference >= stopTime:
						currentMode = 'stopped'
						stoppedCoordinates = self.sliceCoordinates(coordinates, i, j)
						stopPathInDay[dayIndex][stopCount].extend(stoppedCoordinates)
						stopCount += len(stoppedCoordinates)
						i=j
					elif timeDifference >= idleTime:
						currentMode = 'idle'
						idleCoordinates = self.sliceCoordinates(coordinates, i, j)
						idlePathInDay[dayIndex][idleCount].extend(idleCoordinates)
						idleCount += len(idleCoordinates)
						i = j
					else:
						currentMode = 'running'
						runningPathInDay[dayIndex][runCount].append(coordinates[i])
			else:
				currentMode = 'running'
				if prevMode == 'stopped':
					stopPathInDay[dayIndex][stopCount].append(coordinates[i])
					stopCount += 1
				elif prevMode == 'idle':
					idlePathInDay[dayIndex][idleCount].append(coordinates[i])
					idleCount += 1
				runningPathInDay[dayIndex][runCount].append(coordinates[i])
			prevMode = currentMode

			if timeHelp.isDayDifferent (coordinates[i].timestamp, coordinates[i+1].timestamp):
				dayIndex += 1

				runCount = nextDay(runningPathInDay, dayIndex)
				stopCount = nextDay(stopPathInDay, dayIndex)
				idleCount = nextDay(idlePathInDay, dayIndex)

			#
			i += 1
		#
		return [
			runningPathInDay,
			stopPathInDay,
			idlePathInDay
		]
	#

	def sliceCoordinates(self, coordinates, i , j):
		return coordinates[i:j]
	#
