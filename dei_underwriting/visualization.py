"""Dependency-free SVG chart generation for DEI reporting outputs."""

from pathlib import Path

from .analytics import FACTOR_LABELS


TIER_COLORS = {
    "Low": "#2f855a",
    "Moderate": "#2b6cb0",
    "Elevated": "#b7791f",
    "Severe": "#c53030",
}


def generate_risk_distribution_chart(summary: dict[str, object], output_path: str | Path) -> Path:
    """Create an SVG bar chart for risk tier distribution."""

    distribution = summary["risk_tier_distribution"]
    tiers = ["Low", "Moderate", "Elevated", "Severe"]
    values = [distribution.get(tier, 0) for tier in tiers]
    max_value = max(values) if any(values) else 1

    width = 720
    height = 420
    chart_left = 80
    chart_bottom = 340
    bar_width = 100
    gap = 45
    max_bar_height = 240

    bars = []
    labels = []
    for index, tier in enumerate(tiers):
        value = distribution.get(tier, 0)
        bar_height = value / max_value * max_bar_height if max_value else 0
        x = chart_left + index * (bar_width + gap)
        y = chart_bottom - bar_height
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" '
            f'fill="{TIER_COLORS[tier]}" rx="4" />'
        )
        labels.append(f'<text x="{x + bar_width / 2}" y="{chart_bottom + 28}" text-anchor="middle">{tier}</text>')
        labels.append(f'<text x="{x + bar_width / 2}" y="{y - 10:.1f}" text-anchor="middle">{value}</text>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="40" y="42" font-family="Arial" font-size="22" font-weight="700">DEI Risk Tier Distribution</text>
  <line x1="{chart_left - 20}" y1="{chart_bottom}" x2="{width - 80}" y2="{chart_bottom}" stroke="#1a202c" stroke-width="1"/>
  {''.join(bars)}
  <g font-family="Arial" font-size="14" fill="#1a202c">{''.join(labels)}</g>
</svg>
"""
    path = Path(output_path)
    path.write_text(svg, encoding="utf-8")
    return path


def generate_industry_heatmap(summary: dict[str, object], output_path: str | Path) -> Path:
    """Create an SVG heatmap for industry-level factor contributions."""

    rows = summary["industry_factor_heatmap"]
    factors = list(FACTOR_LABELS.values())
    cell_width = 118
    cell_height = 34
    left = 185
    top = 95
    width = left + len(factors) * cell_width + 40
    height = top + len(rows) * cell_height + 70
    max_value = max(float(row[factor]) for row in rows for factor in factors) or 1

    cells = []
    for row_index, row in enumerate(rows):
        y = top + row_index * cell_height
        cells.append(
            f'<text x="24" y="{y + 22}" font-family="Arial" font-size="13" fill="#1a202c">'
            f'{_escape(str(row["industry"]))}</text>'
        )
        for column_index, factor in enumerate(factors):
            x = left + column_index * cell_width
            value = float(row[factor])
            color = _heat_color(value / max_value)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{cell_width - 2}" height="{cell_height - 2}" '
                f'fill="{color}" />'
            )
            cells.append(
                f'<text x="{x + cell_width / 2}" y="{y + 22}" font-family="Arial" '
                f'font-size="12" text-anchor="middle" fill="#1a202c">{value:.1f}</text>'
            )

    headers = []
    for column_index, factor in enumerate(factors):
        x = left + column_index * cell_width + cell_width / 2
        headers.append(
            f'<text x="{x}" y="74" font-family="Arial" font-size="11" text-anchor="middle" '
            f'fill="#1a202c">{_shorten(factor)}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="24" y="36" font-family="Arial" font-size="22" font-weight="700">Industry Risk Factor Heatmap</text>
  <g>{''.join(headers)}</g>
  <g>{''.join(cells)}</g>
</svg>
"""
    path = Path(output_path)
    path.write_text(svg, encoding="utf-8")
    return path


def _heat_color(intensity: float) -> str:
    intensity = max(0.0, min(1.0, intensity))
    red = 255
    green = int(246 - intensity * 130)
    blue = int(214 - intensity * 170)
    return f"#{red:02x}{green:02x}{blue:02x}"


def _shorten(label: str) -> str:
    replacements = {
        "Industry exposure": "Industry",
        "Data sensitivity": "Data",
        "Cloud dependency": "Cloud",
        "Vendor exposure": "Vendor",
        "Workforce distribution": "Workforce",
        "Prior incidents": "Incidents",
        "Regulatory exposure": "Regulatory",
    }
    return replacements.get(label, label)


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
