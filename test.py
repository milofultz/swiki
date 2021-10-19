import os
import shutil
import unittest

import swiki


def touch(path, content: str = ''):
    with open(path, 'a') as f:
        f.write(content)


current_dir = os.path.dirname(os.path.realpath(__file__))


class InitTestCase(unittest.TestCase):
    """ Tests program initialization variations """

    def setUp(self):
        self.test_path = os.path.join(current_dir, '__delete_test')
        if os.path.isdir(self.test_path):
            shutil.rmtree(self.test_path)
        os.makedirs(self.test_path)

    def test_delete_current_html(self):
        # SET UP
        test_file = os.path.join(self.test_path, 'test.html')
        touch(test_file, 'test')
        another_test_file = os.path.join(self.test_path, 'anothertest.html')
        touch(another_test_file, 'test')
        test_css = os.path.join(self.test_path, 'style.css')
        touch(test_css, 'test')
        test_folder = os.path.join(self.test_path, 'keep')
        os.mkdir(test_folder)

        # TEST
        swiki.delete_current_html(self.test_path)

        self.assertFalse(os.path.isfile(test_file))
        self.assertFalse(os.path.isfile(another_test_file))
        self.assertTrue(os.path.isfile(test_css))
        self.assertTrue(os.path.isdir(test_folder))

        # TEAR DOWN
        os.remove(test_css)
        os.rmdir(test_folder)

    def test_update_config(self):
        # SET UP
        swiki_folder = os.path.join(self.test_path, '_swiki')
        os.mkdir(swiki_folder)
        test_config_fp = os.path.join(swiki_folder, 'config.ini')
        touch(test_config_fp, 'TabSize = 4')

        # TEST
        test_config = {'TabSize': 2}
        swiki.update_config(test_config, test_config_fp)
        self.assertEqual(test_config.get('TabSize'), 4)

        # TEAR DOWN
        os.remove(test_config_fp)
        os.rmdir(swiki_folder)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_path)


if __name__ == '__main__':
    unittest.main()
