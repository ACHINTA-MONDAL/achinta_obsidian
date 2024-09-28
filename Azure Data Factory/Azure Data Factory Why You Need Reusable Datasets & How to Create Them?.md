Datasets in Azure Data Factory (ADF) represent a logical reference to the data that you want to ingest, transform, or output in your data pipelines.

![ADF generic and reusable datasets](https://miro.medium.com/v2/resize:fit:602/1*m5VTyNsp95VVhQkSIe2iYA.png)

They usually include information such as the following:

1. data structure of the source and destination (also called sink in ADF).
2. connection details to the data in source and sink.
3. filepath, schema and file format that ADF needs to work with.

# A Scenario

You have a team of 3 data engineers. Let’s call them John, David and Sara. All 3 design ADF pipelines as part of their daily job and thus create datasets.

John’s project reads a combination of json and csv files from a SharePoint to load those into a Synapse dedicated SQL pool table called _table_a_.

![ADF generic and reusable datasets](https://miro.medium.com/v2/resize:fit:1038/1*VQOsmNeY2OJ0AMwlqWiVqg.png)

David’s project reads csv files and binary files from a network drive into another Synapse dedicated SQL pool table called _table_b_.

![ADF generic and reusable datasets](https://miro.medium.com/v2/resize:fit:1054/1*umsnocd_AmJ2dS6oxXn3Dg.png)

Sara’s project reads API data through a JSON and loads it into a third table called _table_c_.

![ADF generic and reusable datasets](https://miro.medium.com/v2/resize:fit:1042/1*K2MbA8WbPOVB7zqdIEIK6w.png)

_All of them store their incoming data into an Azure data lake storage gen2 container._

# Without Generic Datasets

Without creating generic datasets for their needs, John, David and Sara create datasets that cater to their specific use cases.

✓ John creates 3 datasets — csv file, json file and sql dataset for table_a.  
✓ David creates 3 datasets — csv file, binary file and sql dataset for table_b.  
✓ Sara creates 2datasets — json file and sql dataset for table_c.

Following is how their datasets look in ADF —

![](https://miro.medium.com/v2/resize:fit:576/1*z9kKssUFBPqYZBvM5fBpLA.png)

To provide further context, when John, David and Sara created their datasets, they linked those datasets to their data stores only. To put this into perspective, below are the datasets configured for the different tables —

_John’s sink dataset —_

![](https://miro.medium.com/v2/resize:fit:1400/1*PWuxQwEhn1Y1KzSzY8DglA.png)

_David’s sink dataset_ —

![](https://miro.medium.com/v2/resize:fit:1400/1*sPXIEPJq3vnlBA40UgNKLQ.png)

_Sara’s sink dataset —_

![](https://miro.medium.com/v2/resize:fit:1400/1*5SpxTAuuXijfSFnyOZh5Kw.png)

# The Problem

Can their data pipelines function like this? Absolutely. Assuming no other error occurs, all the 3 data pipelines will function and load data into their respective tables.

## So what’s the problem?

The question to ask is if this approach is optimized and can this be sustained? We can see our ADF already contains-

- 3 datasets for the 3 different tables
- 2 datasets for the 2 csv files
- 2 datasets for the 2 json files

What happens six months or a year from now? As the influx of projects increases, new csv/excel/json files are discovered and new tables get created, our original strategy will balloon the resources used in ADF since the number of new datasets created appears to be directly proportional to the number of new files/tables.

![](https://miro.medium.com/v2/resize:fit:664/1*NlziNWwcATu7qoiR-lrltQ.png)

There are additional challenges to be mindful about as well such as-

1. Higher maintenance overhead because the team has to maintain the connection settings of data sources/sink and debug multiple datasets should there be an issue with the network configuration.
2. ADF’s storage consumption increases with the addition of each duplicated dataset.

# The Recommended Solution

To avoid problems like above, consider an approach where you create generic datasets. In simple terms, design a dataset such as a csv or sql table dataset that can be reused for different projects. To apply this approach, let’s analyze how many generic datasets we need to create-

1. As we know, John and David’s project uses csv files and thus I will create 1 generic csv dataset instead of John and David needing to create 2 datasets which is a redundant approach.
2. John and Sara’s project uses a JSON file each to load data into a SQL table. I will also create a generic dataset for a JSON.
3. Finally, all 3 projects feed into different tables which, even thought are different tables, use the same data warehouse/server. So I can create 1 generic dataset that caters to all 3 tables.

# Let’s design the generic dataset

## Generic CSV Dataset

Starting with generic csv dataset, go to parameters, click + New and add 3 different parameters. Since the datasets reside in a folder structure on Azure’s data lake, I will provide the following names —

- main_folder
- directory
- filename

![ADF generic and reusable csv dataset](https://miro.medium.com/v2/resize:fit:1400/1*DQp3RWYUV1f5WHPijRrUZQ.png)

Return to the Connection tab and configure the parameters as shown-

![ADF generic and reusable csv dataset](https://miro.medium.com/v2/resize:fit:1400/1*aqBcxFmih3PxubvaJ3hfrw.png)

Click Save.

## Generic SQL Dataset

Navigate to any SQL dataset and click Parameters. Add 2 parameters-

- schema_name
- table_name

![ADF generic and reusable sql dataset](https://miro.medium.com/v2/resize:fit:1310/1*d8PVUGEJCzDz-XG9Bb9Hug.png)

Return to the Connection tab and check _Enter manually_ checkbox. Next, click Add dynamic content.

![ADF generic and reusable sql dataset](https://miro.medium.com/v2/resize:fit:1400/1*tUSF-Wj2MKL_4HwVePcgsA.png)

## But, what if in another project, a CSV file uses a different column delimiter?

Often, there will be scenarios where despite your generic dataset’s availability, it may not be of use in a project. As an example, the default value of column delimiter property for a csv is comma. If a project you are working on uses a different delimiter, you will have to either modify the existing generic csv dataset or create a new csv dataset.

Here, I advise to have a forethought and parameterize as many fields as you can. This enables users to provide their custom values while still reusing the same dataset.

![ADF generic and reusable csv dataset](https://miro.medium.com/v2/resize:fit:1400/1*r1OnF-avS8Ra_iyafWjVaQ.png)

# How to use a generic dataset?

Going back to the John’s project, he now has 2 generic datasets to work with — one for csv and one for sql. Create a copy activity and from the source, select the generic csv dataset.

![ADF generic and reusable csv dataset](https://miro.medium.com/v2/resize:fit:1400/1*GUSE4eBm6ybitgIwaABnAQ.png)

John can now provide the values for all the parameters as shown above. The same dataset can now be used by David to load his csv file in the table_b.

On the sink side, select the generic sql dataset.

![ADF generic and reusable sql dataset](https://miro.medium.com/v2/resize:fit:1400/1*opXgfH9UDXi6RYAiY3JXfg.png)

Because the schema and table name properties were parameterized, John is able to provide the schema and table name for his project. The same dataset can be used by David and Sara as well by simply providing the names of their schema and table to the parameters.

# Before and After

Shown below is how the datasets look in ADF before creating generic datasets and after creating generic datasets —

![ADF generic and reusable datasets](https://miro.medium.com/v2/resize:fit:1326/1*wHOYz9eBPAWR3M9ru-taww.png)

# Summary

To summarize, creating generic datasets not only optimizes a data team’s organization but also saves time by reducing the maintenance overhead needed to create/troubleshoot existing datasets. They are particularly useful for working with schema-less data sources like NoSQL databases or data lakes. Of course, I’d urge you to evaluate your use case and assess if creating a generic dataset provides any advantages or not.