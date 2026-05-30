#!/usr/bin/env python3
"""Generate HTML index and post pages for Horizon GitHub Pages."""
import urllib.request, json, os, sys

tree_url = "https://api.github.com/repos/sun-kic/Horizon/git/trees/gh-pages?recursive=1"
req = urllib.request.Request(tree_url, headers={"Accept": "application/vnd.github.v3+json"})
try:
    with urllib.request.urlopen(req) as resp:
        tree_data = json.loads(resp.read())
except Exception as e:
    print(f"Failed to fetch gh-pages tree: {e}")
    tree_data = {"tree": []}

posts = []
for item in tree_data.get('tree', []):
    path = item['path']
    if path.startswith('_posts/') and path.endswith('.md') and '-zh' in path:
        posts.append(path)
posts.sort(reverse=True)
posts = posts[:15]

# Generate index.html
index_lines = [
    "<!DOCTYPE html>",
    '<html lang="zh-CN">',
    "<head>",
    '<meta charset="UTF-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    "<title>Horizon Daily</title>",
    "<style>",
    "body { font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.7; color: #333; }",
    "h1 { border-bottom: 2px solid #0066cc; padding-bottom: 0.5rem; color: #0066cc; }",
    "h2 { color: #444; margin-top: 2rem; }",
    "ul { list-style: none; padding: 0; }",
    "li { padding: 0.6rem 0; border-bottom: 1px solid #eee; }",
    "a { color: #0066cc; text-decoration: none; }",
    "a:hover { text-decoration: underline; }",
    ".rss-notice { background: #fff3cd; padding: 1rem; border-radius: 8px; margin: 1.5rem 0; border-left: 4px solid #e67e22; }",
    ".rss-link { font-weight: bold; color: #e67e22; }",
    ".back-link { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee; color: #888; }",
    ".intro { background: #f5f5f5; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; }",
    ".intro p { margin: 0.5rem 0; }",
    ".nav-links { margin: 1rem 0; }",
    ".nav-links a { margin-right: 1.5rem; }",
    "</style>",
    "</head>",
    "<body>",
    "<div class='nav-links'>",
    "<a href='index.html'>首页</a>",
    "<a href='feed-zh.xml'>RSS 中</a>",
    "<a href='feed-en.xml'>RSS EN</a>",
    "</div>",
    "<h1>Horizon Daily</h1>",
    "<div class='intro'>",
    "<p>欢迎来到 <a href='https://github.com/thysrael/Horizon'>Horizon</a>，一个 AI 驱动的信息聚合系统。</p>",
    "<p>每日简报由 AI 自动生成，涵盖 GitHub Trending、Hacker News 等多个信息源。</p>",
    "</div>",
    "<h2>最新内容</h2>",
    "<ul>",
]

for post in posts:
    date = post.split('/')[1].split('-')[0:3]
    date_str = '-'.join(date)
    post_html = post.replace('_posts/', 'posts/').replace('.md', '.html')
    index_lines.append(f"<li><a href='{post_html}'>{date_str} 中文简报</a></li>")

index_lines.extend([
    "</ul>",
    "<div class='rss-notice'>",
    "<strong>订阅提醒：</strong>",
    "你可以使用 RSS 阅读器订阅简报：",
    "<a class='rss-link' href='feed-zh.xml'>中文 RSS</a> | ",
    "<a class='rss-link' href='feed-en.xml'>English RSS</a>",
    "</div>",
    "<div class='back-link'>",
    "<a href='https://github.com/thysrael/Horizon'>Horizon 项目主页</a>",
    "</div>",
    "</body>",
    "</html>",
])

with open('index.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(index_lines))
print(f"Generated index.html with {len(posts)} posts")

# Generate HTML pages for each post
base_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.7; color: #333; }}
h1 {{ border-bottom: 2px solid #0066cc; padding-bottom: 0.5rem; color: #0066cc; }}
a {{ color: #0066cc; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.back-link {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee; }}
pre {{ background: #f5f5f5; padding: 1rem; overflow-x: auto; border-radius: 6px; font-size: 0.85rem; }}
code {{ background: #f5f5f5; padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.85em; }}
blockquote {{ border-left: 4px solid #0066cc; margin: 1rem 0; padding: 0.5rem 1rem; background: #f9f9f9; color: #555; }}
</style>
</head>
<body>
<div style="margin-bottom: 2rem;">
  <a href="index.html">← 返回首页</a>
</div>
<h1>{title}</h1>
<pre>{content}</pre>
<div class="back-link">
  <a href="index.html">← 返回首页</a>
</div>
</body>
</html>"""

for post_path in posts:
    try:
        raw_url = f"https://raw.githubusercontent.com/sun-kic/Horizon/gh-pages/{post_path}"
        req = urllib.request.Request(raw_url)
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
        
        title = post_path.split('/')[1].replace('.md', '')
        html_content = base_html.format(title=title, content=content)
        html_path = post_path.replace('_posts/', 'posts/').replace('.md', '.html')
        
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated {html_path}")
    except Exception as e:
        print(f"Failed: {post_path} - {e}")

print("Done")