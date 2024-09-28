---
share_link: https://share.note.sx/mj5pyctb#aBVnqMNNFKCqxSnAEw2c4GlBJk4hzhGBFgJAm/PY0lM
share_updated: 2024-07-02T02:03:33+05:30
tags:
  - PySpark
  - Spark
  - Interview
source: https://medium.com/@mohitdaxini75/spark-interview-question-4-dabc1dac5f4c
---
> Recently, I came across a spark interview question on handling large datasets efficiently and thought to share the answer that I would have given. So, the question was as below :
> 
> ✅ You are working with skewed data partitions in Spark. How would you handle data skewness and ensure optimal processing?
> 
> Check out the response below :

Handling data skewness in Apache Spark is critical to ensure optimal processing and avoid performance bottlenecks. Data skewness occurs when some partitions have significantly more data than others, leading to uneven processing loads and extended job completion times. Here are several strategies to manage data skewness in Spark 3:

## Salting Technique

Salting involves adding a random value to the keys of the skewed data, thereby distributing the load more evenly across partitions.  
**Steps to Implement Salting:**

- _Identify Skewed Keys:_ Identify the keys that are causing skewness by analyzing the data distribution.
- _Add Salt to Keys:_  
    Add a random salt value to the skewed keys to distribute the data across multiple partitions.
- _Perform Join or Aggregation:_  
    Execute the join or aggregation operation on the salted keys.
- _Remove Salt:_  
    After the operation, remove the salt to restore the original key.

**Example in Spark:**

![](https://miro.medium.com/v2/resize:fit:1400/1*6xQeKs9KB_qJ5nCGXmOdLg.png)

**Salting in Spark**

## Broadcast Join

Broadcast joins can be used when one of the datasets is small enough to fit into memory. Spark broadcasts the smaller dataset to all worker nodes, allowing for a highly efficient join operation.

> **Example in Spark:**  
> import org.apache.spark.sql.functions._
> 
> val largeDF = … // large DataFrame  
> val smallDF = … // small DataFrame
> 
> val broadcastDF = broadcast(smallDF)  
> val joinedDF = largeDF.join(broadcastDF, largeDF(“key”) === broadcastDF(“key”))

## Repartitioning and Coalescing

Repartitioning can be used to increase or decrease the number of partitions in a DataFrame. Coalescing is used to decrease the number of partitions efficiently.

> **Example in Spark:**  
> // Increase the number of partitions  
> val repartitionedDF = largeDF.repartition(100, col(“key”))
> 
> // Decrease the number of partitions  
> val coalescedDF = largeDF.coalesce(10)

## Skew Join Optimization

Spark 3 introduces a built-in feature called skew join optimization. This optimization automatically handles data skew during join operations by splitting the skewed partitions and distributing them more evenly.

> **Enabling Skew Join Optimization:**  
> Add the following configuration settings  
> spark.conf.set(“spark.sql.adaptive.enabled”, “true”)  
> spark.conf.set(“spark.sql.adaptive.skewJoin.enabled”, “true”)

**Adaptive Query Execution (AQE)**  
[Adaptive Query Execution (AQE)](https://medium.com/towardsdev/spark-3-adaptive-query-execution-aqe-3b08f8ccfa94) dynamically adjusts query plans based on runtime statistics. This feature can help manage skewed data by dynamically optimizing join strategies and shuffle partitions.

> Enabling AQE:  
> spark.conf.set(“spark.sql.adaptive.enabled”, “true”)

## Custom Partitioning

Custom partitioning can be used to manually distribute data across partitions based on specific logic. This is useful when you have domain knowledge of the data distribution.

> **Example in Spark:**  
> // Define a custom partitioner  
> val customPartitioner = new Partitioner {  
> override def numPartitions: Int = 100 // define number of partitions  
> override def getPartition(key: Any): Int = {  
> // custom logic to determine partition  
> key.hashCode % numPartitions  
> }  
> }
> 
> // Apply the custom partitioner  
> val rdd = largeDF.rdd.map(row => (row.getAs[String](“key”), row))  
> val partitionedRDD = rdd.partitionBy(customPartitioner)  
> val partitionedDF = spark.createDataFrame(partitionedRDD.map(_._2), largeDF.schema)

## Aggregation Strategies

Using efficient aggregation strategies like reduceByKey instead of groupByKey can help minimize data shuffling and improve performance.

> **Example in Spark:**  
> val rdd = largeDF.rdd.map(row => (row.getAs[String](“key”), row.getAs[Int](“value”)))
> 
> // Use reduceByKey instead of groupByKey  
> val aggregatedRDD = rdd.reduceByKey((x, y) => x + y)

## Conclusion

Handling data skewness in Spark 3 involves a combination of techniques, including salting, broadcast joins, repartitioning, skew join optimization, AQE, custom partitioning, and efficient aggregation strategies. By leveraging these methods, you can ensure more balanced workloads across partitions, leading to optimal performance and efficient resource utilization. Each method has its own use cases and trade-offs, so it’s crucial to analyze your specific data characteristics and processing requirements to choose the best approach.

_If you enjoyed this article please don’t forget to clap or follow to support me!!😊_
