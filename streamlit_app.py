import streamlit as st
import pandas as pd
import io
import xlsxwriter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image

st.set_page_config(page_title="Budget Tool", layout="centered")

# Custom theme with Michigan colors
st.markdown("""
    <style>
    .stApp {
        background: #F7F7F7;
    }
    .main .block-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.12);
        border-top: 6px solid #FFCB05;
    }
    h1 {
        color: #00274C !important;
    }
    h2, h3, h4, h5, h6 {
        color: #FFCB05 !important;
        text-shadow: 0 1px 0 rgba(0, 0, 0, 0.2);
    }
    .stMarkdown h1 {
        color: #00274C !important;
    }
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #FFCB05 !important;
        text-shadow: 0 1px 0 rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h1 {
        color: #00274C !important;
    }
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4,
    div[data-testid="stMarkdownContainer"] h5,
    div[data-testid="stMarkdownContainer"] h6 {
        color: #FFCB05 !important;
        text-shadow: 0 1px 0 rgba(0, 0, 0, 0.2);
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
        background-color: #FFCB05 !important;
        color: #00274C !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
    }
    .stButton button:hover {
        background-color: #F5C400 !important;
    }
    .stDownloadButton button {
        background-color: #00274C !important;
        color: #FFCB05 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
    }
    .stDownloadButton button span,
    .stDownloadButton button p {
        color: #FFCB05 !important;
    }
    .stDownloadButton button:hover {
        background-color: #0A3A6B !important;
    }
    div[data-testid="stMetric"] {
        border-left: 4px solid #FFCB05;
        padding-left: 0.75rem;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] span {
        color: #00274C !important;
        background: transparent !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #00274C !important;
    }
    .tax-equation {
        color: #00274C;
        font-family: inherit;
        font-weight: 600;
    }
    .tax-equation span {
        color: #00274C;
        font-family: inherit;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# 🚀 Header
header_col1, header_col2 = st.columns([1, 6])
with header_col1:
    st.image(
        "https://cdn.worldvectorlogo.com/logos/university-of-michigan-3.svg",
        width=72
    )
with header_col2:
    st.markdown("<h1>Budgetary Tool</h1>", unsafe_allow_html=True)
    st.caption("Track your budget, launch your goals, and orbit financial freedom.")

tab_income, tab_expenses, tab_savings, tab_report = st.tabs(
    ["Income", "Expenses", "Savings Goals", "Visuals & Export"]
)

with tab_income:
    st.subheader("💰 Monthly Income")

    gross_income = st.number_input("Main job (gross)", value=5417.00, format="%.2f")

    st.markdown("#### 🧾 Payroll Withholdings & Contributions")
    state_withholding_percent = st.number_input(
        "State withholding / tax rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=4.05,
        format="%.2f"
    )
    federal_withholding_percent = st.number_input(
        "Federal withholding (%)",
        min_value=0.0,
        max_value=40.0,
        value=12.0,
        format="%.2f"
    )
    fsa_monthly = st.number_input("FSA monthly contribution", min_value=0.0, format="%.2f")
    retirement_percent = st.number_input(
        "Retirement contribution (%)",
        min_value=0.0,
        max_value=100.0,
        format="%.2f"
    )

    retirement_monthly = gross_income * (retirement_percent / 100.0)

    state_withholding_rate = state_withholding_percent / 100.0
    federal_withholding_rate = federal_withholding_percent / 100.0
    taxable_income = max(0.0, gross_income - fsa_monthly - retirement_monthly)
    state_withholding = taxable_income * state_withholding_rate
    federal_withholding = taxable_income * federal_withholding_rate

    ss_wage_base_annual = 168600.0
    ss_wage_base_monthly = ss_wage_base_annual / 12.0
    fica_taxable_income = max(0.0, gross_income - fsa_monthly)
    social_security_tax = min(fica_taxable_income, ss_wage_base_monthly) * 0.062
    medicare_tax = fica_taxable_income * 0.0145

    total_payroll_taxes = (
        social_security_tax + medicare_tax + state_withholding + federal_withholding
    )
    total_payroll_deductions = total_payroll_taxes + fsa_monthly + retirement_monthly
    net_main_income = gross_income - total_payroll_deductions

    st.markdown(
        "**Estimated payroll withholdings (simplified):** "
        f"${total_payroll_taxes:,.2f}"
    )
    st.markdown(f"State withholding: ${state_withholding:,.2f}")
    st.markdown(f"Federal withholding: ${federal_withholding:,.2f}")
    st.markdown(f"Social Security: ${social_security_tax:,.2f}")
    st.markdown(f"Medicare: ${medicare_tax:,.2f}")
    st.markdown(
        "**Estimated net from main job:** "
        f"${net_main_income:,.2f}"
    )
    st.caption(
        "Estimates use flat withholding rates and standard FICA. "
        "FSA and retirement reduce the taxable base used for withholding."
    )

    va_income = st.number_input("VA Benefits", value=4158.17, format="%.2f")

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

with tab_expenses:
    st.subheader("💰 Monthly Expenses")
    home = st.number_input("House Payment", value=1469.61, format="%.2f")
    car_payment = st.number_input("Car Payment", value=472.84, format="%.2f")
    car_insurance = st.number_input("Car Insurance", value=120.00, format="%.2f")
    phone_bill = st.number_input("Phone Bill", value=140.00, format="%.2f")
    internet = st.number_input("Internet Bill", value=50.00, format="%.2f")
    electricity = st.number_input("Electricity Bill", value=180.00, format="%.2f")
    water = st.number_input("Water Bill", value=50.00, format="%.2f")
    spotify = st.number_input("Spotify Subscription", value=18.18, format="%.2f")
    adobe = st.number_input("Adobe Subscription", value=21.39, format="%.2f")
    digital_ocean = st.number_input("Digital Ocean Subscription", value=8.00, format="%.2f")
    health = st.number_input("Health Insurance", value=100.00, format="%.2f")
    dental = st.number_input("Dental Insurance", value=49.81, format="%.2f")
    vision = st.number_input("Vision Insurance", value=15.43, format="%.2f")

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

total_income = gross_income + va_income + total_additional_income
total_expenses = (
    home
    + car_payment
    + car_insurance
    + phone_bill
    + internet
    + electricity
    + water
    + spotify
    + adobe
    + digital_ocean
    + health
    + dental
    + vision
    + total_payroll_taxes
    + fsa_monthly
    + retirement_monthly
    + total_additional_expenses
)
surplus = total_income - total_expenses

with tab_income:
    st.markdown("#### Summary")
    st.metric("Total Income", f"${total_income:,.2f}")
    st.metric("Net Main Job Income", f"${net_main_income:,.2f}")

with tab_expenses:
    st.markdown("#### Summary")
    st.metric("Total Expenses", f"${total_expenses:,.2f}")

with tab_savings:
    st.subheader("🎯 Savings Goals")
    st.markdown("#### ➕ Create Savings Goals")

    total_savings_allocation = 0
    remaining_surplus = surplus

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

        for i, goal in enumerate(st.session_state.savings_goals):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
            with col1:
                st.markdown(f"**{goal['Goal']}**")
            with col2:
                st.markdown(f"Target: ${goal['Target']:,.2f}")
            with col3:
                new_monthly = st.number_input(
                    "Monthly",
                    min_value=0.0,
                    value=float(goal['Monthly']),
                    format="%.2f",
                    key=f"modify_goal_{i}"
                )
                if new_monthly != goal['Monthly']:
                    st.session_state.savings_goals[i]['Monthly'] = new_monthly
                    st.session_state.savings_goals[i]['Months'] = (
                        goal['Target'] / new_monthly if new_monthly > 0 else 0
                    )
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

        total_savings_allocation = sum(goal['Monthly'] for goal in st.session_state.savings_goals)
        remaining_surplus = surplus - total_savings_allocation

    st.markdown("#### Summary")
    st.metric("Total Monthly Savings", f"${total_savings_allocation:,.2f}")
    st.metric("Remaining Surplus", f"${remaining_surplus:,.2f}")

with tab_report:
    st.markdown(f"**💵 Total Income:** ${total_income:,.2f}")
    st.markdown(f"**🧾 Total Expenses:** ${total_expenses:,.2f}")
    st.markdown(f"**📈 Monthly Surplus:** ${surplus:,.2f}")

    st.subheader("🧾 Estimated Tax Return")

    filing_status = st.selectbox(
        "Filing status",
        ["Single", "Married filing jointly", "Married filing separately"],
        index=1
    )

    def compute_federal_tax_2024(taxable_income, brackets):
        remaining = taxable_income
        lower_limit = 0.0
        tax = 0.0
        for upper_limit, rate in brackets:
            if remaining <= 0:
                break
            taxable_at_rate = min(remaining, upper_limit - lower_limit)
            tax += taxable_at_rate * rate
            remaining -= taxable_at_rate
            lower_limit = upper_limit
        return tax

    federal_brackets_by_status = {
        "Single": [
            (11600, 0.10),
            (47150, 0.12),
            (100525, 0.22),
            (191950, 0.24),
            (243725, 0.32),
            (609350, 0.35),
            (float("inf"), 0.37)
        ],
        "Married filing jointly": [
            (23200, 0.10),
            (94300, 0.12),
            (201050, 0.22),
            (383900, 0.24),
            (487450, 0.32),
            (731200, 0.35),
            (float("inf"), 0.37)
        ],
        "Married filing separately": [
            (11600, 0.10),
            (47150, 0.12),
            (100525, 0.22),
            (191950, 0.24),
            (243725, 0.32),
            (365600, 0.35),
            (float("inf"), 0.37)
        ]
    }
    standard_deduction_by_status = {
        "Single": 14600.0,
        "Married filing jointly": 29200.0,
        "Married filing separately": 14600.0
    }

    standard_deduction = standard_deduction_by_status[filing_status]
    annual_taxable_base = taxable_income * 12.0
    annual_taxable_income = max(0.0, annual_taxable_base - standard_deduction)
    annual_federal_tax = compute_federal_tax_2024(
        annual_taxable_income,
        federal_brackets_by_status[filing_status]
    )
    annual_state_tax = taxable_income * 12.0 * state_withholding_rate

    annual_federal_withholding = federal_withholding * 12.0
    annual_state_withholding = state_withholding * 12.0

    annual_total_withholding = annual_federal_withholding + annual_state_withholding
    annual_total_tax = annual_federal_tax + annual_state_tax
    estimated_refund = annual_total_withholding - annual_total_tax
    error_percent = 10.0
    error_percent_amount = abs(estimated_refund) * (error_percent / 100.0)
    refund_low_pct = estimated_refund - error_percent_amount
    refund_high_pct = estimated_refund + error_percent_amount
    refund_label = "Estimated refund" if estimated_refund >= 0 else "Estimated amount owed"
    refund_display = f"${abs(estimated_refund):,.2f}"
    refund_explainer = (
        "Positive means refund; negative means amount owed."
    )

    st.markdown("**How this estimate is calculated:**")
    st.markdown(
        f"<div class='tax-equation'>Taxable income = annual taxable base - standard deduction = "
        f"${annual_taxable_base:,.2f} - ${standard_deduction:,.2f} = ${annual_taxable_income:,.2f}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "Federal tax liability is estimated from this taxable income using 2024 brackets."
    )

    st.markdown(f"Federal tax liability (est.): ${annual_federal_tax:,.2f}")
    st.markdown(f"State tax liability (est.): ${annual_state_tax:,.2f}")
    st.markdown(
        "State liability uses the flat state rate applied to the annual taxable base."
    )
    st.markdown(
        "<div class='tax-equation'>Total tax liability = federal tax + state tax</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='tax-equation'>${annual_federal_tax:,.2f} + "
        f"${annual_state_tax:,.2f} = ${annual_total_tax:,.2f}</div>",
        unsafe_allow_html=True
    )

    st.markdown("")
    st.markdown(
        "<div class='tax-equation'>Total withholdings = federal withholding + state withholding</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='tax-equation'>${annual_federal_withholding:,.2f} + "
        f"${annual_state_withholding:,.2f} = ${annual_total_withholding:,.2f}</div>",
        unsafe_allow_html=True
    )

    st.markdown("")
    st.markdown(
        "<div class='tax-equation'>Refund/owed = total withholdings - total tax liability</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='tax-equation'>${annual_total_withholding:,.2f} - "
        f"${annual_total_tax:,.2f} = ${estimated_refund:,.2f}</div>",
        unsafe_allow_html=True
    )

    st.markdown("")

    st.metric(refund_label, refund_display)
    st.markdown(
        f"<div class='tax-equation'>±{error_percent:.0f}%: "
        f"${refund_low_pct:,.2f} to ${refund_high_pct:,.2f}</div>",
        unsafe_allow_html=True
    )
    st.caption(refund_explainer)
    st.caption(
        "Federal tax uses 2024 brackets with the standard deduction. "
        "State tax uses the same rate as state withholding. Withholdings use your flat % inputs."
    )



    total_savings_allocation = 0
    if "savings_goals" in st.session_state and st.session_state.savings_goals:
        total_savings_allocation = sum(goal['Monthly'] for goal in st.session_state.savings_goals)

    remaining_after_savings = surplus - total_savings_allocation

    col1, col2 = st.columns(2)
    fig1, ax1 = plt.subplots(figsize=(9, 7))
    colors1 = ['#0078D4', '#a64957', '#7cb342', '#fdd835']
    labels1 = ['Total Income', 'Total Expenses', 'Savings Allocation', 'Remaining']
    values1 = [total_income, total_expenses, total_savings_allocation, max(0, remaining_after_savings)]
    explode1 = (0.05, 0.05, 0.05, 0.05)
    wedges, texts, autotexts = ax1.pie(
        values1,
        labels=labels1,
        colors=colors1,
        autopct=lambda pct: f'${pct * sum(values1) / 100:,.0f}\n({pct:.1f}%)',
        startangle=90,
        explode=explode1,
        shadow=True,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    ax1.set_title("Budget Distribution", fontsize=16, fontweight='bold', pad=20)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    with col1:
        st.markdown("##### Income vs Expenses vs Savings")
        st.pyplot(fig1)

    expense_categories = []
    expense_amounts = []

    if home > 0:
        expense_categories.append("House Payment")
        expense_amounts.append(home)
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
    if spotify > 0:
        expense_categories.append("Spotify Subscription")
        expense_amounts.append(spotify)
    if adobe > 0:
        expense_categories.append("Adobe Subscription")
        expense_amounts.append(adobe)
    if digital_ocean > 0:
        expense_categories.append("Digital Ocean Subscription")
        expense_amounts.append(digital_ocean)
    if health > 0:
        expense_categories.append("Health Insurance")
        expense_amounts.append(health)
    if dental > 0:
        expense_categories.append("Dental Insurance")
        expense_amounts.append(dental)
    if vision > 0:
        expense_categories.append("Vision Insurance")
        expense_amounts.append(vision)
    if total_payroll_taxes > 0:
        expense_categories.append("Payroll Withholdings (Est.)")
        expense_amounts.append(total_payroll_taxes)
    if fsa_monthly > 0:
        expense_categories.append("FSA Contribution")
        expense_amounts.append(fsa_monthly)
    if retirement_monthly > 0:
        expense_categories.append("Retirement Contribution")
        expense_amounts.append(retirement_monthly)

    for item in st.session_state.additional_expenses:
        expense_categories.append(item['Expense'])
        expense_amounts.append(item['Amount'])

    expense_data = list(zip(expense_categories, expense_amounts))
    expense_data.sort(key=lambda x: x[1], reverse=True)

    if len(expense_data) > 5:
        top_5 = expense_data[:5]
        other_amount = sum(amt for _, amt in expense_data[5:])
        final_categories = [cat for cat, _ in top_5] + ['Other Expenses']
        final_amounts = [amt for _, amt in top_5] + [other_amount]
    else:
        final_categories = [cat for cat, _ in expense_data]
        final_amounts = [amt for _, amt in expense_data]

    fig2, ax2 = plt.subplots(figsize=(9, 7))
    colors2 = ['#0078D4', '#50E6FF', '#7cb342', '#fdd835', '#f06292', '#b0b0b0']
    explode2 = [0.05] * len(final_amounts)

    wedges2, texts2, autotexts2 = ax2.pie(
        final_amounts,
        labels=final_categories,
        colors=colors2[:len(final_categories)],
        autopct=lambda pct: f'${pct * sum(final_amounts) / 100:,.0f}\n({pct:.1f}%)',
        startangle=90,
        explode=explode2,
        shadow=True,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    ax2.set_title("Where Your Money Goes (Top 5)", fontsize=16, fontweight='bold', pad=20)

    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    with col2:
        st.markdown("##### Expense Breakdown")
        st.pyplot(fig2)

    fig3 = None
    if "savings_goals" in st.session_state and st.session_state.savings_goals:
        st.markdown("##### Savings Goals Progress")
        fig3, ax3 = plt.subplots(figsize=(10, 6))

        goal_names = [goal['Goal'] for goal in st.session_state.savings_goals]
        goal_amounts = [goal['Monthly'] for goal in st.session_state.savings_goals]

        colors3 = ['#0078D4', '#50E6FF', '#7cb342', '#fdd835', '#f06292']
        bars = ax3.bar(goal_names, goal_amounts, color=colors3[:len(goal_names)], edgecolor='black', linewidth=1.5)
        ax3.set_ylabel('Monthly Amount ($)', fontsize=13, fontweight='bold')
        ax3.set_title('Monthly Savings Contributions', fontsize=16, fontweight='bold', pad=20)
        ax3.tick_params(axis='x', rotation=45, labelsize=10)
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        ax3.set_axisbelow(True)

        for bar, goal in zip(bars, st.session_state.savings_goals):
            height = bar.get_height()
            ax3.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f'${height:,.2f}/mo\n{goal["Months"]:.1f} months',
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )

        plt.tight_layout()
        st.pyplot(fig3)

    st.subheader("⬇️ Download Your Budget Spreadsheet")

    income_rows = [
        {"Section": "Income", "Category": "Main Job (Gross)", "Amount": gross_income},
        {"Section": "Income", "Category": "VA Benefits", "Amount": va_income}
    ]
    income_rows += [
        {"Section": "Income", "Category": f"Additional Income: {item['Source']}", "Amount": item["Amount"]}
        for item in st.session_state.additional_income
    ]
    income_rows.append({"Section": "Income", "Category": "Total Income", "Amount": total_income})

    expense_rows = [
        {"Section": "Expenses", "Category": "House Payment", "Amount": home},
        {"Section": "Expenses", "Category": "Car Payment", "Amount": car_payment},
        {"Section": "Expenses", "Category": "Car Insurance", "Amount": car_insurance},
        {"Section": "Expenses", "Category": "Phone Bill", "Amount": phone_bill},
        {"Section": "Expenses", "Category": "Internet Bill", "Amount": internet},
        {"Section": "Expenses", "Category": "Electricity Bill", "Amount": electricity},
        {"Section": "Expenses", "Category": "Water Bill", "Amount": water},
        {"Section": "Expenses", "Category": "Spotify Subscription", "Amount": spotify},
        {"Section": "Expenses", "Category": "Adobe Subscription", "Amount": adobe},
        {"Section": "Expenses", "Category": "Digital Ocean Subscription", "Amount": digital_ocean},
        {"Section": "Expenses", "Category": "Health Insurance", "Amount": health},
        {"Section": "Expenses", "Category": "Dental Insurance", "Amount": dental},
        {"Section": "Expenses", "Category": "Vision Insurance", "Amount": vision},
        {"Section": "Expenses", "Category": "Payroll Withholdings (Est.)", "Amount": total_payroll_taxes},
        {"Section": "Expenses", "Category": "FSA Contribution", "Amount": fsa_monthly},
        {"Section": "Expenses", "Category": "Retirement Contribution", "Amount": retirement_monthly}
    ]
    expense_rows += [
        {"Section": "Expenses", "Category": f"Additional Expense: {item['Expense']}", "Amount": item["Amount"]}
        for item in st.session_state.additional_expenses
    ]
    expense_rows.append({"Section": "Expenses", "Category": "Total Expenses", "Amount": total_expenses})

    summary_rows = [
        {"Section": "Summary", "Category": "Net Main Job Income", "Amount": net_main_income},
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

    export_rows = income_rows + expense_rows + summary_rows + savings_rows
    export_df = pd.DataFrame(export_rows)

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

    def to_excel(df, chart_fig1, chart_fig2, chart_fig3=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Budget")
        charts_worksheet = workbook.add_worksheet("Visualizations")
        tax_worksheet = workbook.add_worksheet("Estimated Tax Return")

        formats = {
            "Income": workbook.add_format({'bg_color': '#e0f7fa', 'num_format': '$#,##0.00'}),
            "Expenses": workbook.add_format({'bg_color': '#ffebee', 'num_format': '$#,##0.00'}),
            "Savings": workbook.add_format({'bg_color': '#e8f5e9', 'num_format': '$#,##0.00'}),
            "Savings Goals": workbook.add_format({'bg_color': '#e8f5e9', 'num_format': '$#,##0.00'}),
            "Summary": workbook.add_format({'bg_color': '#fffde7', 'num_format': '$#,##0.00'}),
            "Header": workbook.add_format({'bold': True, 'bg_color': '#bdbdbd', 'border': 1}),
            "Default": workbook.add_format({'num_format': '$#,##0.00'})
        }
        tax_formats = {
            "Base": workbook.add_format({'bg_color': '#e3f2fd', 'num_format': '$#,##0.00'}),
            "Deduction": workbook.add_format({'bg_color': '#fff8e1', 'num_format': '$#,##0.00'}),
            "Taxable": workbook.add_format({'bg_color': '#e8f5e9', 'num_format': '$#,##0.00'}),
            "Liability": workbook.add_format({'bg_color': '#ffebee', 'num_format': '$#,##0.00'}),
            "Withholding": workbook.add_format({'bg_color': '#e8f5e9', 'num_format': '$#,##0.00'}),
            "RefundPositive": workbook.add_format({'font_color': '#1b5e20', 'num_format': '$#,##0.00'}),
            "RefundNegative": workbook.add_format({'font_color': '#b71c1c', 'num_format': '$#,##0.00'}),
            "Note": workbook.add_format({'font_color': '#5f6368'})
        }

        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, formats["Header"])

        for row_num, row in enumerate(df.itertuples(index=False), 1):
            section = getattr(row, "Section")
            fmt = formats.get(section, formats["Default"])
            worksheet.write(row_num, 0, row.Section)
            worksheet.write(row_num, 1, row.Category)
            worksheet.write_number(row_num, 2, row.Amount, fmt)

        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 35)
        worksheet.set_column(2, 2, 18)

        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'color': '#0078D4'})
        charts_worksheet.write('A1', 'Budget Visualizations', title_format)

        tax_worksheet.write('A1', 'Estimated Tax Return (Annual)', title_format)
        tax_worksheet.write('A3', 'Filing Status', formats["Header"])
        tax_worksheet.write('B3', filing_status)

        tax_worksheet.write('A4', 'Notes', formats["Header"])
        tax_worksheet.write(
            'B4',
            '2024 brackets + standard deduction; flat withholding rates',
            tax_formats["Note"]
        )
        tax_worksheet.write('A5', 'Tax Liability', formats["Header"])
        tax_worksheet.write(
            'B5',
            'Federal tax liability + state tax liability',
            tax_formats["Note"]
        )
        tax_worksheet.write('A6', 'Refund Formula', formats["Header"])
        tax_worksheet.write(
            'B6',
            'Total withholdings - total tax liability',
            tax_formats["Note"]
        )
        tax_worksheet.write('A7', 'Error Range', formats["Header"])
        tax_worksheet.write(
            'B7',
            'Shown as +/-10% of estimated refund/owed',
            tax_formats["Note"]
        )

        tax_rows = [
            ("Annual Taxable Base (gross - FSA - retirement)", annual_taxable_base, "Base"),
            ("Standard Deduction (2024)", standard_deduction, "Deduction"),
            ("Annual Taxable Income", annual_taxable_income, "Taxable"),
            ("Federal Tax Liability (Est.)", annual_federal_tax, "Liability"),
            ("State Tax Liability (Est.)", annual_state_tax, "Liability"),
            ("Federal Withholding (Annual)", annual_federal_withholding, "Withholding"),
            ("State Withholding (Annual)", annual_state_withholding, "Withholding"),
            ("Total Withholding (Annual)", annual_total_withholding, "Withholding"),
            ("Estimated Refund / Amount Owed", estimated_refund, "Refund"),
            ("Refund Range (±10%) Low", refund_low_pct, "RefundRange"),
            ("Refund Range (±10%) High", refund_high_pct, "RefundRange")
        ]

        tax_worksheet.write('A9', 'Category', formats["Header"])
        tax_worksheet.write('B9', 'Amount', formats["Header"])
        for idx, (label, amount, category) in enumerate(tax_rows, start=10):
            tax_worksheet.write(f'A{idx}', label)
            if category in ("Refund", "RefundRange"):
                refund_format = (
                    tax_formats["RefundPositive"]
                    if amount >= 0
                    else tax_formats["RefundNegative"]
                )
                tax_worksheet.write_number(f'B{idx}', amount, refund_format)
            else:
                tax_worksheet.write_number(
                    f'B{idx}',
                    amount,
                    tax_formats.get(category, formats["Default"])
                )

        tax_worksheet.set_column(0, 0, 40)
        tax_worksheet.set_column(1, 1, 20)

        try:
            img1_buffer = io.BytesIO()
            chart_fig1.savefig(img1_buffer, format='png', dpi=100, bbox_inches='tight')
            img1_buffer.seek(0)
            charts_worksheet.insert_image('A3', 'budget_distribution.png', {'image_data': img1_buffer})

            img2_buffer = io.BytesIO()
            chart_fig2.savefig(img2_buffer, format='png', dpi=100, bbox_inches='tight')
            img2_buffer.seek(0)
            charts_worksheet.insert_image('A38', 'expense_breakdown.png', {'image_data': img2_buffer})

            if chart_fig3 is not None:
                img3_buffer = io.BytesIO()
                chart_fig3.savefig(img3_buffer, format='png', dpi=100, bbox_inches='tight')
                img3_buffer.seek(0)
                charts_worksheet.insert_image('A73', 'savings_goals.png', {'image_data': img3_buffer})
        except Exception as e:
            charts_worksheet.write('A3', f'Chart export error: {str(e)}')
            charts_worksheet.write('A4', 'Charts are available in the web app view.')

        charts_worksheet.set_column(0, 0, 100)

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