---
created: 2024-08-11T02:33:59+05:30
modified: 2024-08-11T02:33:59+05:30
---
#CatalystOptimizer 
### Introduction

As a data engineer, we often hear terms like Data Lake, Delta Lake, and Data Lakehouse, which might be confusing at times. In this blog we’ll demystify these terms and talk about the differences of each of the technologies and concepts, along with scenarios of usage for each.

### Data Lake

A Data Lake is storage layer or centralized repository for all structured and unstructured data at any scale. In Synapse, a default or primary data lake is provisioned when you create a Synapse workspace. Additionally, you can mount secondary storage accounts, manage, and access them from the Data pane, directly within Synapse Studio.

It is possible to freely navigate through the Data Lake via the File explorer GUI experience for Data lakes. This includes the uploading and downloading of folders and files, copying and pasting across folders or data Lake accounts, and CRUD (Create, Read, Update & Delete) operations for folders and files.

Definition schema is not mandatory when you are storing the data into a data lake, which means that data does not need to be fitted into a pre-defined scheme before storage. Only when the data is processed and read, it is adapted and parsed into a schema. This saves time which is otherwise spent on schema definition.

It’s important to note that Data Lake does not provide Atomicity, which has the potential for increased corrupt data. As there is no schema enforcement, it can be possible to write a significant amount of orphan data. As it is just a storage layer, DML and ACID transactions are also not supported.

There is also no quality enforcement for data loading. This is a double-edged sword as the advantage of Data Lake enables the storing of multiple types of data, however due to a lack of quality enforcement, this can lead to potential inconsistencies in the data. With Data Lake, there is no consistency or isolation. This means it is not possible to read or append when an update is in progress.


### Delta Lake

[Delta lake](https://docs.delta.io/latest/index.html) is an open-source storage layer (a sub project of The Linux foundation) that sits in Data Lake when you are using it within Spark pool of Azure Synapse Analytics.

Delta Lake provides several advantages, for example:

- It provides ACID properties of transactions, i.e., atomicity, consistency, isolation, and durability of the table data. And it does by doing following,
    - #1, It keeps track of ordered record of every transaction since delta lake table creation in the transaction log and checks it prior to read/write operations allowing atomic transactions.
    - #2, Its serializable snapshot isolation level ensures that readers never see inconsistent data and they continue to read the data while writers are writing data concurrently – this means literally having no impact to read the consistent data even when data load in the table is in progress.
    - And #3, It employs “all or nothing” ACID transaction approach to prevent data corruption from failed write operations. 

- With scalable metadata handling, it leverages Spark distributed processing power to handle all the metadata for petabyte-scale tables with billions of files at ease. 

- It provides unification of streaming and batch processing. With that, a table in Delta Lake is a batch table as well as a streaming source and sink. Streaming ingests data in real-time, batch load processes historical data, interactive queries query data interactively, all the same time and it all just works out of the box. 

- Schema enforcement and evolution feature automatically handles schema variations to prevent insertion of bad records during data ingestion. 

- With Time travel, every operation is automatically versioned. That means, this data versioning enables rollback, full historical audit trails, and reproducible machine learning experiments. 

- For Upserts and deletes scenarios, it supports merge, update and delete operations to enable complex use cases like change-data-capture, slowly-changing-dimension (SCD) operations, streaming Upserts, etc.

- Powered by Apache Spark which is open source. For any existing Spark jobs, batch, or streaming, they can be easily converted to obtain the benefits of using Delta, without having to rewrite those programs from scratch.

### Delta Lake – Transaction log and checkpointing

A key part of Delta Lake is the transaction log. This is the common thread that runs through several of the top features within Delta Lake, to include ACID transactions, scalable metadata handling and time travel amongst others.

The Delta Lake transaction log is an ordered record of every transaction, ever performed on a Delta Lake table since its creation, stored in a JSON file for each commit. It serves as a single source of truth and acts as a central repository to track all changes that users may make to the table. Check out [Delta Transaction Log Protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md) to learn more.

For any users that reviews a Delta Lake table for the first time, Spark checks the transaction log to see what transactions have been posted to the table. The end users table is then updated with those changes, ensuring that the version of the table that the user sees is in sync with the master record and that conflicting changes cannot be made.

Checkpoint files are automatically generated for every 10 commits. Using native parquet format, checkpoint files save the entire state of the table at that point in time. Think of these checkpoint files as a shortcut to fully reproduce a table’s given state, thus enabling Spark to prevent reprocessing potentially large amounts of small inefficient JSON files.

### Data Lakehouse

Traditionally, organizations have been using a data warehouse for their analytical needs. As the business requirements evolve and data scale increases, they started adopting a modern data warehouse architecture, which can process massive amounts of data in a relational format, and in parallel across multiple compute nodes. At the same time, they start collecting and managing their non-relational big data that was in semi-structured or unstructured format with a data lake.

These two disparate yet related systems run in silos, increasing development time, operational overhead, and overall total cost of ownership.  It causes an inconvenience to end users to integrate data if they needed access to the data from both systems to meet their business requirements.

![thumbnail image 7 of blog post titled 
Synapse – Data Lake vs. Delta Lake vs. Data Lakehouse](https://techcommunity.microsoft.com/t5/image/serverpage/image-id/418222i9351C94C0CBD5FB8/image-size/large?v=v2&px=999)

Data Lakehouse platform architecture combines the best of both worlds in a single data platform, offering and combining capabilities from both these earlier data platform architectures into a single unified data platform – sometimes also called as medallion architecture. It means, the data lakehouse is the one platform to unify all your data, analytics, and Artificial Intelligence/Machine Learning (AI/ML) workloads.

A common pattern is to segment your data into different zones due to the lifecycle of the data and as the data transitions from Raw to Enriched to Curated, signifying the change in value of the data which occurs during the process, the quality of the data increases with each stage.

**Raw zone**

- Data could come from multiple and various sources and may not be in the ideal format (‘dirty’). Used as a dump or initial store for raw data files. This is where the data is first captured in its original format.

**Enriched zone**

- Generally, contains intermediary data. Typically, the data has been cleaned to ensure that it is easily query-able for quick queries or debugging purposes. Processing can be applied to the data here to make it consist of normalized raw data which is easier to query.

**Curated zone**

- Contains cleaned data, ready for use and consumption by other services. The data stored here can typically include aggregated key business metrics which can be queried frequently.

**Workspace zone**

- There are times when team members want to bring some additional data which is not part of the regular data ingestion or transformation process, or want to store some data temporarily in data lake. For that purpose, this zone can be used. In other words, this is a zone that contains data ingested by each individual team/data consumers to provide greater value to their specific teams.

![thumbnail image 8 of blog post titled 
Synapse – Data Lake vs. Delta Lake vs. Data Lakehouse](https://techcommunity.microsoft.com/t5/image/serverpage/image-id/418223i2035498FF1A88542/image-size/medium?v=v2&px=400)

Data Lakehouse typically contains these zones; Raw, Enriched, Curated and in some cases Workspace Data (Bring Your Own), used to both store and serve data. It’s even possible to have several zones in-between, as data progresses towards a more curated format, ready for consumption. These can potentially include a ‘Data Science Zone’ and ‘Staging Zone’ further increasing the capabilities of a single data platform.