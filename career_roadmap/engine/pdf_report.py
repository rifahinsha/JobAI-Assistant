from fpdf import FPDF


def _as_text(data) -> str:
    if isinstance(data, list):
        return "\n".join(f"- {item}" for item in data)
    return str(data)


def build_roadmap_pdf(role, required_skills, missing_skills, roadmap, resources, projects, validation) -> bytes:
    """Renders the roadmap report and returns raw PDF bytes (nothing touches disk)."""

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def section(title, body):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, _as_text(body))

    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "Career Roadmap Report", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Target Role: {role}", ln=True)

    section("Required Skills", required_skills)
    section("Missing Skills", missing_skills)
    section("Learning Roadmap", roadmap)
    section("Learning Resources", resources)
    section("Project Recommendations", projects)
    section("Roadmap Validation", validation)

    # fpdf2's output() returns a bytearray; normalize to bytes for HttpResponse.
    raw = pdf.output()
    if isinstance(raw, str):
        raw = raw.encode("latin1")
    return bytes(raw)
