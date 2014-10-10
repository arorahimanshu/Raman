import json
from .page2Component import Page2Component
import cherrypy


class SecuritySettings(Page2Component):
    def __init__(self, parent, **kwargs):
        Page2Component.__init__(self, parent, **kwargs)

    #

    def handler(self, nextPart, requestPath):
        if nextPart == 'securitySettings':
            return self._securitySettings(requestPath)
        elif nextPart == 'securitySettingsAction':
            return self._securitySettingsAction(requestPath)
        elif nextPart == 'userSecuritySettings':
            return self._userSecuritySettings(requestPath)
        elif nextPart == 'roleSecuritySettings':
            return self._roleDetails(requestPath)
        #

    #

    def _securitySettings(self, requestPath):
        proxy, params = self.newProxy()

        params['externalCss'].append(
           self.server.appUrl('etc', 'page2', 'specific', 'css', 'securitySettings.css')
        )
        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'js', 'securitySettings.js')
        )
        params['externalCss'].append(
            self.server.appUrl('etc', 'page2', 'generic', 'css', 'basic.css')
        )

        db = self.app.component('dbHelper')
        self.data = db.returnRoleData(cherrypy.request.fitxData['organizationId'])

        return self._renderWithTabs(
            proxy, params,
            bodyContent=proxy.render('securitySettingsForm.html', tableData=self.data),

            newTabTitle='Security Settings',
            url=self.server.appUrl('securitySettings'),
        )

    #

    def _securitySettingsAction(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])

        roleData = self.data

        users = formData['users']

        db = self.app.component('dbHelper')

        for user in users:
            roles = users[user]
            db.updateRoleFacetForUser(user, roles, formData['organizationId'])

        return self.jsonSuccess()
    #

    def _userSecuritySettings(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])

        data = {}
        user = formData
        roleData = self.data
        for role in roleData['roles']:
            if user in role['users']:
                data[role['name']] = role['permissions']
        return self.jsonSuccess(data)
    #

    def _roleDetails(self, requestPath):
        formData = json.loads(cherrypy.request.params['formData'])

        roleList = formData
        securityData = self.data
        data = []

        for role in securityData['roles']:
            if role['name'] in roleList:
                for permission in role['permissions']:
                    if permission not in data:
                        data.append(permission)

        return self.jsonSuccess(data)