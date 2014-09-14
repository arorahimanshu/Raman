import json
from .page2Component import Page2Component
import cherrypy


class RbacAuth(Page2Component):
    def __init__(self, parent, **kwargs):
        Page2Component.__init__(self, parent, **kwargs)

    #

    def handler(self, nextPart, requestPath):
        if nextPart == 'rbacAuth':
            return self._renderRbacAuth()
        elif nextPart == 'rbacAuthAction':
            return self._RbacAuthAction()
        #

    #

    def _renderRbacAuth(self):
        proxy, params = self.newProxy()

        params['externalCss'].append(
           self.server.appUrl('etc', 'page2', 'specific', 'css', 'rbacTable.css')
        )
        params['externalJs'].append(
            self.server.appUrl('etc', 'page2', 'specific', 'js', 'rbacTable.js')
        )
        params['externalCss'].append(
            self.server.appUrl('etc', 'page2', 'generic', 'css', 'basic.css')
        )

        db = self.app.component('dbHelper')
        self.data = db.returnRoleData(cherrypy.request.fitxData['organizationId'])

        return self._renderWithTabs(
            proxy, params,
            bodyContent=proxy.render('rbacTable.html', tableData=self.data),

            newTabTitle='Security Settings',
            url=self.server.appUrl('rbacAuth'),
        )

    #

    def _RbacAuthAction(self):
        formData = json.loads(cherrypy.request.params['formData'])

        if formData['Roles'] == self.data['roles']:
            print('same obj')

        for item in formData['Roles']:
            flag = True
            for role in self.data['roles']:
                if (role == item):
                    flag = False
                    break
            if (flag):
                db = self.app.component('dbHelper')
                #db.updateRolePermissions(item['name'], item['permissions'], formData['organizationId'])
                #db.updateRoleFacet(item['name'], item['users'], formData['organizationId'])
                db.updateRolePermissions(item['description'], item['permissions'], formData['organizationId'])
                db.updateRoleFacet(item['description'], item['users'], formData['organizationId'])
