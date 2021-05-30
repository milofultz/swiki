# SWIKI

Make a wiki with backlinking from Markdown fast.

## Installation

* Clone the repo.
* Install requirements with pip: `pip install -r requirements.txt`

## Usage

The Swiki takes in any folder of markdown files and a `__frame.html` file to build a flat-file wiki system. Here's the bare minimum of what you need.

### Frame

A `__frame.html` file in the input directory with all of your markdown files. This accepts `{{title}}`, `{{description}}`, and `{{content}}` tags, to fill in the title and description from the page's front matter and the content of the page. A sitemap will also be rendered at `_sitemap.html`, so you can link to that, too. Here is an example 

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <meta name="description" content="{{description}}">
    <title>{{title}}</title>
</head>
<body>
    {{content}}

    <footer>
        <a href="_sitemap.html">Sitemap</a>
    </footer>
</body>
</html>
```

### Pages

[Markdown](https://spec.commonmark.org/0.29/) files with [YAML/Jekyll front matter](https://jekyllrb.com/docs/front-matter/) will be accepted and added into your wiki's file structure. 

* The front matter currently uses the `title` and `description` fields.
* Wiki-style links can be made to other pages with `{{double curly braces}}`. Note that this matches the *title* in the front matter, not the markdown file's *filename*.
* How you organize your markdown files will determine how the sitemap's file structure will be displayed. The sitemap is organized by folder name, and the folder's contents are sorted by title.

```
---
title: Rendering A Page
description: This will become the meta description.
---

stuff {{wikilink}} other stuff {{wiki link with space}}
```

### Rendering

To render your wiki, run the script with the following syntax:

```bash
python3 swiki.py path/to/markdown/folder path/to/output/folder
```
