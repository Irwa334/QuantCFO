import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

# Page Config
st.set_page_config(page_title="QuantCFO | Financial Intelligence Suite", layout="wide", page_icon="🪙")

# Helper function to sanitize text for Streamlit Markdown (prevents dollar signs from triggering LaTeX)
def sanitize_markdown(text: str) -> str:
    return text.replace("$", "\\$")

# Initialize Chat History in Session State
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

st.title("🪙 QuantCFO — AI-Powered Financial Intelligence Dashboard")

# --- SIDEBAR: Controls & Settings ---
with st.sidebar:
    st.header("⚙️ Data & Settings")
    
    uploaded_files = st.file_uploader(
        "Upload Financial CSVs (Single or Multiple)", 
        type=["csv"], 
        accept_multiple_files=True
    )
    
    selected_view = "Combined (All Files)"
    if uploaded_files:
        file_names = [file.name for file in uploaded_files]
        selected_view = st.selectbox(
            "📂 Select Dataset to View:", 
            ["Combined (All Files)"] + file_names
        )
    
    st.markdown("---")
    
    # Global Keyword Search Filter
    search_keyword = st.text_input("🔍 Search Transactions:", placeholder="e.g., software, hotel, ad")
    
    st.markdown("---")
    
    # Currency Symbol Selection
    currency_options = ["Rs", "PKR", "$", "€", "£", "₹", "¥"]
    currency_symbol = st.selectbox("💵 Currency Symbol", currency_options, index=0)
    
    st.markdown("---")
    
    # Chart Color Palette Selection
    palette_choice = st.selectbox("🎨 Chart Color Palette", ["Vibrant", "Cool Tech", "Pastel"])
    
    st.markdown("---")
    st.caption("QuantCFO v2.0 | Portfolio Edition")

# Map Palette Choices
if palette_choice == "Vibrant":
    color_sequence = px.colors.qualitative.Vivid
elif palette_choice == "Cool Tech":
    color_sequence = px.colors.qualitative.Safe
else:
    color_sequence = px.colors.qualitative.Pastel

plotly_template = "plotly_dark"

# --- MAIN APP LOGIC ---
if uploaded_files:
    df_list = []
    for file in uploaded_files:
        if selected_view != "Combined (All Files)" and file.name != selected_view:
            continue
            
        file.seek(0)
        try:
            temp_df = pd.read_csv(file)
        except pd.errors.ParserError:
            # Handle files with preambles (like bank statements)
            file.seek(0)
            lines = file.readlines()
            start_row = 0
            for i, line in enumerate(lines):
                decoded_line = line.decode('utf-8', errors='ignore').lower() if isinstance(line, bytes) else line.lower()
                if any(kw in decoded_line for kw in ['date', 'timestamp', 'description', 'amount']):
                    start_row = i
                    break
            file.seek(0)
            temp_df = pd.read_csv(file, skiprows=start_row)
            
        # --- SMART SCHEMA ADAPTER ---
        rename_dict = {}
        for col in temp_df.columns:
            c_lower = col.lower().strip()
            if c_lower in ['amount', 'cost', 'price', 'value', 'total', 'sum', 'charge']:
                rename_dict[col] = 'Amount'
            elif c_lower in ['category', 'type', 'group', 'class', 'department', 'tag']:
                rename_dict[col] = 'Category'
            elif c_lower in ['description', 'desc', 'name', 'item', 'title', 'memo', 'details']:
                rename_dict[col] = 'Description'
        temp_df = temp_df.rename(columns=rename_dict)

        if 'Amount' not in temp_df.columns:
            numeric_cols = temp_df.select_dtypes(include='number').columns
            temp_df['Amount'] = temp_df[numeric_cols[0]] if len(numeric_cols) > 0 else 0.0

        if 'Category' not in temp_df.columns:
            string_cols = temp_df.select_dtypes(include='object').columns
            temp_df['Category'] = temp_df[string_cols[0]] if len(string_cols) > 0 else 'Uncategorized'

        if 'Description' not in temp_df.columns:
            temp_df['Description'] = 'General Transaction'

        df_list.append(temp_df)

    df = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
    if not df.empty:
        # Handle commas, plus signs, and accounting format parentheses (e.g. "(1,500)" -> "-1500")
        df['Amount'] = df['Amount'].astype(str).str.strip()
        df['Amount'] = df['Amount'].str.replace(',', '', regex=False).str.replace('+', '', regex=False)
        df['Amount'] = df['Amount'].str.replace(r'^\((.*)\)$', r'-\1', regex=True)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        # Prevent errors from blank rows in categorical columns
        if 'Category' in df.columns:
            df['Category'] = df['Category'].fillna('Uncategorized').astype(str)
        if 'Description' in df.columns:
            df['Description'] = df['Description'].fillna('No Description').astype(str)
    else:
        df['Amount'] = pd.Series(dtype=float)

    categories = df['Category'].unique().tolist()
    selected_categories = st.sidebar.multiselect("Filter Categories:", options=categories, default=categories)
    
    filtered_df = df[df['Category'].isin(selected_categories)]

    # Apply Global Keyword Search Filter if provided
    if search_keyword:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)
        filtered_df = filtered_df[mask]

    # --- PANDAS PRE-CALCULATIONS FOR AI ACCURACY ---
    total_revenue = filtered_df[filtered_df['Amount'] > 0]['Amount'].sum()
    total_expenses = abs(filtered_df[filtered_df['Amount'] < 0]['Amount'].sum())
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # PRE-FORMATTING AI CONTEXT (Forces the AI to see clean dollar amounts instead of raw negative numbers)
    ai_totals_df = filtered_df.groupby('Category', as_index=False)['Amount'].sum()
    ai_totals_df['Type'] = ai_totals_df['Amount'].apply(lambda x: 'Income' if x >= 0 else 'Expense')
    ai_totals_df['Formatted Amount'] = ai_totals_df['Amount'].abs().apply(lambda x: f"{currency_symbol} {x:,.2f}")
    category_totals_str = ai_totals_df[['Category', 'Type', 'Formatted Amount']].to_string(index=False)
    
    ai_raw_df = filtered_df.copy()
    ai_raw_df['Type'] = ai_raw_df['Amount'].apply(lambda x: 'Income' if x >= 0 else 'Expense')
    ai_raw_df['Formatted Amount'] = ai_raw_df['Amount'].abs().apply(lambda x: f"{currency_symbol} {x:,.2f}")
    
    # Only pass relevant columns to the AI to prevent confusion
    columns_for_ai = [col for col in ai_raw_df.columns if col not in ['Amount']]
    context_data = ai_raw_df[columns_for_ai].to_string(index=False)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Executive Overview", 
        "📈 Visual Analytics", 
        "🤖 AI Financial Advisor & Chat", 
        "📋 Ledger & Export"
    ])

    # ---------------- TAB 1: OVERVIEW ----------------
    with tab1:
        st.subheader(f"Key Performance Indicators — Viewing: {selected_view}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", f"{currency_symbol} {total_revenue:,.2f}")
        c2.metric("Total Expenses", f"{currency_symbol} {total_expenses:,.2f}")
        c3.metric("Net Cash Flow", f"{currency_symbol} {net_profit:,.2f}")
        c4.metric("Profit Margin", f"{profit_margin:.1f}%")

        st.markdown("---")
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.write("### Expense Breakdown by Category")
            exp_df = filtered_df[filtered_df['Amount'] < 0].copy()
            if not exp_df.empty:
                exp_df['Amount'] = exp_df['Amount'].abs()
                fig_pie = px.pie(exp_df, values='Amount', names='Category', hole=0.4, 
                                 template=plotly_template, color_discrete_sequence=color_sequence)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No negative expense rows detected in this view.")

        with col_right:
            st.write("### Revenue vs Expense Comparison")
            summary_df = pd.DataFrame({
                'Type': ['Revenue', 'Expenses'],
                'Amount': [total_revenue, total_expenses]
            })
            fig_bar = px.bar(summary_df, x='Type', y='Amount', color='Type', template=plotly_template,
                             color_discrete_sequence=color_sequence)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- TAB 2: ANALYTICS ----------------
    with tab2:
        st.subheader("Deep Dive Analytics")
        st.write("### Top 5 Largest Transactions")
        sorted_df = filtered_df.reindex(filtered_df['Amount'].abs().sort_values(ascending=False).index)
        st.dataframe(sorted_df.head(5), use_container_width=True)

        if not exp_df.empty:
            st.write("### Expense Distribution")
            fig_box = px.bar(exp_df, x='Description', y='Amount', color='Category', 
                             template=plotly_template, color_discrete_sequence=color_sequence)
            fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_box, use_container_width=True)

    # ---------------- TAB 3: AI ADVISOR & CHAT ----------------
    with tab3:
        st.subheader("🤖 AI Financial Advisor & Decision Suite")
        
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            st.write("#### 📑 Instant CFO Executive Report")
            if st.button("Generate Full Audit Report"):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    summary_str = f"Dataset: {selected_view}. Revenue: {currency_symbol} {total_revenue:,.2f}, Expenses: {currency_symbol} {total_expenses:,.2f}, Net: {currency_symbol} {net_profit:,.2f}."
                    
                    prompt = f"""
                    You are a Senior CFO Consultant. Analyze this financial summary for dataset '{selected_view}': {summary_str}.
                    Here are the exact category totals:
                    {category_totals_str}
                    
                    1. Provide a 3-bullet Executive Summary on profitability.
                    2. Highlight 1 operational or expense risk based on the specific category totals provided.
                    3. Provide 2 actionable strategic recommendations for the owner.
                    """
                    with st.spinner("Analyzing records..."):
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.1-8b-instant",
                        )
                        raw_report = chat_completion.choices[0].message.content
                        st.success("Audit Generated!")
                        st.write(sanitize_markdown(raw_report))
                except Exception as e:
                    st.error(f"AI Error: {e}")

        with col_ai2:
            st.write("#### 💬 Query Your Data (Natural Language)")
            
            # Chat Interface Container
            chat_container = st.container(height=350)
            
            # Display past messages with sleek minimal icons
            with chat_container:
                for msg in st.session_state.chat_messages:
                    avatar_icon = "👤" if msg["role"] == "user" else "✨"
                    st.chat_message(msg["role"], avatar=avatar_icon).write(sanitize_markdown(msg["content"]))
            
            # Chat Input Form
            if user_query := st.chat_input("Ask a question about your uploaded transactions..."):
                # Display user query immediately
                st.session_state.chat_messages.append({"role": "user", "content": user_query})
                with chat_container:
                    st.chat_message("user", avatar="👤").write(sanitize_markdown(user_query))
                
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    query_prompt = f"""
                    You are a financial data analyst. Answer the user's question accurately using ONLY the provided data.
                    
                    CRITICAL MATH INSTRUCTION: 
                    Do NOT add the pre-calculated totals to the individual transactions. They are the exact same data. When asked for totals or comparisons, ONLY use the pre-calculated exact totals provided below.
                    
                    Pre-calculated Exact Totals:
                    {category_totals_str}
                    
                    Raw Transaction Dataset:
                    {context_data}
                    
                    User Question: {user_query}
                    """
                    with chat_container:
                        with st.spinner("Analyzing data..."):
                            chat_completion = client.chat.completions.create(
                                messages=[{"role": "user", "content": query_prompt}],
                                model="llama-3.1-8b-instant",
                            )
                            ai_response = chat_completion.choices[0].message.content
                            
                            st.chat_message("assistant", avatar="✨").write(sanitize_markdown(ai_response))
                            st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.error(f"Query Error: {e}")

            st.markdown("---")
            st.write("#### 🔮 AI What-If Scenario Simulator")
            st.markdown("Test strategic business shifts and project future financial outcomes.")
            scenario_input = st.text_area(
                "Enter a simulation scenario:", 
                placeholder="e.g., What if we reduce total expenses by 15% next quarter?"
            )
            
            if st.button("Run Simulation"):
                if scenario_input:
                    try:
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        sim_summary = f"Current Revenue: {currency_symbol} {total_revenue:,.2f}, Current Expenses: {currency_symbol} {total_expenses:,.2f}, Net Profit: {currency_symbol} {net_profit:,.2f}."
                        
                        sim_prompt = f"""
                        You are an expert Financial Modeler and CFO. Based on the current baseline ({sim_summary}), evaluate the following user simulation scenario:
                        
                        Scenario: '{scenario_input}'
                        
                        To ensure mathematical accuracy, use these exact category totals for your baseline calculations:
                        {category_totals_str}
                        
                        Provide:
                        1. Estimated quantitative impact on Net Profit and Profit Margin (calculate using the exact category totals provided).
                        2. Strategic feasibility assessment.
                        3. Potential risks or trade-offs.
                        """
                        with st.spinner("Running simulation model..."):
                            sim_completion = client.chat.completions.create(
                                messages=[{"role": "user", "content": sim_prompt}],
                                model="llama-3.1-8b-instant",
                            )
                            raw_sim = sim_completion.choices[0].message.content
                            st.success("Simulation Complete!")
                            st.write(sanitize_markdown(raw_sim))
                    except Exception as e:
                        st.error(f"Simulation Error: {e}")
                else:
                    st.warning("Please enter a simulation scenario first.")

    # ---------------- TAB 4: LEDGER & EXPORT ----------------
    with tab4:
        st.subheader(f"Transaction Ledger — {selected_view}")
        st.dataframe(filtered_df, use_container_width=True)
        
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Processed Report (CSV)",
            data=csv_data,
            file_name=f"report_{selected_view.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

else:
    st.info("👈 Upload one or more CSV files in the sidebar to populate the dashboard.")