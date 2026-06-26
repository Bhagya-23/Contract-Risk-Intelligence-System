import streamlit as st
import fitz
import pandas as pd
import re
import plotly.express as px

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Contract Risk Intelligence",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Powered Contract Risk Intelligence System")

st.markdown("""
### AI Assisted Legal Contract Analyzer

Upload a legal contract and receive an automated
risk assessment with business insights.
""")

st.divider()

# ==========================================================
# FILE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload Contract PDF",
    type=["pdf"]
)

# ==========================================================
# PDF EXTRACTION
# ==========================================================

def extract_pdf(upload):

    pdf = fitz.open(stream=upload.read(), filetype="pdf")

    text = ""

    for page in pdf:

        text += page.get_text()

    return text

# ==========================================================
# CLAUSE DETECTOR
# ==========================================================

def detect_clauses(text):

    text = text.replace("\n"," ")

    text = re.sub(r"\s+"," ",text)

    pattern = r'(?=(?:\d+\.\d+|\d+\.|ARTICLE\s+[IVXLC]+|SECTION\s+\d+))'

    clauses = re.split(pattern,text,flags=re.IGNORECASE)

    clean=[]

    for clause in clauses:

        clause=clause.strip()

        if len(clause)>80:

            clean.append(clause)

    return clean

# ==========================================================
# CLAUSE TYPES
# ==========================================================

CLAUSE_TYPES={

"Payment":[
"payment","invoice","fees","charges","deposit","price","amount"],

"Termination":[
"terminate","termination","cancel","expiry","expiration"],

"Liability":[
"liability","liable","loss","damage","indemnify","indemnification"],

"Confidentiality":[
"confidential","nda","privacy","secret","non disclosure"],

"Warranty":[
"warranty","guarantee","defect"],

"Arbitration":[
"arbitration","court","jurisdiction","dispute"],

"Force Majeure":[
"force majeure","earthquake","pandemic","flood","war"],

"Intellectual Property":[
"copyright","patent","trademark","ip","intellectual property"]

}

def detect_clause_type(clause):

    text=clause.lower()

    for ctype,words in CLAUSE_TYPES.items():

        for word in words:

            if word in text:

                return ctype

    return "General"
# ==========================================================
# RISK ENGINE
# ==========================================================

HIGH_RISK = {

    "unlimited liability":
        "Unlimited financial responsibility",

    "terminate without notice":
        "Immediate termination clause",

    "without notice":
        "No prior notification",

    "exclusive rights":
        "Exclusive ownership clause",

    "penalty":
        "Penalty obligation",

    "indemnify":
        "Legal indemnification",

    "breach":
        "Breach of agreement"

}


MEDIUM_RISK = {

    "renewal":
        "Automatic renewal",

    "payment":
        "Payment obligation",

    "interest":
        "Interest charges",

    "arbitration":
        "Dispute resolution",

    "confidential":
        "Confidentiality obligation",

    "intellectual property":
        "IP ownership"

}


def detect_risk(clause):

    text = clause.lower()

    for keyword, reason in HIGH_RISK.items():

        if keyword in text:

            return (

                "High",

                reason,

                "Review this clause with legal counsel."

            )

    for keyword, reason in MEDIUM_RISK.items():

        if keyword in text:

            return (

                "Medium",

                reason,

                "Verify business requirements before signing."

            )

    return (

        "Low",

        "No major contractual concern detected.",

        "No immediate action required."

    )

# ==========================================================
# CONTRACT ANALYSIS
# ==========================================================

def analyze_contract(clauses):

    results = []

    high = 0

    medium = 0

    low = 0

    for i, clause in enumerate(clauses):

        clause_type = detect_clause_type(clause)

        risk, reason, recommendation = detect_risk(clause)

        if risk == "High":
            high += 1

        elif risk == "Medium":
            medium += 1

        else:
            low += 1

        results.append({

            "Clause No": i + 1,

            "Clause Type": clause_type,

            "Risk": risk,

            "Reason": reason,

            "Recommendation": recommendation,

            "Clause": clause[:350]

        })

    df = pd.DataFrame(results)

    return df, high, medium, low

# ==========================================================
# MAIN APPLICATION
# ==========================================================

if uploaded_file:

    with st.spinner("Reading contract..."):
        pdf_text = extract_pdf(uploaded_file)

    clauses = detect_clauses(pdf_text)

    df, high, medium, low = analyze_contract(clauses)

    total = len(df)

    score = max(0, 100 - ((high * 10) + (medium * 5) + low))

    st.divider()
    st.subheader("📊 Contract Risk Dashboard")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("📄 Total Clauses", total)
    c2.metric("🔴 High Risk", high)
    c3.metric("🟡 Medium Risk", medium)
    c4.metric("🟢 Low Risk", low)
    c5.metric("📈 Risk Score", f"{score}/100")

    risk_df = pd.DataFrame({
        "Risk Level": ["High","Medium","Low"],
        "Count":[high,medium,low]
    })

    fig = px.pie(
        risk_df,
        values="Count",
        names="Risk Level",
        title="Risk Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📑 Executive Summary")

    if score >= 80:
        st.success("Overall Contract Risk: LOW")
    elif score >= 60:
        st.warning("Overall Contract Risk: MEDIUM")
    else:
        st.error("Overall Contract Risk: HIGH")

    st.subheader("📋 Clause Analysis")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Contract Report",
        csv,
        "Contract_Risk_Report.csv",
        "text/csv"
    )
