-- 1. How is the business growing year over year?
SELECT 
    order_year,
    ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
    ROUND(SUM(profit)::numeric, 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales_amount) * 100)::numeric, 1) AS margin_pct
FROM sales_data
GROUP BY order_year
ORDER BY order_year;

--2. Which product category drives the most revenue and profit?
SELECT 
    category,
    ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
    ROUND(SUM(profit)::numeric, 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales_amount) * 100)::numeric, 1) AS margin_pct
FROM sales_data
GROUP BY category
ORDER BY total_revenue DESC;

--3. Which month generates the highest revenue?
SELECT 
    order_month,
    ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
    ROUND(SUM(profit)::numeric, 2) AS total_profit
FROM sales_data
GROUP BY order_month
ORDER BY total_revenue DESC;

--4.Which customer segment is most valuable to the business?
SELECT 
    segment,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
    ROUND(SUM(profit)::numeric, 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales_amount) * 100)::numeric, 1) AS margin_pct,
    ROUND(AVG(sales_amount)::numeric, 2) AS avg_order_value
FROM sales_data
GROUP BY segment
ORDER BY total_revenue DESC;

--5. Which region contributes the most revenue and how does each region rank compared to total company revenue?
WITH region_summary AS (
    SELECT 
        region,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
        ROUND(SUM(profit)::numeric, 2) AS total_profit,
        ROUND((SUM(profit) / SUM(sales_amount) * 100)::numeric, 1) AS margin_pct
    FROM sales_data
    GROUP BY region
)
SELECT 
    region,
    total_orders,
    total_revenue,
    total_profit,
    margin_pct,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    ROUND((total_revenue / SUM(total_revenue) OVER () * 100)::numeric, 1) AS revenue_contribution_pct
FROM region_summary
ORDER BY revenue_rank;

--6.Is discounting actually hurting our profit and how bad is the damage at each discount level?
WITH discount_analysis AS (
    SELECT 
        discount,
        COUNT(order_id) AS total_orders,
        ROUND(AVG(sales_amount)::numeric, 2) AS avg_sales,
        ROUND(AVG(profit)::numeric, 2) AS avg_profit,
        ROUND((AVG(profit) / AVG(sales_amount) * 100)::numeric, 1) AS margin_pct
    FROM sales_data
    GROUP BY discount
)
SELECT 
    discount,
    total_orders,
    avg_sales,
    avg_profit,
    margin_pct,
    ROUND((avg_profit - FIRST_VALUE(avg_profit) OVER (ORDER BY discount)) ::numeric, 2) AS profit_drop_vs_no_discount
FROM discount_analysis
ORDER BY discount;

--7. Who are the top performing sales reps and how do they compare to the company average?
WITH rep_summary AS (
    SELECT 
        sales_rep_id,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
        ROUND(AVG(sales_amount)::numeric, 2) AS avg_order_value
    FROM sales_data
    WHERE sales_rep_id != 'UNASSIGNED'
    GROUP BY sales_rep_id
)
SELECT 
    sales_rep_id,
    total_orders,
    total_revenue,
    avg_order_value,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    ROUND(AVG(total_revenue) OVER ()::numeric, 2) AS company_avg_revenue,
    CASE 
        WHEN total_revenue > AVG(total_revenue) OVER () THEN 'Above Average'
        WHEN total_revenue < AVG(total_revenue) OVER () THEN 'Below Average'
        ELSE 'Average'
    END AS performance_flag
FROM rep_summary
ORDER BY revenue_rank
LIMIT 10;

--8.Which category has the highest return rate and is it affecting profitability
SELECT 
    category,
    COUNT(order_id) AS total_orders,
    SUM(return_flag) AS total_returns,
    ROUND((SUM(return_flag)::numeric / COUNT(order_id) * 100), 1) AS return_rate_pct,
    ROUND(AVG(profit)::numeric, 2) AS avg_profit,
    RANK() OVER (ORDER BY SUM(return_flag)::numeric / COUNT(order_id) DESC) AS return_rank,
    CASE
        WHEN (SUM(return_flag)::numeric / COUNT(order_id) * 100) > 10 THEN 'High Risk'
        WHEN (SUM(return_flag)::numeric / COUNT(order_id) * 100) BETWEEN 7 AND 10 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_flag
FROM sales_data
GROUP BY category
ORDER BY return_rate_pct DESC;

--9.Which payment method is most preferred and does it affect order value?
SELECT 
    payment_method,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
    ROUND(AVG(sales_amount)::numeric, 2) AS avg_order_value,
    ROUND((COUNT(order_id)::numeric / SUM(COUNT(order_id)) OVER () * 100), 1) AS usage_pct
FROM sales_data
GROUP BY payment_method
ORDER BY total_orders DESC;

--10.What is the year over year revenue growth rate?
SELECT 
    order_year,
    ROUND(SUM(sales_amount)::numeric, 2) AS total_revenue,
    ROUND(LAG(SUM(sales_amount)) OVER (ORDER BY order_year)::numeric, 2) AS prev_year_revenue,
    ROUND((
        (SUM(sales_amount) - LAG(SUM(sales_amount)) OVER (ORDER BY order_year)) 
        / LAG(SUM(sales_amount)) OVER (ORDER BY order_year) * 100
    )::numeric, 1) AS yoy_growth_pct
FROM sales_data
GROUP BY order_year
ORDER BY order_year;