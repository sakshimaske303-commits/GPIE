"""I plot the EU-27 vs comparison difference in 12-month blocks, with and without the winter months."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

IN_PATH = "data/stress_tests.json"
OUT_PATH = "outputs/plots/block_event_study.png"
ORDER = ["Jan-Jun 2019", "Jul 2019-Jun 2020", "Jul 2020-Jun 2021", "Jul 2021-Jun 2022",
         "Jul 2022-Jun 2023", "Jul 2023-Jun 2024", "Jul-Dec 2024"]
REFERENCE = "Jul 2020-Jun 2021"


def main():
    with open(IN_PATH, encoding="utf-8") as f:
        country = json.load(f)["country_level"]
    series = (("12-month blocks, all months", "All months", "#2c7fb8", -0.12),
              ("12-month blocks, without Nov-Feb", "Without November-February", "#d95f0e", 0.12))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(ORDER))
    for key, label, color, offset in series:
        est = [0.0 if b == REFERENCE else country[key][b]["coefficient"] for b in ORDER]
        low = [0.0 if b == REFERENCE else country[key][b]["ci_t_low"] for b in ORDER]
        high = [0.0 if b == REFERENCE else country[key][b]["ci_t_high"] for b in ORDER]
        err = [np.array(est) - np.array(low), np.array(high) - np.array(est)]
        ax.errorbar(x + offset, est, yerr=err, fmt="o", color=color, capsize=4, label=label)
    ax.axhline(0, color="black", linewidth=0.8)
    # The reference block falls in the period of COVID-19 restrictions, so I mark it.
    ref = ORDER.index(REFERENCE)
    ax.axvspan(ref - 0.4, ref + 0.4, color="gray", alpha=0.12, linewidth=0)
    ax.text(ref, ax.get_ylim()[0] * 0.92, "reference block\n(COVID-19\nrestrictions)", fontsize=8, color="gray",
            ha="center", va="bottom")
    ax.axvline(2.5, color="gray", linestyle=":", linewidth=1.2)
    ax.text(2.55, ax.get_ylim()[1] * 0.92, "Climate Law\n(July 2021)", fontsize=9, color="gray", va="top")
    ax.set_xticks(x)
    ax.set_xticklabels([b.replace("-", "–\n") if len(b) > 12 else b.replace("-", "–") for b in ORDER],
                       fontsize=9)
    ax.set_ylabel("EU-27 minus comparison group, relative to\nJul 2020 – Jun 2021 (10⁻⁶ mol/m²)")
    ax.set_title("EU-27 vs. comparison group NO₂ in 12-month blocks (95% confidence intervals)", fontsize=12)
    ax.legend(frameon=False, loc="lower left")
    ax.grid(axis="y", alpha=0.3)
    plt.figtext(0.5, 0.01, "Source: Sentinel-5P TROPOMI tropospheric NO₂ column", ha="center", fontsize=8, color="gray")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(OUT_PATH, dpi=200)
    plt.close()
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
