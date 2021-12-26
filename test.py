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
        test_name = 'A local/link, yeah. (it\'s "special"!)'
        expected_output = 'a-locallink-yeah-its-special'
        actual_output = link.kebabify(test_name)
        self.assertEqual(expected_output, actual_output)

    def test_kebabify_long(self):
        test_name = 'lorem ipsum ' * 17
        expected_output = ('lorem-ipsum' + '-lorem-ipsum' * 16)[:200]
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
        another_test_file = os.path.join(self.test_path, 'another_test.html')
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
        touch(test_config_fp, 'tab_size = 4')

        # TEST
        test_config = {'tab_size': 2}
        swiki.update_config(test_config, test_config_fp)
        self.assertEqual(test_config.get('tab_size'), 4)

    def test_update_config_new(self):
        # SET UP
        swiki_folder = os.path.join(self.test_path, '_swiki')
        os.mkdir(swiki_folder)
        test_config_fp = os.path.join(swiki_folder, 'config.ini')
        touch(test_config_fp, 'new_item = 123abc')

        # TEST
        test_config = {'tab_size': 2}
        swiki.update_config(test_config, test_config_fp)
        self.assertEqual(test_config.get('tab_size'), 2)
        self.assertEqual(test_config.get('new_item'), '123abc')

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.test_path):
            shutil.rmtree(cls.test_path)


class BuildUtilitiesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_path = make_test_directory()

    def tearDown(self):
        empty(self.test_path)

    def test_copy_css_file_if_exists(self):
        # SET UP
        test_swiki = os.path.join(self.test_path, '_swiki')
        os.mkdir(test_swiki)
        test_css = os.path.join(test_swiki, 'test.css')
        touch(test_css, 'test')
        test_output = os.path.join(self.test_path, 'output')
        os.mkdir(test_output)

        # TEST
        swiki.copy_css_file(self.test_path, test_output)
        self.assertTrue(os.path.isfile(os.path.join(test_output, 'test.css')))

    def test_copy_css_files_if_multiple_exist(self):
        # SET UP
        test_swiki = os.path.join(self.test_path, '_swiki')
        os.mkdir(test_swiki)
        test_css_1 = os.path.join(test_swiki, 'test1.css')
        touch(test_css_1, 'test')
        test_css_2 = os.path.join(test_swiki, 'test2.css')
        touch(test_css_2, 'test')
        test_output = os.path.join(self.test_path, 'output')
        os.mkdir(test_output)

        # TEST
        swiki.copy_css_file(self.test_path, test_output)
        self.assertTrue(os.path.isfile(os.path.join(test_output, 'test1.css')))
        self.assertTrue(os.path.isfile(os.path.join(test_output, 'test2.css')))

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

    def test_copy_media_if_exists(self):
        # SET UP
        test_media_file_1 = os.path.join(self.test_path, 'file_1.txt')
        touch(test_media_file_1, 'test')
        test_media_file_2 = os.path.join(self.test_path, 'file_2.txt')
        touch(test_media_file_2, 'test')

        test_output = os.path.join(self.test_path, 'output')
        os.mkdir(test_output)

        # TEST
        swiki.copy_media(self.test_path, test_media_file_1, test_output)
        swiki.copy_media(self.test_path, test_media_file_2, test_output)
        self.assertTrue(os.path.isfile(os.path.join(test_output, 'file_1.txt')))
        self.assertTrue(os.path.isfile(os.path.join(test_output, 'file_2.txt')))

    def test_copy_media_if_not_exists(self):
        # SET UP
        test_output = os.path.join(self.test_path, 'output')
        os.mkdir(test_output)

        # TEST
        with self.assertRaises(FileNotFoundError):
            swiki.copy_media(self.test_path, 'nonexistent_file.txt', test_output)
        self.assertEqual(os.listdir(test_output), [])

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.test_path):
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

    def test_add_to_last_modified_pages(self):
        # SET UP
        # Make list of test pages
        oldest_test_page = {
            'folder': 'test',
            'metadata': {
                'title': 'Oldest Page',
                'description': 'uh huh',
                'last_modified': '20000101000000',
            },
            'content': '',
            'links': [],
            'index': False
        }
        middle_test_page = {
            'folder': 'test',
            'metadata': {
                'title': 'Middle Page',
                'description': 'uh huh',
                'last_modified': '20020101000000',
            },
            'content': '',
            'links': [],
            'index': False
        }
        test_pages = [middle_test_page, oldest_test_page]
        # Make max length as length of list
        max = len(test_pages)
        # Create a new test page that is newer than the other pages
        newest_test_page = {
            'folder': 'test',
            'metadata': {
                'title': 'Newest Page',
                'description': 'uh huh',
                'last_modified': '20040101000000',
            },
            'content': '',
            'links': [],
            'index': False
        }

        # TESTS
        actual_last_modified = swiki.add_to_last_modified_pages(newest_test_page, test_pages, max)
        expected_last_modified = [newest_test_page, middle_test_page]
        self.assertListEqual(expected_last_modified, actual_last_modified)
        # Test that older additions won't change the list
        unchanged_actual_last_modified = swiki.add_to_last_modified_pages(oldest_test_page, test_pages, max)
        self.assertListEqual(actual_last_modified, unchanged_actual_last_modified)


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
        if os.path.isdir(cls.test_path):
            shutil.rmtree(cls.test_path)


class SitemapTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first_test_page_dict = {
            'folder': 'sub',
            'metadata': {
                'title': 'First Test',
                'description': 'First Test',
                'last_modified': '202001010000',
            },
            'content': 'The content',
            'links': [],
            'index': True
        }
        cls.second_test_page_dict = {
            'folder': 'sub',
            'metadata': {
                'title': 'Second Test',
                'description': 'Second Test',
                'last_modified': '202001010000',
            },
            'content': 'The content',
            'links': [],
            'index': True
        }

    def test_empty_folder(self):
        test_sitemap = dict()
        test_sitemap = swiki.add_page_to_sitemap(self.first_test_page_dict, 'missing', test_sitemap)
        result_sitemap = dict()
        result_sitemap['missing'] = [self.first_test_page_dict]
        self.assertDictEqual(test_sitemap, result_sitemap)

    def test_existing_folder(self):
        test_sitemap = dict()
        test_sitemap['existing'] = [self.first_test_page_dict]
        test_sitemap = swiki.add_page_to_sitemap(self.second_test_page_dict, 'existing', test_sitemap)
        result_sitemap = dict()
        result_sitemap['existing'] = [self.first_test_page_dict, self.second_test_page_dict]
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
        expected_fatfile = dedent(f"""\
            <html>
                <head>
                    <title>yeah</title>
                    <meta name="description" content="uh huh">
                </head>
                <body>
                    <main id="main"><section id="fatfile"><h1>Fatfile</h1><p>This file contains the contents of every page in the wiki in no order whatsoever.</p>{test_fatfile_content}</section></main>
                </body>
            </html>""")
        self.assertEqual(expected_fatfile, actual_fatfile)

    def test_remove_ids(self):
        test_text = 'Test content'
        test_fatfile_content = f'<p id="remove-this">{test_text}</p>'
        swiki.make_fatfile(self.test_page_dict, test_fatfile_content,
                           self.test_frame, self.test_path)
        with open(self.test_fatfile_path, 'r') as f:
            actual_fatfile = f.read()
        expected_fatfile = dedent(f"""\
            <html>
                <head>
                    <title>yeah</title>
                    <meta name="description" content="uh huh">
                </head>
                <body>
                    <main id="main"><section id="fatfile"><h1>Fatfile</h1><p>This file contains the contents of every page in the wiki in no order whatsoever.</p><p>{test_text}</p></section></main>
                </body>
            </html>""")
        self.assertEqual(expected_fatfile, actual_fatfile)

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.test_path):
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

    def test_no_display_name(self):
        test_sitemap_basic = {'': [self.test_sitemap['folder'][0]]}
        actual_sitemap = swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                                            [], self.test_frame)
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
        actual_sitemap = swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                                            [], self.test_frame)
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
        actual_sitemap = swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                                            [], self.test_frame)
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
        actual_sitemap = swiki.make_sitemap(self.test_index_dict, test_sitemap_basic,
                                            [], self.test_frame)
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
        actual_sitemap = swiki.make_sitemap(self.test_index_dict, self.test_sitemap,
                                            [], self.test_frame)
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
        if os.path.isdir(cls.test_path):
            shutil.rmtree(cls.test_path)


class MakeWikiTestCase(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.test_path = make_test_directory()
        cls.test_input_folder = os.path.join(cls.test_path, 'input')
        os.mkdir(cls.test_input_folder)
        cls.test_output_folder = os.path.join(cls.test_path, 'output')
        os.mkdir(cls.test_output_folder)
        test_file_path = os.path.join(cls.test_input_folder, 'test.md')
        test_file_content = dedent("""\
            ---
            title: Example File
            description: Example description.
            ---
            
            Some content.""")
        touch(test_file_path, test_file_content)
        cls.test_file_lm = time.strftime("%Y%m%d%H%M", time.gmtime(os.path.getmtime(test_file_path)))
        another_test_file_path = os.path.join(cls.test_input_folder, 'another_test.md')
        another_test_file_content = dedent("""\
            ---
            title: Another File
            description: Another description.
            ---

            Another set of content, with *italics*!""")
        touch(another_test_file_path, another_test_file_content)
        cls.another_test_file_lm = time.strftime("%Y%m%d%H%M", time.gmtime(os.path.getmtime(another_test_file_path)))
        test_swiki_folder = os.path.join(cls.test_input_folder, '_swiki')
        os.mkdir(test_swiki_folder)
        test_frame_path = os.path.join(test_swiki_folder, 'frame.html')
        test_frame_content = dedent("""\
            <html>
                <head>
                    <title>{{title}}</title>
                    <meta name="description" content="{{description}}">
                </head>
                <body>{{content}}</body>
            </html>""")
        touch(test_frame_path, test_frame_content)
        test_css_path = os.path.join(test_swiki_folder, 'style.css')
        touch(test_css_path, 'body { font-size: 40rem; color: blue; }')
        cls.test_config = {'tab_size': 2, 'build_fatfile': False,
                           'recent_list': False, 'recent_list_length': 10}

    def tearDown(self):
        empty(self.test_output_folder)

    def test_multiple_pages(self):
        swiki.make_wiki(self.test_input_folder, self.test_output_folder,
                        self.test_config)
        test_example_file_path = os.path.join(self.test_output_folder, 'example-file.html')
        self.assertTrue(os.path.isfile(test_example_file_path))
        expected_example_file_content = dedent(f"""\
            <html><head><title>Example File</title><meta name="description" content="Example description."></head><body><main id="main"><article id="content"><h1 id="title">Example File</h1>
            <p>Some content.</p>
            
            <p class="last-modified">Last modified: {self.test_file_lm}</p></article></main></body></html>""")
        with open(test_example_file_path, 'r') as f:
            actual_example_file_content = f.read()
        self.assertEqual(expected_example_file_content, actual_example_file_content)

        test_another_file_path = os.path.join(self.test_output_folder, 'another-file.html')
        self.assertTrue(os.path.isfile(test_another_file_path))
        expected_another_file_content = dedent(f"""\
            <html><head><title>Another File</title><meta name="description" content="Another description."></head><body><main id="main"><article id="content"><h1 id="title">Another File</h1>
            <p>Another set of content, with <em>italics</em>!</p>
            
            <p class="last-modified">Last modified: {self.another_test_file_lm}</p></article></main></body></html>""")
        with open(test_another_file_path, 'r') as f:
            actual_another_file_content = f.read()
        self.assertEqual(expected_another_file_content, actual_another_file_content)

        test_css_path = os.path.join(self.test_output_folder, 'style.css')
        self.assertTrue(os.path.isfile(test_css_path))

    def test_same_title(self):
        # SET UP
        duplicate_test_file_path = os.path.join(self.test_input_folder, 'test_duplicate.md')
        duplicate_test_file_content = dedent("""\
            ---
            title: Example File
            description: Example description.
            ---
            
            Some content.""")
        touch(duplicate_test_file_path, duplicate_test_file_content)

        # TESTS
        with self.assertRaises(RuntimeError) as e:
            swiki.make_wiki(self.test_input_folder, self.test_output_folder,
                            self.test_config)
        actual_exception_message = str(e.exception)
        expected_exception_message = f'''Page "Example File" with filename "example-file" conflicts with page "Example File" with filename "example-file".'''
        self.assertEqual(expected_exception_message, actual_exception_message)

    def test_same_filename_for_non_pages(self):
        # SET UP
        test_media_file_1 = os.path.join(self.test_input_folder, 'file_1.txt')
        touch(test_media_file_1, 'test')
        test_media_folder = os.path.join(self.test_input_folder, 'another_folder')
        os.mkdir(test_media_folder)
        test_media_file_2 = os.path.join(test_media_folder, 'file_1.txt')
        touch(test_media_file_2, 'test')

        # TEST
        with self.assertRaises(RuntimeError):
            swiki.make_wiki(self.test_input_folder, self.test_output_folder, self.test_config)

    def test_index(self):
        # SET UP
        test_index_file_path = os.path.join(self.test_input_folder, '_swiki', 'index.md')
        test_index_file_content = dedent("""\
            ---
            title: Website Index
            description: Index description.
            ---

            This is the index, wow.""")
        touch(test_index_file_path, test_index_file_content)

        # TESTS
        swiki.make_wiki(self.test_input_folder, self.test_output_folder,
                        self.test_config)
        output_index_file_path = os.path.join(self.test_output_folder, 'index.html')
        self.assertTrue(os.path.isfile(output_index_file_path))
        # Should alphabetize pages in input folder by title metadata
        expected_index_file_content = dedent(f"""\
            <html><head><title>Website Index</title><meta name="description" content="Index description."></head><body><main id="main"><h1 id="title">Website Index</h1><p>This is the index, wow.</p>
            <div><details><summary>[root]</summary><ul><li><a href="another-file.html">Another File</a></li><li><a href="example-file.html">Example File</a></li></ul></details></div></main></body></html>""")
        with open(output_index_file_path, 'r') as f:
            actual_index_file_content = f.read()
        self.assertEqual(expected_index_file_content, actual_index_file_content)

    def test_fatfile(self):
        fatfile_config = {
            **self.test_config,
            'build_fatfile': True
        }
        swiki.make_wiki(self.test_input_folder, self.test_output_folder,
                        fatfile_config)
        test_fatfile_file_path = os.path.join(self.test_output_folder, 'fatfile.html')
        self.assertTrue(os.path.isfile(test_fatfile_file_path))
        # This is ordered by page parse/insertion in pages dict in build
        expected_fatfile_file_content = dedent(f"""\
            <html><head><title>Fatfile</title><meta name="description" content=""></head><body><main id="main"><section id="fatfile"><h1>Fatfile</h1><p>This file contains the contents of every page in the wiki in no order whatsoever.</p><article><h1><a href="another-file.html">Another File</a></h1>
            <p>Another set of content, with <em>italics</em>!</p>
            
            <p class="last-modified">Last modified: {self.another_test_file_lm}</p></article><article><h1><a href="example-file.html">Example File</a></h1>
            <p>Some content.</p>
            
            <p class="last-modified">Last modified: {self.test_file_lm}</p></article></section></main></body></html>""")
        with open(test_fatfile_file_path, 'r') as f:
            actual_fatfile_file_content = f.read()
        self.assertEqual(expected_fatfile_file_content, actual_fatfile_file_content)

    def test_special_chars_in_title_with_fatfile(self):
        # SET UP
        test_file_path_1 = os.path.join(self.test_input_folder, 'cplusplus.md')
        test_file_content_1 = dedent(f"""\
            ---
            title: Regex Doesn't Like These Special Characters
            description: Example description.
            ---
            
            An {{{{ellipsis...}}}} What about {{{{C++}}}}?""")
        touch(test_file_path_1, test_file_content_1)
        fatfile_config = {
            **self.test_config,
            'build_fatfile': True
        }

        # TESTS
        swiki.make_wiki(self.test_input_folder, self.test_output_folder,
                        fatfile_config)
        # should not throw from there being regex special characters in the title
        self.assertTrue(True)

    def test_recent(self):
        test_recent_config = {'tab_size': 2, 'build_fatfile': False,
                              'recent_list': True, 'recent_list_length': 10}
        swiki.make_wiki(self.test_input_folder, self.test_output_folder,
                        test_recent_config)
        # should show both pages added in order of creation
        output_index_file_path = os.path.join(self.test_output_folder, 'index.html')
        self.assertTrue(os.path.isfile(output_index_file_path))
        expected_index_file_content = f"""\
<html><head><title></title><meta name="description" content=""></head><body>\
<main id="main"><h1 id="title">Sitemap</h1><section class="recent-list"><h2>Recent Changes:</h2><ul>\
<li>{self.another_test_file_lm}: <a href="another-file.html">Another File</a></li>\
<li>{self.test_file_lm}: <a href="example-file.html">Example File</a></li></ul></section>\
<div><details><summary>[root]</summary><ul><li><a href="another-file.html">Another File</a></li>\
<li><a href="example-file.html">Example File</a></li></ul></details></div></main></body></html>"""
        with open(output_index_file_path, 'r') as f:
            actual_index_file_content = f.read()
        self.assertEqual(expected_index_file_content, actual_index_file_content)

    def test_recent_list_length(self):
        test_recent_config = {'tab_size': 2, 'build_fatfile': False,
                              'recent_list': True, 'recent_list_length': 1}
        swiki.make_wiki(self.test_input_folder, self.test_output_folder,
                        test_recent_config)
        # should show both pages added in order of creation
        output_index_file_path = os.path.join(self.test_output_folder, 'index.html')
        self.assertTrue(os.path.isfile(output_index_file_path))
        expected_index_file_content = f"""\
<html><head><title></title><meta name="description" content=""></head><body>\
<main id="main"><h1 id="title">Sitemap</h1><section class="recent-list"><h2>Recent Changes:</h2><ul>\
<li>{self.another_test_file_lm}: <a href="another-file.html">Another File</a></li></ul></section>\
<div><details><summary>[root]</summary><ul><li><a href="another-file.html">Another File</a></li>\
<li><a href="example-file.html">Example File</a></li></ul></details></div></main></body></html>"""
        with open(output_index_file_path, 'r') as f:
            actual_index_file_content = f.read()
        self.assertEqual(expected_index_file_content, actual_index_file_content)

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.test_path):
            shutil.rmtree(cls.test_path)


if __name__ == '__main__':
    unittest.main()
