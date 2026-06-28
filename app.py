import streamlit as st
from langchain_groq import ChatGroq
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import os
import time

load_dotenv()

# page config
st.set_page_config(
    page_title="SalesForce Pro — Revenue Intelligence",
    page_icon="📊",
    layout="wide"
)

# custom css
st.markdown("""
<style>
    .stApp { background-color: #0D1B2A; }
    .answer-card {
        background-color: #1B2A3B;
        border-left: 4px solid #4A90D9;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    .metric-highlight {
        background-color: #1B2A3B;
        border: 1px solid #4A90D9;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 42px;
        font-weight: bold;
        color: #4A90D9;
    }
    .metric-label {
        font-size: 14px;
        color: #aaaaaa;
        margin-top: 5px;
    }
    .status-bar {
        background-color: #1B2A3B;
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0;
        font-size: 13px;
    }
    .empty-state {
        background-color: #1B2A3B;
        border: 1px dashed #4A90D9;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        color: #aaaaaa;
    }
    div[data-testid="metric-container"] {
        background-color: #1B2A3B;
        border: 1px solid #4A90D9;
        border-radius: 10px;
        padding: 15px;
    }
    .stButton button {
        background-color: #1B2A3B;
        color: white;
        border: 1px solid #4A90D9;
        border-radius: 20px;
        font-size: 13px;
    }
    .ask-button button {
        background-color: #4A90D9 !important;
        color: white !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        padding: 10px 30px !important;
    }
    .recent-btn button {
        background-color: #0D1B2A !important;
        border: 1px solid #2E6DA4 !important;
        text-align: left !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# setup
engine = create_engine(f"postgresql+psycopg2://postgres:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/salesforce_pro_db")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# load kpis
@st.cache_data
def load_kpis():
    try:
        conn = engine.connect()
        result = pd.read_sql(text("""
            SELECT 
                ROUND(CAST(SUM(sales_amount) AS numeric)/10000000, 1) as revenue_cr,
                COUNT(order_id) as total_orders,
                COUNT(DISTINCT customer_id) as total_customers,
                ROUND(CAST(SUM(profit) AS numeric)/10000000, 1) as profit_cr,
                COUNT(DISTINCT region) as regions
            FROM sales_data
        """), conn)
        conn.close()
        return result.iloc[0]
    except:
        return None

def format_value(val):
    # format raw numbers into readable format
    try:
        f = float(val)
        if f < 1:
            return f"{f * 100:.2f}%"
        elif f > 10000000:
            return f"₹{f/10000000:.1f} Cr"
        elif f > 100000:
            return f"₹{f/100000:.1f} L"
        else:
            return f"{f:,.2f}"
    except:
        return str(val)

def ask_question(question):
    try:
        # step 1 — generate sql
        prompt = f"""
        You are a SQL expert. Write a PostgreSQL SELECT query for this question:
        {question}
        
        Table: sales_data
        Columns: order_id, order_date, category, region, segment, 
        sales_amount, profit, discount, profit_margin, order_year, 
        order_month, sales_rep_id, customer_id, product_name

        Column definitions:
        - sales_amount: total revenue per order in rupees
        - profit: absolute profit per order in rupees  
        - profit_margin: profit percentage per order (0 to 100)
        - discount: discount applied per order (0 to 1)
        - order_year: year of the order (2021 to 2024)
        - order_month: month of the order (1 to 12)

        Rules:
        - Use AVG(profit_margin) when asked about profit margin percentage
        - Use SUM(profit) when asked about total profit in rupees
        - Use SUM(sales_amount) when asked about total revenue
        - Use COUNT(order_id) when asked about number of orders
        - Return ONLY the SQL query ending with semicolon
        - Do not add any explanation after the semicolon
        - Do not use DROP, DELETE, UPDATE or INSERT
        - Query must be valid PostgreSQL
        """
        sql = llm.invoke(prompt).content.strip()
        sql = sql.replace("```sql","").replace("```","").strip()
        if ";" in sql:
            sql = sql.split(";")[0] + ";"

        # safety check
        if not sql.upper().startswith("SELECT"):
            return None, None, None, None, None, "I can only answer questions related to sales data. Please ask about revenue, customers, products, regions or profitability."

        # step 2 — execute sql
        start = time.time()
        with engine.connect() as conn:
            result = pd.read_sql(text(sql), conn)
        exec_time = round((time.time() - start) * 1000)

        # step 3 — extract key metric
        key_metric = None
        key_label = None
        if len(result) == 1 and len(result.columns) <= 2:
            for col in result.columns:
                val = result[col].iloc[0]
                try:
                    float(val)
                    key_metric = format_value(val)
                    key_label = col.replace("_", " ").title()
                except:
                    pass

        # step 4 — generate structured answer
        explain = f"""
        Question: {question}
        SQL Result: {result.to_string()}
        
        Respond in exactly this format:

        ANSWER: [one line direct answer using actual numbers from the data]
        
        INSIGHT: [2 lines explaining why this is the case from a business perspective using actual numbers]
        
        RECOMMENDATION: [one specific data-driven actionable recommendation with numbers]
        
        Use the actual numbers from the SQL result. Do not say data is incomplete.
        """
        response = llm.invoke(explain).content
        return sql, result, exec_time, len(result), key_metric, response

    except Exception as e:
        return None, None, None, None, None, "I can only answer questions related to the sales database. Please ask about revenue, customers, products, sales representatives, regions or profitability."

# ── HEADER ────────────────────────────────────────────────
st.markdown("# 📊 SalesForce Pro Inc.")
st.markdown("### AI Revenue Intelligence System")
st.markdown("*Ask business questions in natural language — v1.0*")
st.divider()

# ── KPI CARDS ─────────────────────────────────────────────
kpis = load_kpis()
if kpis is not None:
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("💰 Total Revenue", f"₹{kpis['revenue_cr']} Cr")
    with k2:
        st.metric("📦 Total Orders", f"{int(kpis['total_orders']):,}")
    with k3:
        st.metric("👥 Customers", f"{int(kpis['total_customers']):,}")
    with k4:
        st.metric("📈 Total Profit", f"₹{kpis['profit_cr']} Cr")
    with k5:
        st.metric("🗺️ Regions", f"{int(kpis['regions'])}")

st.divider()

# ── SUGGESTED QUESTIONS ───────────────────────────────────
st.markdown("**💡 Suggested Questions — click to ask:**")

suggested = [
    "Which category has the highest profit margin?",
    "Which region has the lowest revenue?",
    "Who is the top performing sales rep?",
    "Which month generates the highest revenue?",
    "What is the total revenue for each year?",
    "Which product has the highest sales?",
    "What is the average discount across all orders?",
    "Which customer segment is most profitable?"
]

cols = st.columns(4)
for i, q in enumerate(suggested):
    with cols[i % 4]:
        if st.button(q, key=f"btn_{i}"):
            st.session_state.selected_question = q

st.divider()

# ── SESSION STATE ─────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state.history = []
if 'selected_question' not in st.session_state:
    st.session_state.selected_question = ""
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# ── INPUT ─────────────────────────────────────────────────
question = st.text_input(
    "Ask your question:",
    value=st.session_state.selected_question,
    placeholder="e.g. Which product category has the highest profit margin?",
    key="question_input"
)

# ── EMPTY STATE ───────────────────────────────────────────
if not st.session_state.history and not question:
    st.markdown("""
    <div class="empty-state">
        <h3>👋 Welcome to SalesForce Pro Revenue Assistant</h3>
        <p>Ask a business question to explore your sales data,<br>
        or choose one of the suggested questions above.</p>
        <br>
        <p style="color:#4A90D9">Examples: "Which category is most profitable?" · "Who is the top sales rep?" · "What is revenue by region?"</p>
    </div>
    """, unsafe_allow_html=True)

# ── ASK BUTTON ────────────────────────────────────────────
st.markdown('<div class="ask-button">', unsafe_allow_html=True)
ask_clicked = st.button("🔍 Ask", type="primary")
st.markdown('</div>', unsafe_allow_html=True)

if ask_clicked:
    if question:
        # status bar
        status = st.empty()

        status.markdown('<div class="status-bar">⚙️ Generating SQL query...</div>', unsafe_allow_html=True)
        time.sleep(0.5)

        with st.spinner(""):
            sql, result, exec_time, row_count, key_metric, response = ask_question(question)

        status.markdown(f'<div class="status-bar">✅ SQL Generated → ✅ Executed Successfully → ⚡ {exec_time} ms</div>', unsafe_allow_html=True)

        # parse response
        lines = response.split("\n")
        answer = insight = recommendation = ""
        for line in lines:
            if line.startswith("ANSWER:"):
                answer = line.replace("ANSWER:", "").strip()
            elif line.startswith("INSIGHT:"):
                insight = line.replace("INSIGHT:", "").strip()
            elif line.startswith("RECOMMENDATION:"):
                recommendation = line.replace("RECOMMENDATION:", "").strip()

        # display answer
        st.markdown("---")
        st.markdown("### 💬 Answer")

        col1, col2 = st.columns([2, 1])
        with col1:
            # highlight key metric if single value
            if key_metric:
                st.markdown(f"""
                <div class="metric-highlight">
                    <div class="metric-value">{key_metric}</div>
                    <div class="metric-label">{answer}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="answer-card">
                    <h4 style="color:#4A90D9">📌 {answer if answer else response}</h4>
                </div>
                """, unsafe_allow_html=True)

            if insight:
                st.markdown(f"**📊 Insight:** {insight}")
            if recommendation:
                st.markdown(f"**💡 Recommendation:** {recommendation}")

        with col2:
            if exec_time:
                st.metric("⚡ Execution Time", f"{exec_time} ms")
            if row_count:
                st.metric("📋 Rows Returned", row_count)
            st.metric("🤖 Model", "Llama 3.1 8B")

        if sql:
            with st.expander("🔍 View Generated SQL"):
                st.code(sql, language="sql")

        if result is not None:
            with st.expander("📊 View Raw Data"):
                st.dataframe(result, use_container_width=True)

        # save to history
        st.session_state.history.append({
            'question': question,
            'answer': answer if answer else response
        })
        st.session_state.selected_question = ""

    else:
        st.warning("Please type a question first.")

# ── RECENT QUESTIONS ──────────────────────────────────────
if st.session_state.history:
    st.divider()
    st.markdown("### 🕐 Recent Questions — click to rerun")
    st.markdown('<div class="recent-btn">', unsafe_allow_html=True)
    for item in reversed(st.session_state.history[-5:]):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**Q:** {item['question']}")
            st.markdown(f"*{item['answer'][:100]}...*" if len(item['answer']) > 100 else f"*{item['answer']}*")
        with col2:
            if st.button("↩ Rerun", key=f"rerun_{item['question']}"):
                st.session_state.selected_question = item['question']
                st.rerun()
        st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)