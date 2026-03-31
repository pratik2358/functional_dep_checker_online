from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from utils import (
    compute_all_closures,
    compute_candidate_keys,
    compute_closure,
    discover_fds_with_chase,
    find_prime_attributes,
    group_fds,
    minimal_cover,
    project_dependency,
    check_minimal_cover,
    is_compact_minimal_cover,
)
from web_helpers import (
    format_candidate_keys,
    format_closures,
    format_fds,
    format_prime_attributes,
    generate_random_fds,
    grouped_fds_table,
    literal_eval_dataframe,
    parse_attr_set,
    parse_attributes,
    parse_fds,
)

st.set_page_config(page_title="Functional Dependency Explorer", layout="wide")

DEFAULT_ATTRS = "A, B, C, D, E"
DEFAULT_FDS = """A -> A,B,C
A,B -> A
B,C -> A,D
B -> A,B
C -> D"""
DEFAULT_PROJECTION = "A, B, C, D"
DEFAULT_CLOSURE_SET = "B, C"
DEFAULT_DISCOVER = """{
    'A': [1, 1, 2, 2, 2, 3],
    'B': [5, 5, 6, 6, 7, 8],
    'C': [9, 9, 9, 9, 10, 11],
    'D': [0, 0, 1, 1, 1, 2]
}"""

st.title("Functional Dependency Explorer")
st.caption("Interactive web interface for closure computation, candidate keys, minimal covers, projection, and FD discovery from a table.")

with st.sidebar:
    st.header("Input relation and FDs")
    attrs_text = st.text_input("Attributes", value=DEFAULT_ATTRS)
    fds_text = st.text_area("Functional dependencies", value=DEFAULT_FDS, height=220)
    st.markdown("Use one FD per line, for example `A,B -> C,D`.")

    try:
        attributes = parse_attributes(attrs_text)
        fds = parse_fds(fds_text)
        st.success(f"Parsed {len(attributes)} attributes and {len(fds)} dependencies.")
    except Exception as exc:
        attributes = set()
        fds = []
        st.error(str(exc))


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Closure",
    "All closures",
    "Keys and prime attributes",
    "Minimal cover",
    "Projection",
    "Discover from relation",
    "Check minimal cover",
])

with tab1:
    st.subheader("Compute a closure")
    subset_text = st.text_input("Attribute set to close", value=DEFAULT_CLOSURE_SET)
    if st.button("Compute closure", use_container_width=True):
        try:
            subset = parse_attr_set(subset_text)
            result = compute_closure(subset, fds)
            st.code("{" + ", ".join(sorted(subset)) + "}+ = {" + ", ".join(sorted(result)) + "}")
        except Exception as exc:
            st.error(str(exc))

with tab2:
    st.subheader("Compute all closures")
    if st.button("Compute all closures", use_container_width=True):
        try:
            all_closures = compute_all_closures(attributes, fds)
            rows = []
            for lhs, rhs in sorted(all_closures.items(), key=lambda kv: (len(kv[0]), tuple(sorted(kv[0])))):
                rows.append({"Subset": "{" + ", ".join(sorted(lhs)) + "}", "Closure": "{" + ", ".join(sorted(rhs)) + "}"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
            st.download_button("Download closures as text", format_closures(all_closures), file_name="all_closures.txt")
        except Exception as exc:
            st.error(str(exc))

with tab3:
    st.subheader("Candidate keys and prime attributes")
    if st.button("Compute keys", use_container_width=True):
        try:
            all_closures = compute_all_closures(attributes, fds)
            keys = compute_candidate_keys(all_closures, attributes)
            prime = find_prime_attributes(keys)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Candidate keys**")
                st.code(format_candidate_keys(keys))
            with col2:
                st.markdown("**Prime attributes**")
                st.code(format_prime_attributes(prime))
        except Exception as exc:
            st.error(str(exc))

with tab4:
    st.subheader("Minimal cover")
    randomization = st.slider("Randomization parameter p", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    if st.button("Compute minimal cover", use_container_width=True):
        try:
            result = minimal_cover(fds, p=randomization)
            st.code(format_fds(result))
            st.dataframe(grouped_fds_table(result), use_container_width=True)
        except Exception as exc:
            st.error(str(exc))

    st.markdown("---")
    st.markdown("**Generate a random FD instance**")
    c1, c2, c3 = st.columns(3)
    n_vars = c1.number_input("Number of attributes", min_value=1, value=6)
    num_fds = c2.number_input("Number of FDs", min_value=1, value=5)
    seed = c3.number_input("Seed", min_value=0, value=42)
    if st.button("Generate random FDs", use_container_width=True):
        attrs, rand_fds = generate_random_fds(int(n_vars), int(num_fds), seed=int(seed))
        st.code("Attributes: {" + ", ".join(sorted(attrs)) + "}\n\n" + format_fds(rand_fds))

with tab5:
    st.subheader("Project dependencies onto a sub-relation")
    projection_text = st.text_input("Projected relation R̂", value=DEFAULT_PROJECTION)
    if st.button("Project FDs", use_container_width=True):
        try:
            r_hat = parse_attributes(projection_text)
            result = project_dependency(fds, r_hat)
            st.code(format_fds(result))
            st.dataframe(grouped_fds_table(result), use_container_width=True)
        except Exception as exc:
            st.error(str(exc))

with tab6:
    st.subheader("Discover FDs from a relation")
    st.markdown("Upload a CSV or paste a Python dictionary that can be converted to a pandas DataFrame.")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    df_text = st.text_area("Or paste a Python dictionary", value=DEFAULT_DISCOVER, height=220)
    max_lhs = st.number_input("Maximum LHS size for discovery (value 0 refers to no cap)", min_value=0, value=0, help="0 means no explicit cap.")

    df = None
    parse_error = None
    try:
        if uploaded is not None:
            df = pd.read_csv(uploaded)
        else:
            df = literal_eval_dataframe(df_text)
    except Exception as exc:
        parse_error = str(exc)

    if parse_error:
        st.error(parse_error)
    elif df is not None:
        st.markdown("**Input relation**")
        st.dataframe(df, use_container_width=True)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download input CSV", csv_bytes, file_name="input_relation.csv")

    if st.button("Discover FDs", use_container_width=True):
        try:
            if df is None:
                raise ValueError("Please upload a CSV or paste a valid Python dictionary first.")
            discovered = discover_fds_with_chase(df, max_lhs=None if int(max_lhs) == 0 else int(max_lhs))
            grouped = group_fds(discovered)
            st.code(format_fds(grouped))
            st.dataframe(grouped_fds_table(grouped), use_container_width=True)
        except Exception as exc:
            st.error(str(exc))

st.markdown("---")
st.markdown("### Run locally")
st.code("pip install -r requirements.txt\nstreamlit run app.py")


with tab7:
    st.subheader("Check whether a given FD set is a minimal cover")
    st.markdown("Enter the candidate cover to test against the original FD set from the sidebar.")
    candidate_text = st.text_area(
        "Candidate FD set",
        value="A -> B,C\nB,C -> A,D\nC -> D",
        height=220,
        key="candidate_cover_text",
    )
    if st.button("Check candidate cover", use_container_width=True):
        try:
            candidate_fds = parse_fds(candidate_text)
            result = check_minimal_cover(fds, candidate_fds, attributes=attributes)
            compact_ok = is_compact_minimal_cover(attributes, fds, candidate_fds)

            c1, c2 = st.columns(2)
            with c1:
                if result["is_minimal_cover"]:
                    st.success("This FD set is a minimal cover of the original FD set.")
                else:
                    st.error("This FD set is not a minimal cover of the original FD set.")
            with c2:
                if compact_ok:
                    st.success("It is also a compact minimal cover.")
                elif result["is_minimal_cover"]:
                    st.warning("It is a minimal cover, but not a compact one.")
                else:
                    st.info("Compactness is not satisfied for this candidate.")

            if result["violations"]:
                st.markdown("**Why it fails**")
                for v in result["violations"]:
                    st.write(f"- {v}")

            st.markdown("**Compact form of the candidate**")
            st.code(format_fds(result["merged_form"]))
            st.dataframe(grouped_fds_table(result["merged_form"]), use_container_width=True)
        except Exception as exc:
            st.error(str(exc))
