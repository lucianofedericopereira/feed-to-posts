# Feed to Posts

A lightweight Python script to automatically update your GitHub README with blog posts from RSS/Atom feeds. Perfect for showcasing your latest articles, tutorials, or blog posts directly on your GitHub profile.

## Features

- Fetches posts from any RSS/Atom feed
- Customizable templates for formatting
- Flexible date formatting
- Automatic README updates between markers
- No external dependencies except `feedparser`
- Easy integration with GitHub Actions

## Quick Start

### Local Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add markers to your README.md where you want posts to appear:
```markdown
<!-- BLOG-POST-LIST:START -->
<!-- BLOG-POST-LIST:END -->
```

3. Run the script:
```bash
python update_readme.py \
  --feed-url "https://yourblog.com/feed.xml" \
  --readme-path "README.md"
```

### GitHub Actions Integration

Add this workflow to `.github/workflows/update-blog.yml`:

```yaml
name: Update Blog Posts
on:
  schedule:
    - cron: "0 0 * * *"  # Run daily at midnight
  workflow_dispatch:  # Allow manual trigger

permissions:
  contents: write

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install -r feed-to-posts/requirements.txt

      - name: Update README with blog posts
        run: |
          python feed-to-posts/update_readme.py \
            --feed-url "https://yourblog.com/feed.xml" \
            --readme-path "README.md" \
            --template '$newline- [$title]($url) - $date'

      - name: Commit changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add README.md
          git diff --quiet && git diff --staged --quiet || git commit -m "Update blog posts"
          git push
```

## Configuration Options

### Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--feed-url` | Yes | - | URL of your RSS/Atom feed |
| `--readme-path` | No | `README.md` | Path to your README file |
| `--template` | No | `$newline- [$title]($url)` | Template for formatting each post |
| `--date-format` | No | `UTC: mmm. yyyy` | Date format string |

### Template Variables

Use these variables in your `--template` string:

- `$title` - Post title
- `$url` - Post URL
- `$date` - Publication date (formatted according to `--date-format`)
- `$newline` - Line break

### Template Examples

**Simple list:**
```bash
--template '$newline- [$title]($url)'
```
Output:
```
- [My First Post](https://example.com/post1)
- [My Second Post](https://example.com/post2)
```

**List with dates:**
```bash
--template '$newline- $date: [$title]($url)'
```
Output:
```
- Jan. 2024: [My First Post](https://example.com/post1)
- Dec. 2023: [My Second Post](https://example.com/post2)
```

**HTML table rows:**
```bash
--template '$newline<tr><td>$date</td><td align="left"><a href='"'"'$url'"'"'>$title</a></td></tr>'
```

Your README should include the table structure:
```html
<!-- BLOG-POST-LIST:START -->
<table>
<!-- BLOG-POST-LIST:END -->
</table>
```

Output:
```html
<table>
<tr><td>Jan. 2024</td><td align="left"><a href='https://example.com/post1'>My First Post</a></td></tr>
<tr><td>Dec. 2023</td><td align="left"><a href='https://example.com/post2'>My Second Post</a></td></tr>
</table>
```

### Date Format Options

The `--date-format` parameter supports common patterns:

- `"mmm. yyyy"` → `Jan. 2024`
- `"UTC: mmm. yyyy"` → `Jan. 2024` (UTC prefix is ignored)
- Custom formats use Python's `strftime` patterns

## Examples

### Example 1: Simple Markdown List

```bash
python update_readme.py \
  --feed-url "https://dev.to/feed/yourusername" \
  --template '$newline- [$title]($url)'
```

### Example 2: Numbered List with Dates

```bash
python update_readme.py \
  --feed-url "https://medium.com/feed/@yourusername" \
  --template '$newline1. **$title** ($date) - [Read more]($url)' \
  --date-format "mmm. yyyy"
```

### Example 3: Table Format

```bash
python update_readme.py \
  --feed-url "https://yourblog.com/feed.xml" \
  --template '$newline<tr><td>$date</td><td align="left"><a href='"'"'$url'"'"'>$title</a></td></tr>' \
  --date-format "mmm. yyyy"
```

README.md:
```markdown
## Latest Blog Posts

<!-- BLOG-POST-LIST:START -->
<table>
  <tr><th>Date</th><th>Title</th></tr>
<!-- BLOG-POST-LIST:END -->
</table>
```

## Troubleshooting

### Markers not found
Make sure your README.md contains:
```markdown
<!-- BLOG-POST-LIST:START -->
<!-- BLOG-POST-LIST:END -->
```

### No entries found
- Verify your feed URL is accessible
- Check that the feed contains valid RSS/Atom entries
- Try accessing the feed URL in a browser

### Changes not committing in GitHub Actions
- Ensure the workflow has `permissions: contents: write`
- Check that the README.md file exists in your repository

## Requirements

- Python 3.6+
- feedparser 6.0.11+

## License

MIT License - feel free to use this in your own projects!

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## Alternatives

This project was inspired by [gautamkrishnar/blog-post-workflow](https://github.com/gautamkrishnar/blog-post-workflow) but offers a simpler, more transparent Python-based approach that's easier to customize and debug.
