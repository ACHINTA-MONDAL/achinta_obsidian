---
source: https://medium.com/@abhinav.prakash1804/databricks-a-comprehensive-optimization-guide-7b803289c5a7
tags:
  - Databricks
  - DataEngineering
---


![](https://miro.medium.com/v2/resize:fit:1400/1*TcFtP2rKCAlq-1n5bAQ53A.jpeg)

I have been using Databricks for ETL workloads for 4 years now. In these 4 years, I have come across optimization techniques in bits and pieces, but a comprehensive list was hard to come by.

In this article, I have tried to collect all the various optimization techniques that a Databricks Data Engineer / ETL Developer must know. This is a summarized list and for detailed explanation of any one topic/technique, please refer to Databricks documentation.

What will we cover?

- What is Delta Lake and what lies under the hood
- Data Shuffling — Why It Happens and How to Control It?
- Data Spilling — Why It Happens and How to Get Rid of It?
- Data Skewness — Identification and Remediation
- Data Skipping and Pruning
- Data Caching — Leverage Caching to Speed Up the Workloads
- Intermediate Results — When to Persist Them
- Delta Merge — Let’s Speed It Up
- Data Purging — What to Do With Stale Data
- Databricks Cluster Configuration and Tuning

**Delta Lake**

- Open format storage layer
- Enables building a Lakehouse architecture
- Compute engines including Spark, PrestoDB, Flink, Trino, and Hive
- APIs for Python, SQL, Scala, Java, Rust, and Ruby
- [Many benefits over other open formats like Parquet, Avro, ORC (Link to other article)](https://medium.com/@abhinav.prakash1804/delta-lake-vs-parquet-86e1e926f446)

**What lies under the hood in delta lake?**

- Delta table are Parquet files that store the data.
- Also a subdirectory named _delta_log that stores the Delta transaction logs
- Size of these Parquet files are crucial for query performance. **_Best to have a file size between 16 MB and 1GB._**
- Tiny files problem:
- If using Unity Catalog, DBx will automatically optimize file sizes in the background as a part of it’s auto-tuning capability.
- If not, manually compact files using one of the below methods:
- _1. Optimize & Z-order:_
- > Compacts the files to get a file size of up to 1GB. Even better to combine the OPTIMIZE command with the ZORDER, which physically sorts or co-locates data by chosen column(s).
- > Always choose high cardinality columns for Z-ordering. Columns that are most frequently used in filter clauses or as join keys in the downstream queries.
- > Never use more than 4 columns since too many columns will degrade Z-ordering effectiveness.
- > OPTIMIZE (with or without ZORDER) should be done on a regular basis to maintain a good file layout and query performance.
- > Use a separate dedicated cluster to run these notebooks.

OPTIMIZE table_name [WHERE predicate] [ZORDER BY (col_name1 [, …] ) ]

- 2. Auto optimize:
- > Automatically compacts small files during individual writes to a Delta table.  
    — It tries to achieve a file size of 128MB.  
    — This will add some time to the data write, but the queries will then run faster.

# Table properties  
delta.autoOptimize.optimizeWrite = true   
delta.autoOptimize.autoCompact = true  
  
# In Spark session conf for all new tables  
set spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite = true  
set spark.databricks.delta.properties.defaults.autoOptimize.autoCompact = true

- 3. Partitioning
- > Helps Spark to skip a lot of unnecessary data during scan time.
- > It can speed up your queries if you provide the partition column(s) as:  
    — filters or join on partition column(s)  
    — aggregate on partition column(s)  
    — merge on partition column(s)  
    — Do not partition tables under 1TB in size.  
    — Choose a low cardinality column. Eg. Date
- 4. File size tuning
- > You can set the target file size by using delta.targetFileSize table property and then Auto-optimize and Optimize will binpack to achieve the specified size instead.

# Table properties  
delta.targetFileSize = 134217728

- > We can also let Databricks automatically tune the file sizes based on workloads. Eg. If you do a lot of merges on the Delta table, then the files will automatically be tuned to much smaller sizes than 1GB to accelerate the merge operation.

# Table properties  
delta.tuneFileSizesForRewrite = true

**Shuffling**

- Occures as a result of wide transformations such as joins, aggregations and window operations
- The optimization approaches mentioned below can either eliminate or improve the efficiency and speed of shuffles:
- 1. Broadcast hash join
- > To avoid data shuffle, Broadcast the smaller tables or DataFrames.
- > When executing joins, Spark automatically broadcasts tables less than 10MB; however, we may adjust this threshold to broadcast even larger tables, as demonstrated below:

set spark.sql.autoBroadcastJoinThreshold = <size in bytes>  
set spark.sql.autoBroadcastJoinThreshold = 209715200;  
set spark.databricks.adaptive.autoBroadcastJoinThreshold = 209715200;  
# Since Spark 3.0,   
# Adaptive Query Execution (AEQ) allows   
# any table below this threshold size   
# automatically get converted from sort-merge join   
# into broadcast hash join (BHJ) ]

- > Explicitly tell Spark to broadcast small tables.

SELECT /*+ BROADCAST(t) */ * FROM <table-name> t

- > If you’re running a driver with a lot of memory (32GB+), you can safely raise the broadcast thresholds to something like 200MB
- > Never broadcast a table bigger than 1GB
- > Note that the size of a table in disk and memory will never be the same. Spark might broadcast them based on their size in the disk — however, they might actually be really big (even more than 8GB) in memory after the decompression. In such scenarios:  
    — disable broadcasting by setting **_spark.sql.autoBroadcastJoinThreshold_** to -1  
    — explicit broadcast only really small tables using hints  
    OR  
    — Set spark.sql.autoBroadcastJoinThreshold to smaller values like 100MB or 50MB  
    — The Spark driver can only collect up to 1GB of data in memory at any given time, and anything more than that will trigger an error in the driver, causing the job to fail.  
    — We can increase this limit if we want to broadcast larger tables. Setting this parameter to 8GB for a driver with >32GB memory seems to work fine

spark.driver.maxResultSize 8g  
  
# Because this is a driver setting,   
# it cannot be altered once the cluster is launched.   
# It should be set under the cluster's   
# advanced options as a Spark config

- 2. broadcast hash join (BHJ) > Shuffle hash join > sort-merge join
- > If Spark can’t broadcast tables, it chooses sort-merge join (SMJ) which is not very efficient.
- > We can set our preference to use Shuffle-hash join (SHJ) over sort-merge join (SMJ)

set spark.sql.join.preferSortMergeJoin = false

- 3. Leverage cost-based optimizer (CBO)
- > By default, Spark SQL can use a Cost-based optimizer (CBO) to improve query plans.
- > Especially useful for queries with multiple joins.
- > For CBO to work, it is critical to collect table and column statistics and keep them up to date.
- > Based on the stats, CBO chooses the most economical join strategy.
- > Run the following SQL command on the tables to compute stats. The stats will be stored in the Hive metastore.

ANALYZE TABLE table_name COMPUTE STATISTICS FROM COLUMNS col1, col2, …;

- > Join reorder:  
    — CBO also uses the stats calculated by ANALYZE TABLE command to find the optimal order in which the tables should be joined (joining smaller tables first improves performance)  
    — Join reorder only works on INNER and CROSS joins  
    — To use this feature, set the following configuration:

set spark.sql.cbo.enabled = true  
set spark.sql.cbo.joinReorder.enabled = true  
set spark.sql.statistics.histogram.enabled = true

— CostBasedJoinReorder requires statistics on the table row count at the very least and its accuracy is improved by having statistics on the columns that are being used as join keys and filters.

ANALYZE TABLE table_name COMPUTE STATISTICS FOR COLUMNS col1, col2..;

— The maximum number of tables in a query for which this joinReorder can be used (default is 12)

set spark.sql.cbo.joinReorder.dp.threshold = <number of tables>

**Data Spilling**

- Default setting for the number of Spark SQL shuffle partitions (i.e., the number of CPU cores used to perform wide transformations such as joins, aggregations and so on) is 200
- As a result, each Spark task (or CPU core) is given a large amount of data to process, and if the memory available to each core is insufficient to fit all of that data, some of it is spilled to disk
- Spilling to disk is a costly operation, as it involves data serialization, de-serialization, reading and writing to disk, etc. and needs to be avoided at all costs
- We can do this by tuning the number of shuffle partitions. Two ways to do this:
- 1. AQE auto-tuning  
    — Spark AQE has a feature called autoOptimizeShuffle (AOS), which can automatically find the right number of shuffle partitions.  
    — Set the following configuration to enable auto-tuning:  
    set spark.sql.shuffle.partitions=auto
- 2. Manually fine-tune  
    (i) Find the total amount of shuffled data. How?  
    — Run the Spark query once (Join, Aggregation, other wide transformation query)  
    — Use the Spark UI to retrieve this value. Above the DAG, you will see ‘Shuffle read size’, which is the total size of shuffle and ‘Spill (Disk)’ which is the Data Spill.  
    — After tuning the number of shuffle partitions, each task should approximately be processing 128MB to 200MB of data. (We can see this value in the summary metrics for the shuffle stage in Spark UI)

Formula to compute the right number of shuffle partitions:

> Total number of total worker cores in cluster = T  
> Total amount of data being shuffled in shuffle stage (in megabytes) = B  
> Optimal size of data to be processed per task (in megabytes) = 128  
> Hence the multiplication factor (M): M = ceiling(B / 128 / T)  
> And the number of shuffle partitions (N): N = M x T  
>   
> If we are neither using auto-tune (AOS) nor manually fine-tuning the shuffle partitions, then as a rule of thumb set this to twice, or better thrice, the number of total worker CPU cores.

**Data Skewness**

- Situation where only a few CPU cores wind up processing a huge amount of data due to uneven data distribution.  
    — Eg. When we join or aggregate using the columns(s) around which data is not uniformly distributed
- Identify Data Skew:  
    1. If all the Spark tasks for the shuffle stage are finished and just one or two of them are hanging for a long time, that’s an indication of skew. Can be identified from the Spark UI  
    2. Just count the number of rows while grouping by join or aggregation columns. If there is an enormous disparity between the row counts, then it’s a definite skew.

SELECT COLUMN_NAME,  
COUNT(*)  
FROM TABLE  
GROUP BY COLUMN_NAME

Handle Data Skew:  
1. Filter skew values: Check if we are joining using a column with a lot of null values (This will lead to data skew). In this scenario, filtering out the null values will resolve the issue.  
2. Skew hints: If we are able to identify the table, the column, and the values that are causing data skew, then we can explicitly tell Spark about it using skew hints so that Spark can try to resolve it for us.

SELECT /*+ SKEW('table', 'column_name', (value1, value2)) */ * FROM table

3. AQE skew optimization: AEQ dynamically solves the data skew. It is enabled by default.

**Data Skipping and Pruning**

- It’s extremely important to read only the required data and skip all the unnecessary data.
- Data skipping and pruning techniques:  
    1. Delta data skipping  
    — Delta data skipping automatically collects the stats (min, max, etc.) for the first 32 columns for each underlying Parquet file when you write data into a Delta table.  
    — Databricks takes advantage of this information (minimum and maximum values) at query time to skip unnecessary files in order to speed up the queries.  
    — Configure the table property delta.dataSkippingNumIndexedCols to avoid collecting statistics on long strings  
      
    2. Predicate pushdown  
    — Aim at pushing down the filtering to the “bare metal” — i.e., a data source engine.  
    — It increase the performance of queries since the filtering is performed at a very low level rather than dealing with the entire data set after it has been loaded to Spark’s memory.

-- SQL  
SELECT col1, col2 .. coln FROM table WHERE col1 = <value>

# Pyspark  
dataframe = spark.table("table").select("col1", "col2", … "coln").filter(col("col1") = <value>)

— When performing join operations, apply filters before joins. As a rule of thumb, apply filter(s) right after the table read statement  
  
3. Partition pruning  
— It allows optimizing performance when reading folders from the corresponding file system so that the desired files only in the specified partition can be read.  
— Prevents keeping unnecessary data in memory with the aim of reducing disk I/O.  
— Provide a filter on the column(s) being used as table partition(s).

-- SQL  
SELECT * FROM table WHERE partition_col = <value>

# PySpark  
dataframe = spark.table("table").filter(col("partition_col") = <value>)

— When performing join operations, apply partition filter(s) before joins.

**Data Caching**

- There are two types of caching that can help speed up workloads:  
    1. Disk caching(Earlier called Delta cache)  
    — It accelerates data reads by creating copies of remote files in nodes’ local storage (SSD drives) using a fast intermediate data format.  
    — To enable: set spark.databricks.io.cache.enabled = true  
      
    2. Spark cache  
    — Using cache() and persist() methods, Spark allows users to to cache the intermediate computation of a Spark DataFrame so they can be reused in subsequent actions.  
    — We can also cache a table using the CACHE TABLE command.  
    — Only useful when more than one Spark action (for instance, count, saveAsTable, write, etc.) is being executed on the same DataFrame  
    — Any compute-heavy workload (with wide transformations like joins and aggregations) would benefit from Delta caching, especially when reading from the same tables over and over. Always use Delta cache-enabled instances for those workloads.

**Persist Intermediate Results**

- If a intermediate table is being used just once, turn the data into TEMP VIEW instead of Delta tables

-- SQL  
CREATE OR REPLACE TEMP VIEW <view-name> AS SELECT col1, col2,… FROM <table-name>

- If an intermediate table is being used more than once in the same Spark job, eave it as a Delta table.  
      
    **Delta Merge**
- Use it to upsert into a Delta Lake table using merge
- Use the WHEN NOT MATCHED BY SOURCE clause to UPDATE or DELETE records in the target table that do not have corresponding records in the source table.
- Recommended to add an optional conditional clause to avoid fully rewriting the target table

MERGE INTO target  
USING source  
ON source.key = target.key  
WHEN MATCHED THEN  
UPDATE SET target.lastSeen = source.timestamp  
WHEN NOT MATCHED THEN  
INSERT (key, lastSeen, status) VALUES (source.key, source.timestamp, 'active')  
WHEN NOT MATCHED BY SOURCE AND target.lastSeen >= (current_date() - INTERVAL '5' DAY) THEN  
UPDATE SET target.status = 'inactive'

— The following query shows using this pattern to:  
1. select 5 days of records from the source  
2. update matching records in the target  
3. insert new records from the source to the target  
4. delete all unmatched records from the past 5 days in the target.

MERGE INTO target AS t  
USING (SELECT * FROM source WHERE created_at >= (current_date() - INTERVAL '5' DAY)) AS s  
ON t.key = s.key  
WHEN MATCHED THEN UPDATE SET *  
WHEN NOT MATCHED THEN INSERT *  
WHEN NOT MATCHED BY SOURCE AND created_at >= (current_date() - INTERVAL '5' DAY) THEN DELETE

- Merge optimizations:  
    1. For the merge-heavy tables, it’s recommended to have smaller file sizes from 16MB to 64MB. (If the target table contains large files (for example, 500MB-1GB), many of those files will be returned to the drive during step 1 of the merge operation, as the larger the file, the greater the chance of finding at least one matching row.)  
    2. Provide the partition filters in the ON clause of the merge operation to discard the irrelevant partitions.  
    3. Provide Z-order columns (if any) as filters in the ON clause of the merge operation to discard the irrelevant files.  
    4. Explicitly broadcasting the source(updates) DataFrame to be merged in the target Delta table if the source DataFrame is small enough (<= 200MB)

**Data Purging**

- Use VACUUM feature to purge unused older data files.
- It removes all files from the table directory that are not managed by Delta, as well as data files that are no longer in the latest state of the transaction log for the table and are older than a retention threshold.
- The default threshold is 7 days.

VACUUM table_name

- Step to change the default retention threshold

deltaTable.deletedFileRetentionDuration = "interval 15 days"

- VACUUM will skip all directories that begin with an underscore (_), which includes the _delta_log
- Set deltaTable.deletedFileRetentionDuration and delta.logRetentionDuration to the same value to have the same retention for data and transaction history
- Run the VACUUM command on a weekly basis
- Never run this command as part of your job but run it as a separate job on a dedicated job cluster, usually clubbed with the OPTIMIZE command
- VACUUM is not a very intensive operation (the main task is file listing, which is done in parallel on the workers; the actual file deletion is handled by the driver), so a small autoscaling cluster of 1 to 4 workers is sufficient

**Databricks Cluster Configuration And Tuning**

- All-purpose clusters vs. automated clusters (job clusters)
- All-purpose clusters  
    — for ad hoc query execution and interactive notebook execution
- automated clusters (job clusters)  
    — For an automated job / workflows
- Autoscaling  
    — Always use autoscaling when running ad hoc queries, interactive notebook execution, and developing/testing pipelines using interactive clusters with minimum workers set to 1.  
    — In production, don’t set the minimum instances to 1. Set a higher value.
- Instance types based on workloads
- > Memory Optimized :  
    — For ML workloads  
    — Where a lot of shuffle and spills are involved  
    — When Spark caching is needed
- > Compute Optimized  
    — Structured Streaming jobs  
    — ELT with full scan and no data reuse  
    — To run OPTIMIZE and Z-order Delta commands
- > Storage Optimized  
    — To leverage Delta caching  
    — ML and DL workloads with data caching  
    — For ad hoc and interactive data analysis
- > GPU Optimized  
    — ML and DL workloads with an exceptionally high memory requirement
- > General Purpose  
    — Used in absence of specific requirements  
    — To run VACUUM Delta command
- Number of workers  
    — requires some trials and iterations  
    — Start with 2–4 workers for small workloads  
    — Start with 8–10 workers for medium to big workloads that involve wide transformations like joins and aggregations  
    — Fine-tune the shuffle partitions when applicable to fully engage all cluster cores
- Spot instances  
    — Use spot instances to use spare VM instances for a below-market rate  
    — Great for interactive ad hoc/shared clusters  
    — Not recommended for production jobs with tight SLAs  
    — Never use spot instances for the driver
- Auto-termination  
    — Set it to 10–15 minutes, to further save cost
- Cluster usage  
    — Make sure all worker cores are actively occupied and not idle in any of the iterations  
    — To do so, manually tune number of shuffle partitions as described above.  
    — In the absence of manual shuffle partition tuning set M to 2 or 3 as a rule of thumb  
    — Use Ganglia UI to make sure that all the cores are fully engaged. Ganglia UI can be accessed right from the cluster UI pinned under the metrics tab.  
    — Ganglia UI (For runtimes < 13) / cluster metrics UI (For runtimes > 13)  
    — The average cluster load should always be greater than 80%  
    — During query execution, all squares in the cluster load distribution graph (on the left in the UI) should be red (with the exception of the driver node), indicating that all worker cores are fully engaged  
    — The use of cluster memory should be maximized (at least 60%-70%, or even more)  
    — Ganglia metrics are only available for Databricks Runtime 12.2 and below
- Instance pools  
    — reduces cluster start and autoscaling times by maintaining a set of idle, ready-to-use instances.  
    — Useful for workloads with tight SLAs  
    — When instances are idle in the pool, they only incur Azure VM costs and no DBU costs.
- Photon  
    — Next-generation engine on the Databricks Lakehouse Platform  
    — Provides extremely fast query performance at a low cost.  
    — To be enables when:  
    — ETL pipelines consisting of Delta MERGE operations  
    — ETL pipelines consisting of Delta MERGE operations  
    — Writing large volumes of data to cloud storage (Delta/Parquet)  
    — Scans of large data sets, joins, aggregations and decimal computations  
    — Auto Loader to incrementally and efficiently process new data arriving in storage  
    — Interactive/ad hoc queries using SQL

**Others**

- Use the latest LTS version of Databricks Runtime (DBR)
- Restart all-purpose clusters, at least once per week
- Configure a large driver node (4–8 cores and 16–32GB is mostly enough) only if:  
    — Large data sets are being returned/collected (spark.driver.maxResultSize is typically increased also)  
    — Large broadcast joins are being performed  
    — Many (50+) streams or concurrent jobs/notebooks on the same cluster
- For workloads using single-node libraries (e.g., Pandas), it is recommended to use single-node data science clusters as such libraries do not utilize the resources of a cluster in a distributed manner
- Add cluster tags can be associated with Databricks clusters to attribute costs to specific teams/departments.
- For such shuffle-heavy workloads, it is recommended to use fewer larger node sizes, which will help with reducing network I/O when transferring data between nodes
- Don’t call collect() functions to collect data on the driver
- Prefer Delta cache over Spark cache