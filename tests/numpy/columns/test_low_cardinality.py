try:
    import numpy as np
except ImportError:
    np = None

from tests.numpy.testcase import NumpyBaseTestCase

from datetime import date, timedelta
# from decimal import Decimal


class LowCardinalityTestCase(NumpyBaseTestCase):
    required_server_version = (19, 3, 3)
    stable_support_version = (19, 9, 2)

    def setUp(self):
        super(LowCardinalityTestCase, self).setUp()
        # TODO: remove common client when inserts will be implemented
        self.common_client = self._create_client()

    def tearDown(self):
        self.common_client.disconnect()
        super(LowCardinalityTestCase, self).tearDown()

    def cli_client_kwargs(self):
        if self.server_version >= self.stable_support_version:
            return {'allow_suspicious_low_cardinality_types': 1}

    def test_uint8(self):
        with self.create_table('a LowCardinality(UInt8)'):
            data = [(x, ) for x in range(255)]
            self.common_client.execute('INSERT INTO test (a) VALUES', data)

            query = 'SELECT * FROM test'
            inserted = self.emit_cli(query)
            self.assertEqual(
                inserted,
                '\n'.join(str(x[0]) for x in data) + '\n'
            )

            inserted = self.client.execute(query, columnar=True)
            self.assertArraysEqual(inserted[0], np.array(range(255)))

    def test_int8(self):
        with self.create_table('a LowCardinality(Int8)'):
            data = [(x - 127, ) for x in range(255)]
            self.common_client.execute('INSERT INTO test (a) VALUES', data)

            query = 'SELECT * FROM test'
            inserted = self.emit_cli(query)
            self.assertEqual(
                inserted,
                '\n'.join(str(x[0]) for x in data) + '\n'

            )

            inserted = self.client.execute(query, columnar=True)
            self.assertArraysEqual(
                inserted[0], np.array([x - 127 for x in range(255)])
            )

    # def test_nullable_int8(self):
    #     with self.create_table('a LowCardinality(Nullable(Int8))'):
    #         data = [(None, ), (-1, ), (0, ), (1, ), (None, )]
    #         self.client.execute('INSERT INTO test (a) VALUES', data)
    #
    #         query = 'SELECT * FROM test'
    #         inserted = self.emit_cli(query)
    #         self.assertEqual(inserted, '\\N\n-1\n0\n1\n\\N\n')
    #
    #         inserted = self.client.execute(query)
    #         self.assertEqual(inserted, data)

    def test_date(self):
        with self.create_table('a LowCardinality(Date)'):
            start = date(1970, 1, 1)
            data = [(start + timedelta(x), ) for x in range(300)]
            self.common_client.execute('INSERT INTO test (a) VALUES', data)

            query = 'SELECT * FROM test'
            inserted = self.client.execute(query, columnar=True)
            self.assertArraysEqual(
                inserted[0], np.array(list(range(300)), dtype='datetime64[D]')
            )

    def test_float(self):
        with self.create_table('a LowCardinality(Float)'):
            data = [(float(x),) for x in range(300)]
            self.common_client.execute('INSERT INTO test (a) VALUES', data)

            query = 'SELECT * FROM test'
            inserted = self.client.execute(query, columnar=True)
            self.assertArraysEqual(
                inserted[0], np.array([float(x) for x in range(300)])
            )

    # def test_decimal(self):
    #     with self.create_table('a LowCardinality(Float)'):
    #         data = [(Decimal(x),) for x in range(300)]
    #         self.client.execute('INSERT INTO test (a) VALUES', data)
    #
    #         query = 'SELECT * FROM test'
    #         inserted = self.client.execute(query)
    #         self.assertEqual(inserted, data)
    #
    # def test_array(self):
    #     with self.create_table('a Array(LowCardinality(Int16))'):
    #         data = [([100, 500], )]
    #         self.client.execute('INSERT INTO test (a) VALUES', data)
    #
    #         query = 'SELECT * FROM test'
    #         inserted = self.emit_cli(query)
    #         self.assertEqual(inserted, '[100,500]\n')
    #
    #         inserted = self.client.execute(query)
    #         self.assertEqual(inserted, data)
    #
    # def test_empty_array(self):
    #     with self.create_table('a Array(LowCardinality(Int16))'):
    #         data = [([], )]
    #         self.client.execute('INSERT INTO test (a) VALUES', data)
    #
    #         query = 'SELECT * FROM test'
    #         inserted = self.emit_cli(query)
    #         self.assertEqual(inserted, '[]\n')
    #
    #         inserted = self.client.execute(query)
    #         self.assertEqual(inserted, data)
    #
    def test_string(self):
        with self.create_table('a LowCardinality(String)'):
            data = [
                ('test', ), ('low', ), ('cardinality', ),
                ('test', ), ('test', ), ('', )
            ]
            self.common_client.execute('INSERT INTO test (a) VALUES', data)

            query = 'SELECT * FROM test'
            inserted = self.emit_cli(query)
            self.assertEqual(
                inserted,
                'test\nlow\ncardinality\ntest\ntest\n\n'
            )

            inserted = self.client.execute(query, columnar=True)
            self.assertArraysEqual(inserted[0], list(list(zip(*data))[0]))

    # def test_fixed_string(self):
    #     with self.create_table('a LowCardinality(FixedString(12))'):
    #         data = [
    #             ('test', ), ('low', ), ('cardinality', ),
    #             ('test', ), ('test', ), ('', )
    #         ]
    #         self.client.execute('INSERT INTO test (a) VALUES', data)
    #
    #         query = 'SELECT * FROM test'
    #         inserted = self.emit_cli(query)
    #         self.assertEqual(
    #             inserted,
    #             'test\\0\\0\\0\\0\\0\\0\\0\\0\n'
    #             'low\\0\\0\\0\\0\\0\\0\\0\\0\\0\n'
    #             'cardinality\\0\n'
    #             'test\\0\\0\\0\\0\\0\\0\\0\\0\n'
    #             'test\\0\\0\\0\\0\\0\\0\\0\\0\n'
    #             '\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\n'
    #         )
    #
    #         inserted = self.client.execute(query)
    #         self.assertEqual(inserted, data)
    #
    # def test_nullable_string(self):
    #     with self.create_table('a LowCardinality(Nullable(String))'):
    #         data = [
    #             ('test', ), ('', ), (None, )
    #         ]
    #         self.client.execute('INSERT INTO test (a) VALUES', data)
    #
    #         query = 'SELECT * FROM test'
    #         inserted = self.emit_cli(query)
    #         self.assertEqual(
    #             inserted,
    #             'test\n\n\\N\n'
    #         )
    #
    #         inserted = self.client.execute(query)
    #         self.assertEqual(inserted, data)