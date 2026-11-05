import json
import re

def clean_abstract(text):
    # Remove some common html tags that might be inside the abstract
    text = re.sub(r'<div class="gsh_small">', '', text)
    text = re.sub(r'<div class="gsh_csp">', '', text)
    text = re.sub(r'</div>', '', text)
    text = re.sub(r'<div>', '', text)
    text = re.sub(r'<i>', '', text)
    text = re.sub(r'</i>', '', text)
    return text.strip()

with open('pubs.json', 'r') as f:
    pubs = json.load(f)

# The list is already sorted by date in the JSON (newest first)

html_content = '<ul class="publications-list">\n'
for pub in pubs:
    title = pub['title']
    url = pub['url']
    date = pub['date']
    venue = pub['venue']
    abstract = clean_abstract(pub['abstract'])
    
    venue_date_str = ""
    if venue and date != "Unknown Date":
        venue_date_str = f"{venue} · {date}"
    elif venue:
        venue_date_str = venue
    elif date != "Unknown Date":
        venue_date_str = date

    html_content += '            <li>\n'
    if url:
        html_content += f'                <a href="{url}" target="_blank">{title}</a>\n'
    else:
        html_content += f'                <a style="cursor: text;">{title}</a>\n'
    
    if venue_date_str:
        html_content += f'                <div style="font-size: 14px; color: var(--text-secondary); margin-top: 5px;">{venue_date_str}</div>\n'
    
    if abstract and abstract != "Abstract not available.":
        html_content += '                <details style="margin-top: 10px;">\n'
        html_content += '                    <summary style="cursor: pointer; color: #4facfe; font-size: 14px; font-weight: 600;">View Abstract</summary>\n'
        html_content += f'                    <p style="margin-top: 10px; font-size: 14px; color: var(--text-secondary); line-height: 1.6;">{abstract}</p>\n'
        html_content += '                </details>\n'
    
    html_content += '            </li>\n'
html_content += '        </ul>'

# Read index.html
with open('index.html', 'r') as f:
    content = f.read()

# Replace the publications-list
pattern = re.compile(r'<ul class="publications-list">.*?</ul>', re.DOTALL)

# Be careful, there are multiple publications-list (Featured writing, Pet Projects, Patents, Publications)
# So we need to target the one inside <div id="publications"
def replacer(match):
    return html_content

# We only want to replace the one after <h3 class="section-title">Publications</h3>
split_str = '<div id="publications" class="container">\n        <h3 class="section-title">Publications</h3>\n        '
parts = content.split(split_str)
if len(parts) == 2:
    prefix = parts[0] + split_str
    # find the end of the ul
    ul_end = parts[1].find('</ul>') + 5
    suffix = parts[1][ul_end:]
    
    new_content = prefix + html_content + suffix
    
    with open('index.html', 'w') as f:
        f.write(new_content)
    print("Successfully updated index.html")
else:
    print("Could not find the Publications section accurately.")

