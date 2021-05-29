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

# import marko

# create pages dict

# for each file in all subfolders
    # get front matter and markdown from file
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
