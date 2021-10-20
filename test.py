from collections import defaultdict
import os
import shutil
from textwrap import dedent
import time
import unittest

import swiki


def touch(path, content: str = ''):
    with open(path, 'a') as f:
        f.write(content)


current_dir = os.path.dirname(os.path.realpath(__file__))


class InitTestCase(unittest.TestCase):
    def setUp(self):
        self.test_path = os.path.join(current_dir, '__delete_test')
        if os.path.isdir(self.test_path):
            shutil.rmtree(self.test_path)
        os.makedirs(self.test_path)

    def test_delete_current_html(self):
        # SET UP
        test_file = os.path.join(self.test_path, 'test.html')
        touch(test_file)
        another_test_file = os.path.join(self.test_path, 'anothertest.html')
        touch(another_test_file)
        test_css = os.path.join(self.test_path, 'style.css')
        touch(test_css)
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

    def test_update_config_existing(self):
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

    def test_update_config_new(self):
        # SET UP
        swiki_folder = os.path.join(self.test_path, '_swiki')
        os.mkdir(swiki_folder)
        test_config_fp = os.path.join(swiki_folder, 'config.ini')
        touch(test_config_fp, 'NewItem = 123abc')

        # TEST
        test_config = {'TabSize': 2}
        swiki.update_config(test_config, test_config_fp)
        self.assertEqual(test_config.get('TabSize'), 2)
        self.assertEqual(test_config.get('NewItem'), '123abc')

        # TEAR DOWN
        os.remove(test_config_fp)
        os.rmdir(swiki_folder)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_path)


class BuildUtilitiesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.test_path = os.path.join(current_dir, '__delete_test')
        if os.path.isdir(self.test_path):
            shutil.rmtree(self.test_path)
        os.makedirs(self.test_path)

    def test_copy_css_file_if_exists(self):
        # SET UP
        test_css = os.path.join(self.test_path, '_swiki', 'test.css')
        test_swiki = os.path.join(self.test_path, '_swiki')
        os.mkdir(test_swiki)
        touch(test_css, 'test')
        test_output = os.path.join(self.test_path, 'output')
        os.mkdir(test_output)

        # TEST
        swiki.copy_css_file(self.test_path, test_output)
        self.assertTrue(os.path.isfile(os.path.join(test_output, 'test.css')))

        # TEAR DOWN
        os.remove(test_css)
        os.remove(os.path.join(test_output, 'test.css'))
        os.rmdir(test_swiki)
        os.rmdir(test_output)

    def test_copy_css_file_if_not_exists(self):
        # SET UP
        test_swiki = os.path.join(self.test_path, '_swiki')
        os.mkdir(test_swiki)
        test_output = os.path.join(self.test_path, 'output')
        os.mkdir(test_output)

        # TEST
        swiki.copy_css_file(self.test_path, test_output)
        self.assertEqual(os.listdir(test_swiki), [])
        self.assertEqual(os.listdir(test_output), [])

        # TEAR DOWN
        os.rmdir(test_swiki)
        os.rmdir(test_output)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_path)


class WikiHelpersTestCase(unittest.TestCase):
    def test_place_in_container(self):
        element = swiki.place_in_container('p', 'test', 'Inner text!')
        self.assertEqual(element, '<p id="test">Inner text!</p>')

    def test_place_in_container_if_no_id(self):
        element = swiki.place_in_container('p', None, 'No ID :O')
        self.assertEqual(element, '<p>No ID :O</p>')

    def test_add_last_modified(self):
        html = swiki.add_last_modified('preceding content', 'lm_text')
        self.assertEqual(html, 'preceding content\n<p class="last-modified">Last modified: lm_text</p>')

    def test_detab(self):
        # Assumes config default is 2 spaces per tab
        content = 'Yeah\tthings!'
        self.assertEqual(swiki.detab(content), 'Yeah  things!')


class MakePageDictTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.test_path = os.path.join(current_dir, '__delete_test')
        if os.path.isdir(self.test_path):
            shutil.rmtree(self.test_path)
        os.makedirs(self.test_path)

        self.test_input_path = os.path.join(self.test_path, 'input')
        self.test_page_filename = 'test-page.md'
        os.makedirs(os.path.join(self.test_input_path, 'sub'))
        self.test_page_fp = os.path.join(self.test_input_path, 'sub', self.test_page_filename)
        self.test_page_lm = time.strftime("%Y%m%d%H%M", time.gmtime(time.time()))

    def test_make_page_dict_basic(self):
        # SET UP
        test_page = dedent("""\
            ---
            title: yeah
            description: uh huh
            ---
            
            The content""")
        with open(self.test_page_fp, 'w') as f:
            f.write(test_page)

        # TEST
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_page_filename, 'sub')
        self.assertDictEqual(page_dict, {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': self.test_page_lm,
            },
            'content': 'The content',
            'links': [],
            'index': False
        })

    def test_make_page_dict_no_desc(self):
        # SET UP
        test_page = dedent("""\
            ---
            title: yeah
            ---
            
            The content""")
        with open(self.test_page_fp, 'w') as f:
            f.write(test_page)

        # TEST
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_page_filename, 'sub')
        self.assertDictEqual(page_dict, {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': '',
                'last_modified': self.test_page_lm,
            },
            'content': 'The content',
            'links': [],
            'index': False
        })

    def test_make_page_dict_link(self):
        # SET UP
        test_page = dedent("""\
            ---
            title: yeah
            description: uh huh
            ---
            
            The {{content}}""")
        with open(self.test_page_fp, 'w') as f:
            f.write(test_page)

        # TEST
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_page_filename, 'sub')
        self.assertDictEqual(page_dict, {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': self.test_page_lm,
            },
            'content': 'The {{content}}',
            'links': ['content'],
            'index': False
        })

    def test_make_page_dict_multiple_links(self):
        # SET UP
        test_page = dedent("""\
            ---
            title: yeah
            description: uh huh
            ---
            
            The {{content}} and then...
            
            {{another}}!""")
        with open(self.test_page_fp, 'w') as f:
            f.write(test_page)

        # TEST
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_page_filename, 'sub')
        self.assertDictEqual(page_dict, {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': self.test_page_lm,
            },
            'content': 'The {{content}} and then...\n\n{{another}}!',
            'links': ['content', 'another'],
            'index': False
        })

    def test_make_page_dict_index(self):
        # SET UP
        test_page = dedent("""\
            ---
            title: yeah
            description: uh huh
            ---
            
            The content""")
        with open(self.test_page_fp, 'w') as f:
            f.write(test_page)

        # TEST
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_page_filename, 'sub', True)
        self.assertDictEqual(page_dict, {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': self.test_page_lm,
            },
            'content': 'The content',
            'links': [],
            'index': True
        })

    def tearDown(self):
        shutil.rmtree(self.test_path)


class SitemapTestCase(unittest.TestCase):
    def setUp(self):
        self.test_page_dict = {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': 1_000_000_000,
            },
            'content': 'The content',
            'links': [],
            'index': True
        }

    def test_add_page_to_sitemap_empty_folder(self):
        test_sitemap = defaultdict()
        test_sitemap = swiki.add_page_to_sitemap(self.test_page_dict, 'missing', test_sitemap)
        result_sitemap = defaultdict()
        result_sitemap['missing'] = [self.test_page_dict]
        self.assertDictEqual(test_sitemap, result_sitemap)

    def test_add_page_to_sitemap_existing_folder(self):
        test_sitemap = defaultdict()
        test_sitemap['existing'] = [self.test_page_dict]
        test_sitemap = swiki.add_page_to_sitemap(self.test_page_dict, 'existing', test_sitemap)
        result_sitemap = defaultdict()
        result_sitemap['existing'] = [self.test_page_dict, self.test_page_dict]
        self.assertDictEqual(test_sitemap, result_sitemap)


if __name__ == '__main__':
    unittest.main()
