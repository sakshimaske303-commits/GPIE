"""I put every map and plot from outputs/plots/ into one PDF with a cover page and captions."""
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
     "EU-27 (treatment) and the 9-country non-EU control group - UK, Norway, Switzerland, Iceland, "
     "Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, Serbia."),
    ("no2_choropleth_map.png", "NO2 Choropleth Map",
     "Mean tropospheric NO2 concentration by country, Sentinel-5P TROPOMI."),
    ("no2_before_after_map.png", "NO2 Before vs. After the European Climate Law",
     "Country-level annual mean NO2, all 36 countries, 2019 (pre-treatment) vs. 2024 (post-treatment). Descriptive only."),
    ("eu_vs_control_bar_chart.png", "NO2: EU-27 vs. Control Group",
     "Raw mean NO2, EU-27 vs. 9-country control group, Jan 2019-Jun 2021 vs. Jul 2021-Dec 2024 (descriptive; DiD estimate in title)."),
    ("event_study_plot.png", "Event-Study: Quarter-by-Quarter NO2 Effect",
     "23 quarter-specific EU x quarter coefficients relative to 2021Q2, cluster-robust 95% CIs "
     "(counts of significant quarters in the figure title)."),
    ("ndvi_choropleth_map.png", "NDVI Choropleth Map",
     "Mean vegetation health index (NDVI) by country."),
    ("ndvi_before_after_map.png", "NDVI Before vs. After the European Climate Law",
     "Country-level annual mean NDVI, all 36 countries, 2019 vs. 2024. Descriptive only."),
    ("ndvi_eu_vs_control_bar_chart.png", "NDVI: EU-27 vs. Control Group",
     "Raw mean NDVI, EU-27 vs. control group, pre vs. post (descriptive); exploratory DiD estimate in title, "
     "not attributed to the Climate Law."),
    ("gdp_choropleth_map.png", "GDP Choropleth Map",
     "Control variable - GDP by country (annual, repeated across months in the panel)."),
    ("land_cover_dominant_class_map.png", "Dominant Land Cover Class Map",
     "Descriptive context - dominant land-cover class (static; absorbed by country fixed effects, not a model regressor)."),
    ("dem_elevation_map.png", "Elevation (DEM) Map",
     "Descriptive context - mean elevation (static; absorbed by country fixed effects, not a model regressor)."),
    ("climate_temperature_map.png", "Climate / Temperature Map",
     "Control variable - average temperature by country."),
    ("india_transferability_trend.png", "India Transferability Test",
     "NO2 monthly means over India's national boundary (GADM 4.1), 2019-2024, using the EU-27 request builder. "
     "Acquisition test only, not a causal analysis."),
    ("synthetic_control_gap.png", "Synthetic Control: EU-27 vs. 9-Country Donor Composite",
     "Convex donor weights with pre-period intercept adjustment; complete-data months only. Gap, pre-period "
     "RMSPE and DiD estimate in the figure title. All nine comparison countries are donors."),
    ("no2_change_by_baseline.png", "NO2 Change by Pre-Treatment Pollution Level",
     "Change from July 2023 against the pre-treatment period, by the pixel's pre-treatment NO2 level, "
     "for EU-27 and comparison-group pixels (0.1 degree grid)."),
    ("no2_change_map.png", "Pixel-Level NO2 Change Map",
     "Change in tropospheric NO2 per 0.1 degree pixel, July 2023 - December 2024 minus January 2019 - June 2021."),
    ("moran_lisa_cluster_map.png", "Local Moran's I (LISA) Spatial Cluster Map",
     "LISA clusters of full-period average NO2 (descriptive). Global and month-by-month residual Moran's I "
     "results in the figure title."),
    ("policies_by_year.png", "Policies by Year",
     "Count of records per year in the 10-record EUR-Lex sample scraped for this project (not a complete policy inventory)."),
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
