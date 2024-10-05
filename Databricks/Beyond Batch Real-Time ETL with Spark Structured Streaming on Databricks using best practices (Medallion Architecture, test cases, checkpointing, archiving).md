![](https://miro.medium.com/v2/resize:fit:1400/0*zFwd1aLGgMjbsWwE.jpeg)

[https://miro.medium.com/v2/resize:fit:800/1*qn2gItW3lIvbDtrKlQgtww.jpeg](https://miro.medium.com/v2/resize:fit:800/1*qn2gItW3lIvbDtrKlQgtww.jpeg)

In the dynamic landscape of big data analytics, the demand for real-time insights has become paramount. As organizations strive to make data-driven decisions on the fly, traditional batch processing systems are giving way to more agile and responsive solutions. Enter Spark Structured Streaming, a revolutionary extension of the Apache Spark ecosystem designed to seamlessly integrate real-time data processing into the world of big data.

In this blog we will learn about spark structured streaming using databricks community edition following the best practices, but there are a few pre-requisites for this blog:

**Pre-requisites:**

1. Python
2. Pyspark DataFrame API
3. Spark SQL
4. Databricks UI basic familiarity.

![](https://miro.medium.com/v2/resize:fit:1382/1*cZZrcleBjs2hIGfsXK0Reg.png)

> **Spark streaming execution plan**
> 
> Apache Spark Streaming execution involves a series of steps, from receiving data to processing it in batches. The streaming application starts by ingesting data from a source, such as Kafka, Flume, or custom receivers. we use read stream to read data from a landing zone or from a streaming source.
> 
> We then apply some transformations, do some processing, prepare the result and use right stream to write it to a table or a streaming sink, this is known as the high level spark execution plan.
> 
> **How spark engine will execute this streaming execution plan ?**
> 
> A spark will start a background thread to manage and coordinate the execution of this streaming execution plan. **This background thread is known as streaming query of this execution plan.**
> 
> **Each streaming execution plan will have its own streaming query**
> 
> Once the Streaming execution plan is ready, A spark driver will start a streaming query for that execution plan, and as soon as the streaming query starts, it will prepare the checkpoint location. **Checkpoint location is nothing but a directory location where streaming query will keep some housekeeping information.** So the first thing that is streaming query will do is to initialize the checkpoint location and then it goes and looks into the streaming data source and look into the location and check if there are data files available for processing, If there are no data files available for processing, streaming Query will keep a watch on the landing zone directory and wait.
> 
> Once the data is available in the landing zone, what this streaming query will do, It will note down the file name and update that information in the checkpoint location and then it will trigger the Micro-batch. **Each trigger or each execution of this execution plan is known as batch.** Stream will write the result into a table or a streaming sink.

**Types of stream triggers**

1. Unspecified Trigger: If we don’t specify any kind of trigger it is assumed to be unspecified trigger (which is the default) , in case of unspecified trigger, a streaming query will trigger one micro batch to process your data, once that data is processed the first micro batch is complete. It will immediately trigger the next micro batch, and when the next one finishes, it will immediately trigger the next micro batch and that’s what unspecified trigger means.
2. Fixed Interval: Interval Microbatches will be kicked off at a user specified interval.
3. Available now: One time micro batch trigger to process all the available data and the stop on its own.

**Types of streaming sources**

1. File/Directory
2. Delta Files
3. Kafka
4. Other Connectors

**Types of sinks**

1. File/Directory
2. Delta table
3. Kafka
4. Foreach
5. Other connectors

## Project

We will now create a mini project to implement what we learnt in theory, taking a use case and building a solution for the same, we will also use the best practices like building test cases and using medallion architecture.

> A **medallion architecture** is a data design pattern used to logically organize data in a lakehouse, with the goal of incrementally and progressively improving the structure and quality of data as it flows through each layer of the architecture (from Bronze ⇒ Silver ⇒ Gold layer tables). Medallion architectures are sometimes also referred to as “multi-hop” architectures.

**Use case:**

Imagine you’re part of a retail store selling kitchen stuff and home decorations. People can buy things in different ways: on their phones, on a website, or by coming to the store. All the sales generate invoices, and these invoices end up on a central system, like a big computer that stores all the information. We’re not getting into the nitty-gritty details of that system. Our goal is to ingest the data, process it and produce the results.

**Solution:**

We will follow the medallion architecture, we will have 2 parts:

1. Bronze layer: Read data from the landing zone, ingest the data and create a raw data table. (One single independent stream processing application which only cares about ingesting the raw data and creating a table)
2. Silver layer: Separate application which starts from reading the raw data table and applies the rest of the processing.

**Let’s Code**

Step1 : Start a cluster and download the invoice data from below and upload it on the databricks.

[https://github.com/shorya1996/PySpark/blob/main/invoices.zip](https://github.com/shorya1996/PySpark/blob/main/invoices.zip)

I have created a new path inside My DBFS with the name spark_structured_streaming/invoices/ and inside that I have placed all the invoices files.

![](https://miro.medium.com/v2/resize:fit:1400/1*WYf-hIPIUlmfGKb7P17nwA.png)

Step 2: Create a folder inside your user name in the workspace with the name SparkStreaming and then create a Notebook with the name **Spark_streaming_medallion** and write the below code for bronze layer.

```
class Bronze():  
    def __init__(self):  
        self.base_data_dir = "/FileStore/spark_structured_streaming"  
  
    def getSchema(self):  
        return """InvoiceNumber string, CreatedTime bigint, StoreID string, PosID string, CashierID string,  
                CustomerType string, CustomerCardNo string, TotalAmount double, NumberOfItems bigint,   
                PaymentMethod string, TaxableAmount double, CGST double, SGST double, CESS double,   
                DeliveryType string,  
                DeliveryAddress struct<AddressLine string, City string, ContactNumber string, PinCode string,   
                State string>,  
                InvoiceLineItems array<struct<ItemCode string, ItemDescription string,   
                    ItemPrice double, ItemQty bigint, TotalValue double>>  
            """  
  
    def readInvoices(self):  
        return (spark.readStream  
                    .format("json")  
                    .schema(self.getSchema())  
                    #.option("cleanSource", "delete")  
                    .option("cleanSource", "archive")  
                    .option("sourceArchiveDir", f"{self.base_data_dir}/data/invoices_archive")  
                    .load(f"{self.base_data_dir}/data/invoices")  
                )    
  
    def process(self):  
        print(f"\nStarting Bronze Stream...", end='')  
        invoicesDF = self.readInvoices()  
        sQuery =  ( invoicesDF.writeStream  
                            .queryName("bronze-ingestion")  
                            .option("checkpointLocation", f"{self.base_data_dir}/chekpoint/invoices_bz")  
                            .outputMode("append")  
                            .toTable("invoices_bz")             
                    )   
        print("Done")  
        return sQuery
```

write the below code for Silver layer

```
class Silver():  
    def __init__(self):  
        self.base_data_dir = "/FileStore/spark_structured_streaming"  
  
    def readInvoices(self):  
        return ( spark.readStream  
                    .table("invoices_bz")  
                )  
  
    def explodeInvoices(self, invoiceDF):  
        return ( invoiceDF.selectExpr("InvoiceNumber", "CreatedTime", "StoreID", "PosID",  
                                      "CustomerType", "PaymentMethod", "DeliveryType", "DeliveryAddress.City",  
                                      "DeliveryAddress.State","DeliveryAddress.PinCode",   
                                      "explode(InvoiceLineItems) as LineItem")  
                                    )    
             
    def flattenInvoices(self, explodedDF):  
        from pyspark.sql.functions import expr  
        return( explodedDF.withColumn("ItemCode", expr("LineItem.ItemCode"))  
                        .withColumn("ItemDescription", expr("LineItem.ItemDescription"))  
                        .withColumn("ItemPrice", expr("LineItem.ItemPrice"))  
                        .withColumn("ItemQty", expr("LineItem.ItemQty"))  
                        .withColumn("TotalValue", expr("LineItem.TotalValue"))  
                        .drop("LineItem")  
                )  
          
    def appendInvoices(self, flattenedDF):  
        return (flattenedDF.writeStream  
                    .queryName("silver-processing")  
                    .format("delta")  
                    .option("checkpointLocation", f"{self.base_data_dir}/chekpoint/invoice_line_items")  
                    .outputMode("append")  
                    .toTable("invoice_line_items")  
        )  
  
    def process(self):  
           print(f"\nStarting Silver Stream...", end='')  
           invoicesDF = self.readInvoices()  
           explodedDF = self.explodeInvoices(invoicesDF)  
           resultDF = self.flattenInvoices(explodedDF)  
           sQuery = self.appendInvoices(resultDF)  
           print("Done\n")  
           return sQuery

```
Step 3: Create another notebook and name it **Spark_streaming_medallion_test_suite**.

```
%run ../SparkStreaming/Spark-streaming-medallion  
  
class medallionApproachTestSuite():  
    def __init__(self):  
        self.base_data_dir = "/FileStore/spark_structured_streaming"  
  
    def cleanTests(self):  
        print(f"Starting Cleanup...", end='')  
        spark.sql("drop table if exists invoices_bz")  
        spark.sql("drop table if exists invoice_line_items")  
        dbutils.fs.rm("/user/hive/warehouse/invoices_bz", True)  
        dbutils.fs.rm("/user/hive/warehouse/invoice_line_items", True)  
  
        dbutils.fs.rm(f"{self.base_data_dir}/chekpoint/invoices_bz", True)  
        dbutils.fs.rm(f"{self.base_data_dir}/chekpoint/invoice_line_items", True)  
  
        dbutils.fs.rm(f"{self.base_data_dir}/data/invoices_archive", True)  
        dbutils.fs.rm(f"{self.base_data_dir}/data/invoices", True)  
        dbutils.fs.mkdirs(f"{self.base_data_dir}/data/invoices")  
        print("Done")  
  
    def ingestData(self, itr):  
        print(f"\tStarting Ingestion...", end='')  
        dbutils.fs.cp(f"{self.base_data_dir}/invoices/invoices_{itr}.json", f"{self.base_data_dir}/data/invoices/")  
        print("Done")  
  
    def assertResult(self, expected_count):  
        print(f"\tStarting validation...", end='')  
        actual_count = spark.sql("select count(*) from invoice_line_items").collect()[0][0]  
        assert expected_count == actual_count, f"Test failed! actual count is {actual_count}"  
        print("Done")  
  
    def waitForMicroBatch(self, sleep=30):  
        import time  
        print(f"\tWaiting for {sleep} seconds...", end='')  
        time.sleep(sleep)  
        print("Done.")      
  
    def runTests(self):  
        self.cleanTests()  
        bzStream = Bronze()  
        bzQuery = bzStream.process()  
  
        slStream = Silver()  
        slQuery = slStream.process()  
  
        print("\nTesting first iteration of invoice stream...")   
        self.ingestData(1)  
        self.waitForMicroBatch()          
        self.assertResult(1253)  
        print("Validation passed.\n")  
  
        print("Testing second iteration of invoice stream...")   
        self.ingestData(2)  
        self.waitForMicroBatch()  
        self.assertResult(2510)  
        print("Validation passed.\n")   
  
        print("Testing third iteration of invoice stream...")   
        self.ingestData(3)  
        self.waitForMicroBatch()  
        self.assertResult(3990)  
        print("Validation passed.\n")  
  
        bzQuery.stop()  
        slQuery.stop()  
  
        print("Validating Archive...", end="")   
        archives_expected = ["invoices_1.json", "invoices_2.json"]  
        for f in dbutils.fs.ls(f"{self.base_data_dir}/data/invoices_archive/{self.base_data_dir}/data/invoices"):  
            assert f.name in archives_expected, f"Archive Validation failed for {f.name}"  
        print("Done")  
  
# COMMAND ----------  
  
maTS = medallionApproachTestSuite()  
maTS.runTests()
```

![](https://miro.medium.com/v2/resize:fit:1400/1*aNxCVLy75FwYeHq2jHrYYg.png)

**So what did we do here ?**

We created a Spark_streaming_medallion notebook where we created two classess which will be treated as two different spark streaming applications. The bronze class will read the invoices from the landing zone and will create a table invoices_bz. The silver class will read the data from invoices_bz , perform the transformations and will save the invoice_line_items table.

We create the **Spark_streaming_medallion_test_suite** notebook where we imported the previous notebook, clear the directories and landing zone to begin the tests, ingest the data from the source to landing zone and perfoms the tests.

**What can be added ?**

You can also include a gold layer, This gold data is often highly refined and aggregated, containing data that powers analytics, machine learning, and production applications. While all tables in the lakehouse should serve an important purpose, gold tables represent data that has been transformed into knowledge, rather than just information.