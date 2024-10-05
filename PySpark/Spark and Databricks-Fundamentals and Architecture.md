---
created: 2024-08-15T16:27:16+05:30
modified: 2024-08-15T16:27:16+05:30
---
In this article, we will deep dive into the fundamentals of spark, databricks and its architecture, types of databricks clusters in detail.

## **Spark:**

An open source unified analytics engine for processing big data, created by founders of Databricks

- Massive built-in parallelism i.e Distributed computing platform that comes with auto parallelism.
- Easy to use i.e multilingual that supports **Python, SQL, Scala, Java and R.**
- Unified engine to run streaming, data engineering and machine learning workloads.
- Spark addresses the drawbacks of Hadoop such as incapable of In-memory processing.

## **Architecture:**

Spark cluster is a collection of nodes, one driver node and one or more worker nodes. Each node is a virtual machine with at least 4 or more cores.

**Driver Node:** drives the processing and does not do any computations. It communicates with the cluster managers to allocate resources and identifies the number of jobs, stages and tasks to be created.

**Worker Node:** Each worker node consists of an executor that does the data processing. Each executor consists of 4 or more cores to execute the tasks. The executor returns the results to the driver and the driver returns that to the client.

![](https://miro.medium.com/v2/resize:fit:1400/0*CSDh9YR9f_OQmJHz)

**Vertical scaling / Scale up** can be done by increasing the number of cores in the virtual machine whereas **horizontal scaling / scale out** can be done by adding more number of worker nodes.

**Spark Execution:**

In the following example, spark achieves the **parallelism** by an action that divides the application into jobs, each job is divided into stages and each stage is divided into Tasks.

![](https://miro.medium.com/v2/resize:fit:1400/0*p_7-uymKHoro4eZN)

Reference from Databricks Academy

If the client submits the query **SELECT * from SALES** to a spark cluster and let’s assume the file size is 625 MB. Spark driver divides the file into 5 partitions and sends those to executors of each worker node to run the tasks in parallel as below automatically.

![](https://miro.medium.com/v2/resize:fit:1400/0*l-bMPfkbjfkJJOZU)

Reference from Databricks Academy

## **Databricks:**

Databricks is a unified, open analytics platform for building, deploying, sharing, and maintaining enterprise-grade data, analytics, and AI solutions at scale.

Databricks created by the founders of Apache spark which provides necessary management layers to work with Spark in an easy manner. On top of this, vendors such as Microsoft, AWS offer Databricks in their respective cloud platforms.

Azure Databricks is the first party service which provides deeper integration than other cloud providers. It means that Databricks can be directly purchased from Microsoft and all support requests are handled by Microsoft.

**Azure Databricks Architecture:**

![](https://miro.medium.com/v2/resize:fit:1400/0*s4RB-qW8yDYqHRvn)

**The architecture consists of two components as follows,**

**Control Plane —** It is located in the Databricks account which contains backend services managed by Databricks.

**Compute Plane —** It is located in the customer subscription in which the data is processed. The compute resources are created within each workspace virtual network.

A virtual network (VNet) is a container that allows communication between compute machines (VMs). An NSG (network security group) is a tool that filters network traffic to and from Azure resources in an Azure VNet. NSGs use rules to allow or deny network traffic based on conditions like IP addresses, ports, and protocols.

**Types of compute:**

In databricks, we have the different types of spark clusters as follows,

1. **All purpose Cluster —** This cluster is used to run workloads using interactive notebooks. The compute can be created, terminated and restarted using Databricks UI or CLI or via REST API.More suitable for Development workload and can be shared across many developers.

![](https://miro.medium.com/v2/resize:fit:1400/0*RBDuzumfbZFYtjkE)

**2. Job Cluster —** This cluster is used to run automated workloads. The databricks job scheduler automatically creates a cluster to execute the job once it starts.. As soon as the job is completed, the compute will be terminated automatically.

![](https://miro.medium.com/v2/resize:fit:1400/0*LSrrwO6mo_jVZtbj)

More suitable for production workloads. Job clusters are cheaper than All purpose clusters.

**3. Instance Pools —** Clusters usually take up time to start. Cluster pools will reduce that time by allocating virtual machines which are ready to use from the pool. If there are no more VM’s available in the pool and a new cluster is requested from the pool, then an error will be thrown.

A sample cluster pool configuration as below,

![](https://miro.medium.com/v2/resize:fit:1400/0*DIp5z7cLtKxMC26e)

**Cluster Configuration:**

Here is a sample All-purpose cluster configuration as follows,

![](https://miro.medium.com/v2/resize:fit:1400/0*vqLeBl0uPlrwhTSX)

**Types of Node:**

- **Single Node** -1 Driver Node, No worker nodes. Suitable for light ETL workloads, driver acts as both driver and worker for computations.
- **Multi Node** -1 Driver Node and multiple worker nodes. Suitable for large ETL workloads, computations will be performed based on standard Spark architecture above.

**Access Mode:**

- **Single User —** Only one user can access the nodes.
- **Shared —** Multiple users can access the same nodes. Isolated environments for each process.
- **No Isolation Shared —** Multiple users can access the same nodes. No isolated environments for each process, so failure of one process will affect the other processes.

**Databricks Runtime:**

It is a set of core libraries that run on the compute such as Delta lake, libraries of Python, Java, Scala and R etc, ML libraries (Pytorch, Tensorflow etc). Each version of the runtime improves the usability, security and performance of the big data analytics.

**Auto Termination:** In the above screenshot, the 20 minutes interval of auto termination will terminate the cluster automatically after 20 minutes of inactivity.

**Autoscaling:** This feature in Databricks will help autoscaling of worker nodes based on the workload. The min and max values indicate the lower and higher number of nodes for horizontal scaling.

**On-demand vs Spot Instances:** Enabling the spot instances in the cluster configuration leverages the unused VM capacity from azure capacity which will save some cost. However the spot instances will be evicted once it becomes unavailable in the capacity, so spot instances will be suitable for running development workloads but not to run production/critical workloads. Suitable for worker nodes.

Unlike spot instances, on-demand instances will not be evicted at any circumstances. Suitable for driver nodes.

**Advanced settings of the cluster:**

1. The spark configurations can be set to fine tune the performance of the spark jobs and certain spark configurations can be set via environment variables as below,

![](https://miro.medium.com/v2/resize:fit:1400/0*zCt1ExGw06wdtzkR)

2. Logs can be captured to a DBFS location in order to keep it for a longer time as below,

![](https://miro.medium.com/v2/resize:fit:1400/0*MkpTtmJaBPLYP05a)

3. The init scripts can be set as below which gets executed as soon the cluster starts. For example, if you want to install the python / ML libraries as soon as the cluster starts, you can mention in the init scripts.

![](https://miro.medium.com/v2/resize:fit:1400/0*xiJ_5iW7IXSNj91o)

**Conclusion:**

In this above article, we have seen the architecture of spark and databricks in detail and we have covered the fundamental's of both as well.