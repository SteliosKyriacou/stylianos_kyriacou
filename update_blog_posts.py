import os
import glob
from bs4 import BeautifulSoup

# Define the HTML template with double braces for CSS
template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Stylianos Kyriacou</title>
    <link rel="stylesheet" href="../style.css">
    <style>
        .blog-post-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 40px;
            margin-bottom: 20px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">&larr; Back to Home</a>
        <div class="blog-post-content">
            {content}
        </div>
        <hr>
        <a href="../index.html" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""

blog_files = glob.glob('blog_posts/*.html')

for filepath in blog_files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already updated to prevent double wrapping
    if '<!DOCTYPE html>' in content:
        continue
        
    soup = BeautifulSoup(content, 'html.parser')
    h1 = soup.find('h1')
    title = h1.text if h1 else "Blog Post"
    
    # We remove the weird medium tracking pixel if it exists
    for img in soup.find_all('img'):
        if img.get('src', '').startswith('https://medium.com/_/stat'):
            img.decompose()
            
    clean_content = str(soup)
    
    new_html = template.format(title=title, content=clean_content)
    
    with open(filepath, 'w') as f:
        f.write(new_html)
        
print("Successfully updated all blog posts.")
