"""
Compiles every map/plot in outputs/plots/ into a single PDF - one image per
page, landscape or portrait chosen automatically to match each image's own
aspect ratio, with a cover page and a titled caption above each image.

This is a presentation compilation only (no new analysis) - built at Sakshi's
request for a single PDF containing all GPIE maps and plots.
"""
import os
from PIL import Image
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PLOTS_DIR = "outputs/plots"
OUTPUT_PATH = "GPIE_Maps_and_Plots.pdf"

# (filename, display title, one-line caption)
IMAGES = [
    ("control_group_design_map.png", "Study Design: Treatment vs. Control Group",
     "EU-27 (treatment) and the non-EU control group - United Kingdom, Norway, Switzerland."),
    ("no2_choropleth_map.png", "NO2 Choropleth Map",
     "Mean tropospheric NO2 concentration by country, Sentinel-5P TROPOMI."),
    ("no2_before_after_map.png", "NO2 Before vs. After the European Climate Law",
     "Average NO2 across the EU-27, 2019 (pre-treatment) vs. 2024 (post-treatment)."),
    ("eu_vs_control_bar_chart.png", "NO2: EU-27 vs. Control Group",
     "Mean NO2, pre- and post-treatment, EU-27 vs. control group."),
    ("event_study_plot.png", "Event-Study: Quarter-by-Quarter NO2 Effect",
     "23-quarter Difference-in-Differences event-study estimates, cluster-robust SEs."),
    ("ndvi_choropleth_map.png", "NDVI Choropleth Map",
     "Mean vegetation health index (NDVI) by country."),
    ("ndvi_before_after_map.png", "NDVI Before vs. After the European Climate Law",
     "Average NDVI across the EU-27, pre- vs. post-treatment."),
    ("ndvi_eu_vs_control_bar_chart.png", "NDVI: EU-27 vs. Control Group",
     "Corrected two-group DiD model: coefficient = -0.021, p = 0.012 (cluster-robust)."),
    ("gdp_choropleth_map.png", "GDP Choropleth Map",
     "Control variable - GDP by country."),
    ("land_cover_dominant_class_map.png", "Dominant Land Cover Class Map",
     "Control variable - dominant land-cover classification by country."),
    ("dem_elevation_map.png", "Elevation (DEM) Map",
     "Control variable - digital elevation model."),
    ("climate_temperature_map.png", "Climate / Temperature Map",
     "Control variable - average temperature by country."),
    ("india_transferability_trend.png", "India Transferability Validation",
     "NO2 acquisition pipeline independently tested on India, 2019-2024."),
    ("policies_by_year.png", "Policies by Year",
     "Count of EU environmental/climate policies enacted per year."),
    ("policy_type_distribution.png", "Policy Type Distribution",
     "Breakdown of policy dataset by policy type."),
    ("policy_types_by_year.png", "Policy Types by Year",
     "Policy type composition over time."),
]

MARGIN = 0.5 * inch
TITLE_H = 0.65 * inch


def make_pdf():
    missing = [f for f, _, _ in IMAGES if not os.path.exists(os.path.join(PLOTS_DIR, f))]
    if missing:
        raise SystemExit(f"Missing image files, aborting: {missing}")

    c = canvas.Canvas(OUTPUT_PATH)

    # Cover page
    page_w, page_h = portrait(letter)
    c.setPageSize((page_w, page_h))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(page_w / 2, page_h - 2 * inch, "GPIE")
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(page_w / 2, page_h - 2.4 * inch, "Green Policy Intelligence Engine")
    c.setFont("Helvetica", 13)
    c.drawCentredString(page_w / 2, page_h - 3.0 * inch, "All Maps and Plots")
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_w / 2, page_h - 3.4 * inch, f"{len(IMAGES)} figures compiled from outputs/plots/")
    c.setFont("Helvetica", 9)
    y = page_h - 4.2 * inch
    for i, (_, title, _) in enumerate(IMAGES, start=1):
        c.drawString(1.3 * inch, y, f"{i}.  {title}")
        y -= 0.22 * inch
    c.showPage()

    for fname, title, caption in IMAGES:
        path = os.path.join(PLOTS_DIR, fname)
        img = Image.open(path)
        iw, ih = img.size
        is_landscape = iw >= ih

        page_size = landscape(letter) if is_landscape else portrait(letter)
        page_w, page_h = page_size
        c.setPageSize((page_w, page_h))

        # Title
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(page_w / 2, page_h - MARGIN - 14, title)
        c.setFont("Helvetica", 9)
        c.drawCentredString(page_w / 2, page_h - MARGIN - 30, caption)

        # Available area for the image
        avail_w = page_w - 2 * MARGIN
        avail_h = page_h - 2 * MARGIN - TITLE_H

        scale = min(avail_w / iw, avail_h / ih)
        draw_w = iw * scale
        draw_h = ih * scale
        x = (page_w - draw_w) / 2
        y = MARGIN

        c.drawImage(ImageReader(path), x, y, width=draw_w, height=draw_h,
                    preserveAspectRatio=True, anchor='c')

        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(page_w / 2, MARGIN - 12, "GPIE - Green Policy Intelligence Engine")

        c.showPage()

    c.save()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_pdf()
