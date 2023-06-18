import unittest
import io
import os

from c64os_util import ApplicationMenu, ApplicationMenuEntry


def cmp_buffers(f1, f2):
    while True:
        b1 = f1.read(1024)
        b2 = f2.read(1024)
        if b1 != b2:
            return False
        if not b1:
            break
    return True


class TestApplicationMenu(unittest.TestCase):

    def test_example(self):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        menu_path = os.path.join(tests_dir, 'data', 'menu.m')

        menu = ApplicationMenu('System')
        modifier_keys = 6
        action_key = 'h'
        action_msg = '!'
        entry = ApplicationMenuEntry(
            'Go Home', modifier_keys,
            action_key, action_msg
        )
        menu.add(entry)

        with io.BytesIO() as f1, open(menu_path, 'rb') as f2:
            menu.serialize(f1)
            f1.seek(0)
            assert cmp_buffers(f1, f2)


    def test_roundtrip(self):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        menu_path = os.path.join(tests_dir, 'data', 'menu.m')

        with open(menu_path, 'rb') as f:
            menu = ApplicationMenu.deserialize(f)

        assert isinstance(menu, ApplicationMenu)
        assert menu.name == 'System'
        assert len(menu) == 1

        entry = menu[0]

        assert isinstance(entry, ApplicationMenuEntry)
        assert entry.name == 'Go Home'
        assert entry.modifier_keys == 6
        assert entry.action_key == 'h'
        assert entry.action_msg == '!'

        with io.BytesIO() as f1, open(menu_path, 'rb') as f2:
            menu.serialize(f1)
            f1.seek(0)
            assert cmp_buffers(f1, f2)

