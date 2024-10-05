---
modified: 2024-08-11T02:33:56+05:30
---

### TIME TRAVEL
	
	describe history dl_flights_data


Output looks as following, exactly same as previous screen from history view of the table (Removed some columns for ease of reading here).

![](https://miro.medium.com/v2/resize:fit:1400/1*V-w0i43NJ5CfL_gb405ErA.png)

It’s time look back and forth of the data. Now the question, how my initial data looks like (just after first insert ?) which is nothing but **version — 1**

```
//**Syntax** - select * from **<table_name>** VERSION as of **<version number>** //**Syntax** - select * from **<table_name>**@V**<version number>
**select * from **dl_flights_data** version as of **1
**select * from **dl_flights_data@v1**
```

This gives the data as of first insert

![](https://miro.medium.com/v2/resize:fit:1400/1*RZneGwh9X8OpN3as9bUv_Q.png)

Delta time travel with version

How do we run same query, when we know the timestamp of our version

```
//**Syntax** - select * from **<table_name>** TIMESTAMP as of **<Time Stamp>

**select * from **dl_flights_data** _TIMESTAMP_ as of  **'2021-11-05 05:24:54'**
```

![](https://miro.medium.com/v2/resize:fit:1400/1*3WuHOH8qPAT_HDTyJYrvug.png)

Delta time travel with timestamp

Lets find records which changed between some versions.

```
select * from dl_flights_data version as of 3  
minus   
select * from dl_flights_data version as of 2
```

This gives changed records from version 2 to 3 (in our example, these are 3 updates). This gives a privilege to identify and correct if there are any bad records.

![](https://miro.medium.com/v2/resize:fit:1400/1*PSuDX2wDIPA3qOEoqw0gKw.png)

Delta time travel — Version differences


To restore a previous version of your data, you can use the following SQL statement:

> RESTORE TABLE my_delta_table  
> TO VERSION AS OF TIMESTAMP ‘2023–10–27 16:40:00 PST’;


---------------------------------------------------------------------------------------



Delta Lake’s time travel feature is a powerful capability that allows users to access and query historical versions of data stored in Delta tables. It operates by leveraging the transaction logs maintained by Delta Lake, enabling a granular view of changes made to data over time.

In this blog, we’ll explore how we can retrieve delta table history, understand the delta table time travel concept, data retention in delta tables, restore the delta table to the previous version, and some practical examples where this feature can be useful. Let’s start…

## Retrieve Delta Table History —

Each operation that modifies a Delta Lake table creates a new table version. We can use history information to audit operations, rollback a table, or query a table at a specific point in time using time travel. To understand better, let’s create a Delta table and add some modifications to it. Below are the set of Spark SQL queries for the table —

> [!NOTE]
> CREATE TABLE IF NOT EXISTS employee_delta (  
> id INT,  
> name STRING,  
> age INT  
> )  
> USING DELTA;  
>   
>   
> INSERT INTO employee_delta VALUES  
> (1, 'John', 30),  
> (2, 'Alice', 28),  
> (3, 'Bob', 35);  
>   
> UPDATE employee_delta SET age = 29 WHERE id = 2;  
>   
> UPDATE employee_delta SET age = 36 WHERE id = 3;  
>   
> ALTER TABLE employee_delta  
> ADD COLUMN department AFTER name;

We can retrieve information including the operations, user, and timestamp for each write to a Delta table by running the `HISTORY` command. The operations are returned in reverse chronological order.

> [!NOTE]
> DESCRIBE HISTORY employee_delta;

![](https://miro.medium.com/v2/resize:fit:1400/1*0dNJ8qz6S6VihHrdGwa16A.png)

We can see that the table has 5 versions. The above image shows just a part of the output. The output of the `history` operation has the following columns -

![](https://miro.medium.com/v2/resize:fit:1400/1*DHakQFXnkszOXqVDwPargA.png)

Source: Databricks

## Delta Table Time Travel —

Delta Lake time travel supports querying previous table versions based on timestamp or table version (as recorded in the transaction log). Below is the latest version data of `employee_delta` table.

![](https://miro.medium.com/v2/resize:fit:1400/1*LutXKRJmeDEVziftG4UU_g.png)

Below are the queries to time travel to the previous version of the table.

> [!NOTE]
> SELECT * FROM employee_delta TIMESTAMP AS OF '2023-12-19 07:32:12.000'

![](https://miro.medium.com/v2/resize:fit:1400/1*hfhzDu17prxoy7m9z_IRYw.png)

We can see that we were able to get the data as of a particular timestamp with just a simple query.

```
SELECT * FROM employee_delta VERSION AS OF 2
```

![](https://miro.medium.com/v2/resize:fit:1400/1*6vR9kYpDcjDAp42eH9cAGg.png)

In this output, we can see that it's the data from when we had our first update to the table for `id = 2` .

We can query using timestamp expression as well

> [!NOTE]
> - `'2023-12-19T22:15:12.013Z'`, that is, a string that can be cast to a timestamp
> - `cast('2023-12-19 13:36:32 CEST' as timestamp)`
> - `'2023-12-19'`, that is, a date string
> - `current_timestamp() - interval 12 hours`
> - `date_sub(current_date(), 1)`
> - Any other expression that is or can be cast to a timestamp

We can also use the @ syntax to specify the timestamp or version as part of the table name. The timestamp must be in yyyyMMddHHmmssSSS format. You can specify a version after @ by prepending a v to the version. See the following code for example syntax:

> [!NOTE]
> SELECT * FROM employee_delta@20231219000000000;  
> SELECT * FROM employee_delta@v2;

## Transaction log checkpoints and data retention —

1. Delta Lake records table versions as JSON files within the `_delta_log` directory, which is stored alongside table data.
2. To optimize checkpoint querying, Delta Lake aggregates table versions to Parquet checkpoint files, preventing the need to read all JSON versions of table history.
3. To increase the data retention threshold for Delta tables, we can configure `delta.logRetentionDuration = "interval <interval>"` table property which controls how long the history for a table is kept. The default is `interval 30 days` .
4. We can also change `delta.deletedFileRetentionDuration = “interval <interval>”` table property that determines the threshold that `VACUUM` uses to remove data files no longer referenced in the current table version. We can run VACCUM by just — `VACCUM <name_of_delta_table>;`
5. We can specify Delta properties during table creation or set them with an `ALTER TABLE` statement.

> **Note** : Increasing data retention threshold can cause your storage costs to go up, as more data files are maintained.

## Restore Delta Table to Earlier Version —

We can restore a Delta table to its earlier state by using the `RESTORE` command. A Delta table internally maintains historic versions of the table that enable it to be restored to an earlier state.

Some important points to take care of —

> 1. We can restore an already restored table.
> 
> 2. We can restore a cloned table.
> 
> 3. We must have `MODIFY` permission on the table being restored.
> 
> 4. We cannot restore a table to an older version where the data files were deleted manually or by `vacuum`. Restoring to this version partially is still possible if `spark.sql.files.ignoreMissingFiles` is set to `true`.
> 
> 5. The timestamp format for restoring to an earlier state is `yyyy-MM-dd HH:mm:ss`. Providing only a date(`yyyy-MM-dd`) string is also supported.

Let’s try to restore our employee_delta table to an earlier version, say 2.

> [!NOTE]
> RESTORE TABLE employee_delta to VERSION AS OF 2;

![](https://miro.medium.com/v2/resize:fit:1400/1*PA6jTJZJSE61YNMfm-ljbA.png)

Now if we try to query the table it will be as of version 2.

> [!NOTE]
> SELECT * FROM employee_delta;

![](https://miro.medium.com/v2/resize:fit:1400/1*6vR9kYpDcjDAp42eH9cAGg.png)

## Practical use cases of Delta Lake Time Travel —

After understanding the concept and how to do it, let’s delve into two practical examples where this can help us.

**Use Case 1:** Accidental Deletion Recovery for a Specific User

In a user management system powered by Delta Lake, the `user_data` table stores user information including `user_id`, `name`, `email`, and `registration_date` . Below is the table

![](https://miro.medium.com/v2/resize:fit:1400/1*T4u6FlnatUERTsiRq39GVA.png)

Accidental deletions affected the records of `user_id` `103` in the `user_data` table, resulting in the loss of crucial user information. To rectify this, it's imperative to recover the deleted records for `user_id` 103 and restore the user data to its state before the accidental deletion. Below is the latest version of the table —

![](https://miro.medium.com/v2/resize:fit:1400/1*CEBIuHowYNJmkuFd3UFbYg.png)

Let’s rectify this using Delta Table Time travel capability. We know that yesterday the user with ID 103 was in the table. Below is the query to recover that —

> [!NOTE]
> 
> INSERT INTO user_data  
> SELECT * FROM my_table TIMESTAMP AS OF date_sub(current_date(), 1)  
> WHERE userId = 103
> 
> Now, after restoring if we do a select on the records, we can see that the deleted user_id is recovered.
> 
> SELECT * FROM user_data;

![](https://miro.medium.com/v2/resize:fit:1400/1*PyNUlzW7dlHr7A06lH57JQ.png)

**Use Case 2:** Fix accidental incorrect updates to a table

In a customer management system utilizing Delta Lake, the `customer_data` table holds customer details such as `customer_id`, `name`, `email`, `phone_number`, and `registration_date` . Below is the table —

![](https://miro.medium.com/v2/resize:fit:1400/1*nRkozgP3OjrHTN5QqS9Bbg.png)

Due to an accidental system glitch or human error, the `email` field for some customers is updated incorrectly. Below is the table with incorrect updates —

![](https://miro.medium.com/v2/resize:fit:1400/1*kb_cqN6-ob8l_otFl0E4kA.png)

To solve this issue, we will utilize Delta Lake’s time travel feature to access the state of the `customer_data` table before the incorrect update is applied. We will get the correct emails and then merge them into the current table. Below is the Spark SQL query —

> [!NOTE]
> MERGE INTO customer_data target  
> USING customer_data TIMESTAMP AS OF date_sub(current_date(), 1) source  
> ON source.user_id = target.user_id  
> WHEN MATCHED THEN UPDATE SET target.email = source.email
> 
> Now, after the update, if we do a select on the records, the accidental incorrect updates are corrected.
> 
> SELECT * FROM customer_data

![](https://miro.medium.com/v2/resize:fit:1400/1*VoI3ea6LvBakY4Q8ENE6cg.png)

## Conclusion —

_Delta Lake’s time travel isn’t just a capability for historical data retrieval; it’s a cornerstone in ensuring data reliability, providing a safety mechanism that fortifies data management strategies and supports robust decision-making processes in today’s data-driven environments. It acts as a safety net, allowing us to navigate data incidents with confidence, minimize the impact of errors, and maintain the consistency and trustworthiness of our data assets._


## Delta Lake time travel by version with Python example

Let’s make a Delta table with the following three versions:

[![image1](https://delta.io/static/9c42ea9f028932de03257ed75d35a8ba/8b936/image1.png)](https://delta.io/static/9c42ea9f028932de03257ed75d35a8ba/cf8e5/image1.png)

We’ll build this Delta table with these three versions by creating the Delta table, appending some data, and then performing an overwrite operation.

Let’s start by creating the Delta table to create Version 0:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```lua
df = spark.range(0, 3)
df.repartition(1).write.format("delta").save("tmp/some_nums")
```

Note: We’re using `repartition(1)` to output a single file to simplify this demonstration. You usually shouldn’t output a single file.

Now append some data to the Delta table, which will create Version 1:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```lua
df = spark.range(8, 11)
df.repartition(1).write.mode("append").format("delta").save("tmp/some_nums")
```

Finally, overwrite the Delta table which will create Version 2 of the Delta table:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```scss
df = spark.createDataFrame([(55,), (66,), (77,)]).toDF("id")
df.repartition(1).write.mode("overwrite").format("delta").save("tmp/some_nums")
```

Let’s read in the latest version of the Delta table to confirm it only contains the Version 2 data:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```lua
spark.read.format("delta").load("tmp/some_nums").show()

+---+
| id|
+---+
| 55|
| 66|
| 77|
+---+
```

Let’s look at some examples where we’re time traveling to different versions of the data. Here’s how to time travel back to Version 0 and read an earlier version of the Delta table:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```lua
spark.read.format("delta").option("versionAsOf", "0").load("tmp/some_nums").show()

+---+
| id|
+---+
|  0|
|  1|
|  2|
+---+
```

Now read Version 1 of the Delta table:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```lua
spark.read.format("delta").option("versionAsOf", "1").load("tmp/some_nums").show()

+---+
| id|
+---+
|  8|
|  9|
| 10|
|  0|
|  1|
|  2|
+---+
```

We’ve already seen how Delta Lake will read in the latest version of the table by default when `versionAsOf` is not explicitly set. You can also explicitly read the latest version of the Delta table (Version 2 in this case):

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```lua
spark.read.format("delta").option("versionAsOf", "2").load("tmp/some_nums").show()

+---+
| id|
+---+
| 55|
| 66|
| 77|
+---+
```

Delta Lake makes it easy to time travel and read different versions of your Delta table. You can use the `history` command to show all versions of the Delta table and the associated timestamps.

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```sql
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "tmp/some_nums")
delta_table.history().select("version", "timestamp", "operation").show(truncate=False)
```

Here’s the table that’s displayed:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```sql
+-------+-----------------------+---------+
|version|timestamp              |operation|
+-------+-----------------------+---------+
|2      |2023-01-31 06:27:08.508|WRITE    |
|1      |2023-01-31 06:26:56.895|WRITE    |
|0      |2023-01-31 06:26:35.825|WRITE    |
+-------+-----------------------+---------+
```

Let’s learn more about how Delta Lake is architected to allow for this feature.

## Delta Lake time travel intuition

Delta Lake stores data in Parquet files and information about transactions in the `_delta_log` metadata folder.

The `_delta_log` metadata folder tracks the Parquet data files that are added and removed from the Delta table for each transaction.

The following diagram shows the files added and removed for each transaction in our example.

[![image2](https://delta.io/static/d02755f9b4fb21cd4f164964fbb13223/8b936/image2.png)](https://delta.io/static/d02755f9b4fb21cd4f164964fbb13223/2cefc/image2.png)

Let’s look at how Delta Lake will inspect the transaction log and figure out which files should be read for each version:

- For Version 0, Delta Lake just needs to read File A
- Delta Lake will see both File A and File B should be read for Version 1
- For Version 2, Delta Lake will see that File A, File B, and File C were added, but File A and File B were removed, so only File C should be read. Delta Lake will only read File C and skip the other files when reading Version 2.

Delta Lake is intelligent about reading files by consulting the transaction log. Query engines need to perform expensive file listing operations when reading files stored in data lakes. It’s much more efficient to intelligently query the transaction log to fetch the relevant files for a given version.

## Delta Lake time travel by timestamp

Delta Lake also lets you time travel based on timestamp.

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```lua
spark.read.format("delta").option("timestampAsOf", "2019-01-01").load("tmp/some_nums")
```

Time travel by timestamp is a great way to visit your data at an earlier state without having to figure out the exact version.

Here’s an important detail worth knowing if you’re time-traveling based on timestamps and copying Delta tables to new locations. Delta Lake time-based time travel relies on file timestamps. When you copy a Delta Lake table to another location, it’s possible that the file timestamps will change, which will change the behavior of your time-based time travel code. So when copying Delta tables to another location, it’s crucial to retain the existing file timestamps.

Changing timestamps when you copy files isn’t a factor you need to consider if you’re time-traveling by version number of course.

## Delta Lake time travel SQL example

Here’s the SQL syntax to time travel to a specific version:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```sql
SELECT count(*) FROM my_table VERSION AS OF 5238
```

And here’s the SQL syntax to time travel to a specific timestamp:

 [Copy](https://delta.io/blog/2023-02-01-delta-lake-time-travel/#)

```sql
SELECT count(*) FROM my_table TIMESTAMP AS OF "2019-01-01"
```

Time travel works the same whether you’re using the SQL or Python APIs. The only difference is the syntax.

## Delta Lake time travel after vacuum

Delta Lake supports a `VACUUM` command that removes files from storage that are older than the retention period and have been marked for removal in the transaction log.

If the `VACUUM` command removes a file from storage that a given Delta table version depends on you will no longer be able to time travel to that version of the Delta table.

You need to set the retention period of your Delta tables to suit your time travel needs for a given table. Some tables should never be vacuumed because you want to retain access to every version. Other tables should be vacuumed frequently to save on storage costs. See [this blog post on the vacuum command](https://delta.io/blog/2023-01-03-delta-lake-vacuum-command/) for more details.

You should make sure to set a vacuum strategy for your tables that’s optimized for your time travel needs.

## Delta Lake restore vs. time travel

Delta Lake supports a restore command that makes it easy to bring back a prior version of the Delta table to be considered the “current version”. See [this blog post on the RESTORE command](https://delta.io/blog/2022-10-03-rollback-delta-lake-restore/) for more information.

You have to specify the version every time you time travel because it doesn’t change the current version of the Delta table like RESTORE. Suppose a Delta table has three versions, and you time-travel back to Version 0. When you read the latest version of the Delta table again, it will still default back to the current version, even after you’ve time traveled

RESTORE is better when you want to reset the current version of the table. For example, restore is great for when you ingest bad data and would like to undo the append for other readers.

## Delta Lake time travel vs. data lake support

Delta Lake makes it easy to time travel between different versions of a Delta table. It’s a straightforward operation that’s a natural extension of the Delta Lake transaction log.

Data lakes do not support time travel. When you’re reading a data lake, you always have to read the latest version. Build-in time travel is an important feature Delta Lake offers compared to data lakes.
