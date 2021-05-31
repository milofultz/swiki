import re

re_wikilink = re.compile(r'{{.+?}}')
re_external_link = re.compile(r'<a href=".+"')


def get_local(content: str) -> list:
    """ Get list of all local link filenames """
    local_links = list()
    for match in re_wikilink.finditer(content):
        match_text = match.group()[2:-2]  # remove curly braces
        local_links.append(match_text.rsplit('|')[-1].strip())  # filename if filename else text
    return local_links


def add_external(html: str) -> str:
    """ Modify all anchor tags for external links """
    def add_target_blank(match: re.Match):
        text = match.group()
        return f'{text} target="_blank"'
    return re_external_link.sub(add_target_blank, html)


def add_local(html: str) -> str:
    """ Replace all {{...|?...}} with anchor tags """
    def make_link(match: re.Match):
        match_text = match.group()[2:-2].split('|')
        text = filename = match_text[0].strip()
        if len(match_text) == 2:
            filename = match_text[1].strip()
        filename = kebabify(filename)
        return f'<a href="{filename}.html">{text}</a>'
    return re_wikilink.sub(make_link, html)


def add_backlinks(content: str, backlinks: list) -> str:
    """ Add backlinks section to content """
    if not backlinks:
        return content
    backlinks_html = '<section id="backlinks"><h2>Backlinks:</h2><ul>'
    seen_backlinks = set()
    for backlink in backlinks:
        title, filename = backlink.get('title'), backlink.get('filename')
        if title in seen_backlinks:
            continue
        seen_backlinks.add(title)
        backlinks_html += f'<li><a href="{filename}.html">{title}</a></li>'
    backlinks_html += '</ul></section>'
    return content + backlinks_html


def kebabify(text: str) -> str:
    """ Format text to filename kebab-case """
    return text.replace(' ', '-').lower()
