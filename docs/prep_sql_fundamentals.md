# SQL Fundamentals and Query Patterns

## Overview

SQL is the universal language for data manipulation and a core skill tested in every MLE and data-related interview. Mastery goes beyond basic SELECT: interviewers expect fluency with JOINs, aggregation pipelines, subqueries, CTEs, and window functions -- the building blocks for feature engineering queries, data validation, and analytical deep-dives in production ML systems.

## Core Concepts

### Query Execution Order

Understanding the logical execution order is essential for debugging and optimization:

```
FROM / JOIN  ->  WHERE  ->  GROUP BY  ->  HAVING  ->  SELECT  ->  DISTINCT  ->  ORDER BY  ->  LIMIT
```

Key insight: `WHERE` filters rows before aggregation; `HAVING` filters groups after aggregation. Aliases defined in `SELECT` are not available in `WHERE` or `HAVING` (MySQL allows it in `HAVING` as an extension, but standard SQL does not).

### SELECT Fundamentals

**Core syntax**:

```sql
SELECT column_name
FROM table_name
WHERE condition
ORDER BY column_name ASC | DESC
LIMIT offset, count;
```

**Essential clauses**:
- `DISTINCT` -- deduplicate results: `SELECT DISTINCT department FROM employees`
- `AS` -- alias columns, tables, or subquery results for readability
- `IS NULL / IS NOT NULL` -- NULL comparisons (never use `= NULL`)
- `BETWEEN a AND b` -- inclusive range filter (equivalent to `>= a AND <= b`)
- `IN (val1, val2, ...)` -- set membership test

**Pattern matching**:
- `LIKE`: `%` matches any string, `_` matches any single character. Case-insensitive.
  - `WHERE name LIKE 'b%'` matches "Bob", "bike"
- `REGEXP`: full regex support.
  - `WHERE name REGEXP '^f[a-z]+d$'` matches "fred", "ford"

### JOIN Types

JOINs are the most frequently tested SQL concept. The key is knowing which rows survive each join type.

| JOIN Type | Keeps Left Unmatched | Keeps Right Unmatched | Use Case |
|-----------|:-------------------:|:--------------------:|----------|
| INNER JOIN | No | No | Only matching rows from both tables |
| LEFT (OUTER) JOIN | Yes (NULLs for right) | No | All rows from left, matches from right |
| RIGHT (OUTER) JOIN | No | Yes (NULLs for left) | All rows from right, matches from left |
| FULL OUTER JOIN | Yes | Yes | All rows from both (MySQL: emulate with UNION) |
| CROSS JOIN | N/A | N/A | Cartesian product of both tables |
| SELF JOIN | N/A | N/A | Table joined with itself (requires aliases) |
| NATURAL JOIN | Auto-matches | Auto-matches | Joins on same-named columns (avoid -- implicit) |

**INNER JOIN** (most common):

```sql
SELECT e.name, d.dept_name
FROM employees e
JOIN departments d ON e.dept_id = d.id;
```

**LEFT JOIN** -- keep all left rows even without matches:

```sql
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.id;
-- Employees without departments will show NULL for dept_name
```

**SELF JOIN** -- compare rows within the same table:

```sql
-- Employees earning more than their manager
SELECT e.name AS employee, m.name AS manager, e.salary, m.salary
FROM employees e
JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

**USING** shorthand -- when join columns have the same name:

```sql
SELECT * FROM orders JOIN customers USING (customer_id);
-- Equivalent to: ON orders.customer_id = customers.customer_id
```

**Multi-table JOIN** (avoid more than 3 tables for performance):

```sql
SELECT o.id, c.name, p.product_name
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id;
```

### UNION: Combining Result Sets

```sql
SELECT name, city FROM customers
UNION           -- removes duplicates (slower)
SELECT name, city FROM suppliers;

SELECT name, city FROM customers
UNION ALL       -- keeps duplicates (faster)
SELECT name, city FROM suppliers;
```

Rules:
- Column count and types must match across all SELECT statements
- Column names come from the first SELECT
- `ORDER BY` applies to the final combined result; wrap sub-selects in parentheses if each needs its own sorting + `LIMIT`

### DML: INSERT, UPDATE, DELETE

```sql
-- Insert single row
INSERT INTO customers (first_name, last_name, city)
VALUES ('John', 'Smith', 'NYC');

-- Insert multiple rows
INSERT INTO shippers (name) VALUES ('S1'), ('S2'), ('S3');

-- Insert from query (batch migration)
INSERT INTO orders_archived
SELECT * FROM orders WHERE order_date < '2019-01-01';

-- Update with subquery
UPDATE invoices
SET payment_total = 10
WHERE client_id = (SELECT client_id FROM clients WHERE name = 'Myworks');

-- Delete
DELETE FROM invoices WHERE invoice_id = 1;
```

Key points:
- `LAST_INSERT_ID()` returns the most recent auto-increment ID -- essential for hierarchical inserts
- Always include `WHERE` in UPDATE/DELETE to avoid modifying entire tables
- Cannot UPDATE the same table used in a subquery (create a temp copy or use CTE)

### Aggregate Functions and GROUP BY

**Aggregate functions**: `COUNT()`, `SUM()`, `AVG()`, `MAX()`, `MIN()`

- `COUNT(column)` counts non-NULL values; `COUNT(*)` counts all rows
- `COUNT(DISTINCT column)` counts unique non-NULL values

**GROUP BY** -- group rows by one or more columns, then aggregate each group:

```sql
SELECT department, COUNT(*) AS emp_count, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;
```

**Composite grouping**: `GROUP BY state, city` groups by the tuple (state, city).

**WITH ROLLUP** (MySQL): adds summary rows with subtotals and grand totals.

### WHERE vs HAVING

| Aspect | WHERE | HAVING |
|--------|-------|--------|
| Filters | Individual rows | Groups (after GROUP BY) |
| Timing | Before aggregation | After aggregation |
| Can use aggregates? | No | Yes |
| Performance | Faster (reduces rows early) | Slower (aggregates first) |

```sql
-- WHERE filters rows, HAVING filters groups
SELECT department, AVG(salary) AS avg_sal
FROM employees
WHERE hire_date > '2020-01-01'    -- filter rows first
GROUP BY department
HAVING AVG(salary) > 80000;       -- then filter groups
```

### Subqueries

**Non-correlated** -- executes once, independently of the outer query:

```sql
SELECT name FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

**Correlated** -- references the outer query, executes once per outer row:

```sql
-- Employees earning above their department average
SELECT e.name, e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(salary) FROM employees
    WHERE department = e.department
);
```

**ALL / ANY (SOME)**:

```sql
-- Salary greater than ALL values returned by subquery (i.e., greater than the max)
WHERE salary > ALL (SELECT salary FROM employees WHERE dept = 'Sales')

-- Salary greater than ANY value (i.e., greater than the min)
WHERE salary > ANY (SELECT salary FROM employees WHERE dept = 'Sales')
-- Note: = ANY is equivalent to IN
```

**EXISTS vs IN**:

```sql
-- EXISTS: short-circuits on first match (often faster for large subqueries)
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id);

-- IN: materializes the full subquery result first
SELECT * FROM customers
WHERE id IN (SELECT customer_id FROM orders);
```

EXISTS is generally more efficient than IN for correlated checks because it stops at the first match rather than building the complete result set.

**Subquery in SELECT** -- duplicate an aggregate for row-level arithmetic:

```sql
SELECT name, salary,
       salary - (SELECT AVG(salary) FROM employees) AS diff_from_avg
FROM employees;
```

### Common Table Expressions (CTEs)

CTEs create named temporary result sets scoped to a single query. They improve readability over nested subqueries and can be referenced multiple times.

```sql
WITH high_earners AS (
    SELECT department, name, salary
    FROM employees
    WHERE salary > 100000
)
SELECT department, COUNT(*) AS count
FROM high_earners
GROUP BY department;
```

**Advantages over subqueries**:
- Can reference the same CTE multiple times in one query
- Self-referencing (recursive CTEs)
- Easier to read and maintain for complex queries

**Recursive CTEs** -- traverse hierarchical data or generate sequences:

```sql
-- Generate sequence 1..10
WITH RECURSIVE seq AS (
    SELECT 1 AS n                    -- anchor member
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 10  -- recursive member
)
SELECT * FROM seq;

-- Org chart: find all reports under a manager
WITH RECURSIVE reports AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees WHERE id = 1      -- root manager
    UNION ALL
    SELECT e.id, e.name, e.manager_id, r.level + 1
    FROM employees e
    JOIN reports r ON e.manager_id = r.id
)
SELECT * FROM reports;
```

**CTE vs Subquery decision**: Use CTEs when you need to reference the result multiple times, the logic is deeply nested, or you need recursion. Use subqueries for simple, one-off filtering.

### Window Functions

Window functions compute values across a set of related rows without collapsing them (unlike GROUP BY). They operate on a "window" of rows defined by `PARTITION BY` and `ORDER BY`.

**Syntax**:

```sql
SELECT *,
    window_function() OVER (
        PARTITION BY col1       -- defines groups (optional)
        ORDER BY col2           -- ordering within each group
        ROWS BETWEEN ...        -- frame specification (optional)
    ) AS result
FROM table;
```

**PARTITION BY vs GROUP BY**:
- `GROUP BY` reduces rows: 100 rows with 5 departments -> 5 rows
- `PARTITION BY` preserves rows: 100 rows -> 100 rows, each annotated with its partition's computed value

### Ranking Functions

Given values {3, 3, 3, 7}:

| Function | Result | Behavior |
|----------|--------|----------|
| `RANK()` | {1, 1, 1, 4} | Ties share rank, next rank skips (gaps) |
| `DENSE_RANK()` | {1, 1, 1, 2} | Ties share rank, next rank is consecutive (no gaps) |
| `ROW_NUMBER()` | {1, 2, 3, 4} | No ties -- arbitrary tiebreaking |

**TOP-N per group** (classic interview pattern):

```sql
-- Top 3 earners per department
SELECT * FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY department
            ORDER BY salary DESC
        ) AS rn
    FROM employees
) ranked
WHERE rn <= 3;
```

### Aggregate Window Functions

Aggregate functions (`SUM`, `AVG`, `COUNT`, `MAX`, `MIN`) become window functions when followed by `OVER()`.

```sql
-- Running total of sales by date
SELECT order_date, amount,
    SUM(amount) OVER (ORDER BY order_date) AS running_total
FROM orders;

-- Department average alongside each row
SELECT name, department, salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg
FROM employees;
```

Without `ORDER BY` in the window: the aggregate covers the entire partition (constant per group).
With `ORDER BY`: the aggregate is cumulative (running computation up to the current row).

### Sliding Window Frames

Frame specifications control exactly which rows the window function considers:

```sql
-- Moving average over 3 rows (current + 1 preceding + 1 following)
AVG(price) OVER (
    ORDER BY date
    ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
)

-- Running total from start to current row (default with ORDER BY)
SUM(amount) OVER (
    ORDER BY date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)

-- Time-based window: 7 days before and after
AVG(price) OVER (
    ORDER BY order_date
    RANGE BETWEEN INTERVAL 7 DAY PRECEDING AND INTERVAL 7 DAY FOLLOWING
)
```

**ROWS vs RANGE**:
- `ROWS`: physical row count (e.g., 2 rows before current)
- `RANGE`: logical value range (e.g., all rows within 7 days)

**Named windows** (reuse across multiple functions):

```sql
SELECT *,
    SUM(grade) OVER w AS running_sum,
    AVG(grade) OVER w AS running_avg
FROM scores
WINDOW w AS (PARTITION BY course_id ORDER BY student_id);
```

### Built-in Functions Quick Reference

| Category | Functions | Notes |
|----------|-----------|-------|
| Numeric | `ROUND(n, d)`, `FLOOR()`, `CEILING()`, `ABS()`, `TRUNCATE(n, d)` | `ROUND(2.355, 2)` = 2.36 |
| String | `LENGTH()`, `UPPER()`, `LOWER()`, `TRIM()`, `SUBSTRING(s, pos, len)`, `CONCAT()`, `REPLACE()`, `LOCATE(substr, str)` | Index starts at 1 |
| Date/Time | `NOW()`, `CURDATE()`, `YEAR()`, `MONTH()`, `DAY()`, `DATEDIFF(d1, d2)`, `DATE_ADD(d, INTERVAL n UNIT)` | `DATEDIFF` returns days |
| Conditional | `IF(expr, true_val, false_val)`, `IFNULL(val, default)`, `COALESCE(v1, v2, ...)`, `CASE WHEN ... THEN ... END` | `COALESCE` returns first non-NULL |

## Implementation

### Classic Interview: 2nd Highest Salary

```sql
-- Method 1: Subquery
SELECT MAX(salary) AS second_highest
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Method 2: DENSE_RANK (handles ties correctly)
SELECT salary AS second_highest FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rn
    FROM employees
) ranked
WHERE rn = 2
LIMIT 1;

-- Method 3: OFFSET
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;
```

### Running Total and Moving Average

```sql
SELECT
    order_date,
    daily_revenue,
    SUM(daily_revenue) OVER (ORDER BY order_date) AS cumulative_revenue,
    AVG(daily_revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7day
FROM daily_sales;
```

### Year-over-Year Comparison

```sql
WITH monthly AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m') AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT
    m1.month,
    m1.revenue AS current_revenue,
    m2.revenue AS prev_year_revenue,
    ROUND((m1.revenue - m2.revenue) / m2.revenue * 100, 1) AS yoy_pct
FROM monthly m1
LEFT JOIN monthly m2
    ON DATE_ADD(m2.month, INTERVAL 12 MONTH) = m1.month;
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Self-join | Compare rows within same table | Always use aliases; e.g., employee vs manager salary |
| Subquery in WHERE | Filter based on aggregate | Non-correlated runs once; correlated runs per row |
| EXISTS vs IN | Check existence of related records | EXISTS short-circuits; IN materializes full list |
| CTE + window function | Rank then filter | Cannot use window functions in WHERE -- wrap in CTE |
| DENSE_RANK for Nth value | Find Nth highest/lowest | Handles ties correctly unlike OFFSET |
| GROUP BY + HAVING | Filter on aggregate condition | WHERE before aggregation, HAVING after |
| LEFT JOIN + IS NULL | Find non-matching rows | "Customers with no orders" pattern |
| UNION ALL vs UNION | Combine disjoint result sets | UNION ALL faster (no dedup overhead) |

### Common Interview Questions

- [ ] Write a query to find the 2nd highest salary in a table
- [ ] Explain the difference between WHERE and HAVING
- [ ] When would you use a CTE vs a subquery?
- [ ] Write a window function to calculate a running average
- [ ] Self-join: find employees earning more than their manager
- [ ] What is the difference between RANK, DENSE_RANK, and ROW_NUMBER?
- [ ] Find the top N items per category (TOP-N per group)
- [ ] Explain EXISTS vs IN -- when is each more efficient?

## Comparisons

### JOIN Types

| Aspect | INNER JOIN | LEFT JOIN | CROSS JOIN | SELF JOIN |
|--------|-----------|-----------|------------|-----------|
| Unmatched rows | Excluded | Left kept, right NULL | N/A (all combos) | Depends on join type |
| Result size | <= min(L, R) | = L | L x R | Varies |
| Typical use | Standard lookup | "Find missing" pattern | Generate combinations | Compare rows in same table |

### Subquery vs CTE vs Temp Table

| Aspect | Subquery | CTE | Temp Table |
|--------|----------|-----|------------|
| Reusability | Once per query | Multiple refs in same query | Across queries in session |
| Recursion | No | Yes | No (manual loops) |
| Performance | Inline (optimizer dependent) | Inline (optimizer dependent) | Materialized on disk |
| Readability | Low (nested) | High (named, sequential) | Medium |
| Best for | Simple one-off filters | Complex multi-step logic | Very large intermediate results |

### Window vs GROUP BY

| Aspect | GROUP BY | Window Function |
|--------|---------|-----------------|
| Row count | Reduced (one per group) | Preserved (original row count) |
| Access to detail | Only grouped columns + aggregates | All columns + computed value |
| Running totals | Not possible | Natural fit |
| Ranking | Not possible | RANK, DENSE_RANK, ROW_NUMBER |
| When to use | Summary reports | Annotate rows with context |

## Key Takeaways

- [ ] Execution order matters: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT. WHERE filters before aggregation; HAVING after.
- [ ] JOIN type determines which unmatched rows survive -- INNER drops, LEFT/RIGHT keeps one side, FULL keeps both.
- [ ] EXISTS short-circuits and is generally faster than IN for correlated existence checks.
- [ ] CTEs improve readability, allow multiple references, and support recursion -- prefer them over deeply nested subqueries.
- [ ] Window functions preserve row count while computing across partitions -- PARTITION BY groups without reducing.
- [ ] RANK vs DENSE_RANK vs ROW_NUMBER: gaps vs no gaps vs no ties. Use DENSE_RANK for "Nth highest" to handle ties correctly.
- [ ] Frame specs (ROWS/RANGE BETWEEN) control sliding window scope -- ROWS for physical count, RANGE for logical values.
- [ ] The TOP-N per group pattern (ROW_NUMBER + CTE/subquery + WHERE rn <= N) is one of the most common interview questions.
