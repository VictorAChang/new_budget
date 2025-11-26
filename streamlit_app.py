import streamlit as st
import pandas as pd
import io
import xlsxwriter
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="Chang Budget", layout="centered")

# Custom theme with Microsoft colors
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0078D4 0%, #50E6FF 100%);
    }
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #0078D4 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #0078D4 !important;
    }
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4,
    div[data-testid="stMarkdownContainer"] h5,
    div[data-testid="stMarkdownContainer"] h6 {
        color: #0078D4 !important;
    }
    .stMarkdown p, .stMarkdown strong, .stMarkdown em {
        color: #323130 !important;
    }
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] strong,
    div[data-testid="stMarkdownContainer"] em {
        color: #323130 !important;
    }
    .stButton button {
        background-color: #0078D4 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
    }
    .stButton button:hover {
        background-color: #106EBE !important;
    }
    .stDownloadButton button {
        background-color: #0078D4 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
    }
    .stDownloadButton button:hover {
        background-color: #106EBE !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 🚀 Header
st.title("🧑‍🚀 Chang Family Budgetary Tool")
st.caption("Track your budget, launch your goals, and orbit financial freedom.")

# 📥 Income & Fixed Expenses
st.subheader("💰 Monthly Income & Expenses")

# Base income and expenses
income = st.number_input("Monthly Income", value=4044.91, format="%.2f")
home = st.number_input("House Payment")
home_insurance = st.number_input("Home Insurance")
car_payment = st.number_input("Car Payment")
car_insurance = st.number_input("Car Insurance")
phone_bill = st.number_input("Phone Bill")
internet = st.number_input("Internet Bill")
electricity = st.number_input("Electricity Bill")
water = st.number_input("Water Bill")



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
        st.rerun()

if st.session_state.additional_income:
    for i, income_item in enumerate(st.session_state.additional_income):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"**{income_item['Source']}**")
        with col2:
            st.markdown(f"${income_item['Amount']:,.2f}")
        with col3:
            if st.button("🗑️", key=f"delete_income_{i}"):
                st.session_state.additional_income.pop(i)
                st.rerun()
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
        st.rerun()

if st.session_state.additional_expenses:
    for i, expense in enumerate(st.session_state.additional_expenses):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"**{expense['Expense']}**")
        with col2:
            st.markdown(f"${expense['Amount']:,.2f}")
        with col3:
            if st.button("🗑️", key=f"delete_expense_{i}"):
                st.session_state.additional_expenses.pop(i)
                st.rerun()
    total_additional_expenses = sum(item["Amount"] for item in st.session_state.additional_expenses)
else:
    total_additional_expenses = 0

# Calculate totals
total_income = income + total_additional_income
total_expenses = home + home_insurance + car_payment + car_insurance + phone_bill + internet + electricity + water + total_additional_expenses
surplus = total_income - total_expenses

st.markdown(f"**💵 Total Income:** ${total_income:,.2f}")
st.markdown(f"**🧾 Total Expenses:** ${total_expenses:,.2f}")
st.markdown(f"**📈 Monthly Surplus:** ${surplus:,.2f}")

# 🎯 Savings Goals
st.subheader("🎯 Savings Goals")
st.markdown("#### ➕ Create Savings Goals")

if "savings_goals" not in st.session_state:
    st.session_state.savings_goals = []

with st.form("add_savings_goal_form"):
    goal_name = st.text_input("Goal Name (e.g., Emergency Fund, Vacation)")
    goal_target = st.number_input("Target Amount ($)", min_value=0.0, format="%.2f", key="goal_target")
    goal_monthly = st.number_input("Monthly Contribution ($)", min_value=0.0, format="%.2f", key="goal_monthly")
    add_goal_submit = st.form_submit_button("Add Savings Goal")
    if add_goal_submit and goal_name and goal_target > 0 and goal_monthly > 0:
        months_to_goal = goal_target / goal_monthly if goal_monthly > 0 else 0
        st.session_state.savings_goals.append({
            "Goal": goal_name,
            "Target": goal_target,
            "Monthly": goal_monthly,
            "Months": months_to_goal
        })
        st.rerun()

if st.session_state.savings_goals:
    st.markdown("#### 📊 Your Savings Goals")
    
    # Allow modification of monthly contributions
    for i, goal in enumerate(st.session_state.savings_goals):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        with col1:
            st.markdown(f"**{goal['Goal']}**")
        with col2:
            st.markdown(f"Target: ${goal['Target']:,.2f}")
        with col3:
            new_monthly = st.number_input(
                f"Monthly", 
                min_value=0.0, 
                value=float(goal['Monthly']),
                format="%.2f",
                key=f"modify_goal_{i}"
            )
            if new_monthly != goal['Monthly']:
                st.session_state.savings_goals[i]['Monthly'] = new_monthly
                st.session_state.savings_goals[i]['Months'] = goal['Target'] / new_monthly if new_monthly > 0 else 0
        with col4:
            months = goal['Target'] / goal['Monthly'] if goal['Monthly'] > 0 else 0
            years = months / 12
            if years >= 1:
                st.markdown(f"⏱️ {years:.1f} years ({months:.1f} months)")
            else:
                st.markdown(f"⏱️ {months:.1f} months")
        with col5:
            if st.button("🗑️", key=f"delete_goal_{i}"):
                st.session_state.savings_goals.pop(i)
                st.rerun()
    
    # Calculate total monthly savings allocation
    total_savings_allocation = sum(goal['Monthly'] for goal in st.session_state.savings_goals)
    remaining_surplus = surplus - total_savings_allocation
    
    st.markdown("---")
    st.markdown(f"**💰 Total Monthly Savings Allocation:** ${total_savings_allocation:,.2f}")
    st.markdown(f"**📈 Remaining Surplus After Savings:** ${remaining_surplus:,.2f}")
    
    if remaining_surplus < 0:
        st.warning(f"⚠️ Warning: Your savings goals exceed your surplus by ${abs(remaining_surplus):,.2f}")
else:
    st.info("No savings goals yet. Create one above to track your progress!")

# 📊 Visualizations
st.subheader("📊 Budget Visualizations")

# Calculate savings allocation
total_savings_allocation = 0
if "savings_goals" in st.session_state and st.session_state.savings_goals:
    total_savings_allocation = sum(goal['Monthly'] for goal in st.session_state.savings_goals)

remaining_after_savings = surplus - total_savings_allocation

col1, col2 = st.columns(2)

# Create fig1 - Budget Distribution
fig1 = go.Figure(data=[go.Pie(
    labels=['Total Income', 'Total Expenses', 'Savings Allocation', 'Remaining'],
    values=[total_income, total_expenses, total_savings_allocation, max(0, remaining_after_savings)],
    hole=.3,
    marker=dict(colors=['#43c0d1', '#a64957', '#7cb342', '#fdd835'])
)])
fig1.update_layout(title="Budget Distribution", showlegend=True)

with col1:
    st.markdown("##### Income vs Expenses vs Savings")
    st.plotly_chart(fig1, use_container_width=True)

# Create fig2 - Expense Breakdown
expense_categories = []
expense_amounts = []

if home > 0:
    expense_categories.append("House Payment")
    expense_amounts.append(home)
if home_insurance > 0:
    expense_categories.append("Home Insurance")
    expense_amounts.append(home_insurance)
if car_payment > 0:
    expense_categories.append("Car Payment")
    expense_amounts.append(car_payment)
if car_insurance > 0:
    expense_categories.append("Car Insurance")
    expense_amounts.append(car_insurance)
if phone_bill > 0:
    expense_categories.append("Phone Bill")
    expense_amounts.append(phone_bill)
if internet > 0:
    expense_categories.append("Internet")
    expense_amounts.append(internet)
if electricity > 0:
    expense_categories.append("Electricity")
    expense_amounts.append(electricity)
if water > 0:
    expense_categories.append("Water")
    expense_amounts.append(water)

for item in st.session_state.additional_expenses:
    expense_categories.append(item['Expense'])
    expense_amounts.append(item['Amount'])

fig2 = go.Figure(data=[go.Pie(
    labels=expense_categories,
    values=expense_amounts,
    marker=dict(colors=['#e57373', '#f06292', '#ba68c8', '#9575cd', '#7986cb', '#64b5f6', '#4fc3f7', '#4dd0e1', '#4db6ac'])
)])
fig2.update_layout(title="Where Your Money Goes", showlegend=True)

with col2:
    st.markdown("##### Expense Breakdown")
    st.plotly_chart(fig2, use_container_width=True)

# Create fig3 - Savings Goals Progress
fig3 = None
if "savings_goals" in st.session_state and st.session_state.savings_goals:
    st.markdown("##### Savings Goals Progress")
    fig3 = go.Figure()
    
    for goal in st.session_state.savings_goals:
        fig3.add_trace(go.Bar(
            name=goal['Goal'],
            x=[goal['Goal']],
            y=[goal['Monthly']],
            text=[f"${goal['Monthly']:,.2f}/mo<br>{goal['Months']:.1f} months to ${goal['Target']:,.2f}"],
            textposition='auto',
        ))
    
    fig3.update_layout(
        title="Monthly Savings Contributions",
        yaxis_title="Monthly Amount ($)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)

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
    {"Section": "Expenses", "Category": "Car Payment", "Amount": home},
    {"Section": "Expenses", "Category": "Home Insurance", "Amount": home_insurance},
    {"Section": "Expenses", "Category": "Car Payment", "Amount": car_payment},
    {"Section": "Expenses", "Category": "Car Insurance", "Amount": car_insurance},
    {"Section": "Expenses", "Category": "Phone Bill", "Amount": phone_bill},
    {"Section": "Expenses", "Category": "Internet Bill", "Amount": internet},
    {"Section": "Expenses", "Category": "Electricity Bill", "Amount": electricity},
    {"Section": "Expenses", "Category": "Water Bill", "Amount": water}
]
expense_rows += [
    {"Section": "Expenses", "Category": f"Additional Expense: {item['Expense']}", "Amount": item["Amount"]}
    for item in st.session_state.additional_expenses
]
expense_rows.append({"Section": "Expenses", "Category": "Total Expenses", "Amount": total_expenses})

summary_rows = [
    {"Section": "Summary", "Category": "Monthly Surplus", "Amount": surplus}
]

savings_rows = []
if "savings_goals" in st.session_state and st.session_state.savings_goals:
    for goal in st.session_state.savings_goals:
        savings_rows.append({
            "Section": "Savings Goals",
            "Category": f"{goal['Goal']} (Target: ${goal['Target']:,.2f}, Timeline: {goal['Months']:.1f} months)",
            "Amount": goal['Monthly']
        })
    total_savings_allocation = sum(goal['Monthly'] for goal in st.session_state.savings_goals)
    remaining_surplus = surplus - total_savings_allocation
    savings_rows.append({
        "Section": "Savings Goals",
        "Category": "Total Savings Allocation",
        "Amount": total_savings_allocation
    })
    savings_rows.append({
        "Section": "Savings Goals",
        "Category": "Remaining Surplus",
        "Amount": remaining_surplus
    })

# Combine all rows
export_rows = income_rows + expense_rows + summary_rows + savings_rows
export_df = pd.DataFrame(export_rows)

# Show a styled preview table
def highlight_section(row):
    color = {
        "Income": "#43c0d1",
        "Expenses": "#a64957",
        "Summary": "#a29936",
        "Savings Goals": "#7cb342"
    }.get(row.Section, "#ffffff")
    return [f"background-color: {color}"] * len(row)

st.markdown("##### Preview of Your Budget Spreadsheet")
st.dataframe(
    export_df.style.apply(highlight_section, axis=1).format({"Amount": "${:,.2f}"}),
    use_container_width=True
)

# Download as Excel with formatting and charts
def to_excel(df, chart_fig1, chart_fig2, chart_fig3=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Budget")
    charts_worksheet = workbook.add_worksheet("Visualizations")

    # Define formats
    formats = {
        "Income": workbook.add_format({'bg_color': '#e0f7fa', 'num_format': '$#,##0.00'}),
        "Expenses": workbook.add_format({'bg_color': '#ffebee', 'num_format': '$#,##0.00'}),
        "Savings": workbook.add_format({'bg_color': '#e8f5e9', 'num_format': '$#,##0.00'}),
        "Savings Goals": workbook.add_format({'bg_color': '#e8f5e9', 'num_format': '$#,##0.00'}),
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
    
    # Add charts to the visualizations sheet
    # Save plotly charts as images and insert them
    try:
        # Save fig1 (Budget Distribution)
        img1_bytes = chart_fig1.to_image(format="png", width=800, height=600)
        img1_stream = io.BytesIO(img1_bytes)
        charts_worksheet.insert_image('A2', 'budget_distribution.png', {'image_data': img1_stream})
        
        # Save fig2 (Expense Breakdown)
        img2_bytes = chart_fig2.to_image(format="png", width=800, height=600)
        img2_stream = io.BytesIO(img2_bytes)
        charts_worksheet.insert_image('A35', 'expense_breakdown.png', {'image_data': img2_stream})
        
        # Save fig3 (Savings Goals) if it exists
        if chart_fig3 is not None:
            img3_bytes = chart_fig3.to_image(format="png", width=800, height=600)
            img3_stream = io.BytesIO(img3_bytes)
            charts_worksheet.insert_image('A68', 'savings_goals.png', {'image_data': img3_stream})
    except Exception as e:
        # If image export fails, just skip it
        charts_worksheet.write('A2', 'Note: Chart visualization requires kaleido package. Install with: pip install kaleido')
        pass

    workbook.close()
    output.seek(0)
    return output

excel_data = to_excel(export_df, fig1, fig2, fig3)

st.download_button(
    label="Download Budget with Visualizations as Excel",
    data=excel_data,
    file_name="budget_summary_with_charts.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
