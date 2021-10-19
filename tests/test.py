import os
import shutil
import unittest

import swiki


def touch(path, content: str = ''):
    with open(path, 'a') as f:
        f.write(content)


current_dir = os.path.dirname(os.path.realpath(__file__))


class ArgsTestCase(unittest.TestCase):
    """ Tests different arguments """

    def test_delete_current_html(self):
        # SET UP
        new_path = os.path.join(current_dir, 'delete_test')
        if os.path.isdir(new_path):
            shutil.rmtree(new_path)
        os.makedirs(new_path)
        test_file = os.path.join(new_path, 'test.html')
        touch(test_file, 'test')
        another_test_file = os.path.join(new_path, 'anothertest.html')
        touch(another_test_file, 'test')
        test_css = os.path.join(new_path, 'style.css')
        touch(test_css, 'test')
        test_folder = os.path.join(new_path, 'keep')
        os.mkdir(test_folder)

        # TEST
        swiki.delete_current_html(new_path)

        self.assertFalse(os.path.isfile(test_file))
        self.assertFalse(os.path.isfile(another_test_file))
        self.assertTrue(os.path.isfile(test_css))
        self.assertTrue(os.path.isdir(test_folder))

        # TEAR DOWN
        shutil.rmtree(new_path)


if __name__ == '__main__':
    unittest.main()
