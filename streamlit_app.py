import streamlit as st
import pandas as pd
import io
import xlsxwriter

st.set_page_config(page_title="Victor's Mission Control", layout="centered")

# 🚀 Header
st.title("🧑‍🚀 Victor’s Mission Control")
st.caption("Track your budget, launch your goals, and orbit financial freedom.")

# 📥 Income & Fixed Expenses
st.subheader("💰 Monthly Income & Expenses")

# Base income and expenses
income = st.number_input("Monthly Income", value=6200)
car_payment = st.number_input("Car Payment", value=467)
insurance = st.number_input("Car Insurance", value=100)
phone = st.number_input("Phone Bill", value=100)
food = st.number_input("Food Budget", value=800)
misc = st.number_input("Miscellaneous", value=300)

# Additional income
st.markdown("#### ➕ Add Additional Income Sources")
if "additional_income" not in st.session_state:
    st.session_state.additional_income = []

with st.form("add_income_form"):
    add_income_name = st.text_input("Income Source Name")
    add_income_amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="income_amount")
    add_income_submit = st.form_submit_button("Add Income")
    if add_income_submit and add_income_name and add_income_amount > 0:
        st.session_state.additional_income.append({
            "Source": add_income_name,
            "Amount": add_income_amount
        })

if st.session_state.additional_income:
    add_income_df = pd.DataFrame(st.session_state.additional_income)
    st.dataframe(add_income_df)
    total_additional_income = sum(item["Amount"] for item in st.session_state.additional_income)
else:
    total_additional_income = 0

# Additional fixed expenses
st.markdown("#### ➕ Add Additional Fixed Expenses")
if "additional_expenses" not in st.session_state:
    st.session_state.additional_expenses = []

with st.form("add_expense_form"):
    add_expense_name = st.text_input("Expense Name")
    add_expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="expense_amount")
    add_expense_submit = st.form_submit_button("Add Expense")
    if add_expense_submit and add_expense_name and add_expense_amount > 0:
        st.session_state.additional_expenses.append({
            "Expense": add_expense_name,
            "Amount": add_expense_amount
        })

if st.session_state.additional_expenses:
    add_expense_df = pd.DataFrame(st.session_state.additional_expenses)
    st.dataframe(add_expense_df)
    total_additional_expenses = sum(item["Amount"] for item in st.session_state.additional_expenses)
else:
    total_additional_expenses = 0

# Calculate totals
total_income = income + total_additional_income
total_expenses = car_payment + insurance + phone + food + misc + total_additional_expenses
surplus = total_income - total_expenses

st.markdown(f"**🧾 Total Expenses:** ${total_expenses:,.2f}")
st.markdown(f"**📈 Monthly Surplus:** ${surplus:,.2f}")

# 🎯 Savings Goals
st.subheader("🏦 Savings Goals")
house_fund = st.slider("House Fund Contribution", 0, int(surplus), value=2000)
transition_fund = st.slider("Transition Fund Contribution", 0, int(max(0, surplus - house_fund)), value=1000)
student_loan_fund = st.slider("Student Loan Contribution", 0, int(max(0, surplus - house_fund - transition_fund)), value=500)

remaining_buffer = surplus - house_fund - transition_fund - student_loan_fund
st.markdown(f"**🧮 Remaining Buffer:** ${remaining_buffer:,.2f}")

# 📊 Summary Dashboard
st.subheader("📊 Budget Summary")
st.metric("Total Monthly Income", f"${income:,.2f}")
st.metric("Total Expenses", f"${total_expenses:,.2f}")
st.metric("Savings Contributions", f"${house_fund + transition_fund + student_loan_fund:,.2f}")
st.metric("Remaining Buffer", f"${remaining_buffer:,.2f}")


# Optional: Visual summary charts
col1, col2 = st.columns(2)
with col1:
    st.markdown("##### Income vs Expenses")
    pie_df = pd.DataFrame({
        "Type": ["Total Income", "Total Expenses"],
        "Amount": [total_income, total_expenses]
    })
    st.plotly_chart({
        "data": [{
            "labels": pie_df["Type"],
            "values": pie_df["Amount"],
            "type": "pie",
            "hole": .4
        }],
        "layout": {"showlegend": True}
    }, use_container_width=True)

with col2:
    st.markdown("##### Savings Allocation")
    savings_pie = pd.DataFrame({
        "Fund": ["House", "Transition", "Student Loan", "Buffer"],
        "Amount": [house_fund, transition_fund, student_loan_fund, remaining_buffer]
    })
    st.plotly_chart({
        "data": [{
            "labels": savings_pie["Fund"],
            "values": savings_pie["Amount"],
            "type": "pie"
        }],
        "layout": {"showlegend": True}
    }, use_container_width=True)


# 📥 Downloadable & Visual Budget Spreadsheet
st.subheader("⬇️ Download Your Budget Spreadsheet")


# Organize data into sections for better visualization
income_rows = [
    {"Section": "Income", "Category": "Base Income", "Amount": income}
]
income_rows += [
    {"Section": "Income", "Category": f"Additional Income: {item['Source']}", "Amount": item["Amount"]}
    for item in st.session_state.additional_income
]
income_rows.append({"Section": "Income", "Category": "Total Income", "Amount": total_income})

expense_rows = [
    {"Section": "Expenses", "Category": "Car Payment", "Amount": car_payment},
    {"Section": "Expenses", "Category": "Car Insurance", "Amount": insurance},
    {"Section": "Expenses", "Category": "Phone Bill", "Amount": phone},
    {"Section": "Expenses", "Category": "Food Budget", "Amount": food},
    {"Section": "Expenses", "Category": "Miscellaneous", "Amount": misc}
]
expense_rows += [
    {"Section": "Expenses", "Category": f"Additional Expense: {item['Expense']}", "Amount": item["Amount"]}
    for item in st.session_state.additional_expenses
]
expense_rows.append({"Section": "Expenses", "Category": "Total Expenses", "Amount": total_expenses})

summary_rows = [
    {"Section": "Summary", "Category": "Monthly Surplus", "Amount": surplus}
]

savings_rows = [
    {"Section": "Savings", "Category": "House Fund Contribution", "Amount": house_fund},
    {"Section": "Savings", "Category": "Transition Fund Contribution", "Amount": transition_fund},
    {"Section": "Savings", "Category": "Student Loan Contribution", "Amount": student_loan_fund},
    {"Section": "Savings", "Category": "Remaining Buffer", "Amount": remaining_buffer}
]

# Combine all rows
export_rows = income_rows + expense_rows + summary_rows + savings_rows
export_df = pd.DataFrame(export_rows)

# Show a styled preview table
def highlight_section(row):
    color = {
        "Income": "#e0f7fa",
        "Expenses": "#ffebee",
        "Savings": "#e8f5e9",
        "Summary": "#fffde7"
    }.get(row.Section, "#ffffff")
    return [f"background-color: {color}"] * len(row)

st.markdown("##### Preview of Your Budget Spreadsheet")
st.dataframe(
    export_df.style.apply(highlight_section, axis=1).format({"Amount": "${:,.2f}"}),
    use_container_width=True
)

# Download as Excel with formatting
def to_excel(df):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Budget")

    # Define formats
    formats = {
        "Income": workbook.add_format({'bg_color': '#e0f7fa', 'num_format': '$#,##0.00'}),
        "Expenses": workbook.add_format({'bg_color': '#ffebee', 'num_format': '$#,##0.00'}),
        "Savings": workbook.add_format({'bg_color': '#e8f5e9', 'num_format': '$#,##0.00'}),
        "Summary": workbook.add_format({'bg_color': '#fffde7', 'num_format': '$#,##0.00'}),
        "Header": workbook.add_format({'bold': True, 'bg_color': '#bdbdbd', 'border': 1}),
        "Default": workbook.add_format({'num_format': '$#,##0.00'})
    }

    # Write header
    for col_num, value in enumerate(df.columns):
        worksheet.write(0, col_num, value, formats["Header"])

    # Write data rows
    for row_num, row in enumerate(df.itertuples(index=False), 1):
        section = getattr(row, "Section")
        fmt = formats.get(section, formats["Default"])
        worksheet.write(row_num, 0, row.Section)
        worksheet.write(row_num, 1, row.Category)
        worksheet.write_number(row_num, 2, row.Amount, fmt)

    # Set column widths
    worksheet.set_column(0, 0, 12)
    worksheet.set_column(1, 1, 35)
    worksheet.set_column(2, 2, 18)

    workbook.close()
    output.seek(0)
    return output

excel_data = to_excel(export_df)

st.download_button(
    label="Download Fancy Budget as Excel",
    data=excel_data,
    file_name="budget_summary.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
