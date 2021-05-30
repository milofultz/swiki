# {{SWIKI}}

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
        <a href="index.html">Sitemap</a>
    </footer>
</body>
</html>
```

### Index/Sitemap

A file named `__index.md` can be used for the index and sitemap of your wiki. Whatever you put in here will be rendered as all the other pages will be, but with the sitemap appended to the end.

The sitemap is organized by the structure of your markdown pages and which folders they reside in (e.g. a file in the root folder will be in a different section than a file in a subfolder).

### Pages

[Markdown](https://spec.commonmark.org/0.29/) files with [YAML/Jekyll front matter](https://jekyllrb.com/docs/front-matter/) will be accepted and added into your wiki's file structure. 

* The front matter currently uses the `title` and `description` fields.
* Wiki-style links can be made to other pages with `{{double curly braces}}`. Note that this matches the *title* in the front matter, not the markdown file's *filename*.

```
---
title: Rendering A Page
description: This will become the meta description.
---

This is the content of the {{Markdown}} file. This {{reference}} doesn't exist.
```

This would render out four files:

* `rendering-a-page.html` - The file you see above.
* `markdown.html` - This file exists with only backlinks, as no file with a title of 'Markdown' exists.
* `reference.html` - This file also exists with only backlinks for the same reason.
* `index.html` - The index and sitemap, containing the rendered contents of `__index.md` and a sitemap of all three above pages.

### Rendering

To render your wiki, run the script with the following syntax:

```bash
python3 swiki.py path/to/markdown/folder path/to/output/folder
```
