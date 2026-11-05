import base64

with open('assets/logos/tachyus.png', 'rb') as f:
    img_data = f.read()

b64_data = base64.b64encode(img_data).decode('utf-8')

# We need the dimensions of the image. For an SVG wrapper, 100% width and height is fine.
svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
    <image href="data:image/png;base64,{b64_data}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" />
</svg>'''

with open('assets/logos/tachyus.svg', 'w') as f:
    f.write(svg_content)

print("SVG created")
