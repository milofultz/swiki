from collections import defaultdict
import os
import re
import sys

import marko
import frontmatter


re_wikilink = re.compile(r'{{.+?}}')


def make_page_dict(subfolder: str, file: str, rel_path: str) -> dict:
    """ Make dict of all page specific data """
    page = dict()
    page['folder'] = rel_path
    with open(os.path.join(subfolder, file), 'r') as f:
        file_contents = f.read()
        page['metadata'], page['content'] = frontmatter.parse(file_contents)
    # get all local links in the file
    page['links'] = re_wikilink.findall(page.get('content'))
    return page


def add_page_to_sitemap(page_info: dict, folder: str, sitemap: defaultdict):
    """ Add page info to sitemap """
    updated_folder = sitemap.get(folder, [])
    updated_folder.append(page_info)
    sitemap[folder] = updated_folder
    return sitemap


def kebabify(text: str) -> str:
    """ Format text to filename kebab-case """
    return text.replace(' ', '-').lower()


def add_local_links(html: str) -> str:
    """ Replace all {{...}} with anchor tags """
    def make_link(match: re.Match):
        text = match.group()[2:-2].strip()
        filename = kebabify(text)
        return f'<a href="{filename}.html">{text}</a>'
    return re_wikilink.sub(make_link, html)


def place_in_container(element: str, html_id: str, content: str) -> str:
    """ Place content in container with ID """
    return f'<{element} id="{html_id}">{content}</{element}>'


def add_backlinks(content: str, backlinks: list) -> str:
    """ Add backlinks section to content """
    if not backlinks:
        return content
    backlinks_html = '<section id="backlinks"><h2>Backlinks:</h2><ul>'
    for backlink in backlinks:
        title, filename = backlink.get('title'), backlink.get('filename')
        backlinks_html += f'<li><a href="{filename}.html">{title}</a></li>'
    backlinks_html += '</ul></section>'
    return content + backlinks_html


def fill_frame(frame: str, content: str, metadata: dict) -> str:
    """ Fill out HTML frame with page information """
    frame = frame.replace('{{title}}', metadata.get('title'))
    frame = frame.replace('{{description}}', metadata.get('description'))
    frame = frame.replace('{{content}}', content)
    return frame


def make_sitemap(sitemap: dict, output_dir: str):
    """ Make sitemap out of all seen pages """
    sitemap_html = ''
    for folder, folder_list in sitemap.items():
        sitemap_html += f'<h2>{folder or "[root]"}</h2><ul>'
        # sort the contents on the folder list by title
        folder_list = sorted(folder_list, key=lambda page: page.get('title').lower())
        for page in folder_list:
            title, filename = page.get('title'), page.get('filename')
            sitemap_html += f'<li><a href="{filename}.html">{title}</a></li>'
        sitemap_html += '</ul>'
    sitemap_html = place_in_container('main', 'sitemap', sitemap_html)
    with open(os.path.join(output_dir, '_sitemap.html'), 'w') as f:
        f.write(sitemap_html)


def make_wiki(pages_dir: str, output_dir: str):
    """ Create flat wiki out of all pages """
    pages = defaultdict(dict)
    sitemap = defaultdict(dict)

    for subfolder, _, files in os.walk(pages_dir):
        for file in files:
            # if wiki meta file or not a markdown page, ignore it
            if file[0:2] == '__' or os.path.splitext(file)[1] != '.md':
                continue
            rel_path = subfolder.replace(pages_dir, '')
            page = make_page_dict(subfolder, file, rel_path)
            page_filename = kebabify(page['metadata'].get('title', os.path.splitext(file)[0]))

            # add backlinks to all pages this page links to
            for link in page['links']:
                link_filename = kebabify(link[2:-2])
                # if page not yet in pages or doesn't have a page yet, make an entry
                if not pages[link_filename].get('backlinks'):
                    pages[link_filename]['backlinks'] = []
                # add current page to "backlinks" prop
                pages[link_filename]['backlinks'].append({'title': page['metadata'].get('title'),
                                                          'filename': page_filename})

            # add page info to pages dict
            if pages.get(page_filename):
                pages[page_filename] |= page
            else:
                pages[page_filename] = page

    # Load HTML frame file
    with open(os.path.join(pages_dir, '__frame.html'), 'r') as f:
        frame = f.read()

    for page, info in pages.items():
        # If page is linked to but it hasn't been made yet, give it placeholder metadata
        if not info.get('metadata'):
            info['metadata'] = dict()
        info['metadata'] = {'title': info['metadata'].get('title', page),
                            'description': info['metadata'].get('description', '')}
        content = marko.convert(info.get('content', 'There\'s currently nothing here.'))
        # add a local link to any {{...}} words (href="lower-kebab-case-title.html")
        content = add_local_links(content)
        sitemap = add_page_to_sitemap({'title': info['metadata'].get('title'), 'filename': page},
                                      info.get('folder', ''),
                                      sitemap)
        content = f'<h1>{info["metadata"].get("title")}</h1>\n{content}'
        content = place_in_container('section', 'content', content)
        content = add_backlinks(content, info.get('backlinks', []))
        content = place_in_container('main', 'main', content)
        filled_frame = fill_frame(frame, content, info.get('metadata', []))

        with open(os.path.join(output_dir, f'{page}.html'), 'w') as f:
            f.write(filled_frame)

    make_sitemap(sitemap, output_dir)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit('Args must be input and output folder')
    _, root, output = sys.argv
    if not os.path.isdir(root):
        sys.exit('Input folder not found')
    if not os.path.isdir(output):
        os.mkdir(output)

    make_wiki(root, output)
