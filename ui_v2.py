from __future__ import annotations

import html
import streamlit as st


NAV_ITEMS = [
    ("홈", "⌂"),
    ("시장 현황", "▥"),
    ("종목 분석", "◫"),
    ("공시 분석", "▤"),
    ("테마 & 섹터", "◇"),
    ("포트폴리오", "▣"),
    ("관심 종목", "☆"),
    ("AI 인사이트", "✦"),
    ("데이터 연결 관리", "⚙"),
]


def apply_theme():
    st.markdown(
        """
<style>
:root {
  --bg:#ffffff; --surface:#ffffff; --surface-soft:#f8fafc;
  --line:#e7ebf0; --line-strong:#d9e0e8; --text:#111827; --muted:#667085;
  --blue:#2563eb; --blue-dark:#1d4ed8; --blue-soft:#eff6ff;
  --green:#059669; --red:#dc2626;
}
html, body, [class*="css"] {
  font-family:Pretendard,"Noto Sans KR","Apple SD Gothic Neo",sans-serif;
}
.stApp { background:var(--bg); color:var(--text); }
.block-container { max-width:1440px; padding-top:1.35rem; padding-bottom:4rem; }
header[data-testid="stHeader"] {
  background:rgba(255,255,255,.94); border-bottom:1px solid rgba(231,235,240,.75);
  backdrop-filter:blur(12px);
}
section[data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
section[data-testid="stSidebar"] > div { padding-top:.9rem; }
[data-testid="stSidebar"] .stRadio > label { display:none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap:.2rem; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  border-radius:10px; padding:.58rem .65rem; color:#475467;
  transition:background .15s ease,color .15s ease;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { background:#f5f7fa; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
  background:#eff6ff; color:var(--blue-dark); font-weight:750;
  box-shadow:inset 3px 0 0 var(--blue);
}
h1,h2,h3,h4 { color:var(--text); letter-spacing:-.035em; }
h1 { font-weight:800; } h2,h3 { font-weight:760; }
p,li { line-height:1.62; }
[data-testid="stCaptionContainer"] { color:var(--muted); }
[data-testid="stMetric"] {
  background:#fff; border:1px solid var(--line); border-radius:14px;
  padding:15px 17px; box-shadow:0 5px 18px rgba(16,24,40,.035);
}
[data-testid="stMetricLabel"] { color:var(--muted); }
[data-testid="stMetricValue"] {
  color:var(--text); font-weight:760; font-variant-numeric:tabular-nums;
}
[data-testid="stVerticalBlockBorderWrapper"] {
  border-color:var(--line)!important; border-radius:14px!important; background:#fff;
  box-shadow:0 5px 18px rgba(16,24,40,.028);
}
.stButton > button,.stFormSubmitButton > button {
  border-radius:10px; min-height:2.65rem; font-weight:700;
}
.stButton > button[kind="primary"],.stFormSubmitButton > button[kind="primary"] {
  background:var(--blue); border-color:var(--blue);
}
.stButton > button[kind="primary"]:hover,.stFormSubmitButton > button[kind="primary"]:hover {
  background:var(--blue-dark); border-color:var(--blue-dark);
}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"] > div {
  border-radius:10px!important; border-color:var(--line-strong)!important;
}
.stTextInput input:focus,.stTextArea textarea:focus {
  border-color:#93b4f7!important; box-shadow:0 0 0 1px #93b4f7!important;
}
.stTabs [data-baseweb="tab-list"] { gap:5px; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"] { border-radius:9px 9px 0 0; padding:9px 13px; }
.stDataFrame { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.planx-brand { display:flex; align-items:center; gap:10px; margin:2px 0 22px; }
.planx-brand-mark {
  width:34px; height:34px; border-radius:10px; display:flex; align-items:center;
  justify-content:center; background:linear-gradient(145deg,#2563eb,#60a5fa);
  color:#fff; font-size:18px; font-weight:800; box-shadow:0 5px 12px rgba(37,99,235,.16);
}
.planx-brand-title { font-size:18px; line-height:1.15; font-weight:800; letter-spacing:-.03em; }
.planx-brand-sub { font-size:10px; color:#98a2b3; margin-top:2px; }
.planx-hero {
  background:linear-gradient(135deg,#fff 0%,#f8fbff 72%,#f1f6ff 100%);
  border:1px solid #e4e9f0; border-radius:18px; padding:25px 27px; margin-bottom:16px;
  box-shadow:0 9px 28px rgba(16,24,40,.045);
}
.planx-eyebrow {
  color:#2563eb; font-size:11px; font-weight:800; letter-spacing:.1em;
  text-transform:uppercase; margin-bottom:7px;
}
.planx-hero h1 { margin:0; font-size:32px; line-height:1.2; }
.planx-hero p { margin:8px 0 0; color:#667085; font-size:14px; max-width:760px; }
.planx-card {
  background:#fff; border:1px solid #e7ebf0; border-radius:14px; padding:17px 18px;
  min-height:118px; box-shadow:0 5px 18px rgba(16,24,40,.03);
}
.planx-card:hover { border-color:#d8e1ee; box-shadow:0 8px 24px rgba(16,24,40,.05); }
.planx-card-title { font-size:12px; color:#667085; margin-bottom:7px; font-weight:700; }
.planx-card-value {
  font-size:23px; color:#111827; font-weight:800; letter-spacing:-.03em;
  font-variant-numeric:tabular-nums;
}
.planx-card-note { margin-top:7px; font-size:11px; color:#98a2b3; }
.planx-empty { background:#fff; border:1px dashed #cbd5e1; border-radius:14px; padding:21px; color:#667085; }
.planx-source {
  display:inline-flex; align-items:center; gap:5px; color:#667085; background:#f8fafc;
  border:1px solid #e4e7ec; padding:4px 8px; border-radius:999px; font-size:10px;
}
.planx-status-ok { color:#047857; background:#ecfdf3; border-color:#a7f3d0; }
.planx-status-wait { color:#92400e; background:#fffaeb; border-color:#fedf89; }
.planx-status-bad { color:#b42318; background:#fef3f2; border-color:#fecdca; }
hr { border-color:#e7ebf0!important; }
[data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:12px; }
[data-testid="stExpander"] summary p { font-size:14px; }
.stMarkdown p { line-height:1.65; }
@media(max-width:900px){
  .block-container{padding-left:1rem;padding-right:1rem}
  .planx-hero{padding:21px 19px}.planx-hero h1{font-size:28px}
}
@media(max-width:640px){
  .block-container{padding-top:1.1rem}.planx-hero h1{font-size:26px}
  .planx-card{min-height:100px;padding:14px}.planx-card-value{font-size:21px}
}
</style>
""",
        unsafe_allow_html=True,
    )


def brand():
    st.markdown(
        """
<div class="planx-brand">
  <div class="planx-brand-mark">↗</div>
  <div>
    <div class="planx-brand-title">StockDash</div>
    <div class="planx-brand-sub">Data to Insight.</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "PLANX INVESTMENT OS"):
    st.markdown(
        f"""
<div class="planx-hero">
  <div class="planx-eyebrow">{html.escape(eyebrow)}</div>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def card(title: str, value: str, note: str = "", status: str = ""):
    status_html = f'<div class="planx-card-note">{html.escape(status)}</div>' if status else ""
    st.markdown(
        f"""
<div class="planx-card">
  <div class="planx-card-title">{html.escape(title)}</div>
  <div class="planx-card-value">{html.escape(value)}</div>
  <div class="planx-card-note">{html.escape(note)}</div>
  {status_html}
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state(title: str, message: str):
    st.markdown(
        f"""
<div class="planx-empty">
  <strong style="color:#334155">{html.escape(title)}</strong><br>
  <span>{html.escape(message)}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def source_badge(label: str, state: str = "wait"):
    cls = {"ok": "planx-status-ok", "bad": "planx-status-bad"}.get(state, "planx-status-wait")
    st.markdown(
        f'<span class="planx-source {cls}">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )
