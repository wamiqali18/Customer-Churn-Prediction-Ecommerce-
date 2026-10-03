# AI Powered E-Commerce Customer Intelligence System

End-to-end data science project built on a raw SQLite e-commerce database (`ecommerce_hackathon.db`):
data cleaning → SQL analysis → EDA → churn prediction (Logistic Regression, Random Forest, Neural Network)
→ review sentiment analysis (TF-IDF + Logistic Regression) → Streamlit app.

**Live app:** `<paste your Streamlit Community Cloud link here>`

## Project files
| File | Purpose |
|---|---|
| `hackathon.ipynb` | Cleaning, EDA, ML, DL and NLP work |
| `queries.sql` | The five required SQL queries |
| `app.py` | Streamlit app (Dashboard, Churn Prediction, Sentiment Analysis) |
| `ecommerce_clean.db` | Cleaned database used by the app (dashboard numbers come from SQL on this file) |
| `models/churn_model.pkl`, `models/sentiment_model.pkl` | Saved models loaded by the app |
| `requirements.txt` | Dependencies |

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Key results
- Total net revenue: **PKR 936.5M** across 64,925 valid orders and 8,000 customers (net = quantity × unit price × (1 − discount)).
- Churn (49% of customers churned in Jun–Aug 2026): Logistic Regression and Random Forest both reach ROC-AUC ≈ 0.79 and recall ≈ 0.86. The neural network was slightly worse (AUC 0.78), so **Logistic Regression** is deployed.
- Sentiment: TF-IDF + Logistic Regression scores 1.00 on the held-out set, but the reviews are template-generated, so this will not hold on real customer text.

## Three business insights
1. **Electronics is about 70% of net revenue**, and two headphone products give about 20% on their own. This is a concentration risk, so stock, pricing and supplier backup for these items should be a priority.
2. **Revenue grows steadily but fell about 12% in August 2026** after a July peak (84M → 73M). It should be checked for seasonality or stock issues before it becomes a trend.
3. **Fashion has the highest return rate (about 11%)** and the most orders but only about 6.6% of revenue, so returns eat into a thin margin. Size guides and better product photos could reduce them.

## Notes
- Cleaning decisions are explained in the notebook (Task A).
- Churn features use only orders up to 31 May 2026; the target is no purchase from 1 Jun to 31 Aug 2026, so there is no leakage.
