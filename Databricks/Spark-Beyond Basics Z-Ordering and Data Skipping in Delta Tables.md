---
modified: 2024-08-11T01:33:46+05:30
---
If spark could speak, it would say things about Data Engineers that would put them in depression and give them anxiety for a foreseeable future! 🫢😬

I mean, These Data Engineers (including me 👀) assumes spark can fix the issues which they couldn't (coz they can't code…. I am talking about me🙈).

But Spark DOES fix it! One of such issues it fixes is of executing a query 10–12 times faster by applying Z-Ordering.

# Z-Ordering

Say you have one delta table which is queried “n” number of times in a day. And these queries filter on one specific column every time it runs. 🤔

Spark already uses [_Adaptive Query Optimization (AQE)_](https://towardsdev.com/spark-beyond-basics-adaptive-query-execution-012a47a4c013) to get appropriate number of partitions and to perform [_predicate pushdown_](https://towardsdev.com/spark-beyond-basics-adaptive-query-execution-012a47a4c013) to fasten up these queries.

But Spark is still not at its peak here! We need to help spark unleash its powers😤! It's known to us that we’ll be applying filter on a specific column, so what we can do is, we can enable Z-Ordering on that column 🤨

Enabling Z-Ordering on the column will:

1. _Repartition_ the table on the specified column
2. _Sort within the partition_ on the specified column

Let's take an example for better understanding: 🤓

## Scenario

Consider a delta table with some not-so-interesting columns and “Name” (interesting one!) column. We already have 4 _optimized_ partitions after Spark’s AQE.

![](https://miro.medium.com/v2/resize:fit:1264/1*NTjN7IZFjdxioKqVGTI2Sw.png)

querying on the partitioned delta table

- As soon as we run the mentioned query on the table, _Spark will look at the min-max values in delta transaction logs and ask_, does this file contain the data I need. 🧐
- Hence, spark is going to check the first 3 partitions but won't check the last partition since min _Name is_ “Dan” and thus this partition won't include “Brad”. **_This is called Data Skipping_** 😲

> Why will it check first 3 partitions: coz for all three, min Names (Bob, Andy, Brad) is ≤ Brad

![](https://miro.medium.com/v2/resize:fit:1318/1*w43IyOph8dBUfg6YhLFCwA.png)

Irregular data skipping

- But this kind of **_Data Skipping_** can be termed as **_irregular_** data skipping, since the partitions are not _Optimized_ for ‘Name’ column
- Let's apply Z-Ordering on ‘Name’ column and check what happens! ✨

![](https://miro.medium.com/v2/resize:fit:1290/1*fO2yKp6JqsZCK7wlROjspQ.png)

repartition and sort within partitions performed on ‘Name’ column

![](https://miro.medium.com/v2/resize:fit:638/1*X8xEUM5V0QATJLin_4IbKg.png)

- Now, if you run the above query, Spark will check only the first partition, thus acing the **_Data Skipping._** 😉

> Note: The column you choose to Z-Order by should have high cardinality, i.e., a large number of distinct values

## Syntax of Z-Ordering:

To Z-order data, you specify the columns to order on in the `ZORDER BY` clause.

> Z-Ordering will be applied by running OPTIMIZE with ZORDER BY clause

OPTIMIZE table_name ZORDER BY column_name

## Benefits of Z-Ordering:

1. Z-ordering can lead to significant speedups, potentially reducing query execution times from minutes to seconds🤯
2. Appropriate number of partitions, which creates balance in the cores of the spark worker nodes where tasks are executed⚖️

## Challenges with Z-Ordering:

1. Choosing partitioning columns is a complicated process 🥴
2. Z-Ordering jobs are expensive and require longer write times ⏱️
3. Concurrent writes aren’t possible with tables with Z-Ordering enabled

When you weigh the benefits and challenges, you will surely be in dilemma _to use or not to use._ 😵‍💫

Databricks felt this dilemma too, and they came up with a state-of-the-art solution: **_Liquid Clustering_** 🥂

I’ll be covering Liquid Clustering in my next blog, so watch out!

If you liked the blog, please clap 👏 to make this reach to all the Data Engineers.

Thanks for reading! 😁