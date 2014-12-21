from component import Component
from email._header_value_parser import get_obs_local_part
from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
from datetime import timedelta

class GpsHelper(Component):
    def convertCoordinates(self, coordinates):
        pass

    def getLocation(self, coordinate):
        geoLocator = GoogleV3()
        location = geoLocator.reverse(str(coordinate.latitude) + ', ' + str(coordinate.longitude), exactly_one=True)
        #location = geoLocator.reverse('28.6000000000000014,	77.0300000000000011')
        return location.address
    #

    def getDistance(self, coordinates):
        if len(coordinates) <= 1:
            return 0
        else:
            length = len(coordinates)
            distance = 0
            prevCoordinates = (coordinates[0].latitude, coordinates[0].longitude)
            for i in range(1, length):
                currentCoordinates = (coordinates[i].latitude, coordinates[i].longitude)
                distance += vincenty(prevCoordinates, currentCoordinates).kilometers
                prevCoordinates = currentCoordinates
            return distance

    def separateRecords(self, coordinates, gmtAdjust = None):

        # initialize dayIndex-th day
        def nextDay(modePath, newDayIndex):
            modePath.append([])
            modePath[newDayIndex].append([])
            return 0

        # append coordinates to current count
        def nextEntries(modePath, dayIndex, count, coordinates):
            modePath[dayIndex][count].extend(coordinates)
            return count

        #initialize new Count on dayIndex-th day
        def nextCount(modePath, dayIndex, oldCount):
            modePath[dayIndex].append([])
            return oldCount + 1

        timeHelp = self.app.component('timeHelper')

        #TODO: change these variables to enum
        idleTime = 300  #in seconds
        stopTime = 1800  #in seconds
        inactiveTime = 3600  #in seconds

        prevMode = 'running'
        currentMode = prevMode
        dayIndex = 0

        runningPathInDay = []
        runCount = nextDay(runningPathInDay, dayIndex)

        stopPathInDay = []
        stopCount = nextDay(stopPathInDay, dayIndex)

        idlePathInDay = []
        idleCount = nextDay(idlePathInDay, dayIndex)

        inactivePathInDay = []
        inactiveCount = nextDay(inactivePathInDay, dayIndex)

        length = len(coordinates)

        i = 0
        while i < length - 1:
            flag1 = False
            if coordinates[i].speed == 0:
                currentMode = 'stopped'
                '''
                if i != 0 and prevMode == 'running':
                    runCount = nextEntries(runningPathInDay, dayIndex, runCount, [coordinates[i]])
                    runCount = nextCount(runningPathInDay, dayIndex, runCount)
                '''
                j = i
                while j < length - 1:
                    if coordinates[j].speed != 0:
                        break
                    if timeHelp.isDayDifferent(coordinates[j].timestamp, coordinates[j + 1].timestamp, gmtAdjust):
                        flag1 = True
                        j += 1
                        break
                    j += 1
                #
                timeDifference = timeHelp.getTimeDifferenceInSeconds(coordinates[i].timestamp, coordinates[j].timestamp)
                slicedCoordinates = self.sliceCoordinates(coordinates, i, j)
                if timeDifference >= inactiveTime:
                    currentMode = 'inactive'
                    inactiveCount = nextEntries(inactivePathInDay, dayIndex, inactiveCount, slicedCoordinates)
                    inactiveCount = nextCount(inactivePathInDay, dayIndex, inactiveCount)
                    i = j - 1
                elif timeDifference >= stopTime:
                    currentMode = 'stopped'
                    stopCount = nextEntries(stopPathInDay, dayIndex, stopCount, slicedCoordinates)
                    stopCount = nextCount(stopPathInDay, dayIndex, stopCount)
                    i = j - 1
                elif timeDifference >= idleTime or flag1 == True:
                    currentMode = 'idle'
                    idleCount = nextEntries(idlePathInDay, dayIndex, idleCount, slicedCoordinates)
                    idleCount = nextCount(idlePathInDay, dayIndex, idleCount)
                    i = j - 1
                else:
                    currentMode = 'running'
                    #runningPathInDay[dayIndex][runCount].append(coordinates[i])
                    runCount = nextEntries(runningPathInDay, dayIndex, runCount, slicedCoordinates)
            else:
                currentMode = 'running'
                if prevMode != 'running':
                    runCount = nextCount(runningPathInDay, dayIndex, runCount)
                '''
                if prevMode == 'inactive':
                    inactiveCount = nextEntries(inactivePathInDay, dayIndex, inactiveCount-1, [coordinates[i]])
                    inactiveCount = nextCount(inactivePathInDay, dayIndex, inactiveCount)
                elif prevMode == 'stopped':
                    stopCount = nextEntries(stopPathInDay, dayIndex, stopCount-1, [coordinates[i]])
                    stopCount = nextCount(stopPathInDay, dayIndex, stopCount)
                elif prevMode == 'idle':
                    idleCount = nextEntries(idlePathInDay, dayIndex, idleCount-1, [coordinates[i]])
                    idleCount = nextCount(idlePathInDay, dayIndex, idleCount)
                '''
                runCount = nextEntries(runningPathInDay, dayIndex, runCount, [coordinates[i]])
            prevMode = currentMode

            if flag1 == True or timeHelp.isDayDifferent(coordinates[i].timestamp, coordinates[i + 1].timestamp, gmtAdjust):
                dayIndex += 1

                runCount = nextDay(runningPathInDay, dayIndex)
                stopCount = nextDay(stopPathInDay, dayIndex)
                idleCount = nextDay(idlePathInDay, dayIndex)
                inactiveCount = nextDay(inactivePathInDay, dayIndex)

            #
            i += 1
        #
        return {
            'running': runningPathInDay,
            'stopped': stopPathInDay,
            'idle': idlePathInDay,
            'inactive': inactivePathInDay
        }

    #

    def sliceCoordinates(self, coordinates, i, j):
        return coordinates[i:j]

    #

    def getAvgSpeed(self, runningData, totalRunningDistance):
        timeHelp = self.app.component('timeHelper')
        seconds = 0
        for day in runningData:
            for count in day:
                if (len(count) >= 1):
                    seconds += timeHelp.getTimeDifferenceInSeconds(count[0].timestamp, count[len(count) - 1].timestamp)
        if seconds == 0:
            return 0
        else:
            return totalRunningDistance / seconds * 3600

    #

    def getMaxSpeed(self, runningData):
        maxSpeed = 0
        for day in runningData:
            for count in day:
                for data in count:
                    speed = data.speed
                    if maxSpeed < speed:
                        maxSpeed = speed
        return maxSpeed
    #

    def noneCheck(self, field, value):
        field = self.fieldValueCheck(field, None, value)
        return field

    def fieldValueCheck(self, field, value, replacement):
        if field == value:
            field = replacement
        return field

    def makeReport(self, coordinates, gmtAdjust = None):
        def getDurationAndCount(data):
            timesCount = 0
            totalDuration = None
            for day in data:
                for count in day:
                    if (len(count) >= 1):
                        timesCount += 1
                        duration = timeHelp.getTimeDifference(count[0].timestamp, count[len(count) - 1].timestamp)
                        if totalDuration == None:
                            totalDuration = duration
                        else:
                            totalDuration += duration
            return (totalDuration, timesCount)

        # /getDurationAndCount

        timeHelp = self.app.component('timeHelper')
        data = self.separateRecords(coordinates, gmtAdjust)

        running = data['running']
        stopped = data['stopped']
        idle = data['idle']
        inactive = data['inactive']

        totalRunningDistance = 0

        startLocation = self.getLocation(coordinates[0])
        endLocation = self.getLocation(coordinates[len(coordinates) - 1])

        for day in running:
            for count in day:
                totalRunningDistance += self.getDistance(count)
        #

        (totalRunningDuration, totalRunCount) = getDurationAndCount(running)
        (totalIdleDuration, totalIdleCount) = getDurationAndCount(idle)
        (totalInactiveDuration, totalInactiveCount) = getDurationAndCount(inactive)
        (totalStopDuration, totalStopCount) = getDurationAndCount(stopped)

        if totalRunCount == 0:
            avgDuration = None
        else:
            #avgDuration = totalRunningDuration / totalRunCount
            avgDuration = totalRunningDuration /len(data['running'])
            avgDuration = timedelta(days=avgDuration.days, seconds=avgDuration.seconds)

        avgSpeed = self.getAvgSpeed(running, totalRunningDistance)
        maxSpeed = self.getMaxSpeed(running)

        totalRunningDuration = self.noneCheck(totalRunningDuration, '0:00:00')
        totalIdleDuration = self.noneCheck(totalIdleDuration, '0:00:00')
        totalStopDuration = self.noneCheck(totalStopDuration, '0:00:00')
        totalInactiveDuration = self.noneCheck(totalInactiveDuration, '0:00:00')

        avgDuration = self.noneCheck(avgDuration, '0:00:00')

        return {
            'startLocation': startLocation,
            'totalRunningDistance': totalRunningDistance,
            'totalRunningDuration': totalRunningDuration,
            'totalIdleDuration': totalIdleDuration,
            'totalStopDuration': totalStopDuration,
            'totalInactiveDuration': totalInactiveDuration,
            'avgDuration': avgDuration,
            'avgSpeed': avgSpeed,
            'maxSpeed': maxSpeed,
            'timesStopped': totalStopCount,
            'timesIdle': totalIdleCount,
            'alert': '0',
            'endLocation': endLocation,
        }
    #