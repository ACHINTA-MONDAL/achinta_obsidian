---
tags:
  - SQL
  - DataEngineering
source: https://code.likeagirl.io/sql-essentials-group-by-vs-partition-by-explained-6e9b0a69bd02
data: 2024-07-03T00:48:00
---

When I first stepped into the world of data, I was a college student ==captivated== by the simplicity of SQL. The language seemed straightforward, almost like plain English. With commands like `SELECT`, what you see is what you get. There are no hidden meanings, no complicated syntax.

This initial attraction started to waver when I encountered my first challenge: `**WINDOW FUNCTIONS**`a (I have a good article about these right [**here**](https://medium.com/code-like-a-girl/sql-window-functions-the-ultimate-tool-for-data-enthusiasts-7a3ff6aac057) 😄) and their `**PARTITION BY**` clause. Suddenly, the clear skies of my SQL journey were clouded with confusion, and stormy thoughts of complex queries loomed ahead.

But don’t worry! It’s not as daunting as it seems. If you’re new to the data realm, there’s nothing to fear; with a bit of patience and practice, you’ll master these concepts too. In this article, I will guide you through the differences between `**PARTITION BY**` and `**GROUP BY**`, helping you understand their unique roles and use cases.

> — — Ready? Open your IDE and get started — —

# BY…Not the Same Thing?

Just because both clauses contain ‘**BY**’ doesn’t mean they do the same thing. It’s a good thing they don’t, as having dedicated functions for specific tasks makes SQL more powerful and versatile.

At first glance, the results of using these clauses might seem similar, but there are key differences; it’s quite important to know the difference between these 2 because you’ll know when to use one of them.

# How about having a 1-to-1 meeting with each?

## Let’s do a **GROUP**

The most important and awesome thing about a `**GROUP BY**` clause is that it’s pretty rebellious and wants to be used separately (this guy seems to be a bit of an introvert, right? Me too 😄)

Here is an example:

![](https://miro.medium.com/v2/resize:fit:1202/1*KySgKKdXCMRgVIm6oCKpLg.png)

Source: Made with 💓 by author

As you see, the `**GROUP BY**`clause is used independently and required by SQL when you’re using an aggregation function in your `SELECT` statement. It groups rows with the same values in specified columns into summary rows.

## Now let’s PARTITION things a bit

As an extrovert, `**PARTITION BY**` likes to be around other SQL-dedicated keywords and it is used within the `**OVER**` clause of a window function. It divides the result set into partitions to which the window function is applied.

Here is another example:

![](https://miro.medium.com/v2/resize:fit:1400/1*p3xfKncaIF7oTKWI1-KhgA.png)

Source: Made with 💓 by author

This clause divides the results into partitions or windows, on top of which we will apply the aggregation or function we established at the beginning. After you write this part, you also need to develop the field based on which you partition.

> An interesting article about Window Functions [**here**](https://medium.com/code-like-a-girl/sql-window-functions-the-ultimate-tool-for-data-enthusiasts-7a3ff6aac057) (click it, don’t be shy😁)

# Fine, but….still don’t see the differences

Hold your unicorn, my friend, and allow me to continue the journey:

1. **Point of action** — a `**GROUP BY**` clause likes to have control over everything, so when we use it in our query it restructures our entire result set by summarizing data based on group criteria. On the other hand, a `**PARTITION BY**` is quite understanding and it only adds additional columns based on the partitioning criteria, allowing for detailed analysis within each partition.
2. **Row reduction** — because the `**GROUP BY**` controls the structure of the result set, it returns fewer rows by grouping them with identical values in specified columns into summary rows. `**PARTITION BY**` doesn’t play with the number of rows; instead, it adds additional information (computed columns) based on the partition defined for each row.
3. Aggregation function available — `**GROUP BY**`allows the use of aggregate functions such as `SUM`, `AVG`, `MIN`, `MAX`, and `COUNT`. `PARTITION BY`, used within window functions, also supports these aggregate functions but additionally provides access to ranking and time-series functions, such as `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, and `LEAD`.
4. Overcomplicate things (query complexity) — using `**GROUP BY**` can overcomplicate queries because it requires all non-aggregated columns to be included in both the `SELECT` and `**GROUP BY**`clauses. This makes the query complex and less flexible, especially when you want to aggregate specific columns but still need other detailed data. In contrast, `PARTITION BY` allows you to include any column in the `SELECT` statement without including it in the partitioning criteria, offering more flexibility.
5. Performance — everything goes around performance and tips to optimize, right? Using `**GROUP BY**` can be resource-intensive because it consolidates rows into groups, especially with large datasets. In contrast, `**PARTITION BY**` with window functions run calculations across partitions without reducing the number of rows, preserving the dataset's granularity and adding the necessary calculations as new columns.

# It's time to see them in action, right?

The theory is good, but if you’re like me, you’ll learn more by doing. Let’s take an example and see both clauses in action.

Assuming we have the table below that contains information about transactions done by various customers:

![](https://miro.medium.com/v2/resize:fit:1400/1*lJ5ra9TywrVyEmEZefc0YA.png)

We need to report the situation and show the sum of transaction_amount for each customer. Simple, right?

```
SELECT  
    customer_id,  
    SUM(transaction_amount) AS total_amount  
FROM transactions  
GROUP BY customer_id;
```

and we have this result:

![](https://miro.medium.com/v2/resize:fit:526/1*MXOdLirLRpVb9atTAz3SRA.png)

**— — — Work done 😁 — — —**

But half an hour later, someone comes with a change request: now they need to see details such as customer_id, account_id, transaction_date, transaction_amount, transaction_type, and also the total amount per customer. How do you achieve it? 🤔

> Short advertisement for some time to think :)

Let’s see what we need: first of all, we need the total amount per customer, which means that we will use an aggregation function like `**SUM**`, right?

For some reason, we chose to modify the script and add the needed columns, so our query looks like this:

```
`SELECT`  
 `customer_id,`  
 `account_id,`   
 `transaction_date,`   
 `transaction_amount,`   
 `transaction_type,`  
 `SUM(transaction_amount) AS total_amount`  
`FROM transactions`  
`GROUP BY customer_id;`
```

You run it and see this result:

![](https://miro.medium.com/v2/resize:fit:2000/1*785nQTuzck_9cEoL-BttAA.png)

But how can it happen? Simple, we forgot that the `**GROUP BY**` clause has to contain all the non-aggregated columns from `SELECT` .

So, our query should be:

```
SELECT  
    customer_id,  
    account_id,   
    transaction_date,   
    transaction_amount,   
    transaction_type,  
    SUM(transaction_amount) AS total_amount  
FROM transactions  
GROUP BY   
    customer_id,  
    account_id,   
    transaction_date,   
    transaction_amount,   
    transaction_type;
```

The result:

![](https://miro.medium.com/v2/resize:fit:1400/1*4txkGaaiAcpagCEcZ20IfA.png)

Hmm…something seems wrong, right? How can the customer who has **customer_id = 101** have a different total amount for each of their records, when there should only be one?

![](https://miro.medium.com/v2/resize:fit:1400/1*H6pMofPBtCVN77b8Nt954w.png)

If we sum the values from **transaction_amount** by hand or run our very first `SELECT`we find out that the **total_amount** for **customer_id = 101** is **1750**, so something is wrong.

![](https://miro.medium.com/v2/resize:fit:526/1*MXOdLirLRpVb9atTAz3SRA.png)

## We have to change the tactics 🗺️

What if we make “windows” for each **customer_id**? Doing so, we isolate each customer and calculate the total amount without having all those columns written twice in the same `SELECT` statement.

```
SELECT  
    customer_id,  
    account_id,  
    transaction_date,  
    transaction_amount,  
    transaction_type,  
    SUM(transaction_amount) OVER(PARTITION BY customer_id) AS total_amount_per_customer  
FROM transactions;
```

The result? Look below👇

![](https://miro.medium.com/v2/resize:fit:1400/1*ZSvRA5rbbcB6MfVd0mljmQ.png)

If we do again the check from earlier we see that now the sums match, and also we have all the information we needed.

# When to use what?

It’s known that the window function, which contains the `**PARTITION BY**` clause is used for advanced analytics and allows us to perform advanced calculations across a set of table rows. The`**GROUP BY**` clause, on the other hand, is used to group rows with the same values in specified columns into summary rows (such as total sales by customer, and average salary per department). Below are some examples of scenarios and the recommended approach:

## Use `GROUP BY` when:

1. You need to summarize data by grouping rows that have the same values in specified columns and performing aggregate functions on them (e.g., total transaction amount per customer)

```
SELECT customer_id, SUM(transaction_amount) AS total_amount  
FROM transactions  
GROUP BY customer_id;
```

2. You need to count the number of rows in each group (e.g., number of transactions per account)

```
SELECT account_id, COUNT(*) AS transaction_count  
FROM transactions  
GROUP BY account_id;
```

3. You want to find duplicate values using the `HAVING` clause (e.g., find duplicate transactions)

```
SELECT transaction_id, count(*)  
FROM transactions  
GROUP BY transaction_id  
HAVING count(*) > 1
```

## **Use PARTITION BY when:**

1. You need to calculate running totals or cumulative sums for each row in a partition

```
SELECT   
transaction_id,  
customer_id,  
transaction_amount,   
SUM(transaction_amount) OVER(PARTITION BY customer_id ORDER BY transaction_date) AS running_total  
FROM transactions;
```

2. You want to assign ranks to rows within a partition based on a specific order (e.g., find the second salary)

```
SELECT   
transaction_id,   
customer_id,   
transaction_amount,   
RANK() OVER(PARTITION BY customer_id ORDER BY transaction_amount DESC) AS transaction_rank  
FROM transactions;

1. You need to access data from previous or following rows within the same partition

SELECT transaction_id, customer_id, transaction_amount,   
       LAG(transaction_amount, 1) OVER(PARTITION BY customer_id ORDER BY transaction_date) AS previous_transaction  
FROM transactions;
```

# Conclusion

Knowing when to use `**GROUP BY**`versus `**PARTITION BY**`is important for doing data analysis. Remember, `**GROUP BY**`is great for summarizing data and getting totals for different groups of rows, while `**PARTITION BY**`is awesome for doing more detailed calculations within specific sections of data. If you get good at using both (and I’m sure you are, or will be), you'll be able to do all kinds of data queries efficiently using SQL.

Below is the script with the data I used for the examples above:

```
CREATE TABLE [dbo].[transactions](  
 [transaction_id] [int] NOT NULL PRIMARY KEY,  
 [customer_id] [int] NULL,  
 [account_id] [int] NULL,  
 [transaction_date] [date] NULL,  
 [transaction_amount] [decimal](10, 2) NULL,  
 [transaction_type] [varchar](50) NULL  
)  
  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (1, 101, 1001, CAST(N'2024-01-01' AS Date), CAST(1000.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (2, 102, 1002, CAST(N'2024-01-02' AS Date), CAST(500.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (3, 101, 1001, CAST(N'2024-01-03' AS Date), CAST(-200.00 AS Decimal(10, 2)),'withdrawal')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (4, 103, 1003, CAST(N'2024-01-04' AS Date), CAST(700.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (5, 101, 1001, CAST(N'2024-01-05' AS Date), CAST(300.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (6, 102, 1002, CAST(N'2024-01-06' AS Date), CAST(-100.00 AS Decimal(10, 2)),'withdrawal')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (7, 104, 1004, CAST(N'2024-01-07' AS Date), CAST(1200.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (8, 104, 1004, CAST(N'2024-01-08' AS Date), CAST(-300.00 AS Decimal(10, 2)),'withdrawal')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (9, 101, 1001, CAST(N'2024-01-09' AS Date), CAST(400.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (10, 102, 1002, CAST(N'2024-01-10' AS Date), CAST(600.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (11, 103, 1003, CAST(N'2024-01-11' AS Date), CAST(-150.00 AS Decimal(10, 2)),'withdrawal')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (12, 101, 1001, CAST(N'2024-01-12' AS Date), CAST(250.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (13, 105, 1005, CAST(N'2024-01-13' AS Date), CAST(900.00 AS Decimal(10, 2)),'deposit')  
INSERT [dbo].[transactions] ([transaction_id], [customer_id], [account_id], [transaction_date], [transaction_amount], [transaction_type]) VALUES (14, 105, 1005, CAST(N'2024-01-14' AS Date), CAST(-400.00 AS Decimal(10, 2)),'withdrawal')
```

P.S: I used Microsoft SQL Server Management Studio as my IDE 😄

Until next time, happy querying! 🧑 💻💓