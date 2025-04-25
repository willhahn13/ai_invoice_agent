
import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import date
from num2words import num2words

st.set_page_config(page_title="Invoice to Payment Request AI", layout="centered")
st.title("📄 Invoice to Payment Request Generator")

st.markdown("""
Upload a PDF invoice and the AI will:
- Extract vendor, invoice number, and amount
- Match the cost code from your project's budget
- Generate a payment request output (PDF or Google Sheet-ready)
""")

uploaded_file = st.file_uploader("Upload Invoice PDF", type="pdf")
cost_data = {
    "EXCAVATION/BACKFILL": "18286",
    "FRAMING": "18288",
    "LUMBER": "18289",
    "ROOFING": "18290",
    "SIDING": "18291",
    "GUTTERS": "18293",
    "PLUMBING": "18295",
    "ELECTRICAL": "18296",
    "HVAC": "18294",
    "PAINTING": "18299",
    "DRYWALL": "18298",
    "FOUNDATION": "18311",
    "PERMITS": "18251",
    "WATER/SEWER LINE": "18284",
    "PRE TREATMENT": "18285"
}

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    st.subheader("Extracted Invoice Text")
    st.text(text)

    # Extract payee
    payee_match = re.search(r"(?<=\n)([A-Z][a-zA-Z&,. ]+ Sons)", text)
    payee = payee_match.group(0).strip() if payee_match else "Unknown"

    # Address
    address_match = re.search(r"(\d+\s+.*?,\s*\w+\s+MO\s+\d{5})", text)
    address = address_match.group(0).strip() if address_match else "Unknown"

    # Invoice Number
    invoice_match = re.search(r"\b(\d{4,6})\b", text)
    invoice_number = invoice_match.group(1) if invoice_match else "0000"

    # Amount
    amount_match = re.search(r"\$([\d,.]+)", text)
    amount = amount_match.group(1) if amount_match else "0.00"
    try:
        amount_float = float(amount.replace(",", ""))
    except:
        amount_float = 0.00
    written_amount = num2words(amount_float, to="currency", lang="en").replace("euro", "dollars").replace("cents", "cents")

    # Budget Category Match
    matched_code = "Unknown"
    for k, v in cost_data.items():
        if k.lower() in text.lower():
            matched_code = v
            break

    st.subheader("📋 Auto-Filled Payment Request")
    st.write(f"**Payee:** {payee}")
    st.write(f"**Address:** {address}")
    st.write(f"**Invoice #:** {invoice_number}")
    st.write(f"**Amount:** ${amount_float:,.2f}")
    st.write(f"**Written Amount:** {written_amount}")
    st.write(f"**Budget Category #:** {matched_code}")
    st.write(f"**Date Prepared:** {date.today().strftime('%m/%d/%y')}")
    st.success("Ready to export or copy data.")
