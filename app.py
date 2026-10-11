"""RainWise - Streamlit front end.

Two clearly separated execution modes:
  * Local calculation  - calls rainwise.calculator directly (no network, no AWS)
  * AWS API            - sends a real HTTP POST to RAINWISE_API_URL (API Gateway -> Lambda)
"""
from __future__ import annotations

import csv
import io
import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from rainwise import calculator as calc  # noqa: E402
from api_client import ApiError, call_api  # noqa: E402
from ui_assets import CSS, compact, esc, hero_scene_svg, tank_svg  # noqa: E402

LOCAL, AWS = "Local calculation", "AWS API"


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (stdlib only). Real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(ROOT / ".env")
API_URL = os.environ.get("RAINWISE_API_URL", "").strip()

st.set_page_config(page_title="RainWise · Every Drop Has Potential", page_icon="💧", layout="wide",
                   initial_sidebar_state="collapsed")

EXTRA_CSS = compact("""
<style>
[data-testid="stElementContainer"]:has([data-testid="stRadio"]),[data-testid="stElementContainer"]:has([data-testid="stButton"]),[data-testid="stElementContainer"]:has([data-testid="stDownloadButton"]){width:min(1040px,88vw)!important;margin-left:auto!important;margin-right:auto!important}
[data-testid="stRadio"]{width:100%}
[data-testid="stButton"] button{width:auto;padding:0 20px;margin-top:14px}
[data-testid="stDownloadButton"]{margin-top:18px}
[data-testid="stDownloadButton"] button{margin:0}
[data-testid="stFormSubmitButton"]{margin-top:28px}
[data-testid="stFormSubmitButton"] button p,[data-testid="stDownloadButton"] button p{font-weight:700;color:var(--deep)}
.rw-pillrow{margin-bottom:26px!important}
[data-testid="stDownloadButton"] button{width:auto;min-width:260px;padding:0 24px}
</style>
""")
st.markdown(CSS + "\n" + EXTRA_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- state
ss = st.session_state
ss.setdefault("mode_choice", AWS if API_URL else LOCAL)
ss.setdefault("aws_status", None)   # None | "ok" | "fail"  (only set by real requests)
ss.setdefault("result", None)
ss.setdefault("problem", None)      # {"kind": "input" | "api", "lines": [...]}


def _use_local() -> None:
    ss["mode_choice"] = LOCAL


# ---------------------------------------------------------------- hero
st.markdown(compact(f"""
<section class="rw-hero" aria-label="RainWise introduction">
<div class="rw-hero-inner">
<div>
<div class="rw-eyebrow">ENVIRONMENTAL HACKS 2026</div>
<div class="rw-title" role="heading" aria-level="1">Every Drop Has Potential.</div>
<div class="rw-lead">Discover what your rooftop rainwater could provide — and plan a smarter way to store it.</div>
<div class="rw-sub">Simple calculations. Transparent estimates. Smarter water planning.</div>
</div>
{hero_scene_svg()}
</div>
</section>
"""), unsafe_allow_html=True)

# ---------------------------------------------------------------- calculator
using_aws = bool(API_URL) and ss["mode_choice"] == AWS
if not using_aws:
    pill_cls, pill_txt = "", "Local calculation"
elif ss["aws_status"] == "ok":
    pill_cls, pill_txt = "ok", "AWS API connected"
elif ss["aws_status"] == "fail":
    pill_cls, pill_txt = "bad", "AWS API unavailable"
else:
    pill_cls, pill_txt = "idle", "AWS API configured · not called yet"

st.markdown(compact(f"""
<section class="rw-section"><div class="rw-wrap">
<div class="rw-h2" role="heading" aria-level="2">Calculate your rainwater potential</div>
<div class="rw-kicker">Three inputs. One practical estimate.</div>
<div class="rw-pillrow"><span class="rw-pill {pill_cls}" role="status"><i></i>{esc(pill_txt)}</span></div>
</div></section>
"""), unsafe_allow_html=True)

if API_URL:
    st.radio("Calculation mode", [LOCAL, AWS], key="mode_choice", horizontal=True,
             help="AWS API sends your inputs to the deployed API Gateway + Lambda endpoint.")
    using_aws = ss["mode_choice"] == AWS

with st.form("rainwise_form", border=False):
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        area = st.number_input("Roof area (m²)", min_value=0.0, max_value=calc.MAX_ROOF_AREA_M2,
                               value=200.0, step=10.0, format="%g", key="area")
        st.markdown('<div class="rw-help">Footprint of the roof that drains to your gutter, in square metres.</div>',
                    unsafe_allow_html=True)
    with c2:
        rain = st.number_input("Rainfall per event (mm)", min_value=0.0, max_value=calc.MAX_RAINFALL_MM,
                               value=50.0, step=5.0, format="%g", key="rain")
        st.markdown('<div class="rw-help">Rain depth for one event you want to plan for. 1 mm on 1 m² is 1 litre.</div>',
                    unsafe_allow_html=True)
    with c3:
        eff = st.number_input("Collection efficiency (%)", min_value=0.0, max_value=100.0,
                              value=80.0, step=5.0, format="%g", key="eff")
        st.markdown('<div class="rw-help">Share of rain that actually reaches storage after splash, leaks and first flush.</div>',
                    unsafe_allow_html=True)
    submitted = st.form_submit_button("Calculate My Rainwater Potential", use_container_width=True)

# ---------------------------------------------------------------- compute
if submitted:
    ss["problem"] = None
    try:
        a, r_mm, e = calc.validate_inputs(area, rain, eff)   # front-end validation
    except calc.ValidationError as exc:
        ss["result"] = None
        ss["problem"] = {"kind": "input", "lines": exc.errors}
    else:
        inputs = {"roof_area_m2": a, "rainfall_mm": r_mm, "efficiency_percent": e}
        if using_aws:
            try:
                data = call_api(API_URL, inputs)
            except ApiError as exc:
                ss["aws_status"] = "fail"
                ss["result"] = None
                ss["problem"] = {"kind": "api", "lines": [str(exc)]}
            else:
                ss["aws_status"] = "ok"
                ss["result"] = {"data": data, "inputs": inputs, "source": "aws"}
        else:
            ss["result"] = {"data": calc.calculate(**inputs), "inputs": inputs, "source": "local"}
    st.rerun()   # redraw so the status pill reflects the request that just happened

# ---------------------------------------------------------------- feedback / results
problem, result = ss["problem"], ss["result"]

if problem:
    title = ("The AWS API request failed." if problem["kind"] == "api" else "Please check your inputs.")
    body = "<br>".join(esc(line) for line in problem["lines"])
    extra = ("<br>No result was calculated. Nothing was substituted from a local calculation."
             if problem["kind"] == "api" else "")
    st.markdown(f'<div class="rw-err" role="alert"><b>{esc(title)}</b><br>{body}{extra}</div>',
                unsafe_allow_html=True)
    if problem["kind"] == "api":
        st.button("Switch to local calculation", on_click=_use_local)

if result is None and not problem:
    st.markdown(compact("""
    <section class="rw-section"><div class="rw-wrap"><div class="rw-empty">
    <b>Your rainwater potential starts here.</b>
    Adjust the three inputs above, then calculate to see your estimate and a suitable tank size.
    </div></div></section>
    """), unsafe_allow_html=True)

if result:
    d, inp, source = result["data"], result["inputs"], result["source"]
    litres = float(d["harvestable_litres"])
    kl = float(d["harvestable_kl"])
    kl_text = f"{kl:,.1f}" if round(kl, 3) == round(kl, 1) else f"{kl:,.3f}".rstrip("0")
    tank = d["recommended_tank_litres"]
    exceeded = bool(d.get("capacity_exceeded", tank is None and litres > 0))
    largest = calc.LARGEST_TANK_LITRES

    if exceeded:
        frac, tank_value = 1.0, f"More than {largest:,} L"
        tank_note = f"Largest standard tank: {largest:,} L"
        viz_label = "Tank visual: estimated harvest is larger than the biggest standard tank, shown full."
        warn = ("Estimated volume exceeds the largest standard tank. Multiple tanks or a larger storage system "
                "may be required, and the tank graphic shows the maximum fill.")
    elif tank is None:
        frac, tank_value, tank_note = 0.0, "No tank needed", "Nothing to store for this event"
        viz_label = "Tank visual: empty, because no water would be collected."
        warn = ""
    else:
        frac = litres / tank
        tank_value = f"{int(tank):,} L"
        tank_note = f"Estimated harvest fills about {frac * 100:.0f}% of this tank"
        viz_label = f"Tank visual: {frac * 100:.0f}% full of a {int(tank):,} litre tank."
        warn = ""

    area_s, rain_s, eff_s = (calc.format_litres(inp[k]) for k in ("roof_area_m2", "rainfall_mm", "efficiency_percent"))
    src_text = ("Calculated locally in this app" if source == "local"
                else "Calculated by AWS Lambda via API Gateway (HTTP API)")
    warn_html = f'<div class="rw-warn" role="alert">{esc(warn)}</div>' if warn else ""
    rec = d.get("recommendation", "")
    rec_html = f'<div class="rw-rec">{esc(rec)}</div>' if rec else ""
    explain = (f"Based on your roof area, rainfall and selected collection efficiency, your estimated harvest is "
               f"{calc.format_litres(litres)} litres for this rainfall event.")

    st.markdown(compact(f"""
    <section class="rw-results" aria-live="polite"><div class="rw-wrap">
    <div class="rw-res-grid">
    <div>
    <div class="rw-label">Estimated harvest</div>
    <div class="rw-big">{calc.format_litres(litres)}<small>L</small></div>
    <div class="rw-kl">{kl_text} kL estimated harvest</div>
    <div class="rw-tankinfo"><div class="rw-label">Recommended tank</div><div class="v">{esc(tank_value)}</div><div class="rw-note">{esc(tank_note)}</div></div>
    <div class="rw-explain">{esc(explain)}</div>
    {rec_html}
    {warn_html}
    <details class="rw-details"><summary>How we calculated this</summary><div class="body">
    <div class="rw-formula">{esc(calc.FORMULA)}</div>
    <div class="rw-formula">{area_s} m² × {rain_s} mm × {eff_s} ÷ 100 = {calc.format_litres(litres)} L</div>
    <b>Assumptions</b>
    <ul>
    <li>1 mm of rain on 1 m² equals 1 litre.</li>
    <li>One rainfall event, with the efficiency you entered applied to the whole roof area.</li>
    <li>Standard tank sizes: {", ".join(f"{s:,}" for s in calc.STANDARD_TANKS_LITRES)} litres. The smallest size that holds the estimate is recommended.</li>
    </ul>
    <div class="rw-note">This is a preliminary estimate, not a measurement. Actual usable collection depends on rainfall distribution, first-flush diversion, roof material, leakage, overflow and other site-specific factors. It does not show water that has been saved.</div>
    <div class="rw-note">{esc(src_text)}.</div>
    </div></details>
    </div>
    {tank_svg(frac, viz_label)}
    </div>
    </div></section>
    """), unsafe_allow_html=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["field", "value", "unit"])
    w.writerow(["roof_area", inp["roof_area_m2"], "m2"])
    w.writerow(["rainfall_per_event", inp["rainfall_mm"], "mm"])
    w.writerow(["collection_efficiency", inp["efficiency_percent"], "percent"])
    w.writerow(["estimated_harvest", d["harvestable_litres"], "litres"])
    w.writerow(["estimated_harvest", d["harvestable_kl"], "kilolitres"])
    w.writerow(["recommended_tank", tank if tank is not None else "none", "litres"])
    w.writerow(["capacity_exceeded", str(exceeded).lower(), ""])
    w.writerow(["calculated_by", "local" if source == "local" else "aws_lambda_api", ""])
    w.writerow(["note", "Preliminary estimate; actual collection depends on site conditions.", ""])
    st.download_button("Download CSV summary", buf.getvalue(), file_name="rainwise_summary.csv", mime="text/csv")

# ---------------------------------------------------------------- footer
st.markdown(compact("""
<div class="rw-foot" role="contentinfo"><b>RainWise · Environmental Hacks 2026</b>
<span>Built to make rooftop rainwater potential easier to understand.</span></div>
"""), unsafe_allow_html=True)
