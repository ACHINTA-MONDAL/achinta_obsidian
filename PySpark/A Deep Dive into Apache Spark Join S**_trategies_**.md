
**_Join_** operations are frequently used in big data analytics to merge two data sets, represented as tables or DataFrames, based on a common matching key. Spark’s DataFrame and Dataset APIs, along with Spark SQL, provide a variety of join transformations such as inner joins, outer joins, left joins, right joins, and more. However, these operations often require a significant amount of data movement across Spark executors, similar to how it works in relational databases.

![](https://miro.medium.com/v2/resize:fit:1400/0*sGcNY9Vu49tIa9y3.jpg)

Although many Data Engineers are familiar with ANSI SQL Join types , they may not have a clear understanding of how these joins function within the Spark engine. To gain a better understanding of Spark’s join strategies, it is important to first recognize the various factors that can impact join operations.

**What Factors affect Join Operations?**

> **Data Size:** The size of the data being joined can affect the performance of join operations.
> 
> **Data Distribution:** If the data being joined is not distributed evenly across the cluster, it can result in data **skew**, which can cause performance issues.
> 
> **Join Type:** Different join types, such as inner join, outer join, and left join, can have varying performance characteristics depending on the data being joined. Eg : **_Equi Join_** _— “=” /_ **_Non Equi Join_** _— “<,>,≥, ≤”_
> 
> **Data Format:** The format of the data being joined can also affect performance. For example, **Parquet** or **ORC** format can be more efficient than **CSV** or **JSON** format due to their columnar storage and compression capabilities.
> 
> **Join Hints :** If end-user want more control over the join strategy selection then they supply Join Hints like `/*+ **BROADCAST**(table name)*/*`

Based on these factors Spark has **_5 distinct join strategies_** by which it exchanges_,_ moves, sorts, groups, and merges data across executors:

- Broadcast Hash Join (BHJ)
- Shuffle Hash Join (SHJ)
- Sort Merge Join (SMJ)
- Broadcast Nested Loop Join (BNLP)
- Cartesian Product Join (CPJ)

## **1. Broadcast Hash Join (BHJ)**

In this technique, one of the data sets is small enough to fit in memory and is broadcasted to all the worker nodes in the cluster.

10 mb is the default value of `**spark.sql.autoBroadcastJoinThreshold**`

#Join Hints for broadcast join in Pyspark  
df.hint("broadcast")

  
```
-- Join Hints for broadcast join  
SELECT /*+ BROADCAST(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;  
SELECT /*+ BROADCASTJOIN (t1) */ * FROM t1 left JOIN t2 ON t1.key = t2.key;  
SELECT /*+ MAPJOIN(t2) */ * FROM t1 right JOIN t2 ON t1.key = t2.key;
```

**When to use a Broadcast Hash Join (BHJ) ?**

- When each key within the smaller and larger data sets is hashed to the same partition by Spark
- When one data set is much smaller than the other (and within the default config of 10 MB, or more if you have sufficient memory)
- When you only want to perform an equi-join, to combine two data sets based on matching unsorted keys
- When you are not worried by excessive network bandwidth usage or OOM errors, because the smaller data set will be broadcast to all Spark executors

## **2. Shuffle Hash Join (SHJ)**

In Spark, Shuffle Hash Join is one of the default join strategies used when **joining two large data sets**.

Shuffle Hash Join involves two primary steps:

1. **Shuffling**: This step partitions the data from the Join tables based on the Join key and distributes them across partitions to ensure that records with the same Join keys are assigned to the corresponding partitions.
2. **Hash Join:** After shuffling the data, a classic single node Hash Join algorithm is performed on the data in each partition.

```
#Join Hints for shuffle hash join in Pyspark  
df.hint("shuffle_hash")

-- Join Hints for shuffle hash join  
SELECT /*+ SHUFFLE_HASH(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
```

**When to use a Shuffle Hash Join (SHJ)?**

- The datasets being joined are too large to fit into the memory of a single node.
- The datasets are partitioned across multiple nodes in a cluster.
- The join keys are not skewed, meaning they are evenly distributed across the partitions.
- The join operation requires a full outer join or a left outer join, which cannot be performed using a broadcast join.

In general, Shuffle Hash Join is a good choice when dealing with **large-scale data processing** in distributed environments and can significantly improve performance compared to other join methods.

## 3. Sort Merge Join (SMJ)

Sort Merge Join is a method used in distributed computing to join large datasets that are spread across multiple nodes in a cluster.

In Spark, Sort Merge Join involves the following steps:

1. **Shuffle**: The data from both tables is partitioned based on the join key. The partitioning is done in such a way that records with the same join key are sent to the same partition.
2. **Sort**: The data in each partition is sorted based on the join key.
3. **Merge**: The sorted data is then merged across partitions to perform the join operation.

**_spark.sql.join.preferSortMergeJoin=false (Default value is true)_**

```
#Join Hints for sort merge join in Pyspark  
df.hint("merge")

-- Join Hints for shuffle sort merge join  
SELECT /*+ SHUFFLE_MERGE(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;  
SELECT /*+ MERGEJOIN(t2) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;  
SELECT /*+ MERGE(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
```

**When to use a Sort Merge Join (SMJ)?**

- The data size is too large to fit into the memory of a single node, but not so large that it requires a Shuffle Hash Join.
- The join keys are not evenly distributed across the partitions.
- The data in each partition is already sorted by the join key, or the cost of sorting the data is lower than the cost of shuffling the data.
- The join operation requires a full outer join or a left outer join, which cannot be performed using a broadcast join.

## **4. Broadcast Nested Loop Join (BNLP)**

Broadcast Nested Loop Join is a method used in Spark to join two datasets where one of the datasets is small enough to fit into the memory of a single node. In this method, the smaller dataset is broadcast to all the nodes in the cluster, and then a nested loop join is performed with the larger dataset.

The steps involved in Broadcast Nested Loop Join are as follows:

1. The smaller dataset is broadcast to all the nodes in the cluster.
2. The larger dataset is partitioned based on the join key.
3. For each partition of the larger dataset, a nested loop join is performed with the broadcasted smaller dataset.
4. The results of each partition are then combined to form the final output.

```
SELECT /*+ BROADCAST(t1), MERGE(t1, t2) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
```

**When to use a Broadcast Nested Loop Join (BNLP) ?**

- One of the datasets is small enough to fit into the memory of a single node.
- The join key is selective, meaning it results in a small number of matching records.
- The larger dataset is not skewed, meaning the data is evenly distributed across the partitions.
- The join operation requires an inner join or an equi-join.

## **5. Cartesian Product Join (CPJ)** aka Shuffle-and-Replication Nested Loop Join

Cartesian Product Join (CPJ) is a method used in Spark to join two datasets by generating **all possible combinations of the records in both datasets**. In CPJ, each record in one dataset is paired with every record in the other dataset, resulting in a Cartesian product of the two datasets.

#Join Hints for shuffle-and-replicate nested loop join in Pyspark  
df.hint("shuffle_replicate_nl")

-- Join Hints for shuffle-and-replicate nested loop join  
```
SELECT /*+ SHUFFLE_REPLICATE_NL(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
```

**Note** : Cartesian Product Join can be a **very expensive operation**, especially when dealing with large datasets, as it generates all possible combinations of the records. It is generally not recommended to use this method unless it is absolutely necessary. Instead, other join methods such as Hash Join, Sort Merge Join, and Broadcast Nested Loop Join should be considered first.

# Priority of join hints

For the scenario that multiple different join hints are added for the same table, Spark follows the priority list below:

1. BROADCAST
2. MERGE
3. SHUFFLE_HASH
4. SHUFFLE_REPLACE_NL

# Conclusion

While Apache Spark automatically chooses the best join algorithm, developers can override this decision using **hints**. However, providing hints without a thorough understanding of the data can result in Out Of Memory (OOM) errors. Conversely, if the developer is knowledgeable about the underlying data and chooses not to provide hints, they may miss an opportunity to optimize the join operation. Therefore, it is important for developers to carefully consider the use of hints when performing join operations in Spark.