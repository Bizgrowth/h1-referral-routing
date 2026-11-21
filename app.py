"""Coordinator approval screen. Run: streamlit run app.py"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

import pandas as pd
import streamlit as st

from h1 import importer, scoring
from h1.suggest import Suggester

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "logs" / "decisions.jsonl"
SHOWN = ["referral_source", "product_description", "product_group", "hcpcs_code", "quantity",
         "insurance_company_city", "diag_code_2", "diag_code_4", "year"]  # never the answer key

st.set_page_config(page_title="H1 Referral Routing", layout="centered")
st.markdown("**🔒 Local only · de-identified data**")
st.title("Referral intake and vendor routing")


@st.cache_resource
def load(path: str, modified: float):
    result = importer.load(path)
    train, test = scoring.split(result.rows)
    vendors = sorted(v for v in result.rows["answer_vendor"].unique() if v)
    return Suggester.fit(train), test.to_dict("records"), vendors


def logged_ids() -> set:
    if not LOG.exists():
        return set()
    return {json.loads(line)["row_id"] for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()}


path = Path(os.environ.get("H1_INPUT") or importer.default_input(ROOT / "data"))
if not path.exists():
    st.warning("No referral export found. Put the de-identified export at data/Referrals.xlsx.")
    st.stop()

suggester, test_rows, vendors = load(str(path), path.stat().st_mtime)
done = logged_ids()
queue = [row for row in test_rows if row["row_id"] not in done]
if not queue:
    st.success(f"All {len(test_rows)} referrals from {scoring.TEST_YEAR} are reviewed. "
               "Run: python scripts/totals.py --baseline-seconds <your manual time>")
    st.stop()

row = queue[0]
row_id = int(row["row_id"])
if st.session_state.get("current") != row_id:
    st.session_state.current = row_id
    st.session_state.opened = time.monotonic()
result = scoring.route(row, suggester)
flags, suggestions = result["flags"], result["suggestions"]

st.caption(f"Referral #{row_id} · {len(test_rows) - len(queue) + 1} of {len(test_rows)}")
st.table(pd.DataFrame({"Field": SHOWN, "Value": [str(row.get(f, "")) or "—" for f in SHOWN]}).set_index("Field"))

st.subheader("Missing information")
if flags:
    for flag in flags:
        st.error(flag)
else:
    st.success("No missing or invalid items.")

st.subheader("Suggested vendors")
if suggestions:
    for i, s in enumerate(suggestions, 1):
        st.markdown(f"**{i}. {s.vendor}** — {s.reason}")
else:
    st.info("No vendor history for this referral. Choose a vendor or reject.")


def decide(decision: str, vendor):
    record = {"logged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "row_id": row_id,
              "decision": decision, "vendor": vendor,
              "top_suggestion": suggestions[0].vendor if suggestions else None,
              "flags": len(flags), "seconds": round(time.monotonic() - st.session_state.opened, 1)}
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    st.session_state.current = None
    st.rerun()


st.subheader("Decision")
approve, change, reject = st.columns(3)
if approve.button("Approve top vendor", type="primary", disabled=not suggestions, use_container_width=True):
    decide("approve", suggestions[0].vendor)
choice = change.selectbox("Vendor", vendors, label_visibility="collapsed")
if change.button("Change vendor", use_container_width=True):
    decide("change", choice)
if reject.button("Reject", use_container_width=True):
    decide("reject", None)
st.caption("Nothing is assigned without your decision. Each decision and its review time is logged locally to logs/.")
