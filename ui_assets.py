"""CSS and inline-SVG for the RainWise landing page (no external assets, no remote fonts)."""
from __future__ import annotations

import html
from itertools import count

_ids = count(1)


def compact(markup: str) -> str:
    """Strip indentation and blank lines so Markdown treats the snippet as one HTML block."""
    return "\n".join(line.strip() for line in markup.splitlines() if line.strip())


CSS = compact("""
<style>
:root{--deep:#09252B;--teal:#20C9B7;--aqua:#BDEFE5;--mist:#F4F8F6;--slate:#526A6B;--amber:#F2B866;--white:#FFFFFF;
--serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;}
header[data-testid="stHeader"],[data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important}
html,body,.stApp{background:var(--mist)!important;overflow-x:hidden}
.stApp,.stApp *{font-family:var(--sans)}
[data-testid="stMainBlockContainer"],.block-container{padding:0!important;max-width:100%!important}
[data-testid="stVerticalBlock"]{gap:0!important}
.rw-hero{background:radial-gradient(900px 520px at 78% 30%,rgba(32,201,183,.20),transparent 62%),linear-gradient(165deg,#09252B 0%,#0B2C33 100%);color:var(--mist);padding:72px 6vw 64px;overflow:hidden}
.rw-hero-inner{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:1.02fr .98fr;gap:32px;align-items:center}
.rw-eyebrow{letter-spacing:.24em;font-size:.76rem;font-weight:600;color:var(--teal)}
.rw-title{font-family:var(--serif);font-weight:600;font-size:clamp(2.5rem,6.2vw,4.5rem);line-height:1.03;margin:18px 0 22px;color:var(--mist);letter-spacing:-.01em}
.rw-lead{font-size:clamp(1.02rem,1.6vw,1.2rem);line-height:1.6;color:var(--aqua);max-width:34rem}
.rw-sub{margin-top:22px;font-size:.92rem;color:rgba(244,248,246,.72);letter-spacing:.02em}
.rw-sub::before{content:"";display:inline-block;width:28px;height:2px;background:var(--teal);vertical-align:middle;margin-right:12px}
.rw-scene{width:100%;max-width:560px;justify-self:center}
.rw-scene svg{width:100%;height:auto;display:block}
.rw-drop{animation:rw-fall 1.7s linear infinite;opacity:0}
@keyframes rw-fall{0%{transform:translateY(0);opacity:0}12%{opacity:.85}100%{transform:translateY(230px);opacity:.15}}
@media (prefers-reduced-motion:reduce){.rw-drop{animation:none;opacity:.55}}
@media (max-width:860px){.rw-hero{padding:48px 6vw 40px}.rw-hero-inner{grid-template-columns:1fr;gap:18px}.rw-scene{max-width:440px}}
.rw-section{padding:64px 6vw 8px}
.rw-wrap{max-width:1040px;margin:0 auto}
.rw-h2{font-family:var(--serif);font-weight:600;font-size:clamp(1.7rem,3.4vw,2.35rem);color:var(--deep);line-height:1.15}
.rw-kicker{margin-top:10px;color:var(--slate);font-size:1.02rem}
.rw-pillrow{display:flex;justify-content:flex-start;margin:18px 0 6px}
.rw-pill{display:inline-flex;align-items:center;gap:8px;font-size:.82rem;font-weight:600;color:var(--deep);background:var(--white);border:1px solid rgba(9,37,43,.14);border-radius:999px;padding:6px 14px}
.rw-pill i{width:9px;height:9px;border-radius:50%;background:var(--aqua);box-shadow:0 0 0 2px var(--deep) inset}
.rw-pill.ok i{background:var(--teal);box-shadow:none}
.rw-pill.bad{border-color:var(--amber)}
.rw-pill.bad i{background:var(--amber);box-shadow:none}
.rw-pill.idle i{background:var(--slate);box-shadow:none}
[data-testid="stForm"]{border:0!important;padding:0!important;max-width:1040px;margin:0 auto!important;background:transparent!important}
.stMarkdown,[data-testid="stElementContainer"]{max-width:100%}
[data-testid="stForm"]{padding:0 6vw!important;box-sizing:content-box;width:auto}
[data-testid="stNumberInput"] label p{font-weight:600;color:var(--deep);font-size:.95rem}
[data-testid="stNumberInput"] input{background:var(--white)!important;color:var(--deep)!important;font-size:1.15rem;font-weight:600;border-radius:10px}
[data-testid="stNumberInputContainer"]{border-radius:10px;border:1px solid rgba(9,37,43,.22);background:var(--white);overflow:hidden}
[data-testid="stNumberInputContainer"]:focus-within{outline:3px solid var(--teal);outline-offset:2px;border-color:var(--teal)}
[data-testid="stNumberInputContainer"] button{background:var(--mist)!important;color:var(--deep)!important}
[data-testid="stNumberInput"] [data-testid="stWidgetLabel"]{margin-bottom:2px}
.rw-help{color:var(--slate);font-size:.85rem;line-height:1.45;margin:2px 0 14px}
[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button{width:100%;min-height:56px;border-radius:14px;font-size:1.08rem;font-weight:700;letter-spacing:.01em;background:var(--teal)!important;color:var(--deep)!important;border:0!important;box-shadow:0 8px 24px rgba(32,201,183,.28);transition:transform .15s ease,box-shadow .15s ease,background .15s ease}
[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{background:var(--aqua)!important;transform:translateY(-1px);box-shadow:0 12px 28px rgba(32,201,183,.34)}
[data-testid="stFormSubmitButton"] button:focus-visible,[data-testid="stDownloadButton"] button:focus-visible,[data-testid="stButton"] button:focus-visible{outline:3px solid var(--deep);outline-offset:3px}
[data-testid="stDownloadButton"] button{background:var(--white)!important;border:1.5px solid var(--teal)!important;box-shadow:none;min-height:48px;font-size:.98rem}
[data-testid="stDownloadButton"] button:hover{background:var(--aqua)!important}
[data-testid="stRadio"] label p{color:var(--deep);font-weight:600;font-size:.9rem}
[data-testid="stButton"] button{border-radius:10px;border:1.5px solid var(--deep);color:var(--deep);background:var(--white);font-weight:600}
.rw-ctrl{max-width:1040px;margin:0 auto;padding:0 6vw}
.rw-ctrl-inner{max-width:1040px;margin:0 auto}
.rw-empty{background:var(--white);border:1.5px dashed rgba(32,201,183,.7);border-radius:20px;padding:46px 24px;text-align:center;color:var(--slate)}
.rw-empty b{display:block;font-family:var(--serif);font-size:1.5rem;color:var(--deep);margin-bottom:6px;font-weight:600}
.rw-results{background:linear-gradient(180deg,var(--white),var(--mist));padding:56px 6vw 40px;margin-top:40px;border-top:1px solid rgba(9,37,43,.08)}
.rw-res-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:center}
.rw-label{letter-spacing:.18em;font-size:.74rem;font-weight:700;color:var(--slate);text-transform:uppercase}
.rw-big{font-family:var(--serif);font-size:clamp(3.2rem,9vw,6rem);line-height:1;font-weight:600;color:var(--deep);margin:8px 0 6px;letter-spacing:-.02em}
.rw-big small{font-size:.45em;color:var(--slate);font-weight:500;margin-left:6px}
.rw-kl{font-size:1.15rem;color:var(--slate);font-weight:600}
.rw-tankinfo{margin-top:26px;padding:16px 20px;border-left:4px solid var(--teal);background:rgba(189,239,229,.45);border-radius:0 12px 12px 0}
.rw-tankinfo .v{font-family:var(--serif);font-size:1.9rem;font-weight:600;color:var(--deep)}
.rw-explain{margin-top:22px;color:var(--deep);font-size:1.04rem;line-height:1.65}
.rw-rec{margin-top:10px;color:var(--slate);line-height:1.6}
.rw-warn{margin-top:18px;border:1.5px solid var(--amber);background:rgba(242,184,102,.16);color:var(--deep);border-radius:12px;padding:12px 16px;font-size:.95rem;line-height:1.5}
.rw-tankviz{justify-self:center;width:100%;max-width:300px}
.rw-tankviz svg{width:100%;height:auto;display:block}
.rw-details{margin-top:30px;border:1px solid rgba(9,37,43,.14);border-radius:14px;background:var(--white);padding:0}
.rw-details summary{cursor:pointer;padding:14px 18px;font-weight:700;color:var(--deep);list-style:none}
.rw-details summary::-webkit-details-marker{display:none}
.rw-details summary::after{content:"+";float:right;color:var(--teal);font-weight:800}
.rw-details[open] summary::after{content:"–"}
.rw-details summary:focus-visible{outline:3px solid var(--teal);outline-offset:2px;border-radius:14px}
.rw-details .body{padding:0 18px 18px;color:var(--deep);line-height:1.65;font-size:.95rem}
.rw-formula{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--mist);border-radius:10px;padding:10px 12px;margin:8px 0;overflow-x:auto;font-size:.88rem}
.rw-details ul{margin:8px 0 8px 18px;padding:0}
.rw-note{color:var(--slate);font-size:.88rem;margin-top:10px}
.rw-err{max-width:1040px;margin:20px auto 0;border:1.5px solid var(--amber);background:rgba(242,184,102,.16);border-radius:12px;padding:14px 18px;color:var(--deep);line-height:1.55}
.rw-foot{background:var(--deep);color:var(--aqua);text-align:center;padding:34px 6vw;margin-top:56px}
.rw-foot b{display:block;color:var(--mist);letter-spacing:.04em;margin-bottom:6px}
.rw-foot span{font-size:.9rem;color:rgba(189,239,229,.8)}
@media (max-width:860px){.rw-res-grid{grid-template-columns:1fr;gap:24px}.rw-section{padding-top:44px}}
</style>
""")


def hero_scene_svg() -> str:
    """Original 3D-inspired scene: house roof, falling rain, gutter, downpipe, cylindrical tank."""
    drops = []
    xs = [92, 128, 166, 204, 240, 276, 312, 380, 420, 452, 110, 222, 296, 436]
    for i, x in enumerate(xs):
        y = 62 + (i * 17) % 46
        delay = -((i * 0.37) % 1.7)
        drops.append(
            f'<path class="rw-drop" style="animation-delay:{delay:.2f}s" d="M{x} {y} q-4 9 0 13 q4 -4 0 -13z" fill="#BDEFE5"/>'
        )
    return compact(f"""
    <div class="rw-scene" role="img" aria-label="Illustration of rain falling on a house roof, collected by a gutter and pipe into a cylindrical storage tank">
    <svg viewBox="0 0 560 470" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
    <defs>
    <linearGradient id="rwWall" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1B4E55"/><stop offset="1" stop-color="#0E343B"/></linearGradient>
    <linearGradient id="rwRoof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C6B70"/><stop offset="1" stop-color="#17484E"/></linearGradient>
    <linearGradient id="rwRoofEdge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B2C33"/><stop offset="1" stop-color="#071E23"/></linearGradient>
    <linearGradient id="rwTank" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0E343B"/><stop offset=".35" stop-color="#2A6E73"/><stop offset=".6" stop-color="#1B5258"/><stop offset="1" stop-color="#0A2A30"/></linearGradient>
    <linearGradient id="rwWater" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#14A394"/><stop offset=".45" stop-color="#20C9B7"/><stop offset="1" stop-color="#14A394"/></linearGradient>
    <radialGradient id="rwGlow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#20C9B7" stop-opacity=".32"/><stop offset="1" stop-color="#20C9B7" stop-opacity="0"/></radialGradient>
    <radialGradient id="rwGround" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#000" stop-opacity=".45"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
    <clipPath id="rwTankClip"><rect x="364" y="318" width="112" height="86" rx="4"/></clipPath>
    </defs>
    <ellipse cx="300" cy="230" rx="250" ry="200" fill="url(#rwGlow)"/>
    <g fill="#1B4E55" opacity=".7"><ellipse cx="160" cy="40" rx="70" ry="22"/><ellipse cx="215" cy="30" rx="52" ry="22"/><ellipse cx="400" cy="42" rx="64" ry="20"/><ellipse cx="450" cy="34" rx="44" ry="18"/></g>
    {''.join(drops)}
    <ellipse cx="280" cy="418" rx="250" ry="22" fill="url(#rwGround)"/>
    <rect x="76" y="262" width="236" height="148" fill="url(#rwWall)"/>
    <rect x="76" y="262" width="236" height="148" fill="none" stroke="#BDEFE5" stroke-opacity=".12"/>
    <rect x="104" y="296" width="52" height="46" rx="3" fill="#BDEFE5" fill-opacity=".16" stroke="#BDEFE5" stroke-opacity=".4"/>
    <path d="M130 296v46M104 319h52" stroke="#BDEFE5" stroke-opacity=".35"/>
    <rect x="228" y="318" width="48" height="92" rx="3" fill="#0A2A30" stroke="#BDEFE5" stroke-opacity=".3"/>
    <polygon points="52,266 194,168 336,266" fill="url(#rwRoof)"/>
    <polygon points="52,266 336,266 336,278 52,278" fill="url(#rwRoofEdge)"/>
    <polygon points="194,168 336,266 336,278 200,176" fill="#0B2C33" opacity=".55"/>
    <path d="M90 244L194 174" stroke="#BDEFE5" stroke-opacity=".3" stroke-width="2" fill="none"/>
    <rect x="256" y="274" width="86" height="9" rx="4.5" fill="#BDEFE5" fill-opacity=".85"/>
    <rect x="256" y="274" width="86" height="3" rx="1.5" fill="#FFFFFF" fill-opacity=".7"/>
    <path d="M334 283V330H372" stroke="#0A2A30" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M334 283V330H372" stroke="#BDEFE5" stroke-opacity=".85" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M334 283V330H372" stroke="#FFFFFF" stroke-opacity=".5" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" transform="translate(-1.5 0)"/>
    <rect x="364" y="318" width="112" height="86" fill="url(#rwTank)"/>
    <g clip-path="url(#rwTankClip)"><rect x="364" y="352" width="112" height="60" fill="url(#rwWater)" opacity=".92"/></g>
    <ellipse cx="420" cy="404" rx="56" ry="11" fill="#0A2A30"/>
    <ellipse cx="420" cy="352" rx="56" ry="9" fill="#BDEFE5" fill-opacity=".55"/>
    <ellipse cx="420" cy="318" rx="56" ry="11" fill="#2A6E73"/>
    <ellipse cx="420" cy="318" rx="56" ry="11" fill="none" stroke="#BDEFE5" stroke-opacity=".55"/>
    <rect x="378" y="326" width="7" height="72" rx="3.5" fill="#FFFFFF" fill-opacity=".22"/>
    <ellipse cx="420" cy="424" rx="64" ry="9" fill="#BDEFE5" fill-opacity=".10"/>
    </svg>
    </div>
    """)


def tank_svg(fill_fraction: float, label: str) -> str:
    """Cylinder whose water level equals ``fill_fraction`` (clamped to 0..1)."""
    f = max(0.0, min(1.0, fill_fraction))
    uid = next(_ids)
    top, bottom = 56, 236
    height = bottom - top
    water_h = height * f
    water_y = bottom - water_h
    water = ""
    if f > 0:
        water = (
            f'<g clip-path="url(#tc{uid})"><rect x="30" y="{water_y:.1f}" width="140" height="{water_h + 14:.1f}" fill="url(#tw{uid})"/></g>'
            f'<ellipse cx="100" cy="{water_y:.1f}" rx="70" ry="11" fill="#BDEFE5" fill-opacity=".75"/>'
        )
    return compact(f"""
    <div class="rw-tankviz" role="img" aria-label="{html.escape(label)}">
    <svg viewBox="0 0 200 270" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
    <defs>
    <linearGradient id="tb{uid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E3EEEA"/><stop offset=".4" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D3E3DE"/></linearGradient>
    <linearGradient id="tw{uid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#14A394"/><stop offset=".45" stop-color="#20C9B7"/><stop offset="1" stop-color="#14A394"/></linearGradient>
    <clipPath id="tc{uid}"><rect x="30" y="{top}" width="140" height="{height}"/></clipPath>
    </defs>
    <ellipse cx="100" cy="250" rx="82" ry="10" fill="#09252B" fill-opacity=".14"/>
    <rect x="30" y="{top}" width="140" height="{height}" fill="url(#tb{uid})"/>
    <ellipse cx="100" cy="{bottom}" rx="70" ry="13" fill="#D3E3DE"/>
    {water}
    <rect x="30" y="{top}" width="140" height="{height}" fill="none" stroke="#526A6B" stroke-opacity=".45" stroke-width="1.5"/>
    <ellipse cx="100" cy="{top}" rx="70" ry="13" fill="#F4F8F6" stroke="#526A6B" stroke-opacity=".5" stroke-width="1.5"/>
    <rect x="44" y="{top + 8}" width="8" height="{height - 20}" rx="4" fill="#FFFFFF" fill-opacity=".55"/>
    <g stroke="#526A6B" stroke-opacity=".5" stroke-width="1.5"><path d="M30 {top + height * .25:.1f}h10M30 {top + height * .5:.1f}h10M30 {top + height * .75:.1f}h10"/></g>
    </svg>
    </div>
    """)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)
