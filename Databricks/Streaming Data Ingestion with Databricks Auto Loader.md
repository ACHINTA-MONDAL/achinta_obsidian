![](https://miro.medium.com/v2/resize:fit:1400/1*QI7R_UfAM0r5BpXLhZM6wQ.png)

**Use case:** As part of out Data Ingestion framework we wanted to adapt to a robust, scalable and reusable ingestion mechanism which can cater to both batch as well as Streaming ingestion patterns. The ingestion mechanism should be able to leverage the existing auto scale infrastructure, data quality checks, schema evolution and monitoring.

## What is Auto Loader ?

Autoloader is an optimized _cloud file_ source for **_Apache Spark_** that loads data continuously and efficiently from cloud storage as new data arrives. Auto Loader combines the three approaches of traditional stream based ingestion patterns

1. Storing Metadata about what has been read: The metadata is persisted in a scalable key-value store (RocksDB) in the checkpoint location of Auto Loader pipeline.
2. Using Structured Streaming for immediate processing: Auto Loader provides a Structured Streaming source called **_cloudFiles_**. Given an input directory path on the cloud file storage, the **_cloudFiles_** source automatically processes new files as they arrive, with the option of also processing existing files in that directory.
3. Using Cloud-Native components to optimize identifying newly arriving files: Auto Loader automatically sets up a notification service and queue service that subscribes to file events from the input directory. You can use file notifications to scale Auto Loader to ingest millions of files an hour.

## Auto Loader Job

An Autoloader job has two parts:

1. **CloudFiles** DataReader
2. **CloudNotification** Services (optional)

Reading data into a Spark DataFrame

```
df = (spark  
        .readStream   # a streaming dataframe  
        .format("cloudFiles")  # tells Spark to use AutoLoader  
        .option("cloudFiles.format", "json")  # the actual format of out data files. Tells AutoLoader to expect json files  
        .option("cloudFiles.useNotifications",True) # Should AutoLoader use a notification queue  
        .schema(some_custom_schema)  # custom schema of the actual data file  
        .load(f"{actual_data_location}/directory") # location of the actual data file  
    )
```

## Auto Loader file detection modes

Auto Loader supports two file detection modes

1. Directory Listing mode: Auto Loader uses directory listing mode by **_default_**. In directory listing mode, Auto Loader identifies new files by listing the input directory. Directory listing mode allows you to **_quickly start Auto Loader streams without any permission configurations_** other than access to your data on cloud storage.
2. File Notification mode: Auto Loader automatically sets up a notification service and queue service that subscribes to file events from the input directory. You can use file notifications to scale Auto Loader to ingest millions of files an hour. **_When compared to directory listing mode, file notification mode is more performant and scalable for large input directories or a high volume of files but requires additional cloud permissions._**

![](https://miro.medium.com/v2/resize:fit:1400/1*8-H4jn1hKYvCvriJxxClzQ.png)

File Notification mode working

## Setup for File Notification mode

## Pre-requisites

1. A Service Principal for authentication

2. Assign the Service Principal created in Step 1 **“Contributor”** and **“Storage Queue Data Contributor”** roles to the storage account in which the input path resides.

![](https://miro.medium.com/v2/resize:fit:1400/1*H22ngAlLqnkZCO0mZtRhEw.png)

Contributor and Storage Queue Data Contributor role assignment at Storage account.

3. Assign the Service Principal created in Step 1 “**EventGrid EventSubscription Contributor**” role to the related resource group:

![](https://miro.medium.com/v2/resize:fit:1400/1*9hhWL15-b4bUQ89-vWsxnw.png)

EventGrid EventSubscription Contributor role assignment at Resource Group.

## Configuration Changes

The following configuration parameters has to be provided during reading the Spark DataFrame

file_path = "abfss://parent-container-name@storage-account-name.dfs.core.windows.net/raw/"  
schema_path = "abfss://parent-container-name@storage-account-name.dfs.core.windows.net/schema/"  
  
streaming_df = (spark.readStream  
             .format("cloudFiles")  # Tells Spark to use Auto Loader  
             .option("cloudFiles.format", "csv") # The actual format of raw data file  
             .option("cloudFiles.schemaLocation", schema_path) # The storage path were schema files will be saved  
             .option("cloudFiles.clientId", "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxx") # The application/client ID of the Service Principal  
             .option("cloudFiles.clientSecret", "xxxxxxxxxxxxxxxxxx") # The client secret value  
             .option("cloudFiles.tenantId", "xxxxxx-xxxx-xxxx-xxxx") # The tenant ID  
             .option("cloudFiles.subscriptionId", "xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx") # The Azure resource subscription ID  
             .option("cloudFiles.connectionString","DefaultEndpointsProtocol=https;AccountName=<storage-account-name>;AccountKey=<account-key>;EndpointSuffix=core.windows.net")  
             .option("cloudFiles.resourceGroup", "xxxxxxxxxxxxxxx") # The Azure Resource Group Name  
             .option("cloudFiles.useNotifications", True) # Has to be set to true to enable file notification mode  
             .option("header", True)  
             .load(file_path) # The actual file path  
           )

All the cloudFile configuration can be grouped together and passed as one single config.
```

autoloader_config = {  
"cloudFiles.format":"csv",  
"cloudFiles.clientId": client_id,  
"cloudFiles.clientSecret": client_secret,  
"cloudFiles.tenantId": tenant_id,  
"cloudFiles.subscriptionId": subscription_id,  
"cloudFiles.connectionString": connection_string,  
"clientFiles.resourceGroup": resource_group,  
"cloudFiles.schemaLocation":schema_location,  
"clientFiles.useNotifications": "true",  
"header": True  
}  
  
streaming_df = (spark  
      .readStream  
      .format("cloudFiles")  
      .options(**autoloader_config)  
      .load(source_directory)  
      )
```

You should be able to see an active event subscription and storage queue created.

![](https://miro.medium.com/v2/resize:fit:1400/1*JW2SLr5iARmM9GIZD-x06Q.png)

![](https://miro.medium.com/v2/resize:fit:1400/1*NJSmXmVkxZoK2B8WAYrlOA.png)

## Auto Loader to run Batch job (Batch ETL Pattern)

Auto Loader can be scheduled to run in Databricks Jobs as a batch job by using Trigger.AvailableNow. The AvailableNow trigger will instruct Auto Loader to process all files that arrived before the query start time. New files that are uploaded after the stream has started are ignored until the next trigger.

With Trigger.AvailableNow, file discovery happens asynchronously with data processing and data can be processed across multiple micro-batches with rate limiting.
```

def batch_process():  
    
    query = (spark.readStream  
                        .format("cloudFiles")  
                        .option("cloudFiles.format", "json")  
                        .schema(schema)  
                        .load(raw_path)  
                        .writeStream  
                        .option("checkpointLocation", checkpoint_location)  
                        .trigger(availableNow=True)  
                        .table(table_name))  
      
    query.awaitTermination()
```

## Auto Loader to run Merge patterns

Auto Loader can be used to ingest data into already existing tables. This would be useful in implementing solution which need **_upsert_** operations to be performed on the already existing dataset.

```
```
from  delta.tables import *  
streaming_df = (spark  
      .readStream  
      .format("cloudFiles")  
      .options(**autoloader_config)  
      .load(source_directory)  
      )  
  
def upsertToDelta(microBatchDF, bacthId):  
  
  delta_df = DeltaTable.forName(spark, "ExistingTable")  
  (delta_df.alias("t")  
    .merge(microBatchDF.alias("m"),  
    "m.commonColumn = t.commonColumn"),  
    .whenMatchedUpdateAll()  
    .whenNotMatchedInsertAll()  
    .execute()  
  )  
  
query = (streaming_df  
                     .writeStream  
                     .outputMode("append")  
                     .foreachBatch(upsertToDelta)  
                     .option("checkpointLocation", checkpoint_location)  
                     .trigger(availableNow=True)  
                     .start()  
          )
```
```

## Schema Evolution with Auto Loader

Auto Loader is able to infer the schema using the following

1. schemaLocation: Persistent storage location where all schemas are stored (schema metastore).
2. inferColumnType: Sample the data to infer the data type. Inference can be controlled by specifying number of records or size.
3. schemaHints: Manually specify the data types for key columns.

**Schema Evolution mode options (**cloudFiles.schemaEvolutionMode**_)_**

a. addNewColumns: Fail the ongoing streaming job, **_update the schema metastore_**. During an ongoing batch if there is a new column determined, it will fail the job and update the metastore with a new version of schema for the object. **_On restart the job will pass_** as the new schema file will be picked.

b. failonNewColumns: Fail the ongoing streaming job, **_make no updates to the schema metastore_**. If a schema change is determined, the ongoing job fails without making any updates to metastore. This scenario has to be **_manually checked as the job will fail again on restart._**

c. rescue: Do not fail, put all unexpected columns into **__rescued_data._** Any unexpected columns will be written to a new column (_rescued_data) which can be renamed.

d. none: Ignore any new columns.


```
schema_config = {  
  "cloudFiles.inferColumnTypes": "true",  
  "cloudFiles.schemaHints": "ID int, price decimal",    
  "cloudFiles.schemaLocation": "schema_location",  
  "cloudFiles.schemaEvolutionMode": "rescue",  
  "rescuedDataColumn": "extra_columns"  
  }
```
