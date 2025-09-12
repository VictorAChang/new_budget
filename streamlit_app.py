import streamlit as st
import pandas as pd

st.set_page_config(page_title="Victor's Mission Control", layout="centered")

# 🚀 Header
st.title("🧑‍🚀 Victor’s Mission Control")
st.caption("Track your budget, launch your goals, and orbit financial freedom.")

# 📥 Income & Fixed Expenses
st.subheader("💰 Monthly Income & Expenses")
income = st.number_input("Monthly Income", value=6200)
car_payment = st.number_input("Car Payment", value=467)
insurance = st.number_input("Car Insurance", value=100)
phone = st.number_input("Phone Bill", value=100)
food = st.number_input("Food Budget", value=800)
misc = st.number_input("Miscellaneous", value=300)

total_expenses = car_payment + insurance + phone + food + misc
surplus = income - total_expenses

st.markdown(f"**🧾 Total Expenses:** ${total_expenses:,.2f}")
st.markdown(f"**📈 Monthly Surplus:** ${surplus:,.2f}")

# 🎯 Savings Goals
st.subheader("🏦 Savings Goals")
house_fund = st.slider("House Fund Contribution", 0, int(surplus), value=2000)
transition_fund = st.slider("Transition Fund Contribution", 0, int(surplus - house_fund), value=1000)
student_loan_fund = st.slider("Student Loan Contribution", 0, int(surplus - house_fund - transition_fund), value=500)

remaining_buffer = surplus - house_fund - transition_fund - student_loan_fund
st.markdown(f"**🧮 Remaining Buffer:** ${remaining_buffer:,.2f}")

# 🍱 Spending Log
st.subheader("📅 Daily Spending Log")
if "log" not in st.session_state:
    st.session_state.log = []

with st.form("spending_form"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Car", "Fun", "Bills", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    mood = st.selectbox("Mood", ["😊", "😐", "😍", "😢", "😎"])
    submitted = st.form_submit_button("Add Entry")
    if submitted:
        st.session_state.log.append({
            "Date": date,
            "Category": category,
            "Description": description,
            "Amount": amount,
            "Mood": mood
        })

if st.session_state.log:
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df)

# 📊 Summary Dashboard
st.subheader("📊 Budget Summary")
st.metric("Total Monthly Income", f"${income:,.2f}")
st.metric("Total Expenses", f"${total_expenses:,.2f}")
st.metric("Savings Contributions", f"${house_fund + transition_fund + student_loan_fund:,.2f}")
st.metric("Remaining Buffer", f"${remaining_buffer:,.2f}")

# 🧪 What-If Simulator
st.subheader("🧪 What-If Simulator")
future_income = st.slider("Future Monthly Income (VA + BAH)", 3000, 7000, value=4000)
future_expenses = st.slider("Future Monthly Expenses", 1000, 3000, value=1800)
future_surplus = future_income - future_expenses
st.markdown(f"**🧠 Future Surplus Estimate:** ${future_surplus:,.2f}")

