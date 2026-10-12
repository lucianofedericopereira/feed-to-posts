#!/usr/bin/env python3
"""Render feed entries as pinned-repository style SVG cards, one file per post."""
import html
import math
import os
import re
import urllib.request
from pathlib import Path

# Octicons "repo" 16px (MIT, github.com/primer/octicons)
REPO_ICON = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8"
             "a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8Z"
             "M5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7"
             "a.25.25 0 0 1-.4-.2Z")

NEUTRAL = '#858585'
WORDS_PER_MINUTE = 200

STYLE = '''  <style>
    .sans {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", "DejaVu Sans", Helvetica, Arial, sans-serif; }}
    .primary {{ fill: #1f2328; }}
    .muted   {{ fill: #57544e; }}
    .accent  {{ fill: #0969da; }}
    .rule    {{ stroke: #57544e; stroke-opacity: .35; }}
    @media (prefers-color-scheme: dark) {{
      .primary {{ fill: #f0f6fc; }}
      .muted   {{ fill: #b1aea7; }}
      .accent  {{ fill: #4493f8; }}
      .rule    {{ stroke: #b1aea7; }}
    }}
    .narrow {{ display: none; }}
    @media (max-width: 260px) {{ .wide {{ display: none; }} .narrow {{ display: inline; }} }}
    {custom_css}
  </style>'''


def parse_colors(spec):
    """Parse "Code=#6e7695, Design=#bc776f" into {'Code': '#6e7695', 'Design': '#bc776f'}"""
    colors = {}
    for pair in (spec or '').split(','):
        if '=' in pair:
            name, color = (part.strip() for part in pair.split('=', 1))
            if name and color:
                colors[name] = color
    return colors


def split_title(full):
    """Split "Code › Linknim: A Bookmark Server" into section, name and subtitle"""
    section, title = '', full.strip()
    if '›' in title:
        section, title = (part.strip() for part in title.split('›', 1))
    name, _, subtitle = title.partition(':')
    return section, name.strip(), subtitle.strip()


def wrap(text, width, lines):
    """Word-wrap into at most `lines` lines of `width` characters, ending in … when cut"""
    words = text.split()
    out, current = [], ''
    for word in words:
        if len(current) + len(word) + (1 if current else 0) <= width:
            current = f'{current} {word}'.strip()
        else:
            out.append(current)
            current = word
            if len(out) == lines:
                break
    else:
        if current:
            out.append(current)
    out = [line for line in out[:lines] if line]
    if out and len(' '.join(out)) < len(text.strip()):
        last = out[-1]
        while len(last) + 1 > width and ' ' in last:
            last = last.rsplit(' ', 1)[0]
        out[-1] = last.rstrip(',.;:—-') + '…'
    return out


def reading_minutes(link):
    """Minutes to read the post's Markdown twin (link + .md), or None if it is not published"""
    try:
        with urllib.request.urlopen(link.rstrip('/') + '.md', timeout=20) as response:
            text = response.read().decode('utf-8', 'replace')
    except Exception:
        return None
    text = re.sub(r'^---.*?---', '', text, flags=re.S)
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    words = len(re.findall(r"[A-Za-z0-9À-ÿ'’-]+", text))
    return max(1, math.ceil(words / WORDS_PER_MINUTE)) if words else None


def plain(text):
    """Strip tags and entities from a feed description"""
    return html.unescape(re.sub(r'<[^>]+>', '', text or '')).strip()


def render_card(entry, colors, custom_css):
    """One card: repo icon, name in link colour, subtitle, two-line extract, section dot and reading time"""
    section, name, subtitle = split_title(entry.get('title', 'No title'))
    extract = plain(entry.get('summary', ''))
    if extract.lower().startswith(name.lower()):
        extract = extract[len(name):].lstrip(' :—-')
    minutes = reading_minutes(entry.get('link', ''))

    footer = ' · '.join(part for part in (section, f'{minutes} min read' if minutes else '') if part)
    color = colors.get(section, NEUTRAL)
    e = html.escape
    lines = ''.join(f'\n    <text class="sans muted" x="20" y="{92 + i * 18}" font-size="13">{e(line)}</text>'
                    for i, line in enumerate(wrap(extract, 46, 2)))
    sub = f'\n    <text class="sans primary" x="20" y="62" font-size="14">{e(wrap(subtitle, 40, 1)[0])}</text>' if subtitle else ''
    dot = f'\n    <circle cx="26" cy="131" r="6" fill="{color}"/>' if section else ''
    foot_x = 38 if section else 20
    narrow_foot = f'{minutes} min' if minutes else section
    aria = ' · '.join(part for part in (name + (f': {subtitle}' if subtitle else ''), footer) if part)

    return f'''<svg viewBox="-8 -8 416 166" width="416" height="166" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{e(aria)}">
{STYLE.format(custom_css=custom_css)}
  <rect class="rule" x=".5" y=".5" width="399" height="149" rx="12" stroke-width="1"/>
  <g class="wide">
    <path class="muted" transform="translate(20 19)" d="{REPO_ICON}"/>
    <text class="sans accent" x="46" y="33" font-size="16" font-weight="600">{e(name)}</text>{sub}{lines}{dot}
    <text class="sans muted" x="{foot_x}" y="135" font-size="13">{e(footer)}</text>
  </g>
  <g class="narrow">
    <path class="muted" transform="translate(20 22) scale(2.25)" d="{REPO_ICON}"/>
    <text class="sans accent" x="20" y="96" font-size="34" font-weight="600">{e(wrap(name, 14, 1)[0])}</text>{f"""
    <circle cx="32" cy="128" r="10" fill="{color}"/>""" if section else ''}
    <text class="sans muted" x="{52 if section else 20}" y="137" font-size="26">{e(narrow_foot)}</text>
  </g>
</svg>
'''


def build_cards(entries, count, cards_dir, readme_path, colors, custom_css=''):
    """Write the newest cards (an even number, at most `count`) and return the README markup linking them"""
    dated = sorted(entries, key=lambda x: tuple(x.get('published_parsed') or x.get('updated_parsed') or ()), reverse=True)
    count = min(count, len(dated)) // 2 * 2
    out = Path(cards_dir)
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob('card-*.svg'):
        stale.unlink()

    rel = os.path.relpath(out, Path(readme_path).resolve().parent).replace(os.sep, '/')
    markup = []
    for i, entry in enumerate(dated[:count], 1):
        (out / f'card-{i}.svg').write_text(render_card(entry, colors, custom_css), encoding='utf-8')
        _, name, subtitle = split_title(entry.get('title', ''))
        alt = html.escape(name + (f': {subtitle}' if subtitle else ''), quote=True)
        link = html.escape(entry.get('link', '#'), quote=True)
        markup.append(f'<a href="{link}"><img width="45%" src="./{rel}/card-{i}.svg" alt="{alt}"></a>')

    rows = ['&nbsp;\n'.join(markup[i:i + 2]) for i in range(0, len(markup), 2)]
    return '<p align="center">\n' + '\n<br>\n'.join(rows) + '\n</p>' if rows else ''
