"""Row of buttons that open my PDFs in a new browser tab (Streamlit Cloud blocks iframe embeds)."""
import json


def render_doc_viewer(docs, colors, height=70):
    """docs is a list of {"label", "filename"}; each filename must be a file in the static/ folder."""
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
    embed_html(html, height=height, scrolling=False)
