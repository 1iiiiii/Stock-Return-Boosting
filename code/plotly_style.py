"""Shared Plotly style for the Post 7 figures. Import once at the top of the figure notebook:

    from plotly_style import SITE, COLORS, base_layout, axis_style, source_note, save_html

Same site tokens as plot_style.py in the Post 4–6 repositories (copied from Personal Website/theme.scss),
so the interactive figures sit on the page background like the static ones did.

Figures carry a title, axis labels with units, a legend and a source line only.
No explanatory prose inside figures.
"""

SITE = {
    "paper": "#fffdf9",      # $paper: page background
    "ink": "#16130f",        # $ink: titles
    "muted": "#6e6559",      # $muted: axis labels, ticks
    "faint": "#857b6c",      # $faint: source line, reference lines
    "rule": "#e6dfd2",       # $rule: gridlines
    "axis": "#b5ab9b",       # $fainter: axis lines
}

COLORS = {
    "pre": "#2f5d7c",        # slate blue: the period before the break
    "post": "#a8442a",       # site $accent (rust): the period after the break
    "band": "#d19a3a",       # ochre: secondary series / confidence band
    "teal": "#4f7f73",       # muted teal: third categorical hue (S&P 500)
    "grey": SITE["faint"],
    "ink": SITE["ink"],
}

FONT = "Archivo, system-ui, -apple-system, 'Segoe UI', sans-serif"   # the site's sans-serif


def base_layout(title, height=520, legend_top=True):
    """Layout shared by every figure: site colours, left-aligned title, horizontal legend above the plot."""
    layout = dict(
        template="none",
        paper_bgcolor=SITE["paper"],
        plot_bgcolor=SITE["paper"],
        font=dict(family=FONT, size=13, color=SITE["muted"]),
        title=dict(text=f"<b>{title}</b>", font=dict(size=17, color=SITE["ink"]),
                   subtitle=dict(font=dict(size=12, color=SITE["muted"])),
                   x=0.01, xanchor="left", y=0.97, yanchor="top"),
        margin=dict(l=70, r=30, t=120, b=90),
        height=height,
        hoverlabel=dict(bgcolor="white", bordercolor=SITE["rule"],
                        font=dict(family=FONT, size=12, color=SITE["ink"])),
        hovermode="closest",
    )
    if legend_top:
        layout["legend"] = dict(orientation="h", x=0, xanchor="left", y=1.02, yanchor="bottom",
                                font=dict(color=SITE["muted"]), bgcolor="rgba(0,0,0,0)")
    return layout


def axis_style(title=None, **kw):
    """Recessive axis: light gridlines, no zero line, ticks outside."""
    d = dict(title=dict(text=title, font=dict(color=SITE["muted"])) if title else None,
             showgrid=True, gridcolor=SITE["rule"], gridwidth=1,
             zeroline=False, showline=True, linecolor=SITE["axis"],
             ticks="outside", tickcolor=SITE["axis"], tickfont=dict(color=SITE["muted"]))
    d.update(kw)
    return d


def source_note(fig, text, y=-0.16):
    """Source line in the bottom-left corner, outside the plot area (paper coordinates).
    Lower y (more negative) when a range slider sits below the axis."""
    fig.add_annotation(text=f"Source: {text}", xref="paper", yref="paper", x=0, y=y,
                       xanchor="left", yanchor="top", showarrow=False, align="left",
                       font=dict(size=11, color=SITE["faint"]))


def save_html(fig, path):
    """Self-contained HTML page (plotly.js from the CDN) that the post embeds in an iframe.
    `responsive` lets the figure follow the iframe width on phones."""
    fig.write_html(
        path, include_plotlyjs="cdn", full_html=True,
        config={"responsive": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]},
    )
    return path


# ---------------------------------------------------------------------------------------------------
# Added for Post 8. Two independent controls (for example "portfolio" and "resamples") cannot be built
# with Plotly's own updatemenus, because each menu overwrites the other's trace visibility. This writes
# the figure into a page with plain <select> controls; each combination of choices maps to a list of
# trace visibilities and, optionally, a layout update (an annotation, an axis title).
# ---------------------------------------------------------------------------------------------------
import json as _json

_CONTROL_CSS = """
body{margin:0;background:%(paper)s;font-family:%(font)s;color:%(muted)s}
.controls{display:flex;flex-wrap:wrap;gap:14px 28px;padding:10px 16px 0 16px;font-size:13px}
.controls label{display:flex;align-items:center;gap:8px}
.controls select{font-family:inherit;font-size:13px;color:%(ink)s;background:#fff;border:1px solid %(axis)s;
  border-radius:4px;padding:3px 6px}
"""


def save_html_controls(fig, path, controls, visibility, layouts=None, default=None):
    """fig: the Plotly figure with every trace for every combination already added.
    controls: list of (name, label, [options]) in the order shown; each option a string.
    visibility: dict keyed by "opt1|opt2|…" (one entry per combination) → list of booleans, one per trace.
    layouts: optional dict with the same keys → Plotly relayout dict (annotations, axis ranges …).
    default: the key shown first (defaults to the first option of every control)."""
    keys = list(visibility)
    default = default or keys[0]
    fig_json = fig.to_plotly_json()
    fig_json["data"] = [dict(t, visible=v) for t, v in zip(fig_json["data"], visibility[default])]
    selects = []
    for i, (name, label, options) in enumerate(controls):
        opts = "".join(f'<option value="{o}"{" selected" if o == default.split("|")[i] else ""}>{o}</option>'
                       for o in options)
        selects.append(f'<label>{label} <select id="ctl{i}" data-name="{name}">{opts}</select></label>')
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>{_CONTROL_CSS % dict(paper=SITE['paper'], font=FONT, muted=SITE['muted'], ink=SITE['ink'], axis=SITE['axis'])}</style>
</head><body>
<div class="controls">{''.join(selects)}</div>
<div id="fig"></div>
<script>
const FIG = {_json.dumps(fig_json, default=_np_default)};
const VIS = {_json.dumps(visibility)};
const LAY = {_json.dumps(layouts or {}, default=_np_default)};
const gd = document.getElementById("fig");
const selects = [...document.querySelectorAll(".controls select")];
function update() {{
  const key = selects.map(s => s.value).join("|");
  Plotly.restyle(gd, {{visible: VIS[key]}});
  if (LAY[key]) Plotly.relayout(gd, LAY[key]);
}}
selects.forEach(s => s.addEventListener("change", update));
Plotly.newPlot(gd, FIG.data, FIG.layout, {{responsive: true, displaylogo: false,
    modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"]}}).then(update);
</script>
</body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def _np_default(o):
    import numpy as np
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    raise TypeError(type(o))
