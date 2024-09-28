---
created: 2024-09-02T02:26:47+05:30
modified: 2024-09-14T17:12:56+05:30
---
> Do not define the parameters of my universe by the limits on your own. — Anonymous

A **sunset** is beautiful and daunting. Whenever I see it, I realize I am limited only by perspective and vision. Beyond those limitations is a **world** of **infinite** possibilities. In that world, **I am free**. I am free to imagine, to hope and to dream. I am free to **chart a course** toward unknown destinations of **imagination** and **creativity**. I am neither constrained by **age**, background, gender or **race**. My mind is the canvas and ideas the raw materials. **So**, it is with **SQL Window** functions. **Only** limited perspective and vision hinders their **creative** usage.

To push pass **self-imposed** limitations, I encourage imagination and experimentation. In this **advanced** tutorial, I crack the door to deeper learning by adding the `CASE Expression` into SQL Window functions. As an advanced topic, I cover the basics to the extent they inform learning. If you need a primer on SQL Window functions, I suggest an earlier article I wrote, **SQL Window Functions, A Love Hate Relationship**.

[

## SQL Window Functions

### A Love Hate Relationship

towardsdatascience.com
](https://towardsdatascience.com/sql-window-functions-78593bcabf4?source=post_page-----64c26bd643fd--------------------------------)

## The Basics

We can use the `CASE Expression` in **any** statement or clause that allows a valid expression. For example, you can use `CASE Expression` in statements such as `SELECT`, `UPDATE`, `DELETE`, `SET` and in clauses such as `PARTITION BY`, `ORDER BY`, `WHERE` and `HAVING`. **Harnessing** the power of the `CASE Expression` statement and SQL Window function starts with the **syntax**. We can enclose the `CASE Expression` in the `Window_Function()` as shown in the image below.

![](https://miro.medium.com/v2/resize:fit:2000/1*JIElZPXCTfqwMY5L9L8_tQ.jpeg)

Syntax, Window Function & CASE Expression

When working with window functions, it is important to keep in mind **processing order matters**. The `OVER()` clause executes first, followed by `PARTITION BY`, `ORDER BY` and `Window_Function()`. The `ORDER BY` clause determines how the `Window_Function` applies calculations, `AVG(), SUM(), MAX()`or `CASE Expression` logic, to the rows in the `PARTITION BY` clause. The `CASE Expression` goes through the conditions and returns a **single value** when the first condition evaluates to true. So, once a condition is true, it will stop reading and return the result. If no conditions are true, it returns the value in the ELSE clause.

## Getting Started

It is important to know there are **different** implementations of SQL Window functions across database platforms such as Oracle, SQL Lite, SQL Server, MySQL, Postgres, and Redshift. The number and support for the `CASE Expression` in the `Window_Function()` function may vary across each platform. The **table** below shows if `Window_Function(),` `PARTITION BY` or `ORDER BY` clause supports the `CASE Expression` syntax. The table **does** **not** include all the SQL Window functions. However, I’ve listed some of the more common ones you are likely to encounter.

![](https://miro.medium.com/v2/resize:fit:2000/1*XfRZfRCWkUMtyotqRX1xXg.jpeg)

SQL Window Functions, T-SQL

While the table is a great reference, a quicker and easier way to determine if your database platform supports the case statement is to use `case when 1 = 1 then 1 else 0 end` in the `Window_Function` as shown in the image below.

![](https://miro.medium.com/v2/resize:fit:2000/1*YtLOdCAYL4ZrIyBRZdYSHw.jpeg)

Window Function, CASE Expression Test

When testing, I suggest testing each part of the syntax separately to determine if the SQL platform supports the function. If the query executes, the window function supports the `CASE Expression`.

While it is possible to use the `CASE Expression` in the `PARTITION BY` clause, I’ve **rarely** used it on projects. So, I don’t cover it in this tutorial. With that said, I’ll quickly add, don’t let that limit you from **exploring** it. You may find multiple instances where it’s useful. So, continue to be **creative** and **push** the limits of the possible. It the rest of the tutorial, we’ll look at how to use `Case Expression` with the `Window_Function()` and `ORDER BY` clause.

## Our Data

The data in our fictitious example comprises store revenue data in each state. The aim is to add three additional metrics, Adjusted Revenue, New Store Revenue and State Revenue using the `SUM()` window function along with the `CASE Expression`. We want to measure the impact of **no sales tax** or **new store opening** has on revenue for a company in a state. We can write **individual queries** to get the answer, but the nested `CASE Expression` is the most efficient. By the end of the tutorial, you will see how to **add metrics** with minor modifications to the `CASE Expression`.

With that said, lets dig into the code **shown below** in the SQL Server text editor. For **Adjusted Revenue,** when the `CASE Expression` executes and the record does not have sales tax, `Sales_Tax = NO`, the revenue is 95% of Projected Revenue.

![](https://miro.medium.com/v2/resize:fit:2000/1*zdOXDGaaNdEAocALj_XEfQ.jpeg)

With **New Store Revenue,** when the `CASE Expression` executes, and the record is a new store, `New_Store = 'YES'`, we calculate the revenue. Otherwise, the case statement returns a value of zero. With **State Revenue,** when the `CASE Expression` executes and the record does not have sales tax, `Sales_Tax = NO`, the revenue is 95% of Projected Revenue.

I could have continued to create additional metrics by making modifications to the `CASE Expression`. Last, the `Case Support` column uses `case when 1 = 1 then 1 else 0 end` to test if the `Max()` window function supports `CASE Expression` in SQL Server. Successful query execution means the `CASE Expression` is supported. **Don’t worry** about the value that populates `Case Support` column. The goal is just to make sure the query statement runs.

## ORDER BY: Our Scenario

The `ORDER BY` clause is a hidden **super power** in the `Window_Function()`. Her common usage belies her genuine beauty and elegance. Understanding and **mastering** her finer points will open the door to a new level of problem solving. Let’s look at an example to help explain what I mean.

The data in our scenario comprises the **estimated value** of deals of computer sales for a computer manufacturer. Each year in December, the division sales leader attempts to increase revenue by closing deals with an `OPEN_DATE`. **Based on experience**, she knows business deals with an `OPEN_DATE` date in **June** are **more valuable** than in other months. So, she sends a request to her data team for a list that **prioritizes June** deals at the top in each state. When she receives the list, she will distribute it to the regional sales manager in each state. The data analyst completes the request using the SQL logic shown below.

![](https://miro.medium.com/v2/resize:fit:2000/1*D-jmKbeJxCR6qZCNJwpB5g.jpeg)

**Explanation**: The data analyst uses the `**DENSE_RANK()**` function to create the priority list in each region. The `OVER()` clause creates the execution space. The `PARTITION BY` clause groups the `State` data into distinct groups. The `CASE Expression` returns a `1` if the record has a date between `6/1/2017` and `6/30/2017` and the `ELSE` returns a `0` outside of those dates. The `DESC` sorts the `CASE` expression result set in a descending order from 1 to 0. The `DESC` sorts the `Estimated_Value` for highest to the lowest. The result is a `priority` column with deals with an `OPEN_DATE` in June ranked at the top in estimated value based on the `ORDER BY` sort.

## A Key: Take Your Time

One key to effectively using a `Window_Function()` and `CASE Expression` is **taking the time** to know your dataset. That means exporting sample data to a spreadsheet. You can make notes or **model** the expected results when the `Window_Function()` executes the `CASE Expression`. The combination of a `Window_Function()` and `CASE Expression` offer a lot of **power**, so it’s easy to crash and burn if mishandled. You can **spend hours** trying to make sense of results that would have been spotted in a spreadsheet. Mostly when I’ve made **mistakes**, it’s because I **skipped** this step.

I have done some amazing projects using `Case Expressions` and `Window_Functions()`. This tutorial scratches the surface of a world of infinite creative coding possibilities. I hope the information helps you to explore and creatively solve complex problems. Continue to grow and push the limits of what’s possible with `CASE Expressions` and `Window_Functions()`.

**_Shared Inspiration_**_: With each key stroke and lesson shared, I am reminded of my 8th grade English and Typing teacher Ms. Reeves at Vanguard Jr. High. She helped an awkward little boy believe he could be more than he thought possible with a generous portion of discipline, kindness and love. Keep sharing and inspiring others to be greater than they could have imagined._


