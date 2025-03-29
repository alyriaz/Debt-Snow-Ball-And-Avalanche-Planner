import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit Page Config
st.set_page_config(page_title="Debt Planner", page_icon="💰", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #000000; }
        h1, h2, h3, h4, h5, h6, p, label { color: #ffffff; }
        .stButton > button { width: 100%; background-color: #1f77b4; color: white; }
    </style>
    """, unsafe_allow_html=True)

def calculate_snowball(debts, extra_payment):
    debts = sorted(debts, key=lambda x: x['amount'])
    return calculate_repayment(debts, extra_payment)

def calculate_avalanche(debts, extra_payment):
    debts = sorted(debts, key=lambda x: x['interest'], reverse=True)
    return calculate_repayment(debts, extra_payment)

def calculate_repayment(debts, extra_payment):
    history = []
    total_months = 0
    while any(debt['amount'] > 0 for debt in debts):
        payment_log = {'Month': total_months + 1}
        for debt in debts:
            if debt['amount'] > 0:
                interest = (debt['interest'] / 100 / 12) * debt['amount']
                principal_payment = min(debt['amount'], debt['min_payment'] + extra_payment)
                debt['amount'] -= principal_payment
                extra_payment = max(0, extra_payment - (principal_payment - debt['min_payment']))
                payment_log[debt['name']] = principal_payment
        history.append(payment_log)
        total_months += 1
    return history

def main():
    st.title("💰 Debt Snowball & Avalanche Planner")
    
    st.sidebar.header("📌 Enter Debt Details")
    debt_list = []
    num_debts = st.sidebar.number_input("Number of debts", min_value=1, max_value=10, value=3, step=1)
    
    for i in range(num_debts):
        with st.sidebar.expander(f"⚡ Debt {i+1}"):
            name = st.text_input(f"Debt {i+1}", f"Debt {i+1}")
            amount = st.number_input(f"Amount Owed", min_value=0.0, value=1000.0, step=100.0, key=f"amount_{i}")
            interest = st.number_input(f"Interest Rate (%)", min_value=0.0, value=5.0, step=0.1, key=f"interest_{i}")
            min_payment = st.number_input(f"Minimum Payment", min_value=0.0, value=50.0, step=5.0, key=f"payment_{i}")
            debt_list.append({"name": name, "amount": amount, "interest": interest, "min_payment": min_payment})
    
    extra_payment = st.sidebar.number_input("💸 Extra Monthly Payment", min_value=0.0, value=100.0, step=10.0)
    method = st.sidebar.radio("📊 Choose a repayment method", ["Snowball", "Avalanche"], horizontal=True)
    
    if st.sidebar.button("🚀 Calculate Plan"):
        repayment_history = calculate_snowball(debt_list, extra_payment) if method == "Snowball" else calculate_avalanche(debt_list, extra_payment)
        df = pd.DataFrame(repayment_history).fillna(0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📝 Debt Repayment Schedule")
            st.dataframe(df.style.background_gradient(cmap="coolwarm"))
        
        with col2:
            st.write("### 📈 Debt Reduction Over Time")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.set_theme(style="darkgrid")
            for debt in debt_list:
                if debt['name'] in df.columns:
                    ax.plot(df['Month'], np.cumsum(df[debt['name']]), label=debt['name'], linewidth=2)
            ax.legend()
            ax.set_xlabel("Months")
            ax.set_ylabel("Cumulative Payment")
            ax.set_title("Debt Repayment Progress", color='Black')
            ax.grid(True, linestyle="--", alpha=0.7)
            ax.xaxis.label.set_color('Black')
            ax.yaxis.label.set_color('Black')
            ax.title.set_color('Black')
            ax.tick_params(axis='both', colors='Black')
            st.pyplot(fig)
        
        # Bar Chart of Total Payments
        total_payments = {debt['name']: df[debt['name']].sum() for debt in debt_list}
        st.write("### 📊 Total Payments Per Debt")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=list(total_payments.keys()), y=list(total_payments.values()), ax=ax, palette="mako")
        ax.set_ylabel("Total Amount Paid", color='white')
        ax.set_xlabel("Debt Name", color='white')
        ax.set_title("Total Amount Paid per Debt", color='white')
        for i, value in enumerate(total_payments.values()):
            ax.text(i, value + 100, f"${value:.2f}", ha='center', fontsize=10, fontweight='bold', color='white')
        ax.tick_params(axis='x', colors='Black')
        ax.tick_params(axis='y', colors='Black')
        st.pyplot(fig)
        
        # Pie Chart of Debt Distribution
        st.write("### 🍕 Debt Payment Breakdown")
        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(total_payments.values(), labels=total_payments.keys(), autopct='%1.1f%%', 
               colors=sns.color_palette("mako", len(total_payments)), wedgeprops={'edgecolor': 'black'})
        for text in texts:
            text.set_color('Black')
        for autotext in autotexts:
            autotext.set_color('Black')
        ax.set_title("Debt Payment Proportions", color='white')
        st.pyplot(fig)

if __name__ == "__main__":
    main()

