from appConfig import AppConfig
from testComponent import Mock
import utils

from unittest import TestCase
import random
import itertools


class Fixture:
	def __init__(self, app, testComponent):
		self._app = app
		self._parent = testComponent.fixture('basic1',
		                                     config={
		                                     'basic1.superuser.username': 'superuser',
		                                     'basic1.superuser.password': 'superuser',
		                                     }
		)

	#

	@property
	def app(self): return self._app

	def setUp(self):
		self._parent.setUp()

	#

	def tearDown(self):
		self._parent.tearDown()

	#


#

def collectTests(collector, parent, app, logger):
	@collector
	class TestSuperuser(TestCase):
		def setUp(self):
			self.fixture = Fixture(app, parent)
			self.fixture.setUp()

		#

		def tearDown(self):
			self.fixture.tearDown()

		#

		def test_loginLogout(self):
			userManager = app.component('userManager')
			username = 'superuser'
			password = 'superuser'
			uid = utils.newUuid()

			userManager.attemptLogin(username, uid, password)
			self.assertTrue(userManager.isLoggedIn(username, uid))

			with self.assertRaises(userManager.NotLoggedIn):
				userManager.logout(username, utils.newUuid())
			#

			userManager.logout(username, uid)
			self.assertFalse(userManager.isLoggedIn(username, uid))

		#

		def test_organization(self):
			userManager = app.component('userManager')
			username = 'superuser'
			password = 'superuser'
			uid = utils.newUuid()

			userManager.attemptLogin(username, uid, password)
			worker = userManager.worker(username, uid)
			organizations = worker.organizations()

			self.assertSetEqual(organizations, {AppConfig.AdminOrganization, })

		#

	#

	@collector
	class TestGeneralUser(TestCase):

		def setUp(self):
			self.fixture = Fixture(app, parent)
			self.fixture.setUp()

			db = app.component('dbManager')
			with db.session() as session:
				adminOrganization = session.query(db.Organization).filter_by(
					name=AppConfig.AdminOrganization
				).one()

				org = Mock('org')
				dbOrg = db.Organization.newFromParams({
				'entity': db.Entity.newUnique(),
				'parent': adminOrganization,
				'name': str(org),
				})
				session.add(dbOrg)

				user = Mock('user')
				dbUser = db.User.newFromParams({
				'entity': db.Entity.newUnique(),
				'username': str(user.username),
				'rawPassword': str(user.password),
				})
				session.add(dbUser)

				facet = db.Facet.newFromParams({
				'user': dbUser,
				'organization': dbOrg,
				'preference': 0,
				})
				session.add(facet)

				roles = (org / 'role') * 3
				dbRoles = []
				for role in roles:
					dbRole = db.Role.newFromParams({
					'organization': dbOrg,
					'name': str(role.name),
					})
					session.add(dbRole)
					dbRoles.append(dbRole)
				#

				loginPermission = db.Permission.newFromParams({
				'organization': dbOrg,
				'name': db.Permissions.Login,
				})
				session.add(loginPermission)

				for dbRole in dbRoles:
					session.add(db.Permission_Role.newFromParams({
					'permission': loginPermission,
					'role': dbRole,
					}))
				#

				perms = (org / 'perm') * 3
				dbPerms = []
				for perm in perms:
					dbPerm = db.Permission.newFromParams({
					'organization': dbOrg,
					'name': str(perm.name),
					})
					session.add(dbPerm)
					dbPerms.append(dbPerm)
				#

				permission_role = [
					'001',
					'110',
					'010',
				]
				for permIndex, roleIndex in itertools.product(
						range(len(perms)), range(len(roles))
				):
					if permission_role[permIndex][roleIndex] == '1':
						dbPermission_Role = db.Permission_Role.newFromParams({
						'permission': dbPerms[permIndex],
						'role': dbRoles[roleIndex],
						})
						session.add(dbPermission_Role)
					#
				#

				facet_role = 1
				dbFacet_Role = db.Facet_Role.newFromParams({
				'role': dbRoles[facet_role],
				'facet': facet,
				})
				session.add(dbFacet_Role)
			# /db session

		#

		def tearDown(self):
			self.fixture.tearDown()

		#

		def test_checkPermissions(self):
			db = app.component('dbManager')
			userManager = app.component('userManager')
			sessionId = utils.newUuid()

			with app.requestLock():
				organizationId = userManager.attemptLogin('user.username', sessionId, 'user.password')
			#

			with app.requestLock():
				worker = userManager.worker('user.username', sessionId)
				perms = set(worker.permissions(organizationId))
			#

			self.assertSetEqual(
				perms,
				{'org/perm1.name', 'org/perm2.name', db.Permissions.Login},
			)

		#
		#

#

