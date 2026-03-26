# SQL Database Design and Optimization

## Overview

Database design and query optimization are critical skills for MLE interviews. Interviewers expect you to choose appropriate data types, design normalized schemas, create effective indexes, and diagnose slow queries using EXPLAIN. These skills directly impact production ML systems where feature stores, training data pipelines, and serving infrastructure depend on well-designed, performant databases.

## Core Concepts

### Data Type Selection

Choosing the right data type affects storage, performance, and correctness. The guiding principle: **use the smallest type that accommodates your data**.

**Numeric types**:

| Type | Size | Range / Precision | Use Case |
|------|------|-------------------|----------|
| TINYINT | 1 byte | -128 to 127 (or 0-255 unsigned) | Flags, small enums |
| SMALLINT | 2 bytes | -32768 to 32767 | Counts under 32K |
| INT | 4 bytes | ~2.1 billion | Primary keys, general integers |
| BIGINT | 8 bytes | ~9.2 quintillion | Large IDs (Snowflake, etc.) |
| DECIMAL(p,s) | Variable | Exact precision | Money, financial calculations |
| FLOAT / DOUBLE | 4 / 8 bytes | Approximate (IEEE 754) | Scientific data, ML features |

**Key rule**: Use `DECIMAL` for money, never `FLOAT`. Floating-point arithmetic introduces rounding errors (e.g., `0.1 + 0.2 != 0.3`).

**String types**:

| Type | Max Size | Storage | When to Use |
|------|----------|---------|-------------|
| CHAR(n) | 255 bytes | Fixed-length, padded | Fixed-width codes (country, state) |
| VARCHAR(n) | 65,535 bytes | Variable-length + 1-2 byte prefix | Most strings (names, emails) |
| TEXT | 64 KB | Stored off-row | Medium text blocks |
| MEDIUMTEXT | 16 MB | Stored off-row | Documents, articles |
| LONGTEXT | 4 GB | Stored off-row | Very large content |

**Practical guidelines**:
- VARCHAR(50) for short strings, VARCHAR(255) for longer ones
- Prefer `VARCHAR` over `CHAR` -- variable-length saves space and search is faster on smaller data
- Chinese characters take 3 bytes each in UTF-8; allocate accordingly

**Types to avoid or use carefully**:
- **ENUM**: Hard to modify -- adding/removing values may require table rebuild. Use a lookup table instead.
- **TIMESTAMP**: Only stores dates up to 2038 (4 bytes). Use `DATETIME` for future dates.
- **BLOB**: Storing binary files in the database causes high memory usage and slow I/O. Store files in the filesystem; store the path in the database.

### JSON Column Type

MySQL 5.7+ supports native JSON columns for semi-structured data:

```sql
-- Creating JSON values
JSON_OBJECT('weight', 10, 'dimensions', JSON_ARRAY(1, 2, 3))

-- Extracting values (returns JSON-formatted output)
JSON_EXTRACT(properties, '$.weight')
-- Shorthand:
properties -> '$.weight'          -- returns "sony" (with quotes)
properties ->> '$.weight'         -- returns sony (without quotes)

-- Nested access
properties -> '$.weight.data.sub.time'
properties -> '$.weight[0]'       -- array index access

-- Updating partial attributes
UPDATE products
SET properties = JSON_SET(properties, '$.weight', 30, '$.age', 10)
WHERE id = 1;

-- Removing attributes
SET properties = JSON_REMOVE(properties, '$.weight');
```

**When to use JSON**: Flexible schemas, metadata, configuration. **When not to**: Data you need to filter, join, or index frequently -- use proper columns instead.

### Data Modeling Pipeline

Database design follows a structured progression:

1. **Understand requirements** -- business rules, access patterns, growth projections
2. **Conceptual model** -- entities and relationships (ER diagram), no implementation details
3. **Logical model** -- tables, columns, data types, relationships, normalization
4. **Physical model** -- indexes, partitions, storage engine selection, denormalization decisions

**Forward engineering**: Convert model to SQL DDL scripts (`CREATE TABLE ...`).
**Reverse engineering**: Generate model diagrams from existing tables.
**Synchronize model**: Update tables by modifying the model and syncing changes.

### Foreign Key Constraints

Foreign keys enforce referential integrity. The critical design decision is the **update/delete strategy**:

| Strategy | ON UPDATE | ON DELETE | Use When |
|----------|-----------|-----------|----------|
| RESTRICT | Block update | Block delete | Parent must not change (reference data) |
| CASCADE | Propagate change | Delete children | Children are owned by parent (order items) |
| SET NULL | Set FK to NULL | Set FK to NULL | Relationship is optional (manager reassignment) |
| NO ACTION | Block (deferred) | Block (deferred) | Same as RESTRICT in MySQL |

**Best practice**: Avoid `SET NULL` for identifying relationships -- it creates orphan records with no traceable parent.

### Normalization

Normalization eliminates redundancy and update anomalies. Each normal form builds on the previous.

**First Normal Form (1NF)** -- Atomic values, no repeating groups:
- Each cell contains a single value (not a list or set)
- No duplicate columns for the same type of data
- **Fix**: Extract multi-valued attributes into a separate table with a foreign key

**Second Normal Form (2NF)** -- No partial dependencies (requires 1NF):
- Every non-key attribute depends on the **entire** composite key, not just part of it
- Only relevant when the primary key has multiple columns
- **Fix**: Split the table so each non-key attribute depends on the full key

**Third Normal Form (3NF)** -- No transitive dependencies (requires 2NF):
- Non-key attributes depend only on the primary key, not on other non-key attributes
- **Example violation**: `{student_id} -> {dept_id} -> {dept_name}` -- dept_name transitively depends on student_id
- **Fix**: Move transitively dependent attributes to their own table

**When to denormalize**: Read-heavy workloads where JOIN cost exceeds the cost of data duplication. Common in OLAP, data warehouses, and feature stores. Always denormalize deliberately, not by accident.

### Table Relationship Design

| Relationship | Implementation |
|-------------|---------------|
| One-to-Many (1:N) | Foreign key in the "many" table |
| Many-to-Many (N:N) | Junction table decomposing into two 1:N relationships |
| One-to-One (1:1) | Same primary key in both tables, or FK with UNIQUE constraint |

### Storage Engine Selection

```sql
SHOW ENGINES;                            -- List available engines
ALTER TABLE customers ENGINE = InnoDB;   -- Change engine
```

**InnoDB** (default, recommended): ACID-compliant, row-level locking, foreign keys, crash recovery. Use for most OLTP workloads.

**MyISAM** (legacy): Table-level locking, no transactions, faster full-table scans. Only for read-only analytics tables.

### Index Fundamentals

Indexes accelerate reads but add overhead to writes and storage. They are typically implemented as B-trees, stored in memory when possible.

```sql
-- Create an index
CREATE INDEX idx_state ON customers (state);

-- View indexes on a table
SHOW INDEXES IN customers;

-- Update index statistics
ANALYZE TABLE customers;
```

**When to index**:
- Columns frequently used in WHERE, JOIN, ORDER BY
- Columns with high cardinality (many distinct values)
- Foreign key columns

**When NOT to index**:
- Small tables (full scan is fast enough)
- Columns with low cardinality (e.g., boolean, gender)
- Columns rarely used in queries
- Tables with heavy write workload and few reads

### Index Types

**Prefix index** -- Index only the first N characters of a string column:

```sql
CREATE INDEX idx_name ON customers (last_name(20));

-- Determine optimal prefix length: find N where distinct count plateaus
SELECT COUNT(DISTINCT LEFT(last_name, 5)) AS n5,
       COUNT(DISTINCT LEFT(last_name, 10)) AS n10,
       COUNT(DISTINCT LEFT(last_name, 20)) AS n20,
       COUNT(DISTINCT last_name) AS full_col
FROM customers;
```

**Full-text index** -- For natural language search (similar to search engine inverted indexes):

```sql
CREATE FULLTEXT INDEX idx_ft ON posts (title, body);

-- Natural language search
SELECT * FROM posts WHERE MATCH(title, body) AGAINST ('react redux');

-- Boolean mode: + required, - excluded
SELECT * FROM posts
WHERE MATCH(title, body) AGAINST ('+react -redux +form' IN BOOLEAN MODE);
```

**Composite (multi-column) index** -- Index on multiple columns:

```sql
CREATE INDEX idx_composite ON customers (last_name, state, points);
```

Rules for composite indexes:
- MySQL supports up to 16 columns per composite index (4-6 is practical)
- **Leftmost prefix rule**: The index is usable only when the query includes the leftmost column(s)
- Order columns by: (1) equality conditions first, (2) range conditions, (3) ORDER BY columns
- A composite index on (a, b, c) covers queries on (a), (a, b), and (a, b, c) -- but NOT (b, c) alone

### Covering Index (Index-Only Scan)

When all columns needed by a query are contained in the index, MySQL can satisfy the query from the index alone without reading the table data. This eliminates random I/O to the table and dramatically improves performance.

### Duplicate and Redundant Indexes

- **Duplicate**: Creating the same index twice on (a, b, c) -- pure waste
- **Redundant**: Index on (a) when index on (a, b) already exists -- the composite covers single-column queries on (a)

Periodically audit indexes and remove duplicates/redundancies.

### EXPLAIN Output Interpretation

```sql
EXPLAIN SELECT * FROM customers WHERE state = 'CA';
```

Key EXPLAIN columns:

| Column | What It Tells You | Good Values | Bad Values |
|--------|-------------------|-------------|------------|
| type | Access method | const, ref, range | ALL (full table scan) |
| key | Index actually used | Named index | NULL (no index used) |
| rows | Estimated rows scanned | Small number | Large number |
| Extra | Additional info | Using index (covering) | Using filesort, Using temporary |

**Access type ranking** (best to worst):
```
const > eq_ref > ref > range > index > ALL
```

- **const**: Primary key or unique index lookup (1 row)
- **eq_ref**: Join using primary/unique key (1 row per join)
- **ref**: Non-unique index lookup (few rows)
- **range**: Index range scan (BETWEEN, <, >, IN)
- **index**: Full index scan (reads entire index, better than ALL)
- **ALL**: Full table scan (worst -- reads every row)

### Query Execution Order

Understanding execution order is essential for optimization:

```
Syntax:    SELECT -> FROM -> JOIN -> WHERE -> GROUP BY -> HAVING -> ORDER BY -> LIMIT
Execution: FROM -> ON -> JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> DISTINCT -> ORDER BY -> LIMIT
```

**Optimization implication**: Filter as early as possible (WHERE) rather than late (HAVING), since WHERE operates before grouping/aggregation.

## Index Invalidation Scenarios

These common patterns prevent MySQL from using an index, causing full table scans:

### 1. Function or Expression on Indexed Column

```sql
-- BAD: Index on score is NOT used
SELECT * FROM t WHERE score / 10 = 9;

-- GOOD: Move computation to the right side
SELECT * FROM t WHERE score = 90;
```

### 2. Implicit Type Conversion

```sql
-- BAD: col_varchar is VARCHAR but compared with integer
SELECT * FROM t WHERE col_varchar = 123;
-- MySQL converts every row's col_varchar to int -> full scan

-- GOOD: Match the type
SELECT * FROM t WHERE col_varchar = '123';
```

### 3. Leading Wildcard in LIKE

```sql
-- BAD: Full table scan
SELECT * FROM t WHERE name LIKE '%John';

-- GOOD: Prefix match uses index
SELECT * FROM t WHERE name LIKE 'John%';

-- Alternatives for leading wildcard:
-- 1. INSTR(name, 'John') > 0
-- 2. Full-text index with MATCH AGAINST
-- 3. ElasticSearch for large-scale text search
```

### 4. OR Conditions

```sql
-- BAD: May cause full table scan
SELECT * FROM t WHERE id = 1 OR id = 3;

-- GOOD: Use UNION
SELECT * FROM t WHERE id = 1
UNION ALL
SELECT * FROM t WHERE id = 3;

-- Or use IN for simple value lists
SELECT * FROM t WHERE id IN (1, 3);
```

### 5. IS NULL Comparison

```sql
-- BAD: Index may not be used
SELECT * FROM t WHERE score IS NULL;

-- GOOD: Use a default value and compare against it
SELECT * FROM t WHERE score = 0;  -- with DEFAULT 0 on the column
```

### 6. != or <> Operator

When an indexed column uses `!=` or `<>`, the optimizer often falls back to a full table scan. If inequality filtering is required, consider indexing other columns in the query instead.

### 7. Leftmost Prefix Violation

```sql
-- Composite index on (key_part1, key_part2, key_part3)

-- BAD: Skips key_part1 -> index NOT used
SELECT * FROM t WHERE key_part2 = 1 AND key_part3 = 2;

-- GOOD: Include leftmost column
SELECT * FROM t WHERE key_part1 = 'x' AND key_part2 = 1 AND key_part3 = 2;
```

### 8. ORDER BY Without WHERE

```sql
-- BAD: Index on age is NOT used for sorting
SELECT * FROM t ORDER BY age;

-- GOOD: Include the column in WHERE to activate index
SELECT * FROM t WHERE age > 0 ORDER BY age;
```

This applies to all sorting-related clauses: GROUP BY, UNION, DISTINCT.

## Optimization Techniques

### SELECT Optimization

1. **Never use SELECT \***: Disables covering index optimization, increases bandwidth, I/O, memory, and CPU usage. Always specify needed columns.

2. **Avoid non-deterministic functions in replication**: `NOW()`, `RAND()`, `SYSDATE()` produce different values on master vs slave. They also bypass the query cache.

3. **Place smaller tables first in FROM**: MySQL scans tables left-to-right. Put the smaller table first to reduce the Cartesian product size.

4. **Use table aliases**: Reduces parse time and prevents ambiguity in multi-table queries.

5. **Filter order in WHERE**: Place the most selective condition first (MySQL parses left-to-right, top-to-bottom).

6. **Avoid ORDER BY RAND()**: Generates a random number per row then sorts all rows. Use application-level random key generation instead.

### DML Optimization

**Batch INSERT**:

```sql
-- BAD: One connection + parse per row
INSERT INTO t VALUES (1, 2);
INSERT INTO t VALUES (1, 3);
INSERT INTO t VALUES (1, 4);

-- GOOD: Single parse, single connection, less network I/O
INSERT INTO t VALUES (1, 2), (1, 3), (1, 4);
```

**COMMIT strategically**: Committing transactions releases undo blocks, redo log space, and locks. Frequent commits in batch operations reduce lock contention.

**Avoid re-querying updated data**: Use variables to capture values during UPDATE instead of issuing a separate SELECT.

```sql
-- Instead of UPDATE then SELECT:
UPDATE t1 SET time = NOW() WHERE col1 = 1 AND @now := NOW();
SELECT @now;
```

### GROUP BY Optimization

MySQL implicitly sorts GROUP BY results. If sort order is not needed, suppress it:

```sql
-- Avoid unnecessary sort
SELECT col1, col2, COUNT(*)
FROM t
GROUP BY col1, col2
ORDER BY NULL;  -- disables implicit sorting
```

### JOIN vs Subquery

Prefer JOIN over subquery when possible. Subqueries create temporary virtual tables in memory; JOINs can use indexes directly.

```sql
-- Subquery (may create temp table)
SELECT * FROM A WHERE id IN (SELECT id FROM B);

-- JOIN (uses index on B.id)
SELECT A.* FROM A JOIN B ON A.id = B.id;
```

**Exception**: EXISTS with correlated subqueries can be efficient when the subquery is highly selective.

### UNION Optimization

`UNION` implicitly applies `DISTINCT`, requiring a sort. Use `UNION ALL` when duplicates are acceptable to avoid the dedup cost.

### TRUNCATE vs DELETE

| Aspect | DELETE | TRUNCATE |
|--------|--------|----------|
| Logging | Row-by-row in undo/binlog | Minimal (DDL operation) |
| Speed | Slow for large tables | Very fast |
| WHERE clause | Supported | Not supported (all rows) |
| Auto-increment | Preserved | Reset to 0 |
| Transaction | Can be rolled back | Cannot be rolled back |
| Triggers | Fires DELETE triggers | Does not fire triggers |

Use TRUNCATE only when you want to remove ALL rows and do not need rollback capability.

### Pagination Optimization

**Problem**: `LIMIT offset, count` with large offsets is slow because MySQL reads and discards `offset` rows.

```sql
-- SLOW for large offsets: scans 100,000 + 15 rows
SELECT * FROM t
WHERE thread_id = 10000 AND deleted = 0
ORDER BY gmt_create ASC
LIMIT 100000, 15;
```

**Solution 1: Deferred JOIN (index-only pagination)**:

```sql
-- FAST: Only scans index for offset, then fetches 15 rows by PK
SELECT t.*
FROM (
    SELECT id FROM t
    WHERE thread_id = 10000 AND deleted = 0
    ORDER BY gmt_create ASC
    LIMIT 100000, 15
) a
JOIN t ON a.id = t.id;
```

Requires: primary key `id` + covering index on `(thread_id, deleted, gmt_create)`.

**Solution 2: Keyset pagination (seek method)**:

```sql
-- Remember the last seen value, no offset needed
SELECT * FROM t
WHERE thread_id = 10000 AND deleted = 0
  AND gmt_create > '2024-01-15 10:30:00'
ORDER BY gmt_create ASC
LIMIT 15;
```

Keyset pagination is O(1) regardless of page depth but does not support jumping to arbitrary pages.

### Query Hints

When the optimizer makes poor index choices, override with hints:

```sql
-- Suggest an index
SELECT * FROM t USE INDEX (idx_name) WHERE ...;

-- Exclude an index
SELECT * FROM t IGNORE INDEX (idx_name) WHERE ...;

-- Force an index (stronger than USE)
SELECT * FROM t FORCE INDEX (idx_name) WHERE ...;
```

Use `ANALYZE TABLE` first to update statistics. Only use FORCE INDEX when you have evidence the optimizer is wrong.

## Implementation

### Diagnosing a Slow Query

Step-by-step approach for the interview question "How would you optimize a slow query?":

```sql
-- Step 1: Run EXPLAIN to see the execution plan
EXPLAIN SELECT c.name, o.total
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE c.state = 'CA' AND o.total > 100
ORDER BY o.created_at DESC
LIMIT 10;

-- Step 2: Check for problems in EXPLAIN output
-- Look for: type=ALL, key=NULL, Using filesort, Using temporary

-- Step 3: Create appropriate indexes
CREATE INDEX idx_customers_state ON customers (state);
CREATE INDEX idx_orders_cust_total ON orders (customer_id, total, created_at);

-- Step 4: Rewrite query if needed
-- - Replace SELECT * with specific columns
-- - Ensure WHERE conditions use indexed columns without functions
-- - Check for implicit type conversions

-- Step 5: Re-run EXPLAIN and compare rows scanned, access type
```

### Designing a Normalized Schema

```sql
-- Example: Course enrollment system

-- Students table (entity)
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- Courses table (entity -- satisfies 2NF by separating from enrollment)
CREATE TABLE courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON UPDATE CASCADE
);

-- Departments table (satisfies 3NF -- no transitive dependency)
CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(100) NOT NULL
);

-- Enrollments (junction table for N:N relationship)
CREATE TABLE enrollments (
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| EXPLAIN analysis | "This query is slow" | Check type, key, rows, Extra columns systematically |
| Composite index design | Multi-column WHERE/ORDER | Put equality columns first, then range, then sort columns |
| Covering index | Frequent lightweight queries | Include all SELECT columns in index to avoid table lookup |
| Deferred JOIN pagination | Deep pagination on large tables | Paginate on index-only subquery, then JOIN for full rows |
| Keyset pagination | Infinite scroll, cursor APIs | Use WHERE on last-seen value instead of OFFSET |
| Denormalization | Read-heavy OLAP workloads | Trade write complexity for read performance |
| Prefix index | Long string columns | Find optimal prefix length via COUNT(DISTINCT LEFT(...)) |

### Common Interview Questions

- [ ] "How would you optimize a slow query?" -- EXPLAIN, check access type, add index, rewrite query, re-check
- [ ] "Explain database normalization with examples" -- 1NF (atomic), 2NF (no partial deps), 3NF (no transitive deps)
- [ ] "When would you denormalize?" -- Read-heavy workloads, data warehouses, caching layers, when JOIN cost exceeds duplication cost
- [ ] "What makes a good index?" -- High cardinality, frequently queried, selective, covers the query
- [ ] "EXPLAIN this query plan" -- Walk through type/key/rows/Extra, identify bottleneck
- [ ] "Why is this query not using the index?" -- Check for function on column, implicit type conversion, leading wildcard, leftmost prefix violation
- [ ] "DECIMAL vs FLOAT for financial data?" -- DECIMAL for exact precision, FLOAT for speed with acceptable rounding
- [ ] "How do you handle pagination at scale?" -- Keyset pagination or deferred JOIN; avoid large OFFSET

## Comparisons

### Index Types

| Aspect | B-Tree Index | Full-Text Index | Prefix Index | Composite Index |
|--------|-------------|-----------------|--------------|-----------------|
| Use case | Equality, range | Natural language search | Long strings | Multi-column queries |
| Supports ORDER BY | Yes | No | Limited | Yes (with leftmost prefix) |
| Storage cost | Moderate | High (inverted index) | Low | Moderate to high |
| Maintenance cost | Per-write overhead | High (token processing) | Low | Per-write overhead |

### Normalization vs Denormalization

| Aspect | Normalized (3NF) | Denormalized |
|--------|------------------|--------------|
| Write performance | Fast (no duplication) | Slower (update multiple copies) |
| Read performance | Slower (requires JOINs) | Faster (pre-joined data) |
| Storage | Minimal | Higher (duplicated data) |
| Data integrity | Strong (single source of truth) | Risk of inconsistency |
| Schema changes | Easier (localized) | Harder (ripple effects) |
| Best for | OLTP, transactional systems | OLAP, data warehouses, caches |

### Pagination Methods

| Aspect | OFFSET/LIMIT | Deferred JOIN | Keyset (Seek) |
|--------|-------------|---------------|---------------|
| Deep page performance | O(offset) -- degrades | O(offset on index) -- better | O(1) -- constant |
| Jump to arbitrary page | Yes | Yes | No |
| Implementation complexity | Simple | Moderate | Moderate |
| Requires | Nothing special | Covering index + PK | Unique sortable column |

## Key Takeaways

- [ ] Use DECIMAL for money (not FLOAT) -- floating-point errors are unacceptable in financial calculations
- [ ] Normalize to 3NF by default; denormalize deliberately for read-heavy workloads with documented trade-offs
- [ ] Composite index column order matters: equality columns first, then range, then ORDER BY
- [ ] EXPLAIN is your primary diagnostic tool -- focus on type (access method), key (index used), and rows (scan estimate)
- [ ] Six common index killers: functions on columns, implicit type conversion, leading wildcards, OR, NULL comparisons, leftmost prefix violations
- [ ] For deep pagination, use keyset (seek) pagination or deferred JOIN -- never rely on large OFFSET
- [ ] Prefer JOIN over subquery for performance; prefer UNION ALL over UNION when dedup is unnecessary
- [ ] TRUNCATE is DDL (fast, no rollback); DELETE is DML (slow, logged, rollback-safe) -- choose based on recovery needs
