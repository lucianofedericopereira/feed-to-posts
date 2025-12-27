#!/usr/bin/env python3
import feedparser
import sys
import re
from datetime import datetime
from pathlib import Path

def fetch_feed(feed_url):
    """Fetch and parse RSS/Atom feed"""
    feed = feedparser.parse(feed_url)
    if feed.bozo:
        print(f"Warning: Feed parsing had issues: {feed.bozo_exception}", file=sys.stderr)
    return feed

def format_date(date_string, date_format):
    """Format date according to specified format"""
    try:
        dt = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            return date_string

    if "mmm. yyyy" in date_format.lower():
        return dt.strftime("%b. %Y")
    return dt.strftime("%Y-%m-%d")

def format_entry(entry, template, date_format):
    """Format a feed entry according to template"""
    title = entry.get('title', 'No title')
    link = entry.get('link', '#')

    published = entry.get('published', entry.get('updated', ''))
    formatted_date = format_date(published, date_format) if published else 'N/A'

    result = template.replace('$title', title)
    result = result.replace('$url', link)
    result = result.replace('$date', formatted_date)
    result = result.replace('$newline', '\n')

    return result

def update_readme(readme_path, feed_url, template, date_format, marker_start="<!-- BLOG-POST-LIST:START -->", marker_end="<!-- BLOG-POST-LIST:END -->"):
    """Update README.md with blog posts between markers"""

    feed = fetch_feed(feed_url)

    if not feed.entries:
        print("No entries found in feed", file=sys.stderr)
        return False

    formatted_entries = []
    for entry in feed.entries:
        formatted_entries.append(format_entry(entry, template, date_format))

    content = '\n'.join(formatted_entries)

    readme_file = Path(readme_path)
    if not readme_file.exists():
        print(f"README file not found: {readme_path}", file=sys.stderr)
        return False

    readme_content = readme_file.read_text(encoding='utf-8')

    if marker_start not in readme_content or marker_end not in readme_content:
        print(f"Markers not found in README. Please add:\n{marker_start}\n{marker_end}", file=sys.stderr)
        return False

    pattern = f"({re.escape(marker_start)}).*?({re.escape(marker_end)})"
    replacement = f"{marker_start}\n{content}\n{marker_end}"

    new_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

    if new_content == readme_content:
        print("No changes needed")
        return True

    readme_file.write_text(new_content, encoding='utf-8')
    print(f"Successfully updated {readme_path} with {len(feed.entries)} posts")
    return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Update README with blog posts from RSS/Atom feed')
    parser.add_argument('--feed-url', required=True, help='RSS/Atom feed URL')
    parser.add_argument('--readme-path', default='README.md', help='Path to README file')
    parser.add_argument('--template', default='$newline- [$title]($url)', help='Template for each entry')
    parser.add_argument('--date-format', default='UTC: mmm. yyyy', help='Date format string')

    args = parser.parse_args()

    success = update_readme(
        args.readme_path,
        args.feed_url,
        args.template,
        args.date_format
    )

    sys.exit(0 if success else 1)
