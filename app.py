import streamlit as st
import pandas as pd
import joblib
import xgboost as xgb

# --- LOAD ASSETS ---
@st.cache_resource # This keeps the model in memory so the app is fast
def load_assets():
    model = joblib.load('xgb_match_model.pkl')
    le_ind = joblib.load('le_industry.pkl')
    le_reg = joblib.load('le_region.pkl')
    return model, le_ind, le_reg

model, le_ind, le_reg = load_assets()

# --- MOCK DATA: RFQs FROM BUYERS ---
# In a real app, this would come from your SQL database
rfqs = pd.DataFrame([
    {"rfq_id": "RFQ-99", "buyer_name": "Tesla", "industry": "Automotive", "region": "North America", "budget": 50000},
    {"rfq_id": "RFQ-102", "buyer_name": "Mayo Clinic", "industry": "Healthcare", "region": "Europe", "budget": 12000},
    {"rfq_id": "RFQ-105", "buyer_name": "BMW", "industry": "Automotive", "region": "Europe", "budget": 30000}
])

# --- SELLER VIEW ---
st.title("👨‍💼 Seller Dashboard: Match Scoring")
st.sidebar.header("Seller Profile")
my_industry = st.sidebar.selectbox("Your Industry", ["Automotive", "Healthcare", "Electronics"])
my_region = st.sidebar.selectbox("Your Region", ["North America", "Europe", "APAC"])

st.subheader("Available RFQs & Predictive Match Scores")

# --- PREDICTION LOGIC ---
def get_prediction(rfq):
    # 1. Encode the categorical data exactly as you did in Colab
    try:
        buyer_ind_enc = le_ind.transform([rfq['industry']])[0]
        seller_ind_enc = le_ind.transform([my_industry])[0]
        reg_enc = le_reg.transform([rfq['region']])[0]
        
        # 2. Create the feature array (Must match your Colab X_train columns exactly!)
        # Example order: [buyer_ind, seller_ind, is_match, region, budget]
        features = pd.DataFrame([[
            buyer_ind_enc, 
            seller_ind_enc, 
            1 if rfq['industry'] == my_industry else 0,
            reg_enc,
            rfq['budget']
        ]], columns=['buyer_industry_enc', 'seller_industry_enc', 'is_industry_match', 'region_enc', 'order_value_usd'])
        
        # 3. Predict
        score = model.predict(features)[0]
        return round(float(score), 2)
    except:
        return 0.0

# Display RFQs with Scores
for index, rfq in rfqs.iterrows():
    score = get_prediction(rfq)
    
    # Visual Logic: Higher scores get different colors
    color = "green" if score > 4.0 else "orange" if score > 3.0 else "red"
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        col1.write(f"**{rfq['rfq_id']}**")
        col2.write(f"Buyer: {rfq['buyer_name']} ({rfq['region']})")
        col3.markdown(f"**Match Score: :{color}[{score} / 5.0]**")
        st.divider()
