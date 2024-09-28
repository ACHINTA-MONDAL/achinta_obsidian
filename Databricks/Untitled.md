---
created: 2024-09-26T22:03:43+05:30
modified: 2024-09-27T13:01:04+05:30
---
### What is a Data Lakehouse?

A data lakehouse is a new, open data management architecture that combines the flexibility, cost-efficiency, and scale of [data lakes](https://www.databricks.com/discover/data-lakes/introduction) with the data management and ACID transactions of data warehouses, enabling business intelligence (BI) and machine learning (ML) on all data.


### Key Technology Enabling the Data Lakehouse

There are a few key technology advancements that have enabled the data lakehouse:

- metadata layers for data lakes
- new query engine designs providing high-performance SQL execution on data lakes
- optimized access for data science and machine learning tools.

Historically, data warehouses and data lakes had to be implemented as separate, siloed architectures to avoid overloading the underlying systems and creating contention for the same resources


## Data lakehouse features

The key data lakehouse features include: 

- **Single data low-cost data store** for all data types (structured, unstructured, and semi-structured) 
- **Data management features** to apply schema, enforce data governance, and provide ETL processes and data cleansing
- **Transaction support** for ACID (atomicity, consistency, isolation, and durability) properties to ensure data consistency when multiple users concurrently read and write data 
- **Standardized storage formats** that can be used in multiple software programs
- **End-to-end streaming** to support real-time ingestion of data and insight generation 
- **Separate compute and storage resources** to ensure scalability for a diverse set of workloads

**Direct access for BI apps** to the source data in the lakehouse to reduce data duplication.


## Benefits of using a data lakehouse

|**Simplified architecture**<br><br>A data lakehouse removes the silos of two separate platforms, so you only have to focus on managing and maintaining a single data repository. Tools can also be connected directly to source data so you don’t have to extract or prepare data to be used in a data warehouse.

|**Better data quality** <br><br>You can enforce schemas for structured data and data integrity in data lakehouse architectures, enabling you to ensure consistency. Plus, lakehouses reduce the time to make new data available, ensuring fresher data.

|**Lower costs**<br><br>Store huge volumes of data on low-cost storage and eliminate the need to maintain both a data warehouse and a data lake. Data lakehouses also help reduce costs from ETL processes and de-duplication.

**Increased reliability**<br><br>Data lakehouses reduce ETL data transfers between multiple systems, reducing the chance of quality or technical issues that can occur with data movement.

|**Improved data governance**<br><br>Data and resources get consolidated in one place with data lakehouses, making it easier to implement, test, and deliver governance and security controls.

|**Reduced data duplication**<br><br>The more copies of data that exist in disparate systems, the more likely it is to be inconsistent and less trustworthy. With data lakehouses, you can achieve a single source of data that can be shared across the business to make decisions, preventing any inconsistencies and extra storage costs caused by data duplication.

|**Diverse workloads**<br><br>You can connect multiple tools directly to the lakehouse to support analytics, SQL, machine learning, and data science workloads from the same repository.

**High scalability**<br><br>The low-cost cloud object storage of data lakehouses allows you to decouple compute from storage to provide nearly limitless and instantaneous scalability. You can scale computing power and storage separately according to your business needs.


# Predictive optimization for Unity Catalog managed tables

ALTER CATALOG [catalog_name] {ENABLE | DISABLE} PREDICTIVE OPTIMIZATION;
ALTER {SCHEMA | DATABASE} schema_name {ENABLE | DISABLE} PREDICTIVE OPTIMIZATION;


> OPTIMIZE events;

> OPTIMIZE events WHERE date >= '2017-01-01';

> OPTIMIZE events
    WHERE date >= current_timestamp() - INTERVAL 1 day
    ZORDER BY (eventType)

Delta Lake liquid clustering replaces table partitioning and `ZORDER` to simplify data layout decisions and optimize query performance. Liquid clustering provides flexibility to redefine clustering keys without rewriting existing data, allowing data layout to evolve alongside analytic needs over time.


# Use liquid clustering for Delta tables

Delta Lake liquid clustering replaces table partitioning and `ZORDER` to simplify data layout decisions and optimize query performance. Liquid clustering provides flexibility to redefine clustering keys without rewriting existing data, allowing data layout to evolve alongside analytic needs over time.

Important

Databricks recommends using Databricks Runtime 15.2 and above for all tables with liquid clustering enabled. Public preview support with limitations is available in Databricks Runtime 13.3 LTS and above.


## What is liquid clustering used for?

Databricks recommends liquid clustering for all new Delta tables. The following are examples of scenarios that benefit from clustering:

- Tables often filtered by high cardinality columns.
    
- Tables with significant skew in data distribution.
    
- Tables that grow quickly and require maintenance and tuning effort.
    
- Tables with concurrent write requirements.
    
- Tables with access patterns that change over time.
    
- Tables where a typical partition key could leave the table with too many or too few partitions.

```
-- Create an empty table
CREATE TABLE table1(col0 int, col1 string) CLUSTER BY (col0);

-- Using a CTAS statement
CREATE EXTERNAL TABLE table2 CLUSTER BY (col0)  -- specify clustering after table name, not in subquery
LOCATION 'table_location'
AS SELECT * FROM table1;

-- Using a LIKE statement to copy configurations
CREATE TABLE table3 LIKE table1;
```


[Column mapping feature](https://github.com/delta-io/delta/blob/master/PROTOCOL.md#column-mapping) allows Delta table columns and the underlying Parquet file columns to use different names. This enables Delta schema evolution operations such as `RENAME COLUMN` and `DROP COLUMNS` on a Delta table without the need to rewrite the underlying Parquet files. It also allows users to name Delta table columns by using [characters that are not allowed](https://docs.delta.io/latest/delta-column-mapping.html#-supported-characters-in-column-names) by Parquet, such as spaces, so that users can directly ingest CSV or JSON data into Delta without the need to rename columns due to previous character constraints.

  ALTER TABLE <table_name> SET TBLPROPERTIES (
    'delta.minReaderVersion' = '2',
    'delta.minWriterVersion' = '5',
    'delta.columnMapping.mode' = 'name'
  )
  ALTER TABLE <table_name> RENAME COLUMN old_col_name TO new_col_name
  ALTER TABLE table_name DROP COLUMN col_name
  ALTER TABLE table_name DROP COLUMNS (col_name_1, col_name_2, ...)
  
  ## Supported characters in column names

  When column mapping is enabled for a Delta table, you can include spaces as well as any of these characters in the table’s column names: `,;{}()\n\t=`.

**Benefits of Delta Tables**  
  
Reliability: Delta Tables provide ACID transactions and time travel capabilities, ensuring data integrity and consistency, and making it reliable for mission-critical data workloads.  
  
Scalability: Delta Tables are designed to scale horizontally, making them suitable for processing large datasets in distributed computing environments like Apache Spark.  
  
Performance: Delta Tables optimize data storage and retrieval, enabling faster query performance and reduced data scan times, resulting in improved overall performance of data processing pipelines.  
  
Flexibility: Delta Tables support schema evolution, allowing you to modify your data schema without losing any existing data, making it flexible and adaptable to changing business requirements.


## What Is Schema Evolution?

Schema evolution is a feature that allows users to easily change a table's current schema to accommodate data that is changing over time. Most commonly, it's used when performing an append or overwrite operation, to automatically adapt the schema to include one or more new columns.

```
# Add the mergeSchema option
loans.write.format("delta") \
           .option("mergeSchema", "true") \
           .mode("append") \
           .save(DELTALAKE_SILVER_PATH)
```

## What Is Schema Enforcement?

Schema enforcement, also known as **schema validation****_,_** is a safeguard in Delta Lake that ensures data quality by rejecting writes to a table that do not match the table's schema. Like the front desk manager at a busy restaurant that only accepts reservations, it checks to see whether each column in data inserted into the table is on its list of expected columns (in other words, whether each one has a "reservation"), and rejects any writes with columns that aren't on the list.


```
# Generate a DataFrame of loans that we'll append to our Delta Lake table
loans = sql("""
            SELECT addr_state, CAST(rand(10)*count as bigint) AS count,
            CAST(rand(10) * 10000 * count AS double) AS amount
            FROM loan_by_state_delta
            """)

# Show original DataFrame's schema
original_loans.printSchema()
 
"""
root
  |-- addr_state: string (nullable = true)
  |-- count: integer (nullable = true)
"""
 
# Show new DataFrame's schema
loans.printSchema()
 
"""
root
  |-- addr_state: string (nullable = true)
  |-- count: integer (nullable = true)
  |-- amount: double (nullable = true) # new column
"""
 
# Attempt to append new DataFrame (with new column) to existing table
loans.write.format("delta") \
           .mode("append") \
           .save(DELTALAKE_PATH)

""" Returns:
<span style="color: red;">
A schema mismatch detected when writing to the Delta table.
 
To enable schema migration, please set:
'.option("mergeSchema", "true")\'
 
Table schema:
root
-- addr_state: string (nullable = true)
-- count: long (nullable = true)
 
 
Data schema:
root
-- addr_state: string (nullable = true)
-- count: long (nullable = true)
-- amount: double (nullable = true)
 
If Table ACLs are enabled, these options will be ignored. Please use the ALTER TABLE command for changing the schema.
</span>
"""
```

```
# Add the mergeSchema option
loans.write.format("delta") \
           .option("mergeSchema", "true") \
           .mode("append") \
           .save(DELTALAKE_SILVER_PATH)
```

https://docs.databricks.com/en/delta/update-schema.html


Delta Lake is an open-source storage layer that is designed to bring reliability to data lakes. It is built on top of Apache Spark and provides features such as ACID transactions, schema enforcement, and time travel. Delta Lake is essentially a storage format that provides a set of features for managing data in a data lake environment.


Delta tables, on the other hand, are tables that are created using the Delta Lake storage format. Delta tables are optimized for use in data lake environments and provide features such as ACID transactions, schema enforcement, and time travel. Delta tables are essentially a specific type of table that is built on top of the Delta Lake storage format.

CI/CD:
---------
It is a set of practices used to automate and streamline the process of building testing and deploying the code changes to different code changes to different environment.