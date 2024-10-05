![](https://miro.medium.com/v2/resize:fit:1036/1*aPGUELKk6lC9hv2mZnlC7g.png)

As part of this article I have tried to cover various Spark and Databricks performance optimization strategies. This article is to provide the readers an overview of the various challenges we encounter typically in a production grade Bigdata workloads running on distributed compute. Some of the techniques mentioned can be used as a way to ensure proper engineering standards are enforced.

# Cluster level configuration and optimization

> **Choosing the right type of cluster** — Databricks primarily provides two (2) types of clusters.

- **_Interactive/All-Purpose_** cluster
- **_Job/Automated_** cluster.

Some considerations while choosing the cluster

- **_Interactive/All-Purpose_** clusters **_should_** only be used for **_ad hoc query execution and interactive notebook execution_** during the **_development_** and/or testing phases
- **_Job/Automated_** cluster are created by Databricks job scheduler creates when we run a job on a new job cluster. These cluster **_should_** mainly be used for **_running fast and robust automated tasks_**. They are created when we run a job on new Job Cluster and terminate the Cluster once the job ends
- **_SQL warehouses_** can be used to run SQL queries. A SQL warehouse is a compute resource that lets you run SQL commands on data objects within Databricks SQL. SQL warehouses are also available in **_serverless_** flavor, offering you access to an instant compute

> **Choosing the right cluster mode** — We have an option to select if we want our cluster to be in either of the two modes

- **Single Node** — Intended for jobs with small amounts of data or non-distributed workloads.
- **Multi Node** — Intended for larger jobs with distributed workloads.

> **Using larger clusters** — As an initial thought it may seem logical NOT to spend too much money on larger cluster but it’s actually not any more expensive to use a large cluster for a workload than it is to use a smaller one. **_It’s just faster_**.

The key is that you’re renting the cluster for the **_length of the workload_**. So, if you spin up that two worker cluster and it takes an hour, you’re paying for those workers for the full hour. However, if you spin up a four worker cluster and it takes only half an hour, the cost is actually the same!

> **Use Photon —** Photon is the next-generation engine on the Databricks Lakehouse Platform that provides **extremely fast query performance** at a low cost. Photon is **compatible** with Apache Spark APIs, works **out of the box** with existing Spark code, and provides significant performance benefits over the standard Databricks Runtime.

Advantages of Photon:
- Accelerated queries that process a significant amount of data (> 100GB) and include aggregations and joins
- Faster performance when data is accessed repeatedly from the Delta cache
- More robust scan/read performance on tables with many columns and many small files
- Faster Delta writing using UPDATE, DELETE, MERGE INTO, INSERT, and CREATE TABLE AS SELECT

It is recommended to use Photon for workloads with following characteristics:

- ETL pipelines consisting of Delta MERGE operations
- Writing large volumes of data to cloud storage (Delta/Parquet)
- Scans of large data sets, joins, aggregations and decimal computations
- Auto Loader to incrementally and efficiently process new data arriving in storage
- Interactive/ad hoc queries using SQL

> Use the **latest** LTS version of **Databricks Runtime** (DBR), as the latest Databricks Runtime is almost always faster than the one before it
> 
> For workloads using **single-node libraries** (e.g., Pandas), it is recommended to use **single-node data science clusters** as such libraries do **not** utilize the resources of a cluster in a **distributed** manner
> 
> Configure a **large driver node** (4–8 cores with 16–32GB should be sufficient in most cases) ONLY if

- Large data sets are being returned to driver program.
- Large broadcast joins (default is 10MB) are being performed.
- Many streams or concurrent jobs run on the same cluster.

> For workloads which involve **shuffle-heavy operations**, it is recommended to use **fewer larger nodes** sizes than to use many smaller nodes. This will help to **minimize network I/O** when transferring data among nodes.
> 
> **Automatic Termination —** To save cluster resources, you can terminate a cluster. You can manually terminate a cluster or configure the cluster to terminate automatically after a specified period of inactivity.

- During cluster creation, we have an option to specify an inactivity period in minutes after which we want the cluster to terminate.
- Default auto termination duration is **_120 minutes_**.
- If the difference between the current time and the last command run on the cluster is more than the inactivity period specified, Databricks automatically terminates that cluster.
- Clusters do not report activity resulting from the use of DStreams. This means that an auto-terminating cluster may be terminated while it is running DStreams. **_Turn off_** auto termination for clusters running **_DStreams_** or consider using Structured Streaming.
- When a cluster is terminated **_all state is lost_**, including all variables, temporary tables, caches, functions, objects, and so forth.

> **Garbage Collection** — Providing a large amount of RAM can help jobs perform more efficiently but can also lead to **delays** during garbage collection

- To minimize the impact of long garbage collection sweeps, **_avoid_** deploying clusters with large amounts of RAM configured for each instance. Having more RAM allocated to the executor will lead to longer garbage collection times. Instead, configure instances with smaller RAM sizes, and deploy more instances if you need more memory for your jobs.
- However for shuffle-heavy workloads, it would be beneficial to go fewer larger nodes (as mentioned above).

# Code level configuration and optimization

> **Spark’s lazy evaluation awareness**

- When we write Spark code (transformations), we are just building an execution plan. The code returns almost immediately when we run these functions.
- However when we try to write these results, it takes longer. This is due to lazy evaluation.
- Not being aware of this process will lead to performing same processing multiple times (**_extra computation_**).
- The solution to overcome this scenario is to save (**_caching_**) computed results we reuse.

> **Clean out/Re-assess older configurations**

- There might be some Spark configuration(s) which are being used from version to version. Although NOT all might be causing issues, there could be a few which might be downgrading the performance.
- Hence it is recommended to clean out or re-visit the Spark configurations used frequently.
- Example of some configurations which are deprecated from Spark 2.4 to Spark 3.0 are `shuffleBytesWritten`, `shuffleWriteTime` and `shuffleRecordsWritten`methods.

> **Caching data**

There are two types of caching mechanisms which can be leveraged to make workloads run faster

- **_Disk cache_** (formerly referred as **_Delta cache_**) — Accelerates data reads by creating copies of remote files in nodes’ local storage (SSD drives) using a fast intermediate data format. To explicitly enable, use `set spark.databricks.io.cache.enabled = true`
- **_Spark cache_** (using .cache() and .persist() methods) — Spark provides an optimization mechanism to cache the intermediate computation of a Spark DataFrame so they can be reused in subsequent actions. There are different modes (in the memory, in the disk, in the memory and the disk, with or without serialization) which allows where and how to store the cached data.
- Azure Databricks recommends using **_automatic disk caching_** for most operations.
- The data stored in the disk cache can be read and operated on faster than the data in the Spark cache. This is because the disk cache uses efficient decompression algorithms and outputs data in the optimal format for further processing using whole-stage code generation.
- Unlike the Spark cache, **_disk caching does not use system memory_**. Due to the high read speeds of modern SSDs, the disk cache can be fully disk-resident without a negative impact on its performance.
- Spark caching is **_only_** useful when more than one Spark action (for instance, count, saveAsTable, write, etc.) is being executed on the same DataFrame.

> **Compact data files with optimize on Delta Lake**

- Underneath the hood of a Delta table are Parquet files that store the data. It also contains a subdirectory named `__delta_log_` that stores the Delta transaction logs right next to the Parquet files. The size of these Parquet files is really crucial for query performance.
- When a table has too many underlying tiny files, **_read latency suffers_** as they require a lot of I/O overhead, which is computationally expensive. They also create large metadata transaction logs which cause planning time slowness.
- Delta Lake provides an `**OPTIMIZE**` command that lets users compact the small files into larger files, so their queries are not burdened by the small file overhead.
- Bin-packing optimization is _idempotent_, meaning that if it is run twice on the same dataset, the second run has no effect.

from delta.tables import *  
deltaTable = DeltaTable.forPath(spark, "/tmp/tableName")  
deltaTable.optimize().executeCompaction()

- **OPTIMIZE is** a costly operation because of increased resource usage. Databricks recommends that you start by running **OPTIMIZE on** a daily basis, and then adjust the frequency to balance cost and performance trade-offs.
- Databricks recommends Compute optimized instance types to run `**OPTIMIZE**`.

> **Auto optimize**

- Automatically compacts small files during individual writes to a Delta table, and by default, it tries to achieve a file size of 128MB. It comes with two features : **_Optimize Write_** and **Auto Compact.**
- **_Optimize Write —_** Optimize Write dynamically optimizes Apache Spark partition sizes based on the actual data, and attempts to write out 128MB files for each table partition. It’s done inside the same Spark job. **_Optimized writes require the shuffling of data_** according to the partitioning structure of the target table.
- **Auto Compact —** Following the completion of the Spark job, Auto Compact launches a new job to see if it can further compress files to attain a 128MB file size. Auto compaction can be enabled at the table or session level
- Always enable **_optimizeWrite_** table property if you are not already leveraging the manual OPTIMIZE (with or without ZORDER) command to get a decent file size.

> **File size tuning**

- When the default size targeted by **_Auto Optimize_** _(128MB) or_ `**OPTIMIZE**` (1GB) isn’t working, we have an option to set the target file size as per our requirement using **_delta.targetFileSize_** table property.
- If we want Databricks to automatically tune the file sizes based on workloads, we can use **_delta.tuneFileSizesForRewrite_** to True.

> **Data Shuffling**

Data shuffle occurs as a result of wide transformations such as joins, aggregations and window operations, among others. It is an expensive process since it sends data over the network between worker nodes. We may use a few optimization approaches to either eliminate or improve the efficiency and speed of shuffles.

- **_Broadcast hash join —_** To avoid data shuffling, broadcast one of the two tables or DataFrames (the smaller one) that are being joined together. The table is broadcast by the driver, which copies it to all worker nodes.
- When executing joins, Spark **_automatically_** broadcasts tables less than **_10MB_**; however, we may adjust this threshold to broadcast even larger tables using `spark.sql.autoBroadcastJoinThreshold = <size in bytes>`
- When we are sure that some of the tables in our query are small tables, we can tell Spark to broadcast them explicitly using **_hints_** `SELECT _/*+ BROADCAST(t) */_ * FROM <table-name> t`
- Spark 3.0 and above comes with **_AQE(Adaptive Query Execution)_**, which can also convert the sort-merge join into broadcast hash join (BHJ) when the runtime statistics of any join side is smaller than the adaptive broadcast hash join threshold, which is 30MB by default. We can also increase this threshold by changing the configuration `spark.databricks.adaptive.autoBroadcastJoinThreshold = <size in bytes>`
- Always explicitly broadcast smaller tables using hints or PySpark broadcast function.
- Never broadcast a table bigger than 1GB because broadcast happens via the driver and a 1GB+ table will either cause OOM on the driver
- **_Shuffle Hash Join (SHJ) over Sort-Merge Join (SMJ) —_** In most cases Spark chooses SMJ when it can’t broadcast tables. SMJ are the most expensive ones. SHJ has been found to be faster than SMJ as it does not require an extra sorting step like SMJ.
- We have an option to advise Spark to prefer SHJ over SMJ using `spark.sql.join.preferSortMergeJoin to False.`
- Please note the above setting will **_not guarantee_** Spark will always choose SHJ over SMJ. This setting will define our preference.
- **_Photon_** also replaces SMJ with SHJ to boost query performance.

> **Data Spilling**

The default setting for the number of **_Spark SQL shuffle partitions_** is 200 which isn’t always the best value. If the memory available to each core is **_insufficient_** to fit all of that data, some of it is spilled to disk. Spilling to disk is a costly operation as it involves data serialization, de-serialization, reading and writing to disk, etc. Spilling needs to be avoided at all costs and in doing so, we must tune the number of shuffle partitions. There are few ways to tune the number of Spark SQL shuffle partitions

- **_AQE auto-tuning_** — Spark AQE has a feature called `autoOptimizeShuffle` (AOS), which can automatically find the right number of shuffle partitions. `spark.sql.shuffle.partitions to auto`will enable auto-tuning.
- **_Manually fine tune —_** The below formula can be used to compute the right number of shuffle partitions

Total number of worker nodes in the cluster = T  
Total amount of data being shuffled in shuffle stage (in MBs) = B  
Recommended size of data to be processed per task (in MBs) = 128  
Multiplication factor M = ceiling(B / 128 / T)  
And the Number of Shuffle Partitions N = M * T

- If we are not using AOS nor manually fine-tuning, then as a rule of thumb set the number of Spark SQL shuffle partitions to **_twice or thrice_** the number of total worker cores.

spark.conf.set(“spark.sql.shuffle.partitions”, 2*<number of total worker cores in cluster>)  
Or  
spark.conf.set(“spark.sql.shuffle.partitions”, 2*sc.defaultParallelism)

- Because there may be multiple Spark SQL queries in a single notebook, fine-tuning the number of shuffle partitions for each query is a time-consuming task. So, general advice is to fine-tune it for the **_largest query_** with the greatest number for the total amount of data being shuffled for a shuffle stage and then set that value once for the entire notebook.

> **Data Skewness**

It is the situation in which only a few CPU cores end up processing a huge amount of data due to uneven data distribution.

- **_Identification of a Skew —_** If all the Spark tasks for the shuffle stage are finished and just one or two of them are hanging for a long time, that’s an indication of skew. The same can be viewed in Spark UI

![](https://miro.medium.com/v2/resize:fit:1400/1*dk2z3M9GCYUmTum9XFlaig.png)

Source — Databricks

- In the tasks summary metrics, if you see a huge difference between the min and max shuffle read size, that’s also an indication of data skewness.
- **_Skew Remediation — Filter skew values :_** If it’s possible to filter out the values around which there is a skew, then that will easily solve the issue. If we join using a column with lot of NULL values, filtering out the null values will resolve the issue.
- **_Skew Remediation — Skew Hints:_** In scenarios were we are aware of the exact table, the column and the values causing data skew, we can explicitly tell Spark using Skew Hints so that Spark can try to resolve it.

SELECT /*+ SKEW(’table’, ’column_name’, (value1, value2)) */ * FROM table

- **_Skew Remediation — AQE Skew Optimization:_** Spark’s 3.0+’s AQE can also dynamically solve the data skew. This is enabled by default. By default any partition that has at least 256MB of data and is at least 5 times bigger in size than the average partition size will be considered as a skewed partition by AQE.
- **_Skew Remediation — Salting:_** If none of the above mentioned options work, the last resort would be to do Salting. It’s a strategy for breaking a large skewed partition into smaller partitions by appending random integers as suffixes to skewed column values.

> **Data Skipping and Pruning**

The amount of data to process has a direct relationship with query performance. Therefore, it’s extremely important to read only the required data and skip all the unnecessary data.

- **_Delta data skipping —_** Delta data skipping automatically collects the stats (min, max, etc.) for the first 32 columns for each underlying Parquet file when you write data into a Delta table. Databricks takes advantage of this information (minimum and maximum values) at query time to skip unnecessary files in order to speed up the queries.
- Collecting statistics on long strings is an expensive operation. To avoid collecting statistics on long strings, you can configure the table property `delta.dataSkippingNumIndexedCols` to avoid columns containing long strings.
- **_Column Pruning —_** When reading a table, we generally choose all of the columns, but this is inefficient. To avoid scanning extraneous data, always inquire about what columns are truly part of the workload computation and are needed by downstream queries. Only those columns should be selected from the source database.
- **_Predicate Pushdown —_** This aims at pushing down the filtering to the “bare metal” — i.e., a data source engine. That is to increase the performance of queries since the filtering is performed at a **_very low level_** rather than dealing with the entire data set after it has been loaded to Spark’s memory. To leverage the predicate pushdown, all you need to do is add filters when reading data from source tables.
- Predicate pushdown is data source engine dependent. It works for data sources like Parquet, Delta, Cassandra, JDBC, etc., but it will not work for data sources like text, JSON, XML, etc.
- In situations involving join operations, **_apply filters before joins_**. As a rule of thumb, apply filter(s) right after the table read statement.
- **_Partition Pruning —_** The partition elimination technique allows optimizing performance when reading folders from the corresponding file system so that the desired files only in the specified partition can be read.
- This prevents keeping unnecessary data in memory with the aim of reducing disk I/O.
- To leverage partition pruning, we need to provide a filter on the column(s) being used as table partition(s).
- Ensure **_Dynamic Partition Pruning_** (DPP) and **_Dynamic File Pruning_** (DFP) is enabled. This configurations should be enabled by default.

> **Persist intermediate results**

In large pipelines spanning multiple SQL queries, there could be need to save intermediate results. This allows us to break a big query into small ones for more readability and maintainability. Few recommendations on how to persist them

- Create **_temp views_** instead of materialized Delta tables since temp views are lazily evaluated and are actually not materialized.
- Always turn an intermediate table into a temporary view if it is used only once in the same Spark job.
- If an intermediate table is being used more than once in the same Spark job, it makes sense to use Delta table rather than turning it into a temporary view since **_using a temporary view can cause Spark to execute the related query in part more than once_**.

> **Data Purging**

To remove stale data, Delta comes with a **_VACCUM_** feature to purge unused older data files. It removes all files from the table directory that are not managed by Delta, as well as data files that are no longer in the latest state of the transaction log for the table and are older than a retention threshold.

- The default **_threshold_** is 7 days.
- It is recommended that you set a retention interval to be at least 7 days because old snapshots and uncommitted files can still be in use by concurrent readers or writers to the table.
- If VACUUM cleans up active files, concurrent readers can fail, or, worse, tables can be **_corrupted_** when VACUUM deletes files that have not yet been committed.
- Run the VACUUM command on a daily/weekly basis depending on the frequency of transactions applied on the Delta tables.
- Never run this command **_as part of your job_** but run it as a separate job on a dedicated job cluster, usually **_clubbed_** with the OPTIMIZE command.