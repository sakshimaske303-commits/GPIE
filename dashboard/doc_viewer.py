"""
Reusable no-download document viewer for Streamlit apps.
Renders a row of buttons; clicking one opens the PDF (served from
Streamlit's static file server) in a new browser tab, where the browser's
own PDF viewer displays it inline.

Why a new tab, not an embedded modal: an earlier version of this component
embedded the PDF inside an iframe drawn directly into the page (via
window.parent.document), which worked locally but failed once deployed --
Streamlit Community Cloud blocks iframe-embedding of app content as a
clickjacking protection, so the request came back as a browser-level
"refused to connect", not a missing-file or CORS error. Opening the same
same-origin static-file URL as a normal top-level navigation (a new tab)
sidesteps that restriction entirely, since no framing is involved.
"""
import streamlit.components.v1 as components
import json


def render_doc_viewer(docs, colors, height=70):
    """
    docs: list of {"label": str, "filename": str} -- filename must be the
          exact name of a file placed in the app's static/ folder.
    colors: dict with keys navy_dark, navy_med, magenta, teal, text_light
    height: px height of the button row component.
    """
    docs_json = json.dumps(docs)
    colors_json = json.dumps(colors)
    html = f"""
<style>
  .dv-row {{
    display: flex; flex-wrap: wrap; gap: 14px; justify-content: center;
    font-family: 'Poppins', sans-serif;
  }}
  .dv-btn {{
    border: none; border-radius: 6px; font-weight: 700; font-size: 14px;
    padding: 10px 22px; cursor: pointer; transition: .2s;
  }}
</style>
<div class="dv-row" id="dv-row"></div>
<script>
(function() {{
  var docs = {docs_json};
  var C = {colors_json};

  function appOrigin() {{
    try {{ return window.parent.location.origin; }} catch (e) {{ return window.location.origin; }}
  }}

  var row = document.getElementById('dv-row');
  docs.forEach(function(d) {{
    var btn = document.createElement('button');
    btn.className = 'dv-btn';
    btn.textContent = d.label;
    btn.style.backgroundColor = C.teal;
    btn.style.color = C.navy_dark;
    btn.onmouseenter = function() {{ btn.style.backgroundColor = C.magenta; btn.style.color = 'white'; }};
    btn.onmouseleave = function() {{ btn.style.backgroundColor = C.teal; btn.style.color = C.navy_dark; }};
    btn.onclick = function() {{
      var url = appOrigin() + '/app/static/' + encodeURIComponent(d.filename);
      window.open(url, '_blank');
    }};
    row.appendChild(btn);
  }});
}})();
</script>
"""
    components.html(html, height=height, scrolling=False)
