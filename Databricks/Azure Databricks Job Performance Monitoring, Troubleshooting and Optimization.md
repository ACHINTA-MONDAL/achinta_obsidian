![](https://miro.medium.com/v2/resize:fit:1400/1*ZIq-WSbrAbuQq72XFBgTHw.png)

As a part of Databricks Job performance Monitoring, troubleshooting and Optimization we will be looking into various aspects.

• Azure Databricks Service Architecture

• Azure Databricks job overview

• How to monitor job performance

- What to monitor
- Using Cluster UI
- Using Spark UI
- Spark Logs

• Common root causes for slow job performance

- Due to platform resource constraints
- Due to Spark, Data, and user code.

• Common performance issues drill down.

• Performance tuning and optimization

• Demos

# Azure Databricks Service Architecture.

Azure Databricks service architecture is specifically being segregated into 2 layers.

· Control plane: The control plane encompasses the management and orchestration layer of the Databricks platform.

· Data plane: The data plane encompasses the compute and storage layer where data processing and analytics tasks are performed.

Additional components which primarily manage the execution and management of data processing tasks within the Spark environment are

• Standalone master

• One executor per worker node

• High Concurrency vs. Standard vs. Single Node cluster

• Driver node

- Maintains state information of all notebooks attached to the cluster.
- Maintains Spark Context
- Interprets all commands from a notebook or a library.
- Runs the Apache Spark master.

• Schedule jobs

- Collect data from executors.
- Load libraries
- •Spark REPL
- Write generated code to /local_disk0/tmp

• Worker node

- Runs Spark executors.
- Spark command needs at least one worker node to run.
- Run tasks.
- Send data back to drivers.
- Exchange / shuffle
- Sink data to storage.

• Spark master

- Coordinate work with Spark executors.

![](https://miro.medium.com/v2/resize:fit:1162/1*TAyFh8qgiOecTkyYWsGaQg.png)

# Azure Databricks Jobs overview

Azure Databricks Jobs provide a means to execute non-interactive code, such as notebooks or JAR files, within a Databricks cluster. They can be created and initiated using the Databricks web interface, the command-line interface (CLI), or by invoking the Jobs API. Jobs can vary in complexity, ranging from single-task executions to large, multi-task workflows with intricate dependencies.

![](https://miro.medium.com/v2/resize:fit:1158/1*u-VIcY_joL5Y89AHKN3pGw.png)

Azure Databricks Documentation — Jobs: [https://docs.databricks.com/api/workspace/jobs](https://docs.databricks.com/api/workspace/jobs)

Azure Databricks Documentation — Common Job Issues: [https://docs.databricks.com/en/workflows/jobs/repair-job-failures.html](https://docs.databricks.com/en/workflows/jobs/repair-job-failures.html)

# How to monitor job performance

Monitoring Databricks job performance is crucial for ensuring efficient execution of data processing tasks and identifying potential bottlenecks or issues. Here are some approaches to monitor Databricks job performance. There are different ways to monitor your Databricks job performance it is based on

· Cluster

· Notebook command output

· Host Operating system VM

· JVM

Here is an extended detail.

• Cluster

- Cluster UI
- Ganglia
- Grafana

• Job Run page / Notebook command output

• Spark Applications and Jobs

- Spark UI
- Spark Logs — driver log, executor log, event log

• Host Operating System/Machine/VM

- CPU
- Memory
- Network
- Disk
- IO
- Tools — dstat, iostat, iotop

• JVM — low level debugging beyond what Spark UI and Spark Logs can provide

- jstack — providing stack trace
- jmap — creating heap-dumps
- jstat — reporting time-series statistics
- jconsole — visually exploring various JVM properties
- jvisualvm — profile Spark jobs

What to Monitor : Some of the common elements for monitoring in Databricks are based on Driver and executor processes which is crucial for understanding Resource utilization and performance bottlenecks.

Below is the extended list of things to monitor.

• Metrics from driver process and executor process

- • Driver process is the most critical within a Databricks cluster.
- • Metrics are emitted to Ganglia.
- • Metrics can be configured in `**$SPARK_HOME/conf/metrics.properties**`.

• Queries, jobs, stages, tasks

Spark logs:

- o Scala, Java: Utilize a logging framework to enable application log along with Spark’s logs.
- o Python: Use the logging module or print statement to print results to standard error.
- o Change Spark’s log level with spark.sparkContext.setLogLevel(“INFO”).

Spark UI:

- Accessible via web interface.
- Provides detailed information on job execution:
- Jobs tab: Summary info on jobs
- o Stages tab: Individual stages and their relevant tasks.
- o Storage tab: Cached RDDs and DataFrames.
- o Environment tab: Configurations and current settings of the Spark application.
- o SQL tab: Query plan for Structured API queries (SQL and DataFrames).
- o Executor tab: Detailed info on each executor running the application.

Monitoring these aspects provides insights into the performance and execution of your Databricks jobs, enabling you to identify and address any issues efficiently.

# Using Cluster UI

Databricks Cluster UI provides a comprehensive interface for managing and monitoring clusters within the Databricks environment. Here’s some information about the features and functionalities typically found in the Databricks Cluster UI.

Where you can check configuration of your cluster, notebooks associated with that cluster, Libraries (associated/attached), Spark UI, Driver logs, Metrics (specific to cluster usage), Apps etc.

![](https://miro.medium.com/v2/resize:fit:1150/1*eONaNeX2KrrFFQwChfTq3A.png)

Spark UI:

It is a web-based interface provided by Apache Spark for monitoring and debugging Spark applications. It offers detailed insights into the execution of Spark jobs, stages, tasks, and resource utilization within a Spark cluster.

• Spark UI provides high level summary of the jobs running or completed on the cluster, most important tool for job performance

- Sequence of jobs
- Stages of each job
- Tasks of each job
- Delay in between
- Timeline
- Metrics

• Spark UI provides high level view and information that logs do not provide. Logs provide precise root cause analysis. Combining both give the complete view of the issue.

[https://docs.databricks.com/en/compute/debugging-spark-ui.html](https://docs.databricks.com/en/compute/debugging-spark-ui.html)

# Spark UI offers additional information about jobs based on

· Jobs

· Stages

· Storage

· Environment

· Executors

· SQL / DataFrame

· JDBC/ODBC Server

· Structured Streaming

· Connect

![](https://miro.medium.com/v2/resize:fit:1196/1*KsxN_0-CyPy3Efpq72BK7g.png)

• Jobs page

- • Jobs total run time duration
- • Sort by duration to find the slow run job

# Stages of Each Job:

- The Spark UI provides a detailed breakdown of each job into multiple stages, where each stage represents a distinct set of tasks.
- Users can examine the stages tab to view information such as stage ID, description, number of tasks, input/output size, and duration for each stage.

# Sorting by Duration to Find Slow Stages:

- Users can sort the stages tab by duration to identify stages that are taking longer to execute.
- Slow stages may indicate potential bottlenecks in the Spark application, such as data skew, inefficient transformations, or resource contention.

# Observing Tasks Count:

- The tasks column in the stages tab shows the count of partitions or tasks associated with each stage.
- Monitoring the tasks count can help users understand the parallelism and distribution of work within each stage.

# Shuffle Read/Write Data Size:

- The shuffle read/write data size metrics provide insights into the amount of data shuffled across the network during the execution of each stage.
- Monitoring shuffle read/write data size can help identify stages with excessive data shuffling, which may indicate inefficient join operations or skewed data distribution

![](https://miro.medium.com/v2/resize:fit:1400/1*TC2_E30E6t0qYuXoHSaOMA.png)

# Stages of each job: you can further check each jobs and its properties based on

![](https://miro.medium.com/v2/resize:fit:1400/1*bvenFrjbNi3UEKN4-Q3ZZA.png)

# DAG diagram

DAG visualization: Visual representation of the directed acyclic graph of this job where vertices represent the RDDs or DataFrames and the edges represent an operation to be applied on RDD.

![](https://miro.medium.com/v2/resize:fit:1400/1*b_4-54NmDfg1okZg1vX43Q.png)

You can read more about DAG: [https://spark.apache.org/docs/3.1.2/web-ui.html#:\~:text=DAG visualization%3A Visual representation of,to be applied on RDD](https://spark.apache.org/docs/3.1.2/web-ui.html#:%5C~:text=DAG%20visualization%3A%20Visual%20representation%20of,to%20be%20applied%20on%20RDD).

- Event timeline : Displays in chronological order the events related to the executors (added, removed) and the jobs.

![](https://miro.medium.com/v2/resize:fit:1400/1*6ohpG0x45oYvDQ-TjO5uAQ.png)

- Summary metrics for completed tasks.: Summary metrics for all tasks are represented in a table and in a timeline.

![](https://miro.medium.com/v2/resize:fit:1400/1*0AsRJhLkPdqVwbGmpO--vA.png)

# Spark UI: Storage

The Storage tab displays the persisted RDDs and DataFrames, if any, in the application. The summary page shows the storage levels, sizes and partitions of all RDDs, and the details page shows the sizes and using executors for all partitions in an RDD or DataFrame.

• Look for cache size / cache not un-cached

• IO / Delta table state are internal cache and can be ignored

![](https://miro.medium.com/v2/resize:fit:1400/1*TcHZdT6oVNi9eZXaVe05xw.png)

# Spark UI: Environment

The Environment tab displays the values for the different environment and configuration variables, including JVM, Spark, and system properties.

This environment page has 8 parts. It is a useful place to check whether your properties have been set correctly. The first part ‘Runtime Information’ simply contains the [runtime properties](https://spark.apache.org/docs/3.1.2/configuration.html#runtime-environment) like versions of Java and Scala. The second part ‘Spark Properties’ lists the [application properties](https://spark.apache.org/docs/3.1.2/configuration.html#application-properties) like [‘spark.app.name’](https://spark.apache.org/docs/3.1.2/configuration.html#application-properties) and ‘spark.driver.memory’.

![](https://miro.medium.com/v2/resize:fit:1400/1*2H27FE_rDOW5JOpaQ7Fehg.png)

# Executors Tab

The Executors tab displays summary information about the executors that were created for the application, including memory and disk usage and task and shuffle information. The Storage Memory column shows the amount of memory used and reserved for caching data.

Mainly look for.

• Driver / executor IP address

• GC time

• Shuffle

• Thread dump or heap histogram dump

• GC log / executor logs on a live cluster

![](https://miro.medium.com/v2/resize:fit:1400/1*2xqVaAflAXODVCCWa-KQJw.png)

You can always view additional metrics based on “On Heap memory”, “Off heap memory” etc, here is a full list of options.

![](https://miro.medium.com/v2/resize:fit:1400/1*KId83wXuE7VxsxH-PiSmmg.png)

Spark Logs:

Spark driver log provides essential information about the Spark driver, including stack traces of exceptions.

summary of the key aspects related to **Databricks** and its Spark logs:

- **Driver Log**:
- The driver log provides essential information about the Spark driver, including stack traces of exceptions.
- It’s a valuable resource for debugging issues related to job execution.
- **Checkpoint / Commit / Transaction**:
- Checkpoints are crucial for building fault-tolerant and resilient Spark applications.
- They store progress information about streaming queries, ensuring data durability.
- Transactions and commits play a role in maintaining data consistency during processing.
- **Batch Initialization**:
- Batch initialization refers to the process of setting up resources and configurations for batch tasks.
- It ensures that each batch starts with the necessary context and environment.
- **Tasks Scheduling**:
- Task scheduling involves allocating resources (CPU, memory) to individual tasks within a Spark job.
- Efficient scheduling enhances overall job performance.
- **Chauffeur (jmap/jstack/kill driver)**:
- The “Chauffeur” likely refers to a tool or process for managing the Spark driver.
- Commands like jmap, jstack, or kill can be used to diagnose issues or control the driver.
- **Driver Heartbeat Failure Causes Executor Task to Fail**:
- If the driver fails to send heartbeats to the executors, it can lead to executor task failures.
- Heartbeat failures disrupt communication and coordination between the driver and executors.
- **Timestamp and Duration Between Timestamps**:
- Timestamps are critical for correlating events across different logs (e.g., driver and executor).
- Analyzing the time duration between timestamps helps understand job behavior and performance.
- **Matching Timestamp from Driver Log with Executor Log**:
- Aligning timestamps between driver and executor logs allows tracing events across the entire Spark application.
- It aids in diagnosing issues and understanding the sequence of operations.

# Spark Logs – Executor logs

Executor logs are sometimes helpful if you see certain tasks are misbehaving and would like to see the logs for specific tasks.

Here are some common events captured in executor logs:

- **Read from Input**: Details about reading data from input sources (e.g., files, databases, streams).
- **Write to Sink**: Information related to writing data to output sinks (e.g., saving results to files, databases).
- **Shuffle**: Logs related to data shuffling during operations like joins or aggregations.
- **Time Spent on Read/Write to Storage**: Duration metrics for reading/writing data.
- **Timestamp and Duration Between Timestamps**: Timing information for correlating events.
- **Matching Timestamp from Driver Log with Execution Log**: Aligning timestamps between driver and executor logs for comprehensive analysis.

# GC Logs

GC logs you can find heap memory related info; you can find additional info such as

- **GC Time in Spark UI**: The log mentions that GC time is also visible in the Spark UI.
- **GC Frequency**: It discusses the frequency of garbage collection.
- **Heap Size Optimization**: If GC takes too long, it indicates that the heap size might be too big. The log suggests optimizing the application, adding more nodes, or reducing shuffles.
- **Full GC and Pauses**: Full GC events can lead to pauses, causing delays in job execution.
- **OldGen Accumulation**: An increase in OldGen over time indicates object accumulation. Restarting the driver or executor can help clean up heap space.

# Common root causes for slow job performance

# Platform Resource Constraints:

- Cluster Sizing:
- o Driver size: Overloaded driver can lead to out-of-memory errors. Ensure sufficient memory and cores for the driver node.
- o Worker node size: Overloaded worker nodes can impact performance. Properly size worker nodes based on workload requirements.
- o Quota Limit: Quota limits may prevent auto-scaling to the desired number of nodes, affecting cluster performance.
- o Slow VM Node: Slow VMs skipped during cluster startup can result in fewer initial worker nodes than configured.
- o Auto-scaling Performance Variation: Frequent scaling up and down can impact performance stability.
- Throttling:
- o Azure Storage Account:
- o Egress Limit: Throttling due to storage account egress limit.
- o Network:
- o NRP (Network Resource Provider) and CRP (Customer Resource Provider) throttling.
- o SQL Server throttling.
- Concurrent Workload:
- o Interactive Cluster: Concurrent workload on interactive clusters can lead to resource contention and slow job execution.
- o Stream Jobs: Concurrent number of stream jobs can impact cluster performance.
- o Hard Coded Limits:
- o Workspaces are limited to 150 concurrent running jobs and 1000 active jobs (running and pending).
- o High Memory Usage and GC (Garbage Collection):
- High memory usage and frequent garbage collection on clusters that have not restarted for a long time can degrade performance.
- Network Latency:
- o Internal IP Changes: Changes in internal IP addresses can cause slowness in Databricks workspace, resolved by updating route tables.
- o Temporary Network Delay: Network delays can impact job execution speed.
- Disk Issues:
- o Driver or executor running out of disk space can cause jobs to hang.
- o These root causes highlight various factors that can contribute to slow job performance in Databricks clusters, ranging from resource constraints to throttling issues and network latency.

# Due to Spark, Data, and User code

![](https://miro.medium.com/v2/resize:fit:1400/1*Ns36i4ItAFRrH2aj1N0XLg.png)

# Approach for debugging.

![](https://miro.medium.com/v2/resize:fit:1400/1*biccdzMujzm9FJgGaxyyEw.png)

# Common Performance Issues Drill Down

# Slow cluster startup

![](https://miro.medium.com/v2/resize:fit:1400/1*jDADuXSU7iUJHk9RqDD8Bw.png)

# Slow tasks (Stragglers) due to data skew

![](https://miro.medium.com/v2/resize:fit:1400/1*omsWN_iK1LSbD5GBbISlmA.png)

# Slow tasks (Stragglers) due to PyPI libraries install on executor.

![](https://miro.medium.com/v2/resize:fit:1400/1*VWNIGvj2pSxXhSBD7heUEw.png)

# Slow Aggregations

![](https://miro.medium.com/v2/resize:fit:1400/1*4M4itu8-uL1eI2rNiZGhAQ.png)

# Slow joins

![](https://miro.medium.com/v2/resize:fit:1400/1*mgMz59eqPc5tuR-UupdQGw.png)

# Slow Reads and Writes

![](https://miro.medium.com/v2/resize:fit:1400/1*KA29omxZzLAYgsUawokO0w.png)

# Driver unresponsive or OutOfMemoryError

![](https://miro.medium.com/v2/resize:fit:1400/1*MwsKhJAnQVn0CHobssRBJQ.png)

# Executor unresponsive or OutOfMemoryError

![](https://miro.medium.com/v2/resize:fit:1400/1*d0kASDqlTJHl-TwTc3LovQ.png)

# Job running forever.

![](https://miro.medium.com/v2/resize:fit:1400/1*clq26_v1qeoFG4swzFcnVA.png)

# Spark Job Not Starting

![](https://miro.medium.com/v2/resize:fit:1400/1*tycJX6nSuR1su44XdJR_ng.png)

# Performance Tuning

**Performance tuning and optimization techniques – Cluster configuration**

• Choose the right size and type of cluster.

- • Number of worker nodes
- • Type of VM for the driver and work nodes

 o   Memory optimized =\> caching, shuffle  
 o   Compute optimized =\> degree of parallelism of computation, narrow transformation  
 o   Storage optimized =\> caching, shuffle

• Cluster of many small nodes vs cluster of fewer large nodes

o   Total number of executor cores determines max degree of parallelism  
  
o   Total memory across all executors determines how much data can be stored in memory before spill to disk  
  
o   Large memory VM can have significant GC causing delay  
  
o   Shuffle operation performs better on cluster with large memory and fewer worker nodes to  reduce network and disk IO

• Cluster mode

- High concurrency cluster vs. standard cluster

• Enable auto scaling for high concurrency cluster

- If Delta caching is used, cached data will be lost if node is terminated

• Use Azure Databricks pools to leverage predefined VM instance for faster cluster start, or scaling up

• Use the latest DBR version for all-purpose clusters – latest optimization

• Enable Query Watchdog on high concurrency cluster to prevent large ad hoc query from monopolizing the cluster resources

- spark.conf.set("spark.databricks.queryWatchdog.enabled", true)
- spark.conf.set("spark.databricks.queryWatchdog.outputRatioThreshold", 1000L)
- spark.conf.set("spark.databricks.queryWatchdog.minTimeSecs", 10L)
- spark.conf.set("spark.databricks.queryWatchdog.minOutputRows", 100000L)
- Storage account in the same region as the cluster

Reference: [Best practices: Cluster configuration - Azure Databricks | Microsoft Docs](https://docs.microsoft.com/en-us/azure/databricks/clusters/cluster-config-best-practices)

# Performance tuning and optimization techniques – Data and Partition

- How data are stored

•        Choose the most efficient storage format possible  
  
               •        CSV file – slow to parse  
               •        Parquet file - most efficient file format, binary format, column oriented storage, statistics about data available  
              •        Splitable file for parallel operation by the number of cores  
                      •        Zip or tar file not splitable  
                      •        Gzip, bzip2, lz4 are splitable.  
             •        Multiple files for parallel operation by the number of cores  
                      •        Avoid many small files  
                      •        Each file should be at least a few tens of megabytes.  
                      •        Control the number of records per file through maxRecordsPerFile write option

- • Partition on columns frequently used in filter.

 •        Avoid over partitioning.  
  
 •        Compaction is done on per partition basis.

- Bucketing on column(s) of join or aggregation

• Collect and Maintain Table and column statistics to help join, aggregation, filter, broadcast join, etc.

•        ANALYZE TABLE table_name COMPUTE STATISTICS  
  
•        ANALYZE TABLE table_name COMPUTE STATISTICS FOR COLUMNS column_name1, column_name2, …

• sortWithinPartitions

• Use Kryo serialization over Java serialization.

•        Spark.serializer = org.apache.park.serializer.KryoSerializer

# Performance tunning and optimization techniques – Garbage Collection for RDD and UDF

• Goal GC tunning – avoid full GC

•        Ensure only long-lived cached datasets are stored in the Old generation  
  
•        Young generation is sufficiently sized to store all short-lived objects

• Gather GC information - how frequently garbage collection occurs and the amount of time GC takes

•        Adding –verbose:gc –XX:+PrintGCDetails –XX:+PrintGCTimeStamps to Spark’s JVM options using the spark.executor.extraJavaOptions configuration parameter

• GC tunning:

•        Full GC multiple times before task completion =\> decrease memory used for caching  
  
•        Too many minor collections, not many major garbage collections =\> allocate more memory for Eden region  
  
•        Try G1GC garbage collector with –XXL+UseG1GC  
  
•        Increase G1 region size with –XX:+G1HeapRegionSize

# Performance tunning and optimization techniques – Spark application

• Parallelism – spark.default.paralleslim, spark.sql.shuffle.partitions

• Move filter as early as possible

• Try coalesce first

• Repartition before join or cache call

• Custom repartition at the RDD level for finer level of precision

• Avoid UDF

•        UDF force representing data as objects in the JVM  
  
•        Black box to Spark – can not leverage the code optimization on structured API

• Broadcast join threshold

• Cache dataset that will be used multiple times

•        RDD.cache cache the actual physical data  
  
•        Caching in structured API is based on the physical plan

• Broadcast variables for large look up table

# Other Best Practices

• Use Python for majority of the application, use Scala for writing custom transformation using RDD or UDF in Scala, to have the best of overall usability, maintainability, and performance

•        Serialization of objects to and from Python for UDF and RDD is very expensive

• Use Kryo serialization over Java serialization

•        Spark.serializer = org.apache.park.serializer.KryoSerializer

• setJobDescription, to help debug a job easier

Finally, you can get support from Microsoft and make sure to provide following information while opening a case with them.

• Providing the following information when raising a support ticket will expedite the resolution of job-related issues.

• Workspace ID

• Cluster ID

• Job run URL.

• Timestamp of the slow job run.