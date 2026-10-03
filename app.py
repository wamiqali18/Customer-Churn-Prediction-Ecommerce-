import sqlite3

from pathlib import Path



import joblib

import pandas as pd

import streamlit as st



# ---------- Page setup (must be the first Streamlit command) ----------

st.set_page_config(page_title="E-Commerce Intelligence", page_icon="🛒", layout="wide")



BASE = Path(__file__).parent                              # folder of this file (works on Streamlit Cloud)

DB = BASE / "ecommerce_clean.db"                          # cleaned database

NET = "o.quantity * o.unit_price * (1 - o.discount)"      # net revenue formula (o = orders table)



# Colours used in charts and result cards

CYAN, PURPLE, PINK = "#00E5FF", "#8B5CF6", "#FF4D8D"

GREEN, AMBER, RED = "#2EE6A6", "#FFC857", "#FF4D6D"



# ---------- Dark theme styling (CSS) ----------

st.markdown("""

<style>

.stApp { background-color: #000000; }

[data-testid="stSidebar"] { background-color: #08080c; border-right: 1px solid #1f1f2b; }

[data-testid="stMetric"] {

    background: linear-gradient(145deg, #0f0f16, #16161f);

    border: 1px solid #2a2a3b; border-radius: 16px; padding: 18px 12px;

    box-shadow: 0 0 18px rgba(0, 229, 255, 0.08);

}

[data-testid="stMetricLabel"] { color: #9aa0b4; }

[data-testid="stMetricValue"] {

    color: #00E5FF;

    font-weight: 700;

    font-size: 1.4rem !important;

    white-space: nowrap;

}

h1 { background: linear-gradient(90deg, #00E5FF, #8B5CF6);

     -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.stButton > button {

    background: linear-gradient(90deg, #00B8D9, #8B5CF6); color: white; border: none;

    border-radius: 12px; padding: 0.6rem 1.6rem; font-weight: 600;

}

.stButton > button:hover { box-shadow: 0 0 16px rgba(139, 92, 246, 0.6); color: white; }

.result-card { border-radius: 16px; padding: 22px; text-align: center; border: 1px solid; margin: 14px 0; }

.result-card h2 { margin: 0; }

.result-card p { margin: 6px 0 0 0; color: #cfcfe0; }

</style>

""", unsafe_allow_html=True)





# ---------- Helper functions ----------

@st.cache_data                                            # remember SQL results -> faster app

def run_sql(sql):

    with sqlite3.connect(DB) as con:

        return pd.read_sql(sql, con)





@st.cache_resource                                        # load each model only once

def load_model(name):

    return joblib.load(BASE / "models" / name)





def result_card(title, subtitle, color):

    """Coloured box that shows the prediction."""

    st.markdown(f"<div class='result-card' style='border-color:{color}; background:{color}18'>"

                f"<h2 style='color:{color}'>{title}</h2><p>{subtitle}</p></div>", unsafe_allow_html=True)





# ---------- Sidebar navigation ----------

st.sidebar.title("🛒 E-Commerce AI")

page = st.sidebar.radio("Go to", ["Dashboard", "Churn Prediction", "Sentiment Analysis"])

st.sidebar.caption("Data: ecommerce_clean.db (SQLite)\nModels: scikit-learn")



# ====================================================================== Dashboard

if page == "Dashboard":

    st.title("Sales Dashboard")



    # --- numbers from SQL ---

    kpi = run_sql(f"SELECT SUM({NET}) AS revenue, COUNT(*) AS orders, AVG(o.returned) AS ret FROM orders o").iloc[0]

    customers = run_sql("SELECT COUNT(*) AS n FROM customers").n[0]



    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total net revenue", f"PKR {kpi.revenue / 1e6:,.1f}M")

    c2.metric("Total orders", f"{int(kpi.orders):,}")

    c3.metric("Total customers", f"{customers:,}")

    c4.metric("Return rate", f"{kpi.ret:.1%}")



    monthly = run_sql(f"SELECT strftime('%Y-%m', o.order_date) AS month, SUM({NET}) AS revenue "

                      "FROM orders o GROUP BY month ORDER BY month")

    category = run_sql(f"SELECT p.category, SUM({NET}) AS revenue FROM orders o "

                       "JOIN products p ON p.product_id = o.product_id "

                       "GROUP BY p.category ORDER BY revenue DESC")

    city = run_sql(f"SELECT c.city, SUM({NET}) AS revenue FROM orders o "

                   "JOIN customers c ON c.customer_id = o.customer_id "

                   "GROUP BY c.city ORDER BY revenue DESC LIMIT 10")

    top_cust = run_sql(f"SELECT c.customer_name AS customer, c.city, COUNT(*) AS orders, "

                       f"ROUND(SUM({NET})) AS total_spending FROM orders o "

                       "JOIN customers c ON c.customer_id = o.customer_id "

                       "GROUP BY c.customer_id ORDER BY total_spending DESC LIMIT 10")

    top_prod = run_sql(f"SELECT p.product_name AS product, p.category, ROUND(SUM({NET})) AS net_revenue "

                       "FROM orders o JOIN products p ON p.product_id = o.product_id "

                       "GROUP BY p.product_id ORDER BY net_revenue DESC LIMIT 5")



    # --- charts and tables ---

    st.subheader("Monthly net revenue")

    st.line_chart(monthly, x="month", y="revenue", color=CYAN)



    left, right = st.columns(2)

    left.subheader("Revenue by category")

    left.bar_chart(category, x="category", y="revenue", color=PURPLE)

    right.subheader("Revenue by city (top 10)")

    right.bar_chart(city, x="city", y="revenue", color=PINK)



    left.subheader("Top 10 customers")

    left.dataframe(top_cust, hide_index=True)

    right.subheader("Top 5 products")

    right.dataframe(top_prod, hide_index=True)



# ============================================================ Churn Prediction

elif page == "Churn Prediction":

    st.title("Customer Churn Prediction")

    st.caption("Enter a customer's purchase history up to the cut-off date. The saved model estimates "

               "the chance that the customer makes NO purchase in the next 3 months.")

    model = load_model("churn_model.pkl")



    c1, c2 = st.columns(2)

    # Updated input limits matching training data bounds (1–60 orders, 0–1.5M PKR, 0–1400 days)

    total_orders = c1.number_input("Total orders", 1, 60, 10)

    total_spending = c2.number_input("Total spending (PKR)", 0.0, 1_500_000.0, 150_000.0, step=5_000.0)

    days_since = c1.number_input("Days since last order", 0, 1400, 60)

    return_rate = c2.slider("Return rate", 0.0, 1.0, 0.05)

    delivery = c1.number_input("Average delivery days", 1.0, 15.0, 3.6, step=0.1)

    age = c2.number_input("Age", 18, 80, 30)

    membership = c1.selectbox("Membership type", ["Standard", "Silver", "Gold", "Premium"])



    # Average Order Value check

    aov = total_spending / total_orders if total_orders > 0 else 0

    if aov < 82:

        st.warning(f"⚠️️ Unrealistic input: Calculated Average Order Value is **PKR {aov:,.2f}**, "

                   "which is below the cheapest product price (~82 PKR). Predictions may be inaccurate.")



    if st.button("Predict churn"):

        tiers = {"Standard": 0, "Silver": 1, "Gold": 2, "Premium": 3}

        row = pd.DataFrame([{

            "total_orders": total_orders,

            "total_spending": total_spending,

            "avg_order_value": aov,

            "days_since_last_order": days_since,

            "return_rate": return_rate,

            "avg_delivery_days": delivery,

            "age": age,

            "membership_type": tiers[membership]

        }])

        row = row[list(model.feature_names_in_)]                         # matching feature order



        prob = model.predict_proba(row)[0, 1]                            # probability of churn

        stay_prob = 1.0 - prob                                          # probability of staying



        subtitle_text = f"Churn probability: {prob:.1%} | Stay probability: {stay_prob:.1%}"



        if prob >= 0.5:

            result_card("Likely to CHURN", subtitle_text, RED)

        else:

            result_card("Likely to STAY", subtitle_text, GREEN)

       

        st.progress(float(prob))



# ========================================================== Sentiment Analysis

else:

    st.title("Review Sentiment Analysis")

    model = load_model("sentiment_model.pkl")

    text = st.text_area("Write a product review", "Very satisfied, quality feels premium. Highly recommended.")



    if st.button("Analyze sentiment"):

        if not text.strip():

            st.warning("Please type a review first.")

        else:

            label = model.predict([text])[0]

            probs = pd.Series(model.predict_proba([text])[0], index=model.classes_, name="probability")

            icon = {"Positive": "😊", "Neutral": "😐", "Negative": "😞"}[label]

            color = {"Positive": GREEN, "Neutral": AMBER, "Negative": RED}[label]

            result_card(f"{icon} {label}", f"Confidence: {probs[label]:.1%}", color)

            st.bar_chart(probs, color=PURPLE)

            st.caption("The model was trained on template-style reviews, so unusual wording may be misclassified.") 