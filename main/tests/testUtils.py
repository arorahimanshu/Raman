from utils import Validator

from unittest import TestCase


def collectTests(collector, parent, app, logger):
	@collector
	class TestValidator(TestCase):
		def setUp(self):
			pass

		#

		def tearDown(self):
			pass

		#

		def test_validation(self):
			v = Validator({})
			self.assertEqual(v.errors, None)

			v = Validator({})
			name = v.required('name')

			self.assertSetEqual(
				set(v.errors.keys()),
				{'name'},
			)

			v = Validator({
			'name': 'abc',
			})
			name = v.required('name')
			name.validate('lengthRange', 5, 10)
			self.assertGreater(len(v.errors['name']), 0)

			v = Validator({
			'name': 'abc'
			})
			name = v.required('name')
			name.validate('or',
			              ('maxLength', 2),
			              ('value', 'allowed'),
			              ('errorMsg', 'TEST_ERROR'),
			)

			self.assertDictEqual(v.errors, {'name': 'TEST_ERROR'})

			v = Validator({})
			name = v.optional('name')
			name.validate('value', 'NAME')
			self.assertEqual(v.errors, None)

			def customValidator(n):
				if n > 10:
					return 'invalid'
				#

			#

			v = Validator({'x': 10})
			x = v.required('x')
			x.validate('custom', customValidator)
			self.assertEqual(v.errors, None)

			v = Validator({'x': 20})
			x = v.required('x')
			x.validate('custom', customValidator)
			self.assertDictEqual(v.errors, {'x': 'invalid'})

			v = Validator({'x': 10, 'y': 15, 'z': '20'})
			x = v.required('x')
			x.validate('inRange', 10, 20)
			y = v.required('y')
			y.validate('inRange', 10, 20)
			z = v.required('z')
			z.validate('inRange', 10, 20)
			self.assertDictEqual(v.errors, {'z': 'must be >=10 and <20'})

			v = Validator({'x': 'something', 'y': 'something else'})
			v.required('x')
			v.optional('y')
			v.optional('z')
			v.required('t')

			errors = v.errors

			self.assertNotIn('x', errors)
			self.assertNotIn('y', errors)
			self.assertNotIn('z', errors)
			self.assertIn('t', errors)

		#
		#

#

