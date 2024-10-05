---
created: 2024-09-15T06:59:48+05:30
modified: 2024-09-15T07:00:16+05:30
---
In this article, we are going to deep dive into techniques of spark optimization in Databricks. This article is written based on the training sessions from the Databricks academy.

> **File formats:**

File formats that are supported in spark are CSV, Json, Parquet, Delta, ORC, AVRO etc.

1. **Row oriented storage: (CSV) —** This stores the data row wise as below,

![](https://miro.medium.com/v2/resize:fit:1400/0*0E4SMD_NDvmMT-a7)

**2. Columnar storage: (Parquet, Delta) —** This stores the data column wise as below,

![](https://miro.medium.com/v2/resize:fit:1400/0*xQbmNvBAxKjBamI5)

The columnar storage provides better performance over row oriented storage. For example, if the user wants to cherry pick 4 columns out of 1000, the row oriented storage will have to scan all the rows whereas columnar storage will only scan the 4 fields that are required.

> **Lazy Evaluation:**

Transformations in spark are evaluated lazily i.e Job won’t start until the action is triggered.

![](https://miro.medium.com/v2/resize:fit:1086/0*E-Kk_IbVUsvWxHUP)

In the above screenshot, you can see the schema is generated but the job has not started.

![](https://miro.medium.com/v2/resize:fit:1400/0*LgWnKwuVUPcmA1bQ)

In the above screenshot, you can see the actions which are methods that trigger the job. In this example the select, where and Orderby are lazy transformations.

The benefit of this feature is that spark can make optimized decisions after it has a chance to look at the DAG (**Directed Acyclic Graph**) entirely.

> T**ransformations:**

There are two transformations in Spark as below,

1. **Narrow transformation** — It starts with one memory partition and stays within the same memory partition after transformation.
2. **Wide transformation —** It starts with many partitions and ends up with new partitions after transformation. The transformation involves shuffling i.e redistributing or repartitioning the data so the data is grouped differently across partitions.

![](https://miro.medium.com/v2/resize:fit:1400/0*Hguh616G_Ecafzh2)

**Scenario 1 (Narrow Transformation):**

![](https://miro.medium.com/v2/resize:fit:968/0*pkRvRo5-9Zwm2_qs)

![](https://miro.medium.com/v2/resize:fit:1400/0*ZN_C3b_vfomJS2oa)

In the above scenario, there is only one stage because of no shuffling. So the worker nodes filter out the brown color rows out of 5 total rows and send the result back to the driver node.

**Scenario 2 (Wide Transformation):**

![](https://miro.medium.com/v2/resize:fit:1400/0*cynnvtXdKD9EwdCw)

Every time we have a shuffle, a new stage is generated and then new memory partitions are created to continue the processing. In the above example, there are 2 stages. In the first stage, the initial partitions are shuffled to summarize by color and count locally, whereas in the second stage, the partitions are shuffled again to summarize by color and count globally across all worker nodes. Eventually the global count will be sent to the driver and then to clients.

In the above example, the initial number of partitions were 4 and it turned into 200 shuffle partitions at the end.

_Based on the data size the number of shuffle partitions can be set using_ **_spark.sql.shuffle.partitons_**_._

**Shuffle Explanation:**

![](https://miro.medium.com/v2/resize:fit:1400/0*hUpBAFUMAoNZMUvP)

In the above example, the initial partitions are 6. In the first stage or shuffle, the local count is calculated within each memory partition, the results (568 B) are written to the disk in the worker nodes. In the second stage or shuffle, the global count is calculated across all the partitions from reading the shuffle 1 results and the results are sent back to the driver.

> **Optimization Techniques:**

## **_1. Catalyst Optimizer:_**

![](https://miro.medium.com/v2/resize:fit:1400/0*jtL5LS4nUx4gwoSw)

When we submit a query (either SQL or Python dataframe), the spark goes through the different plans as follows,

- **Unresolved logical plan** — Here the driver will confirm if the schema is correct or not ?
- **Analyzed logical plan** — If the schema is correct, the driver will add the respective data types for the columns.

For example, you have a join based on the dept_id column and in one side of the join the data type of dept_id is string and on the other side the data type is double. In this case, spark will automatically cast the string type into double to make it consistent inline with the data model.

- **Optimized logical plan** — In this plan, the driver optimizes the logical plan. For example, if filters can be moved before join, so that there are less rows to join.
- **Physical plan —** In this plan, the driver creates different types of physical plans that can be sent to the worker nodes for processing.

For example, you have an inner join in your query and spark determines the best join strategy based on the data frame sizes which will be effecient for the use case.

- **Selected physical plan** — The driver node will go through all the physical plans and select the best cost effective physical plan among all the plans.

To select the best plan based on cost based optimization (CBO), you need to turn on the below settings.

**spark.conf.set(“spark.sql.cbo.enabled”, “True”)**

For example, if we have 3 tables (1 small, 1 medium and 1 large), spark will decide the best joining strategy if you set the following setting. This setting will join the medium table with small table first and then finally join with large table which is a smart way to do joining)

spark.conf.set(“spark.sql.cbo.joinReorder.enabled”,”True”)

The final selected plan will be sent over to the driver nodes for executing it in terms of RDD ( Resilient Distributed Dataset which is nothing but an array of data ).

## **_2. Adaptive Query Execution:_**

In spark 3.2, AQE is enabled by default, whereas in spark 3.0 AQE is disabled and to be turned on.

spark.conf.set("spark.sql.adaptive.enabled", "False")  
spark.conf.set("spark.sql.adaptive.coalescePartitions", "False")

![](https://miro.medium.com/v2/resize:fit:1400/0*eYXPIpCRxIuAZo4j)

Once the RDD is created at the end of every stage, spark will look at the run time statistics i.e look at shuffle writes for wide transformation and see how big they are and come back to the catalyst optimizer to see if it can be fine tuned further i.e may be 10 shuffle partitions are enough.

**_A. Shuffle partition example without AQE:_**

spark.conf.set("spark.sql.adaptive.enabled", "False")  
spark.conf.set("spark.sql.adaptive.coalescePartitions", "False")  
from pyspark.sql.functions import col  
products_df = spark.read.table('`dev-sales-catalog`.bronze.products')  
count_df = products_df.groupBy(col('Category')).count().collect()

![](https://miro.medium.com/v2/resize:fit:1400/0*Kwplcyq8gUlYTmFA)

![](https://miro.medium.com/v2/resize:fit:1400/0*VYuVCDyUh-4vrGAz)

In this above example, we started with 1 initial memory partition and ended up with 200 shuffle partitions (default). For just 240 B, 200 shuffle partitions does not make any sense here.

**_B. Shuffle partition example with AQE:_**

spark.conf.set("spark.sql.adaptive.enabled", "True")  
spark.conf.set("spark.sql.adaptive.coalescePartitions", "True")  
from pyspark.sql.functions import col  
products_df = spark.read.table('`dev-sales-catalog`.bronze.products')  
count_df = products_df.groupBy(col('Category')).count().collect()

![](https://miro.medium.com/v2/resize:fit:1400/0*L4KH5NNjQIBI93p1)

![](https://miro.medium.com/v2/resize:fit:1400/0*xjk2U8CM-Tzf4ujj)

![](https://miro.medium.com/v2/resize:fit:1400/0*0y5Aj1jaIhMWEwJe)

With AQE turned on, we started with 1 initial memory partition and ended up with 1 shuffle partition because data size for shuffle is just 240 B.

## **_3. Predicate push down:_**

This feature in spark pushes down the filtering to the datasource, reducing the number of rows returned to the spark reader from the source database via SELECT/FILTER/WHERE. By default spark automatically does this and improves the performance.

CAST functions cannot be pushed down.

products_df = (spark.read  
.format("sqlserver")  
.option("host", "server.database.windows.net")  
.option("port", "1433") # optional, can use default port 1433 if omitted  
.option("user", "db")  
.option("password", "password")  
.option("database", "datamart")  
.option("dbtable", "products") # (if schemaName not provided, default to "dbo")  
.load()  
)  
from pyspark.sql.functions import col  
pushdown_df = products_df.filter(col('Category') == "Furniture")  
pushdown_df.explain()

![](https://miro.medium.com/v2/resize:fit:1400/0*XQi5-IJDamkhfqnp)

In this above example, you can see how the spark pushes down the filter to the sql server database by default.

## **4. Spark Caching and best practices**

Caching dataframe results is good , if the data frame will be used multiple times. Otherwise don’t cache.

products_df = spark.read.table(‘`dev-sales-catalog`.bronze.products’)

products_df.cache() #cache is a lazy transformation

products_df.count() #This puts the RDD into cache memory

products_df.unpersist() #This removed the RDD from cache

![](https://miro.medium.com/v2/resize:fit:1400/0*KqhDQ1nP2zNo9sa9)

## **5. Memory partitioning guidelines:**

**a.** Regardless of cluster size, the best practice for initial memory partitioning is between 128 MB and 1 GB.

Spark driver determines the number of initial memory partitions based on the number of cores in the cluster. More cores, more partitions.

In order to get the number of partitions, you can use the following method,

df.rdd.getNumPartitions()

![](https://miro.medium.com/v2/resize:fit:1400/0*j-5cdhsQ8letiZK-)

Access **SparkContext** through **SparkSession** to get the number of cores or slots.

Use the **defaultParallelism** attribute to get the number of cores in a cluster.

![](https://miro.medium.com/v2/resize:fit:1286/0*stQLkSCABV-MQGjT)

**b.** The default shuffle partition size is 200 MB but which can be changed manually using the settings below.

spark.conf.set("spark.sql.shuffle.partitions", "20000")

For example, if your largest shuffle stage input is 4TB and you want to have the partition size as 200 MB, then you can decide the shuffle partitions size as below,

4TB / 200MB = 20000 shuffle partition count

To get the default shuffle partition size in your cluster, you can run the following command.

spark.conf.get(“spark.sql.shuffle.partitions”)

![](https://miro.medium.com/v2/resize:fit:1400/0*eiuHOxV_4rq2hFXr)

**c. Repartitioning:**

AQE solves some partition issues after shuffling ( for example, AQE won’t create 200 shuffle partitions if the dataset is small ).

![](https://miro.medium.com/v2/resize:fit:1400/0*O_tKgRL9vgbrXJWp)

However if you want to play around with your own partitioning, then you can. We will cover that in this section. There are 2 methods to repartition a dataframe: **reparation** and **coalesce**

![](https://miro.medium.com/v2/resize:fit:1400/0*m3QD_shm9IebnpC2)

As Number of partitions goes up, size goes down

As Number of partitions goes down, size goes up.

**Repartition:**

Let’s look at the below dataframe which has 4 initial partitions.

![](https://miro.medium.com/v2/resize:fit:1400/0*qkcWyl0hhKBkO6om)

As we have 8 cores in the cluster, let’s repartition the dataframe to distribute the data across 8 cores equally to achieve maximum parallelism.

![](https://miro.medium.com/v2/resize:fit:1400/0*i8UH4ZawR15jiCLz)

**Coalesce:**

Let’s take the same dataframe with 4 partitions and apply coalesce as follows,

![](https://miro.medium.com/v2/resize:fit:1124/0*Gs9Wed6pkHZg29hv)

Coalesce will only decrease the partitions, so in the above example, the initial 4 partitions remain the same though the coalesce was applied with 8 partitions.

**6. Join strategies:**

We know that shuffling is an expensive operation which happens due to the wide transformation and the data has to be exchanged between the worker nodes. One of the wide transformations is join and we will see how the joins in spark can be optimized using a few join strategies available in spark.

**Shuffle Merge Join:**

This is the default join spark does use to join two dataframes / tables. The Sort-Merge Join algorithm is a two-step process that involves sorting and merging datasets to efficiently combine records with matching keys.

**Sorting:** This sorts the partitions based on the join key.

**Merge:** This merges the sorted partitions based on the join key.

This is efficient when you are processing two large tables.

**Shuffle Hash Join:**

Sort merge join is the default one that spark chooses for joining a large set of tables. However the default join strategy in spark is Shuffle Merge join over Hash join, so you need to turn off the shuffle merge join in order to use this.

spark.config.set(“spark.sql.join.preferSortMergeJoin”, “false”)

This is efficient when you are processing two large tables / dataframes and the data is uniformly distributed.

**Broadcast Join:**

This is efficient when one of the tables / dataframes is smaller in the joins. Broadcast join copies / broadcasts the data from small data frames across all worker nodes.

Spark automatically broadcasts the table with less than 10 MB, however this threshold can be changed with the following configuration. The below setting sets the table size as 30 MB for spark to consider for Broadcast join.

spark.conf.set(“spark.sql.autoBroadcastJoinThreshold”, “31457280” )

The other way is explicitly tell spark to use broadcast join using hints as below,

## **Conclusion:**

In this article, we looked into the performance optimization techniques in spark.