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

import os
import sys

import marko
import frontmatter


def make_wiki(pages_dir: str):
    # create pages dict
    pages = dict()

    # for each page in pages
    for subfolder, _, files in os.walk(pages_dir):
        for file in files:
            with open(os.path.join(subfolder, file), 'r') as f:
                file_contents = f.read()
                # get front matter and markdown from file
                metadata, content = frontmatter.parse(file_contents)
            print(metadata, content)

            # get all local links in the file and add to dict "links" prop
            # for each link
                # if page not in dict, make one
                # add current page to "backlinks" prop
            # add a local link to any {{...}} words (href="lower-kebab-case-title.html")
            # split relative path into folders and set "folder" to that or just ['.']

    # for each page in dict
        # render the markdown
        # fill HTML `head` with front matter
        # put into HTML frame (has everything but the content)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit('Args must be input and output folder')
    _, root, output = sys.argv
    if not os.path.isdir(root):
        sys.exit('Input folder not found')
    if not os.path.isdir(output):
        os.mkdir(output)

    make_wiki(root)
