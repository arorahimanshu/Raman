from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class TravelReport(Page2Component):
    def __init__(self, parent, **kwargs):
        Page2Component.__init__(self, parent, **kwargs)


    #

    def handler(self, nextPart, requestPath):
        if nextPart == 'newTravelReportForm':
            return self._newTravelReportForm(requestPath)
        elif nextPart == 'newTravelReportFormAction':
            return self._newTravelReportFormAction(requestPath)
        elif nextPart == 'travelReportVehicleListNested':
            return self._travelReportVehicleListNested(requestPath)
        #

    #



    def _newTravelReportForm(self, requestPath):
        proxy, params = self.newProxy()

        params['externalCss'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'css', 'travelReportForm.css')
        )

        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'js', 'travelReportForm.js')
        )

        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'generic', 'js', 'flexigrid.js')
        )
        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'generic', 'js', 'flexigrid.pack.js')
        )
        params['externalCss'].append(
            self.server.appUrl('etc', 'page2', 'generic', 'css', 'flexigrid.pack.css')
        )
        params['externalCss'].append(
            self.server.appUrl('etc', 'page2', 'generic', 'css', 'flexigrid.css')
        )

        self.classData = ['S.No.', 'Company', 'Branch', 'Vehicle Information', 'Driver Information', 'Start Location',
                          'Total Running(km)', 'Total Running Duration', 'Total Idle Duration', 'Total Stop Duration',
                          'Total Inactive Duration', 'Avg Duration', 'Avg Speed', 'Max Speed', 'Times Stopped',
                          'Times Idle', 'Alert', 'End Location']

        primaryOrganizationId = None
        with self.server.session() as serverSession:
            primaryOrganizationId = serverSession['primaryOrganizationId']
        dbHelp = self.app.component('dbHelper')
        vehiclesListNested = self._travelReportVehicleListNested(requestPath)
        return self._renderWithTabs(
            proxy, params,
            bodyContent=proxy.render('travelReportForm.html', classdata=self.classData,
                                     vehicleListNested=json.loads(vehiclesListNested),
                                     vehicles=json.dumps(vehiclesListNested)),
            newTabTitle='Travel Report',
            url=requestPath.allPrevious(),
        )

    #


    def _newTravelReportFormValidate(self, formData):
        pass

    #

    def _newTravelReportFormAction(self, requestPath):

        formData = json.loads(cherrypy.request.params['formData'])

        gmtAdjust = formData['gmtAdjust']
        fromDate = formData['fromDate']
        toDate = formData['toDate']

        orgId = formData['company']
        branchId = formData['branch']
        vehicleGroupId = formData['vehicleGroup']

        db = self.app.component('dbManager')
        dbHelp = self.app.component('dbHelper')
        vehiclesListNested = json.loads(self._travelReportVehicleListNested(requestPath))
        vehicleIds = dbHelp.filterVehicles(vehiclesListNested, orgId, branchId, vehicleGroupId)

        timeHelp = self.app.component('timeHelper')
        time = timeHelp.getDateAndTime(fromDate[0], fromDate[1], fromDate[2], 0, 0, 0)
        fromTime = timeHelp.getDateAndTime_subtract(gmtAdjust, time)

        time = timeHelp.getDateAndTime(toDate[0], toDate[1], toDate[2], 23, 59, 59)
        toTime = timeHelp.getDateAndTime_subtract(gmtAdjust, time)

        rows = []
        for id in vehicleIds:
            rawCoordinates = dbHelp.getRawCoordinatesForDeviceBetween(id, fromTime, toTime)
            rawCoordinates = rawCoordinates.order_by(db.gpsDeviceMessage1.timestamp)
            report = self._makeTravelReport(rawCoordinates.all())
            vehicleData = dbHelp.getVehicleDetails(vehiclesListNested, id)
            # data = gpsHelp.getTravelReport (rawCoordinates.all())
            #data = self._dummyFunction(id)
            row = {}
            row['cell'] = [len(rows) + 1]
            row['cell'].append(vehicleData['company'])
            row['cell'].append(vehicleData['branch'])
            row['cell'].append(vehicleData['vehicleInfo'])
            row['cell'].append(vehicleData['driverInfo'])
            row['cell'].append(report['startLocation'])
            row['cell'].append('{0:.2f}'.format(report['totalRunningDistance']))
            row['cell'].append(str(report['totalRunningDuration']))
            row['cell'].append(str(report['totalIdleDuration']))
            row['cell'].append(str(report['totalStopDuration']))
            row['cell'].append(str(report['totalInactiveDuration']))
            row['cell'].append(str(report['avgDuration']))
            row['cell'].append('{0:.2f}'.format(report['avgSpeed']))
            row['cell'].append('{0:.2f}'.format(report['maxSpeed']))
            row['cell'].append(report['timesStopped'])
            row['cell'].append(report['timesIdle'])
            row['cell'].append(report['alert'])
            row['cell'].append(report['endLocation'])
            rows.append(row)
            t = 0

        pageNo = int((cherrypy.request.params).get('pageNo', '1'))
        if 'pageNo' not in cherrypy.request.params:
            self.numOfObj = 10
        if 'rp' in cherrypy.request.params and 'pageNo' in cherrypy.request.params:
            self.numOfObj = int(cherrypy.request.params['rp'])

        rows = dbHelp.getSlicedData(rows, pageNo, self.numOfObj)

        data = {
            'classData': self.classData,
            'sendData': rows,
        }

        if data != None:
            return self.jsonSuccess(data)
        else:
            return self.jsonFailure('No Data Found')

        #

    #

    def _travelReportVehicleListNested(self, requestPath):
        primaryOrganizationId = None
        with self.server.session() as serverSession:
            primaryOrganizationId = serverSession['primaryOrganizationId']
        dbHelp = self.app.component('dbHelper')
        vehiclesListNested = json.dumps(dbHelp.getVehiclesListNested(primaryOrganizationId))
        return vehiclesListNested

    #

    def _dummyFunction(self, id):
        row = {}
        row['cell'] = [1]
        for i in range(0, 17):
            row['cell'].append(id)
        return row

    def _makeTravelReport(self, coordinates):
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

        gpsHelp = self.app.component('gpsHelper')
        timeHelp = self.app.component('timeHelper')
        data = gpsHelp.separateRecords(coordinates)

        running = data['running']
        stopped = data['stopped']
        idle = data['idle']
        inactive = data['inactive']

        totalRunningDistance = 0

        startLocation = gpsHelp.getLocation(coordinates[0])
        endLocation = gpsHelp.getLocation(coordinates[len(coordinates) - 1])

        for day in running:
            for count in day:
                totalRunningDistance += gpsHelp.getDistance(count)
        #

        (totalRunningDuration, totalRunCount) = getDurationAndCount(running)
        (totalIdleDuration, totalIdleCount) = getDurationAndCount(idle)
        (totalInactiveDuration, totalInactiveCount) = getDurationAndCount(inactive)
        (totalStopDuration, totalStopCount) = getDurationAndCount(stopped)

        if totalRunCount == 0:
            avgDuration = None
        else:
            avgDuration = totalRunningDuration / totalRunCount

        avgSpeed = gpsHelp.getAvgSpeed(running, totalRunningDistance)
        maxSpeed = gpsHelp.getMaxSpeed(running)

        totalRunningDuration = gpsHelp.noneCheck(totalRunningDuration, '0:00:00')
        totalIdleDuration = gpsHelp.noneCheck(totalIdleDuration, '0:00:00')
        totalStopDuration = gpsHelp.noneCheck(totalStopDuration, '0:00:00')
        totalInactiveDuration = gpsHelp.noneCheck(totalInactiveDuration, '0:00:00')

        avgDuration = gpsHelp.noneCheck(avgDuration, '0:00:00')

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