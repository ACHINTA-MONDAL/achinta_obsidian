1.![[Pasted image 20240714032011.png]]
2.What are the ways you can implement securities in Azure synapse? N/W or Row Level 
3.Performance tuning of serverless sql pool and dedicated sql pool
4.Partition options in azure synapse.
5.

![[Pasted image 20240714171433.png]]

Native external tables have better performance when compared to external tables with `TYPE=HADOOP` in their external data source definition. This is because native external tables use native code to access external data.

![[Pasted image 20240714171901.png]]


# CETAS with Synapse SQL


You can use CREATE EXTERNAL TABLE AS SELECT (CETAS) in dedicated SQL pool or serverless SQL pool to complete the following tasks:

- Create an external table
    
- Export, in parallel, the results of a Transact-SQL SELECT statement to:
    
    - Hadoop
    - Azure Storage Blob
    - Azure Data Lake Storage Gen2

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-tables-cetas?source=recommendations#cetas-in-dedicated-sql-pool)

## CETAS in dedicated SQL pool

For dedicated SQL pool, CETAS usage and syntax, check the [CREATE EXTERNAL TABLE AS SELECT](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-table-as-select-transact-sql?view=azure-sqldw-latest&preserve-view=true) article. Additionally, for guidance on CTAS using dedicated SQL pool, see the [CREATE TABLE AS SELECT](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?view=azure-sqldw-latest&preserve-view=true) article.

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-tables-cetas?source=recommendations#cetas-in-serverless-sql-pool)

## CETAS in serverless SQL pool

When using serverless SQL pool, CETAS is used to create an external table and export query results to Azure Storage Blob or Azure Data Lake Storage Gen2.

For complete syntax, refer to [CREATE EXTERNAL TABLE AS SELECT (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-table-as-select-transact-sql).
```
-- use CETAS to export select statement with OPENROWSET result to  storage
CREATE EXTERNAL TABLE population_by_year_state
WITH (
    LOCATION = 'aggregated_data/',
    DATA_SOURCE = population_ds,  
    FILE_FORMAT = census_file_format
)  
AS
SELECT decennialTime, stateName, SUM(population) AS population
FROM
    OPENROWSET(BULK 'https://azureopendatastorage.dfs.core.windows.net/censusdatacontainer/release/us_population_county/year=*/*.parquet',
    FORMAT='PARQUET') AS [r]
GROUP BY decennialTime, stateName
GO

-- you can query the newly created external table
SELECT * FROM population_by_year_state
```


```
-- use CETAS with select from external table
CREATE EXTERNAL TABLE population_by_year_state
WITH (
    LOCATION = 'aggregated_data/',
    DATA_SOURCE = population_ds,  
    FILE_FORMAT = census_file_format
)  
AS
SELECT decennialTime, stateName, SUM(population) AS population
FROM census_external_table
GROUP BY decennialTime, stateName
GO

-- you can query the newly created external table
SELECT * FROM population_by_year_state
```

# Query JSON files using serverless SQL pool in Azure Synapse Analytics

- Article
- 04/24/2023
- 13 contributors

Feedback

## In this article

1. [Read JSON documents](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#read-json-documents)
2. [Parse JSON documents](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#parse-json-documents)
3. [Next steps](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#next-steps)

In this article, you'll learn how to write a query using serverless SQL pool in Azure Synapse Analytics. The query's objective is to read JSON files using [OPENROWSET](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-openrowset).

- Standard JSON files where multiple JSON documents are stored as a JSON array.
- Line-delimited JSON files, where JSON documents are separated with new-line character. Common extensions for these types of files are `jsonl`, `ldjson`, and `ndjson`.

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#read-json-documents)

## Read JSON documents

The easiest way to see to the content of your JSON file is to provide the file URL to the `OPENROWSET` function, specify csv `FORMAT`, and set values `0x0b` for `fieldterminator` and `fieldquote`. If you need to read line-delimited JSON files, then this is enough. If you have classic JSON file, you would need to set values `0x0b` for `rowterminator`. `OPENROWSET` function will parse JSON and return every document in the following format:

Expand table

|doc|
|---|
|{"date_rep":"2020-07-24","day":24,"month":7,"year":2020,"cases":3,"deaths":0,"geo_id":"AF"}|
|{"date_rep":"2020-07-25","day":25,"month":7,"year":2020,"cases":7,"deaths":0,"geo_id":"AF"}|
|{"date_rep":"2020-07-26","day":26,"month":7,"year":2020,"cases":4,"deaths":0,"geo_id":"AF"}|
|{"date_rep":"2020-07-27","day":27,"month":7,"year":2020,"cases":8,"deaths":0,"geo_id":"AF"}|

If the file is publicly available, or if your Microsoft Entra identity can access this file, you should see the content of the file using the query like the one shown in the following examples.

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#read-json-files)

### Read JSON files

The following sample query reads JSON and line-delimited JSON files, and returns every document as a separate row.

SQLCopy

```
select top 10 *
from openrowset(
        bulk 'https://pandemicdatalake.blob.core.windows.net/public/curated/covid-19/ecdc_cases/latest/ecdc_cases.jsonl',
        format = 'csv',
        fieldterminator ='0x0b',
        fieldquote = '0x0b'
    ) with (doc nvarchar(max)) as rows
go
select top 10 *
from openrowset(
        bulk 'https://pandemicdatalake.blob.core.windows.net/public/curated/covid-19/ecdc_cases/latest/ecdc_cases.json',
        format = 'csv',
        fieldterminator ='0x0b',
        fieldquote = '0x0b',
        rowterminator = '0x0b' --> You need to override rowterminator to read classic JSON
    ) with (doc nvarchar(max)) as rows
```

The JSON document in the preceding sample query includes an array of objects. The query returns each object as a separate row in the result set. Make sure that you can access this file. If your file is protected with SAS key or custom identity, you would need to set up [server level credential for sql login](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-storage-files-storage-access-control?tabs=shared-access-signature#server-level-credential).

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#data-source-usage)

### Data source usage

The previous example uses full path to the file. As an alternative, you can create an external data source with the location that points to the root folder of the storage, and use that data source and the relative path to the file in the `OPENROWSET` function:

SQLCopy

```
create external data source covid
with ( location = 'https://pandemicdatalake.blob.core.windows.net/public/curated/covid-19/ecdc_cases' );
go
select top 10 *
from openrowset(
        bulk 'latest/ecdc_cases.jsonl',
        data_source = 'covid',
        format = 'csv',
        fieldterminator ='0x0b',
        fieldquote = '0x0b'
    ) with (doc nvarchar(max)) as rows
go
select top 10 *
from openrowset(
        bulk 'latest/ecdc_cases.json',
        data_source = 'covid',
        format = 'csv',
        fieldterminator ='0x0b',
        fieldquote = '0x0b',
        rowterminator = '0x0b' --> You need to override rowterminator to read classic JSON
    ) with (doc nvarchar(max)) as rows
```

If a data source is protected with SAS key or custom identity, you can configure [data source with database scoped credential](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-storage-files-storage-access-control?tabs=shared-access-signature#database-scoped-credential).

In the following sections, you can see how to query various types of JSON files.

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#parse-json-documents)

## Parse JSON documents

The queries in the previous examples return every JSON document as a single string in a separate row of the result set. You can use functions `JSON_VALUE` and `OPENJSON` to parse the values in JSON documents and return them as relational values, as it's shown in the following example:

Expand table

|date_rep|cases|geo_id|
|---|---|---|
|2020-07-24|3|AF|
|2020-07-25|7|AF|
|2020-07-26|4|AF|
|2020-07-27|8|AF|

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#sample-json-document)

### Sample JSON document

The query examples read _json_ files containing documents with following structure:

JSONCopy

```
{
    "date_rep":"2020-07-24",
    "day":24,"month":7,"year":2020,
    "cases":13,"deaths":0,
    "countries_and_territories":"Afghanistan",
    "geo_id":"AF",
    "country_territory_code":"AFG",
    "continent_exp":"Asia",
    "load_date":"2020-07-25 00:05:14",
    "iso_country":"AF"
}
```

 Note

If these documents are stored as line-delimited JSON, you need to set `FIELDTERMINATOR` and `FIELDQUOTE` to 0x0b. If you have standard JSON format you need to set `ROWTERMINATOR` to 0x0b.

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#query-json-files-using-json_value)

### Query JSON files using JSON_VALUE

The query below shows you how to use [JSON_VALUE](https://learn.microsoft.com/en-us/sql/t-sql/functions/json-value-transact-sql?view=azure-sqldw-latest&preserve-view=true) to retrieve scalar values (`date_rep`, `countries_and_territories`, `cases`) from a JSON documents:

SQLCopy

```
select
    JSON_VALUE(doc, '$.date_rep') AS date_reported,
    JSON_VALUE(doc, '$.countries_and_territories') AS country,
    CAST(JSON_VALUE(doc, '$.deaths') AS INT) as fatal,
    JSON_VALUE(doc, '$.cases') as cases,
    doc
from openrowset(
        bulk 'latest/ecdc_cases.jsonl',
        data_source = 'covid',
        format = 'csv',
        fieldterminator ='0x0b',
        fieldquote = '0x0b'
    ) with (doc nvarchar(max)) as rows
order by JSON_VALUE(doc, '$.geo_id') desc
```

Once you extract JSON properties from a JSON document, you can define column aliases and optionally cast the textual value to some type.

[](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-json-files?source=recommendations#query-json-files-using-openjson)

### Query JSON files using OPENJSON

The following query uses [OPENJSON](https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql?view=azure-sqldw-latest&preserve-view=true). It will retrieve COVID statistics reported in Serbia:

SQLCopy

```
select
    *
from openrowset(
        bulk 'latest/ecdc_cases.jsonl',
        data_source = 'covid',
        format = 'csv',
        fieldterminator ='0x0b',
        fieldquote = '0x0b'
    ) with (doc nvarchar(max)) as rows
    cross apply openjson (doc)
        with (  date_rep datetime2,
                cases int,
                fatal int '$.deaths',
                country varchar(100) '$.countries_and_territories')
where country = 'Serbia'
order by country, date_rep desc;
```

The results are functionally same as the results returned using the `JSON_VALUE` function. In some cases, `OPENJSON` might have advantage over `JSON_VALUE`:

- In the `WITH` clause you can explicitly set the column aliases and the types for every property. You don't need to put the `CAST` function in every column in `SELECT` list.
- `OPENJSON` might be faster if you are returning a large number of properties. If you are returning just 1-2 properties, the `OPENJSON` function might be overhead.
- You must use the `OPENJSON` function if you need to parse the array from each document, and join it with the parent row.




![[Pasted image 20240714214310.png]]

![[Pasted image 20240714214355.png]]

![[Pasted image 20240715003713.png]]
![[Pasted image 20240715014754.png]]

![[Pasted image 20240715130849.png]]
![[Pasted image 20240715135014.png]]

> exec sp_refreshview @viewname

Date:Tuesday, July 16, 2024

Start Time: 04:50pm

End Time: 05:30pm

Time Zone:IST

Location: https://deloitte.zoom.us/j/95040772819?pwd=wBaReHQWEiuU7jnyhazNRrcTdxanax.1 Passcode: 222547