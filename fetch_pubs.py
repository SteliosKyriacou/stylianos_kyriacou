import urllib.request
import re
import json

urls = [
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:roLk4NBRz8UC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:LkGwnXOMwfcC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:ufrVoPGSRksC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:WF5omc3nYNoC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:eQOLeE2rZwMC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:IjCSPb-OGe4C",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:qjMakFHDy7sC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:2osOgNQ5qMEC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:YsMSGLbcyi4C",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:W7OEmFMy1HYC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:Tyk-4Ss8FVUC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:_FxGoFyzp5QC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:d1gkVwhDpl0C",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:u5HHmVD_uO8C",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:u-x6o8ySG0sC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:UeHWp8X0CEIC",
    "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=JQmiXi8AAAAJ&pagesize=100&sortby=pubdate&citation_for_view=JQmiXi8AAAAJ:9yKSN-GCB0IC"
]

results = []
for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Extract title
        title_match = re.search(r'<a class="gsc_oci_title_link" href="[^"]*">([^<]+)</a>', html)
        if not title_match:
            title_match = re.search(r'<div id="gsc_oci_title"[^>]*>.*?(?:<a[^>]*>)?([^<]+)(?:</a>)?</div>', html)
            
        title = title_match.group(1) if title_match else "Unknown Title"
        
        # Extract date
        date_match = re.search(r'<div class="gsc_oci_field">Publication date</div><div class="gsc_oci_value">([^<]+)</div>', html)
        date = date_match.group(1) if date_match else "Unknown Date"
        
        # Extract abstract
        abstract_match = re.search(r'<div class="gsc_oci_descr">.*?<div class="gsh_csp">(.*?)</div>', html, re.DOTALL)
        if not abstract_match:
            abstract_match = re.search(r'<div class="gsc_oci_value" id="gsc_oci_descr">(.*?)</div>', html, re.DOTALL)
        
        abstract = abstract_match.group(1) if abstract_match else "Abstract not available."
        
        # Extract venue/journal/conference (optional)
        venue_match = re.search(r'<div class="gsc_oci_field">(?:Journal|Conference|Book)</div><div class="gsc_oci_value">([^<]+)</div>', html)
        venue = venue_match.group(1) if venue_match else ""
        
        results.append({
            'title': title,
            'date': date,
            'abstract': abstract,
            'url': url,
            'venue': venue
        })
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# The user explicitly wants the enzyme one included (it's already in the HTML but manually added without a URL, wait no, let me add it manually)
enzyme_paper = {
    'title': 'Enzyme engineering by means of reaction space indexing coupled with machine learning algorithms',
    'date': '2022/8/7',
    'abstract': "Modern molecular manufacturing is limited in the products that can be built. Using catalysis by enzymes is often a preferred way to overcome these challenges. Every enzyme can catalyze thousands of diverse new-to-nature reactions, however, existing technologies test enzymes against only a few reactions at a time. Aether Biomachines is building a platform that enables indexing millions of possible enzyme-substrate reactions and optimization of reactions that are discovered throughout the process. Aether’s automated platform enables building thousands of variants, running miniaturized enzymatic experiments on high density plates to reduce per sample cost, and parallel detection of substrates-products combinations via mass spectrometry to maximize data rate per chip. Aether’s platform enables us to generate data at a scale and diversity that unlocks an unprecedented capacity to index reaction space.<br><br>Aether’s predictive models, trained on the aforementioned diverse datasets, learn the reaction space and, in combination with search and optimization algorithms, can algorithmically mine it. With those learnings comes the ability to propose enzymes performing desired reactions even if they have not been observed. Aether’s predictive models are hybrid physics/ML systems. The model's architecture is a message passing neural network where the graph embedding of the active site is featurized as a set of nodes (atoms) connected by edges (representing chemical bonds or enzyme-substrate interactions). Graph level features such as stability, accessibility and numerous descriptors are also included before the final deep dense part of the model.<br><br>The aforementioned strategy is demonstrated through a case study targeting a molecule with antiviral activity. The model’s ability to locate never seen before reactions will be quantified by the area under the True-Positive-Rate vs False-Positive-Rate curve for reactions intentionally hidden from their training set.",
    'url': None,
    'venue': '2022 SIMB Annual Meeting'
}
results.append(enzyme_paper)

# Sort by date descending
# Date format is usually YYYY/MM/DD or YYYY
def parse_date(d):
    parts = d.split('/')
    if len(parts) == 1:
        return (int(parts[0]), 0, 0)
    elif len(parts) == 2:
        return (int(parts[0]), int(parts[1]), 0)
    else:
        return (int(parts[0]), int(parts[1]), int(parts[2]))

results.sort(key=lambda x: parse_date(x['date']), reverse=True)

with open('pubs.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Done")
