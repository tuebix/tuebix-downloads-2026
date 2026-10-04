#!/usr/bin/env python3
from pathlib import Path
import shutil
from jinja2 import Environment, select_autoescape
import subprocess
import tempfile
import urllib.parse

repo = Path(__file__).parent

public = Path("public")
public.mkdir()

template_str = """
<ul>
{% for name, url in links %}
<li> <a href="{{ url }}">{{ name }}</a> </li>
{% endfor %}
</ul>
"""

links = []
for fp in repo.iterdir():
    fn = fp.parts[-1]
    if fn.startswith("."):
        continue
    if fn in [
        "README.md",
        "sitegen.py",
        "public",
        "style.css",
    ]:
        continue

    if fp.is_dir():
        shutil.make_archive(public / fp.parts[-1], "zip", fp)
        hr_name = fp.parts[-1]
        outfn = fp.parts[-1] + ".zip"
    elif fp.is_file():
        shutil.copy(fp, public / fp.parts[-1])
        hr_name = fp.stem
        outfn = fp.parts[-1]
    else:
        raise ValueError
    links.append((hr_name, urllib.parse.quote(outfn)))

env = Environment(autoescape=select_autoescape())
template = env.from_string(template_str)
rendered = template.render(links=links)

with tempfile.NamedTemporaryFile(suffix=".html") as tmp:
    tmp.write(rendered.encode())
    tmp.flush()
    subprocess.check_call(
        [
            "pandoc",
            "--standalone",
            "--embed-resources",
            "--metadata",
            "title=Folien etc. der Tübix-Vorträge zum herunterladen",
            "--output",
            Path(public / "index.html"),
            "--css",
            Path(repo / "style.css"),
            tmp.name,
        ]
    )
