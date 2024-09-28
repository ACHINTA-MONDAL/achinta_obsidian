
Spark Streaming has emerged as a dominant force as a streaming framework, known for its scalable, high-throughput, and fault-tolerant handling of live data streams. While Spark Streaming and Databricks Autoloader inherently support standard file formats like JSON, CSV, PARQUET, AVRO, TEXT, BINARYFILE, and ORC, their versatility extends far beyond these. This blog post delves into the innovative use of Spark Streaming and Databricks Autoloader for processing file types which are not natively supported.

# The Process Flow:

1. **File Detection with Autoloader**: Autoloader identifies new files, an essential step for real-time data processing. It ensures every new file is detected and queued for processing, providing the actual file path for reading.
2. **Custom UDF for File Parsing:** We develop a custom User-Defined Function (UDF) to manage unsupported file types. This UDF is crafted specifically for reading and processing the designated file format.
3. **Data Processing and Row Formation**: Within the UDF, we process the file content, transforming it into structured data, usually in row format.
4. **Writing Back to Delta Table**: We then write the processed data back to a Delta table for further use.

In the below example is for ROS Bag but the same method could be translated for **any other file type.**

![](https://miro.medium.com/v2/resize:fit:1400/0*AC8LOigS5YGj3E84)

Photo by [Mattias Olsson](https://unsplash.com/@mattiaswolsson?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com/?utm_source=medium&utm_medium=referral)

## Setting Up the Environment

Firstly, we need to prepare our Databricks environment:

```
# Databricks notebook source  
# MAGIC %pip install bagpy  
dbutils.library.restartPython()
```

We install `bagpy`, a Python library for ROS bag files, and restart the Python environment to ensure the library is properly loaded.Importing Necessary Libraries

Next, we import the required Python libraries:

```
from typing import List, Dict  
import boto3  
import rosbag  
import tempfile  
from pyspark.sql.functions import udf, explode  
from pyspark.sql.types import ArrayType, StructType, StructField, IntegerType, LongType, FloatType  
from pyspark.sql import SparkSession
```

These imports include standard data manipulation tools, AWS S3 access (`boto3`), ROS bag reading capabilities (`rosbag`), and necessary PySpark components.

# Detect new files and file path using Autoloader

```
# Spark streaming setup for ROS bag files  
s3_data_path = "s3a://one-env/jiteshsoni/Vehicle/"  
table_name = "rosbag_imu"  
checkpoint_location = f"/tmp/checkpoint/{table_name}/"  
  
stream_using_autoloader_df = (spark.readStream  
                    .format("cloudFiles")  
                    .option("cloudFiles.format", "binaryfile")  
                    .option("cloudFiles.includeExistingFiles", "true")  
                    .load(s3_data_path)  
                    )  
```
  
display(stream_using_autoloader_df)Custom UDF to read & parse any file type

![](https://miro.medium.com/v2/resize:fit:1400/1*Vu9gZvt6lHLc6XvP9wD5Ew.png)

The core function `extract_rosbag_data` reads data from a ROS bag file in an S3 bucket and returns a list of dictionaries containing the extracted data:

```
def extract_rosbag_data(s3_rosbag_path: str) -> List[Dict]:  
    """  
    Extracts data from a ROS bag file stored in S3, converting it into a list of dictionaries.  
  
    Args:  
        s3_rosbag_path (str): The S3 path to the ROS bag file.  
  
    Returns:  
        List[Dict]: A list of dictionaries with data from the ROS bag.  
    """  
    interested_topics = ['/ublox_trunk/ublox/esfalg']  
    extracted_data = []  
  
    # Extracting the S3 bucket and file key from the provided path  
    bucket_name, s3_file_key = s3_rosbag_path.split('/', 3)[2:4]  
  
    # Using boto3 to download the ROS bag file into memory  
    s3 = boto3.resource('s3')  
    obj = s3.Object(bucket_name, s3_file_key)  
    file_stream = obj.get()['Body'].read()  
  
    # Storing the downloaded file temporarily  
    with tempfile.NamedTemporaryFile() as temp_file:  
        temp_file.write(file_stream)  
        temp_file.flush()  
  
        # Reading messages from the ROS bag file  
        with rosbag.Bag(temp_file.name, 'r') as bag:  
            for topic, msg, timestamp in bag.read_messages(topics=interested_topics):  
                message_data = {field: getattr(msg, field) for field in msg.__slots__}  
                message_data['timestamp'] = timestamp.to_sec()  
                extracted_data.append(message_data)  
  
    return extracted_data
```

This function uses `boto3` to access the S3 bucket, reads the ROS bag file, and extracts the relevant data. At this point, we should test the function before we proceed. For your use case, you want to change this function to read your file type.

```
extract_rosbag_data(s3_rosbag_path= "s3a://bucket_name/jiteshsoni/Vehicle/2023-08-04-16-30-24_63.bag")
```

Things to note here: In this example, _I am downloading the file on the cluster which could be avoided depending if your file reader supports it._

## Defining the Data Schema

Before ingesting data into Spark, define the schema that aligns with the data structure in ROS bags. This is important because Spark needs to know what schema to expect.

```
# Define the schema that matches your ROS bag data structure  
rosbag_schema = ArrayType(StructType([  
    StructField("Alpha", LongType(), True),  
    StructField("Beta", IntegerType(), True),  
    StructField("Gamma", IntegerType(), True),  
    StructField("Delta", IntegerType(), True),  
    StructField("Epsilon", IntegerType(), True),  
    StructField("Zeta", IntegerType(), True),  
    StructField("Eta", IntegerType(), True),  
    StructField("Theta", IntegerType(), True),  
    StructField("Iota", FloatType(), True)  
]))  
```
  
# Creating a User Defined Function (UDF) for processing ROS bag files  
process_rosbag_udf = udf(extract_rosbag_data, returnType=rosbag_schema)

Now let’s test with if Autoloader & Parsing if custom UDF is working using the display command

```
rosbag_stream_df = (stream_using_autoloader_df  
                    .withColumn("rosbag_rows", process_rosbag_udf("path"))  
                    .withColumn("extracted_data", explode("rosbag_rows"))  
                    .selectExpr("extracted_data.*", "_metadata.*")  
                   )  
```
# Displaying the DataFrame  
display(rosbag_stream_df)

# Writing the Stream to a Delta Table

Finally, we write the streaming data to a Delta table, enabling further processing or querying:

```
streaming_write_query = (  
    rosbag_stream_df.writeStream  
    .format("delta")  
    .option("mergeSchema", "true")  
    .option("queryName", f"IngestFrom_{s3_data_path}_AndWriteTo_{table_name}")  
    .option("checkpointLocation", checkpoint_location)  
    .trigger(availableNow=True)  
    .toTable(table_name)  
)
```

# Best Practices & Considerations

1. Write UDFs (User-Defined Functions) that are efficient and optimized to minimize processing time and resource utilization.
2. Implement graceful exception handling in UDFs to avoid disruptions in the data pipeline.
3. Access files directly from the cloud within UDFs, rather than downloading them.
4. Understand that UDFs operate on Spark Executors, not on the driver, with parallelization occurring at the file level.
5. Be aware that large files (around 2GB) are processed serially by UDFs, which can affect performance.
6. Adjust Spark executor memory settings if you encounter out-of-memory errors with large files.
7. Aim for similar file sizes in your data pipeline to ensure better resource utilization.
8. If Auto Loader supports your file format natively, prefer using it for better integration and performance.