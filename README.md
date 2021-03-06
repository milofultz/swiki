# Ported to codeberg: https://codeberg.org/milofultz/swiki

# {{SWIKI}}

Make a wiki with backlinking from [Markdown][] fast.

## Installation

* Clone the repo.
* Install requirements with pip: `pip install -r requirements.txt`

## Usage

The Swiki takes in any folder of markdown files and a `frame.html` file to build a flat-file wiki system. Here's what you'll need:

### Pages

The necessary format for your pages are [Markdown][] files with [YAML/Jekyll front matter](https://jekyllrb.com/docs/front-matter/).

* The front matter currently uses the `title` and `description` fields. Note that these are case sensitive. Each page must have a unique name, once all [special characters](#special-characters) have been removed.
* Wiki-style links use `{{double curly braces}}` and are case insensitive. They can be made two ways (note that they reference the *title* in the front matter, not the *filename*):
    * `{{example}}` - Displays the text 'example' and goes to the page whose title is 'example'.
    * `{{shown text|example}}` - Displays the text 'shown text' and goes to the page whose title is 'example'.

#### Special Characters

These special characters in page titles end up being removed when converting to a filename: `/()'".!?,`

#### Non-Markdown Files

Any files that exist in your input directory or any subdirectories will be copied to the root directory of the output directory. Useful for linking to images, code files, or anything else you want to link to directly.

### `_swiki` Directory

Create a directory named `_swiki` in your input directory. This is where you will put the following files.

    _swiki
     ├─ frame.html
     ├─ styles.css
     ├─ index.md
     └─ config.ini

#### Frame

A `frame.html` file in the `_swiki` directory with all of your markdown files. This accepts `{{title}}`, `{{description}}`, and `{{content}}` tags, to fill in the title and description from the page's front matter and the content of the page. A sitemap will also be rendered at `index.html`, so you can link to that, too.

Tags | Description
--- | ---
`{{title}}` | Title described in the front matter of your index.md file
`{{description}}` | Description described in the front matter of your index.md file
`{{content}}` | The content within your index.md file

Here is an example that includes basic CSS to make a generally good looking and easy to read webpage.

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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

Instead of using a `<style>` tag in your frame file for styling, you can also link in CSS files. If you include CSS files in the `_swiki` folder, it will be copied over to the root of your output folder. For instance, if you had a file named `styles.css` and a file named `altstyle.css` in your `_swiki` folder, you could replace your `<style>...</style>` tags with `<link rel="stylesheet" href="./styles.css"><link rel="stylesheet alternate" href="./altstyle.css" title="Cool style">`.

#### Index/Sitemap

By default, `index.html` will be rendered in your wiki with a title of "Sitemap". The sitemap is organized by the structure of your markdown pages and which folders they reside in (e.g. a file in the root folder will be in a different section than a file in a subfolder). Any page that is linked to but does not yet exist will be in its own section at the bottom of the sitemap as a "stub".

To customize the title, description, and basic content preceding the sitemap, a file named `index.md` can be used.

```markdown
---
title: Website Title
description: This will become the meta description.
---

This will be prepended to the sitemap/index of your wiki.
```

#### Config File

A `config.ini` file can be used to overwrite certain parser parameters. For example:

    key_one = Value
    key_two = 123

Key | Effect | Default Value
--- | --- | ---
`recent_list` | Whether to build the [recent list](#recent-list) into the sitemap | `False`
`recent_list_length` | How many items should be included in the [recent list](#recent-list) | `10`
`tab_size` | How many spaces a tab character wil be converted to when parsing the page content | `2`

### Rendering

To render your wiki, run the script with the following syntax:

```bash
python3 swiki.py input_folder output_folder [flags]
```

Flag | Effect
--- | ---
`--delete-current-html`, `-d` | Non-recursively delete all existing HTML files in the build directory
`--recent-list`, `-rl` | Create a [recent changes list](#recent-list)
`--recent-list-length [n]`, `-rll [n]` | Set the length of the [recent list](#recent-list) to `n` entries
`--verbose`, `-v` | Print debug information during build to `build.log`. Use `-vv` for (many) more details

### Recent List

A list of recent changes will be created and placed below the content found in `index.md`, if provided.

### Ignoring Files and Folders

Any files or folders with a preceding underscore will be ignored in the rendering process.

#### Example

```markdown
---
title: Rendering A Page
description: This will become the meta description.
---

This is the content of the {{Markdown}} file. This {{Markdown reference|Markdown}} doesn't exist, but the {{page}} will.
```

This would render out five files, all using the frame:

* `index.html` - The index and sitemap, containing the rendered contents of `index.md` and a sitemap of all three above pages.
* `rendering-a-page.html` - The file you see above.
* `markdown.html` - This file exists with only backlinks, as no file with a title of 'Markdown' exists.
* `page.html` - This file exists with only backlinks, for the same reason.

## Future Improvements

- Add tags for categorical linking by meta ideas, like "#activities", etc.
- Make the index page have nested and indented subcategories (`details`/`summary`) instead of flat.

[Markdown]: https://spec.commonmark.org/0.29/
