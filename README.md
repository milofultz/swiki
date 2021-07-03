# {{SWIKI}}

Make a wiki with backlinking from Markdown fast.

## Installation

* Clone the repo.
* Install requirements with pip: `pip install -r requirements.txt`

## Usage

The Swiki takes in any folder of markdown files and a `.frame.html` file to build a flat-file wiki system. Here's the bare minimum of what you need.

### Frame

A `.frame.html` file in the input directory with all of your markdown files. This accepts `{{title}}`, `{{description}}`, and `{{content}}` tags, to fill in the title and description from the page's front matter and the content of the page. A sitemap will also be rendered at `_sitemap.html`, so you can link to that, too. Here is an example 

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <meta name="description" content="{{description}}">
    <title>{{title}}</title>
    <style>
        html, body {
          margin: auto;
          max-width: 38rem;
          padding: 2rem;
        }
    </style>
</head>
<body>
    {{content}}

    <footer>
        <a href="index.html">Sitemap</a>
    </footer>
</body>
</html>
```

#### CSS File

For styling, you can put a `<style>` tag in your `frame` file or link in a CSS file. If you include a CSS file in the root of your input folder, it will be copied over to the root of your output folder.

### Index/Sitemap

A file named `.index.md` can be used for the index and sitemap of your wiki. Whatever you put in here will be rendered as all the other pages will be, but with the sitemap appended to the end.

The sitemap is organized by the structure of your markdown pages and which folders they reside in (e.g. a file in the root folder will be in a different section than a file in a subfolder).

```markdown
---
title: Website Title
description: This will become the meta description.
---

This will be prepended to the sitemap/index of your wiki.
```

### Fatfile

A `fatfile.html` will be created when making your wiki. This fatfile contains all of your page contents compiled into one huge file for easy searching. 

### Pages

[Markdown](https://spec.commonmark.org/0.29/) files with [YAML/Jekyll front matter](https://jekyllrb.com/docs/front-matter/) will be accepted and added into your wiki's file structure. 

* The front matter currently uses the `title` and `description` fields.
* Wiki-style links are made using `{{double curly braces}}` and are case insensitive. They can be made two ways (note that they reference the *title* not the *filename*):
    * `{{example}}` - Displays the text 'example' and goes to the page whose title is 'example'.
    * `{{shown text|example}}` - Displays the text 'shown text' and goes to the page whose title is 'example'.

```markdown
---
title: Rendering A Page
description: This will become the meta description.
---

This is the content of the {{Markdown}} file. This {{Markdown reference|Markdown}} doesn't exist, but the {{page}} will.
```

This would render out four files:

* `rendering-a-page.html` - The file you see above.
* `markdown.html` - This file exists with only backlinks, as no file with a title of 'Markdown' exists.
* `page.html` - This file exists with only backlinks, for the same reason.
* `index.html` - The index and sitemap, containing the rendered contents of `.index.md` and a sitemap of all three above pages.
* `fatfile.html` - The fatfile containing the contents of every page.

### Rendering

To render your wiki, run the script with the following syntax:

```bash
python3 swiki.py input_folder output_folder [flags]
```

Flag | Effect
--- | ---
--delete-current-html | Non-recursively delete all existing HTML files in the build directory
--no-fatfile | Do not create [fatfile](#fatfile) on build 

## Future Improvements

- Ignore files and folders with a preceding underscore
- Handle special characters in links and in backlinks. E.g. `{{async/await}}` throws because it resolves to `async/await.html`. Replace `/` with something else, like `:`? Also when a paren etc. is in the title, it just uses that. Should replace with something like the colon.
