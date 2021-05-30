"""
pages dict schema
{
    page_name: {
        "title": str,
        "description": str,
        "markdown": str,
        "folder": list[str],
        "links": list[str],
        "backlinks": list[str]
        "html": str
    },
    ...
}

"""

from collections import defaultdict
import os
import re
import sys

import marko
import frontmatter

re_wikilink = re.compile(r'{{.+?}}')


def make_page_dict(subfolder: str, file: str) -> dict:
    page = dict()
    # split relative path into folders and set "folder" to that or just ['.']
    page['folder'] = os.path.split(subfolder)
    with open(os.path.join(subfolder, file), 'r') as f:
        file_contents = f.read()
        # get front matter and markdown from file
        page['metadata'], page['content'] = frontmatter.parse(file_contents)
    # get all local links in the file and add to dict "links" prop
    page['links'] = re_wikilink.findall(page.get('content'))
    return page


def kebabify(text: str) -> str:
    return text.replace(' ', '-').lower()


def add_local_links(html: str) -> str:
    def make_link(match: re.Match):
        text = match.group()[2:-2]
        filename = kebabify(text)
        return f'<a href="{filename}.html">{text}</a>'
    return re_wikilink.sub(make_link, html)


def add_title(content: str, title: str) -> str:
    return f'<h1>{title}</h1>\n{content}'


def contain(content: str) -> str:
    return f'<section class="content">{content}</section>'


def add_backlinks(content: str, backlinks: list) -> str:
    # if no backlinks
    if not backlinks:
        # return content
        return content
    # create div
    backlinks_html = '<section id="backlinks">'
    # create heading and unordered list
    backlinks_html += '<h2>Backlinks:</h2><ul>'
    # for each link
    for backlink in backlinks:
        title, filename = backlink.get('title'), backlink.get('filename')
        # fill out list item and link inside
        backlinks_html += f'<li><a href="{filename}.html">{title}</a></li>'
    # close unordered list
    backlinks_html += '</ul>'
    # close div
    backlinks_html += '</section>'
    # append new div to content
    return content + backlinks_html


def fill_frame(frame: str, content: str, metadata: dict) -> str:
    frame = frame.replace('{{title}}', metadata.get('title'))
    frame = frame.replace('{{description}}', metadata.get('description'))
    frame = frame.replace('{{content}}', content)
    return frame


def make_wiki(pages_dir: str, output: str):
    # create pages dict
    pages = defaultdict(dict)

    # for each page in pages
    for subfolder, _, files in os.walk(pages_dir):
        for file in files:
            if file[0:2] == '__':
                continue
            page = make_page_dict(subfolder, file)
            page_filename = kebabify(page['metadata'].get('title'))

            # add backlinks to all pages this page links to
            for link in page['links']:
                # Remove the curlys and kebabify
                link_filename = kebabify(link[2:-2])
                # if page not in dict, make one
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

    with open(os.path.join(pages_dir, '__frame.html'), 'r') as f:
        frame = f.read()

    # for each page in dict
    for page, info in pages.items():
        if not info.get('metadata'):
            info['metadata'] = {'title': page, 'description': ''}
        # render the markdown
        if markdown := info.get('content', ''):
            content = marko.convert(markdown)
            # add a local link to any {{...}} words (href="lower-kebab-case-title.html")
            content = add_local_links(content)
        else:
            content = 'There\'s currently nothing here.'
        content = add_title(content, info['metadata'].get('title'))
        # put content into section container
        content = contain(content)
        # add backlinks
        content = add_backlinks(content, info.get('backlinks', []))
        # fill HTML `head` with front matter
        # put into HTML frame (has everything but the content)
        filled_frame = fill_frame(frame, content, info.get('metadata', []))
        with open(os.path.join(output, f'{page}.html'), 'w') as f:
            f.write(filled_frame)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit('Args must be input and output folder')
    _, root, output = sys.argv
    if not os.path.isdir(root):
        sys.exit('Input folder not found')
    if not os.path.isdir(output):
        os.mkdir(output)

    make_wiki(root, output)
