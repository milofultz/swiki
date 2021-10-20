from collections import defaultdict
import os
import shutil
from textwrap import dedent
import time
import unittest

import swiki
import modules.link_utilities as link


def touch(path, content: str = ''):
    with open(path, 'a') as f:
        f.write(content)


def empty(input_path: str):
    for root, dirs, files in os.walk(input_path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def make_test_directory():
    test_path = os.path.join(current_dir, '__delete_test')
    if os.path.isdir(test_path):
        shutil.rmtree(test_path)
    os.makedirs(test_path)
    return test_path


current_dir = os.path.dirname(os.path.realpath(__file__))


class LinkUtilitiesTestCase(unittest.TestCase):
    """ These are used after markdown conversion """
    def setUp(self):
        self.test_backlinks = [
            {
                'title': 'yeah',
                'filename': 'yeah'
            },
            {
                'title': 'yeah 2',
                'filename': 'yeah-2',
            }
        ]

    def test_kebabify_basic(self):
        test_name = 'A local link'
        expected_output = 'a-local-link'
        actual_output = link.kebabify(test_name)
        self.assertEqual(expected_output, actual_output)

    def test_kebabify_special_chars(self):
        test_name = 'A local/link (special)'
        expected_output = 'a-locallink-special'
        actual_output = link.kebabify(test_name)
        self.assertEqual(expected_output, actual_output)

    def test_get_local(self):
        test_content = """A {{local link}}, a {{local link|with another name}}, and an <a href="www.example.com">external link</a>."""
        expected_local_links = ['local link', 'with another name']
        actual_local_links = link.get_local(test_content)
        self.assertListEqual(expected_local_links, actual_local_links)

    def test_add_local(self):
        test_content = """A {{local link}}, a {{local link|with another name}}, and an <a href="www.example.com">external link</a>."""
        expected_output = """A <a href="local-link.html">local link</a>, a <a href="with-another-name.html">local link</a>, and an <a href="www.example.com">external link</a>."""
        actual_output = link.add_local(test_content)
        self.assertEqual(expected_output, actual_output)

    def test_add_external(self):
        test_content = """A {{local link}}, a {{local link|with another name}}, and an <a href="www.example.com">external link</a>."""
        expected_output = """A {{local link}}, a {{local link|with another name}}, and an <a href="www.example.com" target="_blank">external link</a>."""
        actual_output = link.add_external(test_content)
        self.assertEqual(expected_output, actual_output)

    def test_add_backlinks_no_backlinks(self):
        test_content = expected_content = "Test content"
        actual_content = link.add_backlinks(test_content, [])
        self.assertEqual(expected_content, actual_content)

    def test_add_backlinks_basic(self):
        test_content = "<p>Test content</p>"
        expected_content = """<p>Test content</p><section id="backlinks"><details><summary>Backlinks</summary><ul><li><a href="yeah.html">yeah</a></li><li><a href="yeah-2.html">yeah 2</a></li></ul></details></section>"""
        actual_content = link.add_backlinks(test_content, self.test_backlinks)
        self.assertEqual(expected_content, actual_content)

    def test_add_backlinks_duplicates(self):
        test_backlinks = [*self.test_backlinks, self.test_backlinks[0]]
        test_content = "<p>Test content</p>"
        expected_content = """<p>Test content</p><section id="backlinks"><details><summary>Backlinks</summary><ul><li><a href="yeah.html">yeah</a></li><li><a href="yeah-2.html">yeah 2</a></li></ul></details></section>"""
        actual_content = link.add_backlinks(test_content, test_backlinks)
        self.assertEqual(expected_content, actual_content)


class InitTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_path = make_test_directory()

    def tearDown(self):
        empty(self.test_path)

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

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.test_path):
            shutil.rmtree(cls.test_path)


class BuildUtilitiesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_path = make_test_directory()

    def tearDown(self):
        empty(self.test_path)

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

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.test_path):
            shutil.rmtree(cls.test_path)


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


class MakePageDictTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_path = make_test_directory()

        cls.test_input_path = os.path.join(cls.test_path, 'input')
        cls.test_input_rel_path = 'sub'
        cls.test_page_filename = 'test-page.md'
        os.makedirs(os.path.join(cls.test_input_path, cls.test_input_rel_path))
        cls.test_page_fp = os.path.join(cls.test_input_path, cls.test_input_rel_path, cls.test_page_filename)
        cls.test_page_lm = time.strftime("%Y%m%d%H%M", time.gmtime(time.time()))

    def test_basic(self):
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
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_input_rel_path, self.test_page_filename)
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

    def test_no_desc(self):
        # SET UP
        test_page = dedent("""\
            ---
            title: yeah
            ---
            
            The content""")
        with open(self.test_page_fp, 'w') as f:
            f.write(test_page)

        # TEST
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_input_rel_path, self.test_page_filename,)
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

    def test_link(self):
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
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_input_rel_path, self.test_page_filename)
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

    def test_multiple_links(self):
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
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_input_rel_path, self.test_page_filename)
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

    def test_index(self):
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
        page_dict = swiki.make_page_dict(self.test_input_path, self.test_input_rel_path, self.test_page_filename, True)
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

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.test_path):
            shutil.rmtree(cls.test_path)


class SitemapTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_page_dict = {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': '202001010000',
            },
            'content': 'The content',
            'links': [],
            'index': True
        }

    def test_empty_folder(self):
        test_sitemap = defaultdict()
        test_sitemap = swiki.add_page_to_sitemap(self.test_page_dict, 'missing', test_sitemap)
        result_sitemap = defaultdict()
        result_sitemap['missing'] = [self.test_page_dict]
        self.assertDictEqual(test_sitemap, result_sitemap)

    def test_existing_folder(self):
        test_sitemap = defaultdict()
        test_sitemap['existing'] = [self.test_page_dict]
        test_sitemap = swiki.add_page_to_sitemap(self.test_page_dict, 'existing', test_sitemap)
        result_sitemap = defaultdict()
        result_sitemap['existing'] = [self.test_page_dict, self.test_page_dict]
        self.assertDictEqual(test_sitemap, result_sitemap)


class FillFrameTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_page_dict = {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': '202001010000',
            },
            'content': 'The content',
            'links': [],
            'index': True
        }
        cls.test_frame = dedent("""\
            <html>
                <head>
                    <title>{{title}}</title>
                    <meta name="description" content="{{description}}">
                </head>
                <body>
                    {{content}}
                </body>
            </html>""")
        cls.test_content = 'Test content'

    def test_empty_metadata(self):
        test_metadata = dict()
        filled = swiki.fill_frame(self.test_frame, self.test_content, test_metadata)
        self.assertEqual(filled, dedent("""\
            <html>
                <head>
                    <title></title>
                    <meta name="description" content="">
                </head>
                <body>
                    Test content
                </body>
            </html>"""))

    def test_with_metadata(self):
        test_metadata = {
            'title': 'The title',
            'description': 'The description'
        }
        filled = swiki.fill_frame(self.test_frame, self.test_content, test_metadata)
        self.assertEqual(filled, dedent("""\
            <html>
                <head>
                    <title>The title</title>
                    <meta name="description" content="The description">
                </head>
                <body>
                    Test content
                </body>
            </html>"""))


class MakeFatfileTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_path = make_test_directory()
        cls.test_page_dict = {
            'folder': 'sub',
            'metadata': {
                'title': 'yeah',
                'description': 'uh huh',
                'last_modified': '202001010000',
            },
            'content': 'The content',
            'links': [],
            'index': True
        }
        cls.test_frame = dedent("""\
            <html>
                <head>
                    <title>{{title}}</title>
                    <meta name="description" content="{{description}}">
                </head>
                <body>
                    {{content}}
                </body>
            </html>""")
        cls.test_fatfile_path = os.path.join(cls.test_path, 'fatfile.html')

    def tearDown(self):
        if os.path.isfile(self.test_fatfile_path):
            os.remove(self.test_fatfile_path)

    def test_basic(self):
        test_fatfile_content = 'Test content'
        swiki.make_fatfile(self.test_page_dict, test_fatfile_content,
                           self.test_frame, self.test_path)
        with open(self.test_fatfile_path, 'r') as f:
            actual_fatfile = f.read()
        expected_fatfile = dedent("""\
            <html>
                <head>
                    <title>yeah</title>
                    <meta name="description" content="uh huh">
                </head>
                <body>
                    <main id="main"><section id="fatfile"><h1>Fatfile</h1><p>This file contains the contents of every page in the wiki in no order whatsoever.</p>Test content</section></main>
                </body>
            </html>""")
        self.assertEqual(expected_fatfile, actual_fatfile)

    def test_remove_ids(self):
        test_fatfile_content = '<p id="remove-this">Test content</p>'
        swiki.make_fatfile(self.test_page_dict, test_fatfile_content,
                           self.test_frame, self.test_path)
        with open(self.test_fatfile_path, 'r') as f:
            actual_fatfile = f.read()
        expected_fatfile = dedent("""\
            <html>
                <head>
                    <title>yeah</title>
                    <meta name="description" content="uh huh">
                </head>
                <body>
                    <main id="main"><section id="fatfile"><h1>Fatfile</h1><p>This file contains the contents of every page in the wiki in no order whatsoever.</p><p>Test content</p></section></main>
                </body>
            </html>""")
        self.assertEqual(expected_fatfile, actual_fatfile)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.test_path):
            shutil.rmtree(cls.test_path)


class MakeSitemapTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_path = make_test_directory()
        cls.test_sitemap_path = os.path.join(cls.test_path, 'index.html')
        cls.test_index_dict = {
            'metadata': {
                'title': 'Index Title',
                'description': 'Index description'
            },
            'content': 'Index content',
            'index': True
        }
        cls.test_frame = dedent("""\
            <html>
                <head>
                    <title>{{title}}</title>
                    <meta name="description" content="{{description}}">
                </head>
                <body>
                    {{content}}
                </body>
            </html>""")
        cls.test_sitemap = {
            'folder': [
                {
                    'title': 'yeah',
                    'filename': 'yeah'
                },
                {
                    'title': 'yeah 2',
                    'filename': 'yeah-2',
                }
            ],
            'another folder': [
                {
                    'title': 'yeah again',
                    'filename': 'yeah-again'
                }
            ]
        }
        cls.test_stubs = [
            {
                'title': 'stub',
                'filename': 'stub'
            },
        ]

    def tearDown(self):
        os.remove(self.test_sitemap_path)

    def test_no_display_name(self):
        test_sitemap_basic = {'': [self.test_sitemap['folder'][0]]}
        swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                           self.test_frame, self.test_path)
        with open(self.test_sitemap_path, 'r') as f:
            actual_sitemap = f.read()
        expected_sitemap = dedent("""\
            <html>
                <head>
                    <title>Index Title</title>
                    <meta name="description" content="Index description">
                </head>
                <body>
                    <main id="main"><h1 id="title">Index Title</h1><p>Index content</p>
            <div><details><summary>[root]</summary><ul><li><a href="yeah.html">yeah</a></li></ul></details></div></main>
                </body>
            </html>""")
        self.assertEqual(expected_sitemap, actual_sitemap)

    def test_single_page(self):
        test_sitemap_basic = {'folder': [self.test_sitemap['folder'][0]]}
        swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                           self.test_frame, self.test_path)
        with open(self.test_sitemap_path, 'r') as f:
            actual_sitemap = f.read()
        expected_sitemap = dedent("""\
            <html>
                <head>
                    <title>Index Title</title>
                    <meta name="description" content="Index description">
                </head>
                <body>
                    <main id="main"><h1 id="title">Index Title</h1><p>Index content</p>
            <div><details><summary>folder</summary><ul><li><a href="yeah.html">yeah</a></li></ul></details></div></main>
                </body>
            </html>""")
        self.assertEqual(expected_sitemap, actual_sitemap)

    def test_another_page(self):
        test_sitemap_basic = {'folder': self.test_sitemap['folder']}
        swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                           self.test_frame, self.test_path)
        with open(self.test_sitemap_path, 'r') as f:
            actual_sitemap = f.read()
        expected_sitemap = dedent("""\
            <html>
                <head>
                    <title>Index Title</title>
                    <meta name="description" content="Index description">
                </head>
                <body>
                    <main id="main"><h1 id="title">Index Title</h1><p>Index content</p>
            <div><details><summary>folder</summary><ul><li><a href="yeah.html">yeah</a></li><li><a href="yeah-2.html">yeah 2</a></li></ul></details></div></main>
                </body>
            </html>""")
        self.assertEqual(expected_sitemap, actual_sitemap)

    def test_with_stubs(self):
        test_sitemap_basic = {
            'folder': [self.test_sitemap['folder'][0]],
            '.stubs': self.test_stubs
        }
        swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                           self.test_frame, self.test_path)
        with open(self.test_sitemap_path, 'r') as f:
            actual_sitemap = f.read()
        expected_sitemap = dedent("""\
            <html>
                <head>
                    <title>Index Title</title>
                    <meta name="description" content="Index description">
                </head>
                <body>
                    <main id="main"><h1 id="title">Index Title</h1><p>Index content</p>
            <div><details><summary>folder</summary><ul><li><a href="yeah.html">yeah</a></li></ul></details></div><div><details><summary>Wiki Stubs</summary><ul><li><a href="stub.html">stub</a></li></ul></details></div></main>
                </body>
            </html>""")
        self.assertEqual(expected_sitemap, actual_sitemap)

    def test_another_folder(self):
        swiki.make_sitemap(self.test_index_dict, self.test_sitemap,
                           self.test_frame, self.test_path)
        with open(self.test_sitemap_path, 'r') as f:
            actual_sitemap = f.read()
        expected_sitemap = dedent("""\
            <html>
                <head>
                    <title>Index Title</title>
                    <meta name="description" content="Index description">
                </head>
                <body>
                    <main id="main"><h1 id="title">Index Title</h1><p>Index content</p>
            <div><details><summary>another folder</summary><ul><li><a href="yeah-again.html">yeah again</a></li></ul></details></div><div><details><summary>folder</summary><ul><li><a href="yeah.html">yeah</a></li><li><a href="yeah-2.html">yeah 2</a></li></ul></details></div></main>
                </body>
            </html>""")
        self.assertEqual(expected_sitemap, actual_sitemap)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.test_path):
            shutil.rmtree(cls.test_path)



if __name__ == '__main__':
    unittest.main()
