Both are the queries for creating table from select statements. CTAS refers to creating table while CETAS refers to creating an external table. First, we need to understand when we need external tables. And when to use when.

In azure synapse analytics, there are 2 kinds of SQL pools:

- Serverless SQL Pool
- Dedicated SQL Pool

In dedicated SQL pool, a compute engine is assigned and as long as this resource is active , costing takes place. This is required to store the data as well as to compute queries.

But in the case of built-in SQL, there is no such engine available. Therefore no direct storage capacity. But, here we can leverage storage like hadoop ,azure blob storage , Azure Data Lake. Data could be read/write from the files over there . It works as an abstract layer of a table. It is a kind of logical database where only the metadata is stored. Whenever a query is fired, it goes to the storage and reads data from there. And we can leverage T SQL to query the data.

In a nutshell, whenever we are required to leverage the storage of azure, creating an external table could be used. In case of external table, it could be used to write/store the data on azure storage like data lake gen2.

It could be used to import that data from files to tables in dedicated sql pool.

Don’t get confused, external tables could be used both in built-in as well as dedicated sql pool while normal table could be used only in dedicated sql pool.

# CTAS (Create Table As Select)

When using CTAS in Azure Synapse Analytics, a new table is created based on the results of a SELECT statement. This is a useful operation when you want to create a new table that is based on the results of a complex query. The syntax for the CTAS statement is as follows:

CREATE TABLE new_table AS SELECT * FROM existing_table

# CETAS (Create External Table As Select)

When using CETAS in Azure Synapse Analytics, a new external table is created based on the results of a SELECT statement. This is useful when you want to create a table that references data that is stored outside of the Synapse Analytics workspace. The syntax for the CETAS statement is as follows:

`CREATE EXTERNAL TABLE new_table`  
`(<column definition>)`  
`WITH`   
`(`  
    `DATA_SOURCE = data_source_name,`  
    `LOCATION = 'path_to_folder',`  
    `FILE_FORMAT = CsvFormat/ParquetFormat`  
`) AS SELECT * FROM existing_table (or using OPENROWSET)`

Note that the `LOCATION` parameter specifies the location of the external data.

To create an external table, it is required to create first data source and file format.

# Key Differences

The main difference between CTAS and CETAS is that CTAS creates an internal table within the Synapse Analytics workspace, while CETAS creates an external table that references data stored outside of the workspace. CTAS tables are stored in the workspace’s storage account, while CETAS tables reference data stored in an external location such as Azure Data Lake Storage or Azure Blob Storage.

Another key difference is that CTAS tables are optimized for performance and can take advantage of Synapse Analytics’s distributed query processing capabilities, while CETAS tables are limited by the performance of the external data source.

Overall, CTAS and CETAS are both useful tools for creating new tables based on the results of a SELECT statement, but the choice between the two will depend on the specific needs of your data workflow.

**Tips**

To get quick hands-on external sources on Azure Synapse analytics, I would recommend doing this lab which is provided by Microsoft.

[https://microsoftlearning.github.io/DP-500-Azure-Data-Analyst/Instructions/labs/01-analyze-data-with-sql.html](https://microsoftlearning.github.io/DP-500-Azure-Data-Analyst/Instructions/labs/01-analyze-data-with-sql.html)