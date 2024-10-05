---
source: https://roysandip.medium.com/unity-catalog-whats-the-buzz-around-it-and-how-it-could-address-common-challenges-8749e657d691
tags:
  - Databricks
  - UnityCatalog
  - Interview
data: 2024-07-02T01:12:33+05:30
---

For any analytics program implementation to succeed and yield business value, optimum data quality is a pre-requisite. Enabling data quality at enterprise scale requires multi-faceted approaches, enablement and technologies that make up the enterprise-wide Data Governance program. Therefore, well conceptualized and executed DG organization and program are essential to enable high-performance analytics to deliver insights that will be trusted as single version of the truth and will support business decisions and actions across the enterprise.

With Databricks becoming more and more popular day-by-day in last couple of years as a solution for data engineering & data science the onus was on Databricks to provide unified and integrated solution within their platform to support further on Data Governance; i.e. keeping a governed overview of all data assets, data access management, data quality & the lineage driven by old saying “with great power comes great responsibility” and though there were few options in the market they observed that existing tools were cloud-platform-specific, i.e., AWS Glue Catalog for platforms built on AWS and Azure Data Catalog for platforms built on Azure etc and hence the idea was to create a data cataloging, discovery, and governance solution that would work seamlessly with the Databricks ecosystem within Databricks itself — this ended up Databricks creating Unity Catalog and since then in the Databricks world, Unity Catalog has been the talk of the town for a while; however, not many people realize that it only had its [GA release](https://docs.databricks.com/release-notes/unity-catalog/20220825.html) less than a year ago, in August 2022. Since then, it has been the preferred choice for existing Databricks customers as it ties seamlessly with the other components of the [Databricks ecosystem](https://www.databricks.com/product/data-lakehouse).

**What is Unity Catalog?**

Unity catalogue is Databricks solution to support Data Governance: it enables data governance and security management using ANSI SQL or the Web UI interface and offers a tool that allows to:

§ Control **data accesses** across data assets, tables, files & notebooks

§ Create a **data catalog** of data assets present in the Lakehouse

§ Offer a **lineage view** on data origin & usage across jobs/notebooks running in Databricks

§ Allow for **data sharing** in a governed managed way

§ & like — over time — much more

![](https://miro.medium.com/v2/resize:fit:1400/1*p-6IEm5R6-AncFmhiOFF9Q.png)

_Unity Catalog — Features Snapshot_

**Where do we see Unity Catalog helping organizations?**

**_Streamlining Data Sharing between Databricks Workspaces_**




**_Implementing Access Isolation Through Least Privileges_**

<p align="justify">Prior Unity Catalog, there was no straightforward method to restrict user permissions at the workspace level. So separate workspaces seemed like a potential solution. However it introduced its own set of challenges, particularly regarding data sharing. With Unity Catalog, enterprise can define fine-grained access controls at the table and column level, ensuring that users only had access to the data necessary for their specific roles.</p>

**_Tracking Audit Trails, Data Assets and Workload Information_**

Before Unity Catalog came into the scene, we could not track who accessed a table, when last time it was tracked by anyone, how permissions over a secured object got change over time, how to analyse table relationships and many more.

As an example we have seen occasions where we might want to search any columns in any table having certain keyword etc but we are not sure which table which column have it — now with Unity Catalog situations like this is easily addressable through information schema.

On a workload side, we can now easily track daily DBU consumption, DBU consumption against each SKUs, which job costed most DBUs etc.

**_Tracking Data Lineage for the Lakehouse Data Assets_**

With the introduction on Unity Catalogs, customers can now track lineages up to column level giving better understanding of data flow and transparency for ML model performance to regulatory compliance.

Customers are usually looking for information like where do the data set come from, what are the transformation that data set went through at very bare minimum and with Unity Catalog into play, we can track runtime operations — not just confined to SQL but any language supported by Databricks.

**_Improving User Management and Governance_**

With organizations having more and more workspaces for their different LOBs/teams and each one operating independently, resulted in duplicate user management efforts and fragmented governance processes. So be it adding new user to the organization or updating permissions for existing user across workspaces — it caused complexity and time, particularly as the organization scaled and the number of users increased.

Often we have seen in our experience that whenever a new member joins the team we had to manually create a new user account within each workspace, configure the appropriate permissions, and manage user access separately in each environment and this not only becomes overhead but also incurs risk of human error and inconsistencies in user provisioning.

Databricks integration with identity providers e.g. AAD, Okta, OneLogin etc along with Unity Catalog centralized user management addresses this issue by providing a unified and consistent approach across the organization.

**_Enriching Overall Enterprise Data Governance and User Access Experience_**

Unity Catalog has wide integration with other enterprise governance/catalog/security solution partners to give customers wholistic experience. Partners like Alation, Collibra, Azure Purview, Informatica IDMC, Immuta, Privacera, Atlan are just to name a few that have rich integration point with Unity Catalog. The idea behind these integrations is to leverage customer’s existing investments and build a future-proof governance model without expensive migration costs where Unity Catalog will manage the governance solution within Lakehouse estate while the other partner(s) will manage the rest of the data infrastructure that is spread across multiple cloud platforms, data processing frameworks, orchestration engines, [BI tools](https://ask.atlan.com/hc/en-us/sections/6319365253137-Tableau-Connectivity?ref=https%3A%2F%2Fatlan.com%2Fdatabricks-unity-catalog%2F) etc and then finally stich the enterprise level governance/catalog/security solution together.

**What’s coming up next in Unity Catalog?**

**_Lakehouse Federation_**

With Lakehouse Federation in action soon, organizations can leverage a consistent data management, discovery (e.g. tagging or lineage), and governance (e.g. RBAC. ACL) experience for all their data across various platforms (e.g. Synapse, SQL Server, Snowflake, Google BQ, Redshift, My SQL, PostgreSQL) within Databricks.

**_Support for Volume_**

For use cases handling unstructured data, Volume which is a new type of object will enable you to manage, govern and track lineage in Unity Catalog.

**_Lakehouse Monitoring and Observability_**

With new AI-driven monitoring service that encompasses the entire data pipeline, including data, ML models, and features enables pro-active alerting by utilizing Unity Catalog’s real-time data lineage, down to the column level.

With public preview of System Tables in Unity Catalog which serve as a centralized analytical store and provide comprehensive cost and usage analytics, offering valuable insights into resource consumption and expenditure.

**_AI Governance_**

With Unity Catalog expanding governance model to include AI assets like Feature Store and Model Registry along with data assets, it will address both DataOps and MLOps processes together.

**Summary**

Distributing data governance through Databricks Unity Catalog transformed many of our customers the way they manage and govern data. Customers who were facing difficulty to track and measure various metrics and activity actions, are now getting comprehensive view of the Lakehouse with the data lineage and rich system tables for auditing while eventually unlocking new opportunities for growth, innovation, and data-driven decision-making. Since Unity Catalog comes with scalable foundation and extensible framework to accommodate future requirements, it will eventually help organizations to be future proof and less vulnerable to any major architectural changes.