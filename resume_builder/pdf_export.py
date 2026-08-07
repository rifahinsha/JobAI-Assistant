"""Converts the AI-generated resume HTML into a PDF that matches the
on-screen preview.

Previously this manually re-parsed a fixed set of resume-* CSS classes
with reportlab and rebuilt the layout from scratch -- anything the model
didn't emit in exactly the expected shape was silently dropped, and the
result never really matched what the user saw in the preview panel.

Instead, we now render the *same* HTML the user sees, wrapped in a
lightweight print stylesheet that mirrors the preview's CSS (see
templates/resume_builder.html #resumePreview rules) using xhtml2pdf,
which is pure-Python (no system/Cairo/Pango dependency) and gives a much
closer match to the browser preview than a hand-rolled reportlab layout.
"""
import io

from xhtml2pdf import pisa

# Keep these in sync with the `.tpl-*` rules in templates/resume_builder.html
# so the PDF a user downloads matches whichever template they picked.
TEMPLATES = {
    "classic": {
        "font": "'Times New Roman', Georgia, serif",
        "accent": "#163C2C",
        "ink": "#16241C",
        "ink_soft": "#5C6B62",
        "name_transform": "none",
        "name_align": "center",
        "section_transform": "uppercase",
        "header_border": "2px solid #16241C",
    },
    "modern": {
        "font": "Helvetica, Arial, sans-serif",
        "accent": "#1F6FEB",
        "ink": "#16241C",
        "ink_soft": "#5C6B62",
        "name_transform": "uppercase",
        "name_align": "left",
        "section_transform": "uppercase",
        "header_border": "3px solid #1F6FEB",
    },
    "minimal": {
        "font": "Helvetica, Arial, sans-serif",
        "accent": "#16241C",
        "ink": "#16241C",
        "ink_soft": "#7A8A80",
        "name_transform": "none",
        "name_align": "left",
        "section_transform": "none",
        "header_border": "1px solid #D9DFDA",
    },
}


def _pdf_css(template: str) -> str:
    t = TEMPLATES.get(template, TEMPLATES["classic"])
    return f"""
        @page {{ size: letter; margin: 0.6in 0.65in; }}
        body {{ font-family: {t['font']}; color: {t['ink']}; font-size: 10.5pt; }}
        .resume-header {{
            text-align: {t['name_align']}; border-bottom: {t['header_border']};
            padding-bottom: 10px; margin-bottom: 14px;
        }}
        .resume-name {{
            font-size: 20pt; font-weight: bold; letter-spacing: 1px;
            margin-bottom: 4px; text-transform: {t['name_transform']}; color: {t['ink']};
        }}
        .resume-contact {{ font-size: 9pt; color: {t['ink_soft']}; }}
        .resume-contact a {{ color: {t['accent']}; text-decoration: none; }}
        .resume-section {{ margin: 12px 0; }}
        .resume-section-title {{
            font-size: 11pt; font-weight: bold; color: {t['accent']};
            text-transform: {t['section_transform']}; letter-spacing: 0.5px;
            border-bottom: 1px solid #D9DFDA; padding-bottom: 2px; margin-bottom: 6px;
        }}
        .resume-item {{ margin: 8px 0; }}
        .resume-item-header {{ font-weight: bold; font-size: 10.5pt; color: {t['ink']}; }}
        .resume-item-subtitle {{ font-style: italic; color: {t['ink_soft']}; font-size: 10pt; }}
        .resume-item-location {{ font-style: italic; color: {t['ink_soft']}; font-size: 9pt; float: right; }}
        .resume-list {{ margin: 4px 0 4px 18px; padding: 0; list-style: none; }}
        .resume-list li {{ margin: 3px 0; font-size: 10pt; }}
        .resume-list li:before {{ content: "\\2022  "; color: {t['accent']}; }}
        .coursework-grid {{ margin: 4px 0 4px 18px; padding: 0; list-style: none; }}
        .coursework-grid li {{ font-size: 10pt; margin: 2px 0; }}
        .skill-item {{ font-size: 10pt; margin: 3px 0; }}
        .skill-label {{ font-weight: bold; }}
    """


def resume_pdf_bytes(html: str, template: str = "classic") -> bytes:
    """Renders the (possibly user-edited) resume HTML to a PDF using the
    same class structure and a stylesheet that mirrors the live preview."""
    full_html = f"""<html>
<head>
<meta charset="utf-8">
<style>{_pdf_css(template)}</style>
</head>
<body>{html or '<p>Resume content could not be parsed.</p>'}</body>
</html>"""

    buffer = io.BytesIO()
    result = pisa.CreatePDF(src=full_html, dest=buffer, encoding="utf-8")

    if result.err:
        # Defensive fallback so a rendering hiccup never surfaces as a 500.
        buffer = io.BytesIO()
        pisa.CreatePDF(
            src=f"<html><body><p>{ (html or '') }</p></body></html>",
            dest=buffer,
            encoding="utf-8",
        )

    buffer.seek(0)
    return buffer.read()