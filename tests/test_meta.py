import unittest
import io
import os

from c64os_util import ApplicationMetadata
from util import cmp_buffers


class TestApplicationMetadata(unittest.TestCase):

    def test_example(self):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        meta_path = os.path.join(tests_dir, 'data', 'about.t')

        meta = ApplicationMetadata('example-app', '0.1', 2023, 'voidstar')

        with io.BytesIO() as f1, open(meta_path, 'rb') as f2:
            meta.serialize(f1)
            f1.seek(0)
            assert cmp_buffers(f1, f2)


    def test_roundtrip(self):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        meta_path = os.path.join(tests_dir, 'data', 'about.t')
        
        with open(meta_path, 'rb') as f:
            meta = ApplicationMetadata.deserialize(f)

        assert meta.name == 'example-app'
        assert meta.version == '0.1'
        assert meta.year == 2023
        assert meta.author == 'voidstar'

        with io.BytesIO() as f1, open(meta_path, 'rb') as f2:
            meta.serialize(f1)
            f1.seek(0)
            assert cmp_buffers(f1, f2)
