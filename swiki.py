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


def kebabify(text: str) -> str:
    return text.replace(' ', '-').lower()


def add_local_links(html: str) -> str:
    def make_link(match: re.Match):
        text = match.group()[2:-2]
        filename = kebabify(text)
        return f'<a href="{filename}.html">{text}</a>'
    return re_wikilink.sub(make_link, html)


def make_wiki(pages_dir: str):
    # create pages dict
    pages = defaultdict(dict)

    # for each page in pages
    for subfolder, _, files in os.walk(pages_dir):
        for file in files:
            page = dict()
            page_filename = kebabify(os.path.splitext(file)[0])
            # split relative path into folders and set "folder" to that or just ['.']
            page['folder'] = os.path.split(subfolder)
            with open(os.path.join(subfolder, file), 'r') as f:
                file_contents = f.read()
                # get front matter and markdown from file
                page['metadata'], page['content'] = frontmatter.parse(file_contents)
            # get all local links in the file and add to dict "links" prop
            page['links'] = re_wikilink.findall(page.get('content'))

            # for each link
            for link in page['links']:
                # Remove the curlys and kebabify
                link_filename = kebabify(link[2:-2])
                # if page not in dict, make one
                if not pages[link_filename].get('backlinks'):
                    pages[link_filename]['backlinks'] = []
                # add current page to "backlinks" prop
                pages[link_filename]['backlinks'].append(page_filename)

            # add page info to pages dict
            if pages.get(page_filename):
                pages[page_filename] |= page
            else:
                pages[page_filename] = page


    # for each page in dict
    for page, info in pages.items():
        # render the markdown
        html = marko.convert(info.get('content', ''))
        # add a local link to any {{...}} words (href="lower-kebab-case-title.html")
        html_with_links = add_local_links(html)
        # fill HTML `head` with front matter
        # put into HTML frame (has everything but the content)
        print(html_with_links)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit('Args must be input and output folder')
    _, root, output = sys.argv
    if not os.path.isdir(root):
        sys.exit('Input folder not found')
    if not os.path.isdir(output):
        os.mkdir(output)

    make_wiki(root)
