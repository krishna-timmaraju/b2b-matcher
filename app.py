import streamlit as st
import pandas as pd

# 1. Create Mock Data (So you don't need a DB file for the POC)
buyers = pd.DataFrame([
    {"id": "BUYER_01", "name": "AutoParts Corp", "ind": "Automotive", "reg": "North America"},
    {"id": "BUYER_02", "name": "HealthGrid", "ind": "Healthcare", "reg": "Europe"}
])

sellers = pd.DataFrame([
    {"name": "FastBuild Steel", "ind": "Automotive", "reg": "North America", "iso": True, "cap": 0.9},
    {"name": "EuroMed Supplies", "ind": "Healthcare", "reg": "Europe", "iso": True, "cap": 0.4},
    {"name": "Global Parts Co", "ind": "Automotive", "reg": "APAC", "iso": False, "cap": 0.8},
    {"name": "Quality Medical", "ind": "Healthcare", "reg": "North America", "iso": True, "cap": 0.7}
])

# 2. Web App Interface
st.title("🤝 B2B Buyer-Seller Matchmaker POC")

# Sidebar for Selection
st.sidebar.header("Select Buyer")
selected_id = st.sidebar.selectbox("Choose a Buyer Account", buyers['id'])
buyer_row = buyers[buyers['id'] == selected_id].iloc[0]

st.write(f"### Matching Sellers for: {buyer_row['name']}")
st.write(f"Target Industry: **{buyer_row['ind']}** | Location: **{buyer_row['reg']}**")

# Match Logic (Simulating the Model)
st.sidebar.divider()
require_iso = st.sidebar.toggle("Require ISO Certification")

# Filter logic
results = sellers[sellers['ind'] == buyer_row['ind']] # Match by Industry
if require_iso:
    results = results[results['iso'] == True]

# Calculate a simple "Match Score"
def calculate_score(row):
    score = 70 # Base for industry match
    if row['reg'] == buyer_row['reg']: score += 20 # Proximity bonus
    if row['iso']: score += 10 # Certification bonus
    return score

results['match_score'] = results.apply(calculate_score, axis=1)
results = results.sort_values(by='match_score', ascending=False)

# Display Results
for _, seller in results.iterrows():
    with st.expander(f"{seller['name']} - Match Score: {seller['match_score']}%"):
        col1, col2 = st.columns(2)
        col1.write(f"📍 Region: {seller['reg']}")
        col1.write(f"📜 ISO Certified: {'Yes' if seller['iso'] else 'No'}")
        col2.metric("Available Capacity", f"{int(seller['cap']*100)}%")
        
        if seller['reg'] == buyer_row['reg']:
            st.success("✅ Geographic Match: Reduced Freight Costs Predicted.")
