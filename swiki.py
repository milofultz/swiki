import argparse
import os
import re
import shutil
import sys
from textwrap import dedent
import time

from marko import Markdown
import frontmatter

import modules.link_utilities as links


IGNORE = ['.DS_Store']
RESERVED = ['index', 'fatfile']

marko = Markdown(extensions=['gfm'])


#############
# Utilities #
#############


def update_config(internal_config: dict, external_config_fp: str):
    """ Update default config with any user values """
    with open(external_config_fp, 'r') as f:
        config_file = f.read()
    for line in config_file.split('\n'):
        if line == '':
            continue
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip()
        # Cast the config value to the type that's in the default
        internal_config[key] = type(internal_config.get(key, 'string'))(value)


def delete_current_html(directory: str):
    """ Delete all existing HTML files in directory """
    for file in os.listdir(directory):
        if os.path.splitext(file)[1] == '.html':
            os.remove(os.path.join(directory, file))


def copy_css_file(pages_dir: str, output_dir: str):
    """ If CSS files in _swiki directory, copy to output """
    swiki_folder = os.path.join(pages_dir, '_swiki')
    if not os.path.isdir(swiki_folder):
        return
    for file in os.listdir(swiki_folder):
        if os.path.splitext(file)[1] == '.css':
            shutil.copy2(os.path.join(swiki_folder, file), os.path.join(output_dir, file))


def copy_media(current_folder: str, media_file: str, output_dir: str):
    """ If non-Markdown file exists in folder, copy to output """
    shutil.copy2(os.path.join(current_folder, media_file), output_dir)


################
# Wiki Helpers #
################


def place_in_container(element: str, html_id: str or None, content: str) -> str:
    """ Place content in container with ID """
    id_attr = f' id="{html_id}"' if html_id else ''
    return f'<{element}{id_attr}>{content}</{element}>'


def add_last_modified(content: str, lm_text: str) -> str:
    if not lm_text:
        return content
    return f'{content}\n<p class="last-modified">Last modified: {lm_text}</p>'


def make_page_dict(root: str, rel_path: str, file: str, is_index: bool = False) -> dict:
    """ Make dict of all page specific data """
    page = {'folder': rel_path}
    fp = os.path.join(root, rel_path, file)
    with open(fp, 'r') as f:
        file_contents = f.read()
    page['metadata'], page['content'] = frontmatter.parse(file_contents)
    page['metadata']['description'] = page['metadata'].get('description') or ''
    last_modified = time.gmtime(os.path.getmtime(fp))
    page['metadata']['last_modified'] = time.strftime("%Y%m%d%H%M", last_modified)
    page['links'] = links.get_local(page.get('content'))
    page['index'] = True if is_index else False
    return page


def add_to_last_modified_pages(new_page: dict, last_modified: list, max_length: int) -> list:
    end = min(len(last_modified), max_length)

    index = 0
    while index < end:
        current_lm = last_modified[index]['metadata']['last_modified']
        new_lm = new_page['metadata']['last_modified']
        if current_lm < new_lm:
            break
        index += 1

    if index < max_length:
        last_modified.insert(index, new_page)

    return last_modified[:max_length]


def add_page_to_sitemap(page_info: dict, folder: str, sitemap: dict):
    """ Add page info to sitemap """
    updated_folder = sitemap.get(folder, [])
    updated_folder.append(page_info)
    sitemap[folder] = updated_folder
    return sitemap


def fill_frame(frame: str, content: str, metadata: dict) -> str:
    """ Fill out HTML frame with page information """
    frame = frame.replace('{{title}}', metadata.get('title', ''))
    frame = frame.replace('{{description}}', metadata.get('description', ''))
    frame = frame.replace('{{content}}', content)
    return frame


def make_fatfile(info: dict, fatfile: str, frame: str, output_dir: str):
    """ Make fatfile out of content of every page """
    fatfile = re.sub(re.compile(r'\sid=".*?"'), '', fatfile)
    fatfile = '<h1>Fatfile</h1><p>This file contains the contents of every page in the wiki in no order whatsoever.</p>' + fatfile
    fatfile = place_in_container('section', 'fatfile', fatfile)
    fatfile = place_in_container('main', 'main', fatfile)
    filled_frame = fill_frame(frame, fatfile, info.get('metadata', dict()))
    with open(os.path.join(output_dir, 'fatfile.html'), 'w') as f:
        f.write(filled_frame)


def make_recent_list(last_modified: list) -> str:
    if len(last_modified) == 0:
        return ''

    html = '<section class="recent-list"><h2>Recent Changes:</h2><ul>'
    for page in last_modified:
        lm = page['metadata']['last_modified']
        title = page['metadata']['title']
        html += f'''<li>{lm}: <a href="{links.kebabify(title)}.html">{title}</a></li>'''
    html += '</ul></section>'
    return html


def make_sitemap(index: dict, sitemap: dict, recent_list: list, frame: str):
    """ Make sitemap out of index and all seen pages """
    index_html = f'<h1 id="title">{index["metadata"].get("title", "Sitemap")}</h1>'
    index_html += marko.convert(index.get('content', ''))
    index_html += make_recent_list(recent_list)
    
    sitemap_html = ''

    def convert_folder_to_html(folder_name: str, display_name: str = None) -> str:
        if not display_name:
            display_name = folder_name if folder_name else "[root]"
        display_name = display_name.replace('/', '/<wbr/>')
        html = ''
        sorted_folder_list = sorted(sitemap.get(folder_name), key=lambda page_info: page_info.get('title').lower())
        html += f'<details><summary>{display_name}</summary><ul>'
        for page in sorted_folder_list:
            title, filename = page.get('title'), page.get('filename')
            html += f'<li><a href="{filename}.html">{title}</a></li>'
        html += '</ul></details>'
        html = place_in_container('div', None, html)
        return html

    sorted_folders = sorted(sitemap.keys(), key=lambda folder_name: folder_name.lower())
    for folder in sorted_folders:
        if folder == '.stubs':
            continue
        sitemap_html += convert_folder_to_html(folder)

    if sitemap.get('.stubs'):
        sitemap_html += convert_folder_to_html('.stubs', 'Wiki Stubs')

    page_html = place_in_container('main', 'main', index_html + sitemap_html)
    return fill_frame(frame, page_html, index.get('metadata', dict()))


################
# Wiki Builder #
################


def make_wiki(pages_dir: str, output_dir: str, build_config: dict):
    """ Create flat wiki out of all pages """
    pages = dict()
    media_files = set()

    ff_bytes = 0
    last_modified_pages = list()

    with open(os.path.join(pages_dir, '_swiki', 'frame.html'), 'r') as f:
        frame_bytes = len(f.read().encode('utf-8'))

    for subfolder, _, files in os.walk(pages_dir):
        rel_path = subfolder.replace(pages_dir, '').lstrip('/')
        # Ignore all folders with preceding underscore
        if rel_path and rel_path[0] == '_':
            continue
        for file in files:
            filename, extension = os.path.splitext(file)
            # Ignore all files with preceding underscore or non-Markdown files
            if filename[0] == '_' or filename in IGNORE:
                continue
            if extension != '.md':
                if file in media_files:
                    raise RuntimeError(f'''File "{rel_path}/{file}" conflicts with another file "{file}".''')
                copy_media(subfolder, file, output_dir)
                media_files.add(file)
                continue
            page = make_page_dict(pages_dir, rel_path, file)
            page_filename = links.kebabify(page['metadata'].get('title') or filename)
            if page_filename in RESERVED:
                page_filename += '_'

            ff_bytes += len(page.get('content', '').encode('utf-8')) + frame_bytes
            if build_config.get('recent_list'):
                last_modified_pages = add_to_last_modified_pages(page, last_modified_pages, build_config.get('recent_list_length'))

            # add backlinks to all pages this page links to
            for link in page['links']:
                link_filename = links.kebabify(link)
                # if page being linked to does not yet exist, give it the title
                # as seen in the current page (e.g. Bob Fossil, not bob-fossil).
                # This will be overwritten by the given title if the page exists.
                if not pages.get(link_filename):
                    pages[link_filename] = dict()
                if not pages[link_filename].get('metadata'):
                    pages[link_filename]['metadata'] = {'title': link, 'description': ''}
                if not pages[link_filename].get('backlinks'):
                    pages[link_filename]['backlinks'] = []
                # add current page to "backlinks"
                pages[link_filename]['backlinks'].append({'title': page['metadata'].get('title', page_filename),
                                                          'filename': page_filename})

            # add page info to pages dict
            if pages.get(page_filename) and pages[page_filename].get('folder') is not None:
                current_folder = page.get('folder') + '/' if page.get('folder') else ''
                existing_folder = rel_path + '/' if rel_path else ''
                raise RuntimeError(f'''Page "{current_folder}{page['metadata'].get('title')}" with filename "{page_filename}" conflicts with page "{existing_folder}{pages[page_filename]['metadata'].get('title')}" with filename "{page_filename}".''')
            elif pages.get(page_filename):
                pages[page_filename] |= page
            else:
                pages[page_filename] = page

    swiki_dir = os.path.join(pages_dir, '_swiki')

    # If there is an index file, build page dict
    if os.path.isfile(os.path.join(swiki_dir, 'index.md')):
        pages['{{SITE INDEX}}'] = make_page_dict(pages_dir, '_swiki', 'index.md', True)

    # Load frame file
    with open(os.path.join(swiki_dir, 'frame.html'), 'r') as f:
        frame = f.read()
        # Remove extra space in frame code
        frame = re.sub(r'(?<=\n)\s*', '', frame)
        frame = re.sub(r'(?<=>)\s*(?=<)', '', frame)
        frame = re.sub(re.compile(r'(?<=[;{}(*/)])[\s]*'), '', frame)
        ff_bytes *= 1.024  # roughly correct at least for my purposes
        if ff_bytes < 1_000_000:
            ff_size = f"~{int(ff_bytes // 1_000)}kb"
        else:
            ff_size = f"~{round(ff_bytes / 1_000_000, 2)}mb"
        frame = frame.replace('{{ff_size}}', ff_size)

    # Build all files and populate sitemap dict
    sitemap = dict()
    fatfile = ''
    index = {'metadata': dict()}
    for filename, info in pages.items():
        # If it's the index/sitemap page, don't build it
        if info.get('index'):
            index = info
            continue
        # If page is linked to but it hasn't been made yet, give it placeholder metadata
        if not info.get('metadata'):
            info['metadata'] = dict()
        info['metadata'] = {'title': info['metadata'].get('title', filename),
                            'description': info['metadata'].get('description', ''),
                            'last_modified': info['metadata'].get('last_modified', '')}

        content = marko.convert(info.get('content', 'There\'s currently nothing here.'))
        content = content.replace('\t', ' ' * build_config.get('tab_size'))
        content = dedent(f'''\
            <h1 id="title">{info["metadata"].get("title")}</h1>\n\
            {content}''')
        content = links.add_external(content)
        content = links.add_local(content)
        content = links.add_backlinks(content, info.get('backlinks', []))
        content = add_last_modified(content, info['metadata'].get('last_modified'))

        if build_config.get('build_fatfile'):
            fatfile_content = re.sub(rf'(?<=<h1 id="title">){info["metadata"].get("title")}(?=</h1>)',
                                     f'<a href="{filename}.html">{info["metadata"].get("title")}</a>',
                                     content)
            fatfile += place_in_container('article', None, fatfile_content)

        content = place_in_container('article', 'content', content)
        content = place_in_container('main', 'main', content)
        filled_frame = fill_frame(frame, content, info.get('metadata', dict()))

        with open(os.path.join(output_dir, f'{filename}.html'), 'w') as f:
            f.write(filled_frame)

        sitemap = add_page_to_sitemap({'title': info['metadata'].get('title'), 'filename': filename},
                                      # If no folder here, then it is a stub
                                      info.get('folder', '.stubs'),
                                      sitemap)

    if build_config.get('build_fatfile'):
        fatfile_title = 'Fatfile'
        if site_title := index["metadata"].get("title"):
            fatfile_title = f'{site_title} - Fatfile'
        fatfile_description = index["metadata"].get("description", "")
        fatfile_info = {'metadata': {
            'title': fatfile_title,
            'description': fatfile_description
        }}
        make_fatfile(fatfile_info, fatfile, frame, output_dir)
    filled_frame = make_sitemap(index, sitemap, last_modified_pages, frame)
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
            f.write(filled_frame)
    copy_css_file(pages_dir, output_dir)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Create wiki at output dir from input dir.')
    argparser.add_argument('input_dir', metavar='input', type=str, help='the path to the input directory')
    argparser.add_argument('output_dir', metavar='output', type=str, help='the path to the output directory')
    argparser.add_argument('--delete-current-html', '-d', action='store_true', help='delete all HTML in output directory before building')
    argparser.add_argument('--no-fatfile', '-nf', action='store_false', default=True, dest="build_fatfile", help='do not create fatfile on build')
    argparser.add_argument('--recent-list', '-rl', default=False, action="store_true", help='create most recently modified pages list on index')
    argparser.add_argument('--recent-list-length', '-rll', default=10, help='length of most recently modified pages list')
    args = argparser.parse_args()

    if not os.path.isdir(args.input_dir):
        sys.exit(f'Input folder not found: {args.input_dir}')
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    if args.delete_current_html:
        delete_current_html(args.output_dir)

    config = {
        'tab_size': 2,
        'build_fatfile': args.build_fatfile,
        'recent_list': args.recent_list,
        'recent_list_length': args.recent_list_length,
    }
    config_fp = os.path.join(args.input_dir, '_swiki', 'config.ini')
    if os.path.isfile(config_fp):
        update_config(config, config_fp)

    make_wiki(args.input_dir, args.output_dir, config)
