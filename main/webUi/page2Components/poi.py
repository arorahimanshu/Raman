from .page2Component import Page2Component
from appConfig import AppConfig
from utils import Validator
import cherrypy
import json


class Poi(Page2Component):
    def __init__(self, parent, **kwargs):
        Page2Component.__init__(self, parent, **kwargs)

    #

    def handler(self, nextPart, requestPath):
        if nextPart == 'newPoiForm':
            return self._newPoiForm(requestPath)
        elif nextPart == 'newPoiFormAction':
            return self._newPoiFormAction(requestPath)
        elif nextPart == 'getPoiData':
            return self.getPoiData(requestPath)
        elif nextPart == 'generateReport':
            return self.generateReport(requestPath)
        #

    #

    def generateReport(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])
        db = self.app.component('dbHelper')
        # TODO: Himanshu When done with branch of organization just pass the company name and branch too here
        with self.server.session() as session:
            poidata = db.returnPoiReport(session['userId'], formData['reportAddressCategory'])

        print(poidata)

        return self.jsonSuccess(poidata)


    def getPoiData(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])
        db = self.app.component('dbHelper')
        # todo:db query for poi list
        # return self.jsonSuccess(db.returnPoiList(self.userId, formData['userEnteredString']['vehicle']))
        return self.jsonSuccess("done")


    def _newPoiForm(self, requestPath):
        primaryOrganizationId = None
        with self.server.session() as session:
            self.username = session['username']
            self.userId = session['userId']
            primaryOrganizationId = session['primaryOrganizationId']
        #
        proxy, params = self.newProxy()
        params['externalCss'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'css', 'poiForm.css')
        )
        params['externalJs'].append('http://maps.googleapis.com/maps/api/js?v=3.exp')
        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'js', 'poiForm.js')
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

        db = self.app.component('dbHelper')
        vehicleList = db.returnVehicleList(self.userId)

        addresscatfile = open('./dataModel/addCategory.json')
        addressList = json.load(addresscatfile)

        orgList = db.returnOrgList(primaryOrganizationId)
        branchList2 = []
        companyList2 = orgList
        vehicleGroupList2 = []
        vehicleList2 = []
        for org in orgList:
            if org['value'] != primaryOrganizationId:
                branchList = db.returnBranchListForOrg(org['value'])
                branchList2.extend(branchList)
                for branch in branchList:
                    vehicleGroupList = db.returnVehicleGroupListForBranch(branch['value'])
                    vehicleGroupList2.extend(vehicleGroupList)
                    for vehicleGroup in vehicleGroupList:
                        vehicleList = db.returnVehicleListForVehicleGroup(vehicleGroup['value'])
            vehicleList2.extend(vehicleList)
        classdata = ['Company', 'Branch', 'Poi Name', 'Address Category', 'Street', 'City', 'State']
        return self._renderWithTabs(
            proxy, params,
            bodyContent=proxy.render('poiForm.html', vehicleList=vehicleList2, addressList=addressList,
                                     branchList=branchList2, companyList=companyList2, vehicleGroupList=vehicleGroupList2,
                                     classdata=classdata),
            newTabTitle='Add POI',
            url=requestPath.allPrevious(),
        )

        #


    def _newPoiFormValidate(self, formData):
        pass


    def _newPoiFormAction(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])
        print(formData)
        errors = self._newPoiFormValidate(formData)
        if errors:
            return self.jsonFailure('validation failed', errors=errors)
        #

        db = self.app.component('dbManager')

        with db.session() as session:
            entity = db.Entity.newUnique()
            session.add(entity)

            poi_data = db.Gps_Poi_Info.newFromParams({
                'Poi_Id': entity.id,
                'User_Id': self.userId,
                'Vehicle_Id': formData['vehicleID'],
                'Poi_Name': formData['poiplaceName'],
                'Poi_Latitude': formData['latitude'],
                'Poi_Longitude': formData['longitude'],
                'Category': formData['addressCategory']
            })
            session.add(poi_data)

            address = formData['street'] + ";" + formData['state'] + ";" + formData['city']

            session.add(db.Info.newFromParams({
                'id': db.Entity.newUuid(),
                'entity_id': entity.id,
                'enumType': db.Info.Type.Address,
                'preference': 0,
                'data': address,
            }))

        return self.jsonSuccess('Poi Successfully Saved')


    #
#