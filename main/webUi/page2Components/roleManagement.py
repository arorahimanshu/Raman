import cherrypy
from .page2Component import Page2Component
import json


class RoleManagement(Page2Component):
    def __init__(self, parent, **kwargs):
        Page2Component.__init__(self, parent, **kwargs)
    #

    def handler(self, nextPart, requestPath):
        if nextPart == 'newRoleManagementForm':
            return self._newRoleManagementForm(requestPath)
        elif nextPart == 'newRoleManagementFormAction':
            return self._newRoleManagementFormAction(requestPath)
        elif nextPart == 'addRole':
            return self._addRole(requestPath)
        elif nextPart == 'editRole':
            return self._editRole(requestPath)
        elif nextPart == 'delRole':
            return self._delRole(requestPath)
        #
    #

    def _newRoleManagementForm(self, requestPath):
        proxy, params = self.newProxy()

        params['externalCss'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'css', 'roleManagement.css')
        )
        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'js', 'roleManagement.js')
        )
        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'js', 'flexiBasic.js')
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

        params['config'].update({
            'roleManagementFormAction': requestPath.allPrevious(
                ignore=1,
                additional=['roleManagementFormAction'],
            )
        })

        self.classData = ['S.No', 'Role Name', 'Permissions']

        orgId = cherrypy.request.fitxData['organizationId']

        dbHelp = self.app.component('dbHelper')
        roleData = dbHelp.returnRoleData(orgId)
        permissions = roleData['permissions']

        return self._renderWithTabs(
            proxy, params,
            bodyContent=proxy.render('roleManagementForm.html', classdata=self.classData, permissions=permissions),
            newTabTitle='Role Management',
            url=requestPath.allPrevious(),
        )

    #

    def _newRoleManagementFormAction(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])
        pageNo = int(formData.get('pageNo', '1'))
        numOfObj = int(formData.get('rp', '10'))

        orgId = cherrypy.request.fitxData['organizationId']

        dbHelp = self.app.component('dbHelper')
        roleData = dbHelp.returnRoleData(orgId)

        roles = roleData['roles']

        rows = []
        for role in roles:
            row = {'cell': [len(rows) + 1]}
            row['cell'].append(role['name'])
            permissions = ''
            for permission in role['permissions']:
                permissions = permissions + permission + ', '
            permissions = permissions[:len(permissions)-2]
            row['cell'].append(permissions)
            rows.append(row)

        rows = dbHelp.getSlicedData(rows, pageNo, numOfObj)

        data = {
            'sendData': rows,
            'classData': self.classData
        }

        return self.jsonSuccess(data)
    #

    def _roleManagementValidation(self):
        pass

    def _addRole(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])
        roleName = formData['name']
        permissions = formData['permissions']
        orgId = formData['organizationId']
        db = self.app.component('dbHelper')
        db.createNewRole(roleName, orgId)
        db.updateRolePermissions(roleName, permissions, orgId)
        return self.jsonSuccess()
    #

    def _editRole(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])
        roleName = formData['name']
        oldName = formData['oldName']
        permissions = formData['permissions']
        orgId = formData['organizationId']
        db = self.app.component('dbHelper')
        if roleName != oldName:
            db.deleteRole(oldName)
            db.createNewRole(roleName, orgId)
        #
        db.updateRolePermissions(roleName, permissions, orgId)
        return self.jsonSuccess()
    #

    def _delRole(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])
        db = self.app.component('dbHelper')

        roleName = formData['name']

        db.deleteRole(roleName)

        return self.jsonSuccess()
    #