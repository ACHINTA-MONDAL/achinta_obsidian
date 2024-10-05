---
tags:
  - PySpark
  - Interview
  - DataEngineering
  - Spark
data: 2024-07-03T00:24:00
---

All of the data analysis and manipulation tools I’ve worked with have window operations. Some are more flexible and capable than others but it is a must to be able to do calculations over a window.

What is a window in data analysis?

Window is a set of rows that are related in some ways. This relation can be of belonging to the same group or being in the n consecutive days. Once we generate the window with the required constraints, we can do calculations or aggregations over it.

In this article, we will go over 5 detailed examples to have a comprehensive understanding of window operations with PySpark. We’ll learn to create windows with partitions, customize these windows, and how to do calculations over them.

PySpark is a Python API for Spark, which is an analytics engine used for large-scale data processing.

# Data

I prepared a sample dataset with mock data for this article, which you can download from my [datasets](https://github.com/SonerYldrm/datasets/tree/main) repository. The dataset we’ll use in this article is called “sample_sales_pyspark.csv”.

Let’s start a spark session and create a DataFrame from this dataset.

```
`from pyspark.sql import SparkSession`  
`from pyspark.sql import Window, functions as F`  
  
`spark = SparkSession.builder.getOrCreate()`  
  
`data = spark.read.csv("sample_sales_pyspark.csv", header=True)`  
  
`data.show(15)`  
```
  
# output  
+----------+------------+----------+---------+---------+-----+  
|store_code|product_code|sales_date|sales_qty|sales_rev|price|  
+----------+------------+----------+---------+---------+-----+  
|        B1|       89912|2021-05-01|       14|    17654| 1261|  
|        B1|       89912|2021-05-02|       19|    24282| 1278|  
|        B1|       89912|2021-05-03|       15|    19305| 1287|  
|        B1|       89912|2021-05-04|       21|    28287| 1347|  
|        B1|       89912|2021-05-05|        4|     5404| 1351|  
|        B1|       89912|2021-05-06|        5|     6775| 1355|  
|        B1|       89912|2021-05-07|       10|    12420| 1242|  
|        B1|       89912|2021-05-08|       18|    22500| 1250|  
|        B1|       89912|2021-05-09|        5|     6555| 1311|  
|        B1|       89912|2021-05-10|        2|     2638| 1319|  
|        B1|       89912|2021-05-11|       15|    19575| 1305|  
|        B1|       89912|2021-05-12|       21|    28182| 1342|  
|        B1|       89912|2021-05-13|        7|     9268| 1324|  
|        B1|       89912|2021-05-14|       17|    22576| 1328|  
|        B1|       89912|2021-05-15|       16|    20320| 1270|  
+----------+------------+----------+---------+---------+-----+

## Example 1

We first create a window by partitioning and ordering columns. In our DataFrame, we have store, product, and sales information including quantity, price, revenue, and date. If we want to calculate cumulative sales of each product in each store separately, we define our window as follows:

```
window = Window.partitionBy("store_code", "product_code").orderBy("sales_date")

To calculate the cumulative sales, we simply apply the sum function over this window:

data = data.withColumn("total_sales", F.sum("sales_qty").over(window))

This line creates a new column called “total_sales”, which includes the cumulative sum of sales quantities calculated over the window we defined earlier.

Let’s check the first 30 rows for store “B1” to make sure cumulative values are calculated correctly:

data \  
.filter((F.col("store_code")=="B1")) \  
.select("store_code", "product_code", "sales_date", "sales_qty", "total_sales") \  
.show(30)  
```
  
# output    
+----------+------------+----------+---------+-----------+    
| store_code | product_code | sales_date | sales_qty | total_sales |
|:-----------|:-------------|:-----------|:----------|:------------|
     
+----------+------------+----------+---------+-----------+    
        B1       899122021-05-01       14       14.0    
        B1       899122021-05-02       19       33.0    
        B1       899122021-05-03       15       48.0    
        B1       899122021-05-04       21       69.0    
        B1       899122021-05-05        4       73.0    
        B1       899122021-05-06        5       78.0    
        B1       899122021-05-07       10       88.0    
        B1       899122021-05-08       18      106.0    
        B1       899122021-05-09        5      111.0    
        B1       899122021-05-10        2      113.0    
        B1       899122021-05-11       15      128.0    
        B1       899122021-05-12       21      149.0    
        B1       899122021-05-13        7      156.0    
        B1       899122021-05-14       17      173.0    
        B1       899122021-05-15       16      189.0    
        B1       899152021-05-01       20       20.0    
        B1       899152021-05-02        0       20.0    
        B1       899152021-05-03       10       30.0    
        B1       899152021-05-04       13       43.0    
        B1       899152021-05-05       21       64.0    
        B1       899152021-05-06        4       68.0    
        B1       899152021-05-07       20       88.0    
        B1       899152021-05-08       16      104.0    
        B1       899152021-05-09       21      125.0    
        B1       899152021-05-10        2      127.0    
        B1       899152021-05-11       15      142.0    
        B1       899152021-05-12       15      157.0    
        B1       899152021-05-13       14      171.0    
        B1       899152021-05-14        3      174.0    
        B1       899152021-05-15        1      175.0    
+----------+------------+----------+---------+-----------+

## Example 2

Once we create the window, we can calculate many different aggregations. For instance, if we apply the max function over the window defined earlier, the output will be the cumulative maximum price of products in the given store.

I’ll be writing the code to create the window so that you don’t have to search above for it.

```
# define the window  
window = Window.partitionBy("store_code", "product_code").orderBy("sales_date")  
  
# cumulative max price  
data = data.withColumn("max_price", F.max("price").over(window))  
  
# check the output  
data \  
.filter((F.col("store_code")=="B1")) \  
.select("store_code", "product_code", "sales_date", "price", "max_price") \  
.show(15)  
```
  
# output  
+----------+------------+----------+-----+---------+  
|store_code|product_code|sales_date|price|max_price|  
+----------+------------+----------+-----+---------+  
|        B1|       89912|2021-05-01| 1261|     1261|  
|        B1|       89912|2021-05-02| 1278|     1278|  
|        B1|       89912|2021-05-03| 1287|     1287|  
|        B1|       89912|2021-05-04| 1347|     1347|  
|        B1|       89912|2021-05-05| 1351|     1351|  
|        B1|       89912|2021-05-06| 1355|     1355|  
|        B1|       89912|2021-05-07| 1242|     1355|  
|        B1|       89912|2021-05-08| 1250|     1355|  
|        B1|       89912|2021-05-09| 1311|     1355|  
|        B1|       89912|2021-05-10| 1319|     1355|  
|        B1|       89912|2021-05-11| 1305|     1355|  
|        B1|       89912|2021-05-12| 1342|     1355|  
|        B1|       89912|2021-05-13| 1324|     1355|  
|        B1|       89912|2021-05-14| 1328|     1355|  
|        B1|       89912|2021-05-15| 1270|     1355|  
+----------+------------+----------+-----+---------+

The values in the “max_price” column increase or remain the same. In the 7th row, the price actually drops but the max price value remains the same because it shows the cumulative maximum value.

## Example 3

The lag and lead are some of the commonly used window functions. I use them quite frequently when analyzing time series data. They return the value that is offset before or after the current row.

- `lag("sales_qty", 1)` : 1 row before
- `lag("sales_qty", 2)` : 2 rows before
- `lead("sales_qty", 1)` : 1 row after
- `lead("sales_qty", 2)` : 2 row after

We can specify the offset by using negative values so `lag("sales_qty", 1)` is the same as `lead("sales_qty", -1)` . Both of them give us the value in the previous row. Let’s test it.

```
# define the window  
window = Window.partitionBy("store_code", "product_code").orderBy("sales_date")  
  
# previous day sales qty  
data = data.withColumn("prev_day_sales_lag", F.lag("sales_qty", 1).over(window))  
data = data.withColumn("prev_day_sales_lead", F.lead("sales_qty", -1).over(window))  
  
# check the output for a different product-store pair  
data \  
.filter((F.col("store_code")=="A1") & (F.col("product_code")=="95955")) \  
.select("sales_date", "sales_qty", "prev_day_sales_lag", "prev_day_sales_lead") \  
.show(15)  
```
  
# output  
+----------+---------+------------------+-------------------+  
|sales_date|sales_qty|prev_day_sales_lag|prev_day_sales_lead|  
+----------+---------+------------------+-------------------+  
|2021-05-01|       13|              NULL|               NULL|  
|2021-05-02|        3|                13|                 13|  
|2021-05-03|       22|                 3|                  3|  
|2021-05-04|       17|                22|                 22|  
|2021-05-05|       20|                17|                 17|  
|2021-05-06|       14|                20|                 20|  
|2021-05-07|       10|                14|                 14|  
|2021-05-08|       10|                10|                 10|  
|2021-05-09|       15|                10|                 10|  
|2021-05-10|       15|                15|                 15|  
|2021-05-11|        8|                15|                 15|  
|2021-05-12|        9|                 8|                  8|  
|2021-05-13|       13|                 9|                  9|  
|2021-05-14|        6|                13|                 13|  
|2021-05-15|       21|                 6|                  6|  
+----------+---------+------------------+-------------------+

The value in the first row for the previous day is `null` because they do not have a previous day.

## **Example 4**

Once we define a window based on a partition (e.g. store and product in our case), we can narrow it down by using the `rowsBetween` method.

Let’s say we want to calculate the average sales quantity of the last three days within the window. We can define this window as follows:

```
window = Window \  
.partitionBy("store_code", "product_code") \  
.orderBy("sales_date") \  
.rowsBetween(-3, -1)
```

The first parameter is the start and the second one is the end. We customized the window to cover the last three rows for each row. “-1” indicates the row before the current row and “-3” is the third row before the current row.

![](https://miro.medium.com/v2/resize:fit:1400/1*9iqkbLDK_MGA_upsaGv4hA.png)

Row indexes in window operations (image by author)

To calculate the average sales quantity in the last three days, we just need to apply the mean function over this window.

```
# define window  
window = Window \  
.partitionBy("store_code", "product_code") \  
.orderBy("sales_date") \  
.rowsBetween(-3, -1)  
  
# calculate mean  
data = data.withColumn("last_3_day_avg", F.mean("sales_qty").over(window))  
  
# display the data  
data \  
.filter((F.col("store_code")=="A1") & (F.col("product_code")=="95955")) \  
.select("sales_date", "sales_qty", "last_3_day_avg") \  
.show()  
```
  
# output  
+----------+---------+------------------+  
|sales_date|sales_qty|    last_3_day_avg|  
+----------+---------+------------------+  
|2021-05-01|       13|              NULL|  
|2021-05-02|        3|              13.0|  
|2021-05-03|       22|               8.0|  
|2021-05-04|       17|12.666666666666666|  
|2021-05-05|       20|              14.0|  
|2021-05-06|       14|19.666666666666668|  
|2021-05-07|       10|              17.0|  
|2021-05-08|       10|14.666666666666666|  
|2021-05-09|       15|11.333333333333334|  
|2021-05-10|       15|11.666666666666666|  
|2021-05-11|        8|13.333333333333334|  
|2021-05-12|        9|12.666666666666666|  
|2021-05-13|       13|10.666666666666666|  
|2021-05-14|        6|              10.0|  
|2021-05-15|       21| 9.333333333333334|  
+----------+---------+------------------+

For instance, for the fourth row (i.e. “2021–05–04”), the last 3 day average is 13.75, which is average of the values in the previous three rows (13, 3, and 22).

## Example 5

Consider a case where we need to calculate the cumulative average value of a column within the defined windows. For each row, the calculation should cover the rows between the first row of the window and the current row.

We can do so by defining the starting point with `unboundedPreceding` . Similarly, if we want to go until the end of the window, we can use the `unboundedFollowing` .

![](https://miro.medium.com/v2/resize:fit:1400/1*lIWAnbBhLiL1PnM95RFHfQ.png)

Unbounded preceding and following within a window (image by author)

After the window is defined, the rest is the same.

```
# define window  
window = Window \  
.partitionBy("store_code", "product_code") \  
.orderBy("sales_date") \  
.rowsBetween(Window.unboundedPreceding, -1)  
  
# calculate mean  
data = data.withColumn("cumulative_mean", F.mean("sales_qty").over(window))  
  
# display the data  
data \  
.filter((F.col("store_code")=="A1") & (F.col("product_code")=="95955")) \  
.select("sales_date", "sales_qty", "cumulative_mean") \  
.show()  
```
  
# output  
+----------+---------+------------------+  
|sales_date|sales_qty|   cumulative_mean|  
+----------+---------+------------------+  
|2021-05-01|       13|              NULL|  
|2021-05-02|        3|              13.0|  
|2021-05-03|       22|               8.0|  
|2021-05-04|       17|12.666666666666666|  
|2021-05-05|       20|             13.75|  
|2021-05-06|       14|              15.0|  
|2021-05-07|       10|14.833333333333334|  
|2021-05-08|       10|14.142857142857142|  
|2021-05-09|       15|            13.625|  
|2021-05-10|       15|13.777777777777779|  
|2021-05-11|        8|              13.9|  
|2021-05-12|        9|13.363636363636363|  
|2021-05-13|       13|              13.0|  
|2021-05-14|        6|              13.0|  
|2021-05-15|       21|              12.5|  
+----------+---------+------------------+

The cumulative mean column contains the average sales quantity of all the rows up to the current row (current row is exclusive). If we want the current row to be included in cumulative mean calculation, we can use define the window as follows:

```
window = Window \  
.partitionBy("store_code", "product_code") \  
.orderBy("sales_date") \  
.rowsBetween(Window.unboundedPreceding, Window.currentRow)
```

# Final words

Window operations are fundamental for data analysis. Especially when we work with time series data or creating machine learning models for predictive analytics on time series data, we use window operations for creating several different features.

Most data analysis and manipulation tools provide functions to simplify performing window operations. In this article, we learned how to do them with PySpark.

Thank you for reading. Please let me know if you have any feedback.