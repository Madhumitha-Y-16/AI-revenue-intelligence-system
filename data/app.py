import streamlit as st
from langchain_groq import ChatGroq
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

# page config
st.set_page_config(
    page_title="SalesForce Pro — Revenue Assistant",
    page_icon="📊",
    layout="centered"
)

# title
st.title("📊 SalesForce Pro Inc.")
st.subheader("AI Revenue Intelligence Assistant")
st.markdown("Ask any question about company revenue, customers, products or sales performance.")
st.divider()

# setup
engine = create_engine(f"postgresql+psycopg2://postgres:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/salesforce_pro_db")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_question(question):
    # generate sql
    prompt = f"""
    You are a SQL expert. Write a PostgreSQL query for this question:
    {question}
    
    Table: sales_data
    Columns: order_id, order_date, category, region, segment, 
    sales_amount, profit, discount, profit_margin, order_year, 
    order_month, sales_rep_id, customer_id, product_name
    
    Return ONLY the SQL query, nothing else.
    """
    sql = llm.invoke(prompt).content.strip()
    sql = sql.replace("```sql","").replace("```","").strip()
    
    # run sql
    with engine.connect() as conn:
        result = pd.read_sql(text(sql), conn)
    
    # explain result
    explain = f"""
    Question: {question}
    Data: {result.to_string()}
    Give a clear 2-3 line business answer a non-technical manager can understand.
    """
    answer = llm.invoke(explain).content
    return sql, result, answer

# chat history
if 'history' not in st.session_state:
    st.session_state.history = []

# example questions
st.markdown("**Try asking:**")
col1, col2 = st.columns(2)
with col1:
    st.markdown("- Which category has highest profit?")
    st.markdown("- What is revenue by region?")
with col2:
    st.markdown("- Who is the top sales rep?")
    st.markdown("- Which month has lowest sales?")

st.divider()

# input box
question = st.text_input("Type your question here:", placeholder="e.g. Which product category is most profitable?")

if st.button("Ask", type="primary"):
    if question:
        with st.spinner("Thinking..."):
            try:
                sql, result, answer = ask_question(question)

                st.success("Answer")
                st.write(answer)

                # save to history
                st.session_state.history.append({
                    'question': question,
                    'answer': answer
                })

                with st.expander("See the SQL query generated"):
                    st.code(sql, language="sql")

                with st.expander("See the raw data"):
                    st.dataframe(result)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please type a question first.")

# show previous questions
if st.session_state.history:
    st.divider()
    st.markdown("**Previous Questions:**")
    for item in reversed(st.session_state.history[:-1]):
        st.markdown(f"**Q:** {item['question']}")
        st.markdown(f"**A:** {item['answer']}")
        st.divider()