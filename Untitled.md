With Databricks becoming more popular day-by-day as a solution for data engineering & data science, the onus was on Databricks to provide unified and integrated solution within their platform to support further on Data Governance; i.e. keeping a governed overview of all data assets, data access management, data quality & the lineage driven by old saying “with great power comes great responsibility “.

Similarly organizations expected Databricks to provide mechanism around sharing live data with diverse set of clients in a scalable manner with high reliability and efficiency.

Sooner Databricks responded by accommodating two features viz. Unity Catalog and Delta Sharing to above requirements.

![](https://miro.medium.com/v2/resize:fit:1400/1*oqOPuLBGc4K_SJYJn_OO7g.png)

Fig-0

In this article I’ll touch upon these two new features in Databricks — in terms of what value they bring to the table and most importantly how we configure them in our workspace.

**1.** **What is Unity Catalog?**

Unity catalogue is Databricks solution to support Data Governance: it enables data governance and security management using ANSI SQL or the Web UI interface and offers a tool that allows to:

**·** Centralized metadata, User Management and Data Access controls

· Data Lineage, Data Access Auditing, Data Search and Discovery

· Secure data sharing with Delta Sharing

And like — over time — much more. However in this blog, we would mostly cover data sharing aspect and setting up of Unity Catalog as pre-requisites using Azure platform.

**1.1 How to setup Unity Catalog?**

**1.1.1** **Prerequisites**

Refer [Requirements](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/create-metastore) section from Azure documentation.

Please note that the Databricks Account Admin role is different from Databricks Workspace Admin. If you are Azure Global Admin (this is Azure AD level role and simple Azure roles to manipulate Azure resources) then automatically you become Databricks Account Admin or else you have to seek support from current Databricks Account Admin to make you Databricks Account Admin.

**1.1.2 Detailed Steps**

**Step #1 Create Storage account and containers**

Create ADLS Gen2 storage account and container underneath it for further use. You may refer [here](https://learn.microsoft.com/en-us/azure/storage/blobs/create-data-lake-storage-account) for detailed steps if you need help.

![](https://miro.medium.com/v2/resize:fit:1400/1*EoOAIRdqnK6zWZu5zDVjMg.png)

Fig-1

**Step #2 Configure a managed identity for Unity Catalog**

Create Access connector for Azure Databricks and assign Managed Identity (add Access connector as member) access to the storage account you created in above step. Refer [this](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/azure-managed-identities#config-managed-id) for detailed steps.

Note the resource Id (sample format /subscriptions/<subscription-id>/resourceGroups/<resource_group>/providers/Microsoft.Databricks/accessConnectors/<connector-name>) which would be needed in future steps as Access Connector Id

**Step #3 Create Unity Catalog Metastore as following**

**·** Log into Azure Databricks account admin portal using [https://accounts.azuredatabricks.net/](https://accounts.azuredatabricks.net/) (for AWS Databricks account admin portal use [https://accounts.cloud.databricks.com/)](https://accounts.cloud.databricks.com/))

**·** Click Data and then on **Create Metastore** to fill out following. Make sure you enable/attach your workspace to Unity Catalog in net tab

![](https://miro.medium.com/v2/resize:fit:1400/1*_HTTrJEtcR14rXe1P5qxxQ.png)

Fig-2

Once metastore is successfully created, you can see the same as below:

![](https://miro.medium.com/v2/resize:fit:1400/1*GX6JjY3U56UV12k010hO4A.png)

Fig-3

![](https://miro.medium.com/v2/resize:fit:1400/1*lkW_BcY5XWsYG77paRc7Wg.png)

Fig-4

![](https://miro.medium.com/v2/resize:fit:1400/1*iH31lxTyRabMZR0t2VDZSg.png)

Fig-5

**Step #4 Make use of Unity Catalog — create schema and tables**

Launch the Unity catalog enabled workspace and for sample import quick start notebook from [https://docs.databricks.com/_static/notebooks/unity-catalog-example-notebook.html](https://docs.databricks.com/_static/notebooks/unity-catalog-example-notebook.html) to create delta tables using three level namespace i.e. <catalog>.<schema>.<table>

Once the notebook is executed, you can view the data in Notebook or SQL Editor.

![](https://miro.medium.com/v2/resize:fit:1400/1*LAtM1BVEbc6vY1GPwhq7lQ.png)

Fig-6

Now that Unity Catalog is set up, let’s understand what is Delta Sharing and how that can be enabled.

**2.** **What is Delta Sharing?**

Databricks Delta Sharing is an open solution to securely share live data across different computing platforms.

It’s built into Unity Catalog data governance platform, enabling a Databricks user, called a data provider, to share data with a person or group inside or outside of their organization, called a data recipient.

Delta Sharing’s native integration with [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html) allows you to manage, govern, audit, and track usage of the shared data on one platform. In fact, your data must be registered in Unity Catalog to be available for secure sharing.

The various use cases Delta Sharing can solve are following:

**Commercialization —** Simplify data as service with easy to implement trusted data sharing and no lock in.

**B2B Sharing and Reporting** — Partners/counter parties can consume data using tools and platforms of their choice

**Internal Sharing Data Mesh** — Share data across divisions in different clouds or regions without moving data.

**Privacy Safe Data Cleanrooms** — Secure way to share and join data across partners while enabling compliance with data privacy.

![](https://miro.medium.com/v2/resize:fit:1400/1*oyk3Ol8OZf8_WZezYLRXlQ.png)

Fig-7

**2.1** **How to enable Delta Sharing?**

Delta sharing can be achieved in either of the two modes i.e. Open sharing or Databricks to Databricks sharing

_Open sharing_ lets you share data with any user, whether or not they have access to Databricks.

_Databricks-to-Databricks sharing_ lets you share data with Databricks users who have access to a Unity Catalog metastore that is different from yours.

In this article, we will see how to setup both the options — first the Open Sharing followed by Databricks to Databricks Sharing option.

**2.1.1 Pre-requisites**

Refer [Requirements](https://learn.microsoft.com/en-us/azure/databricks/data-sharing/set-up) section from Azure documentation.

**2.1.1.1 Scenario 1: Open Sharing — Detailed Steps**

**_Step #1 Enable Delta Sharing and set expiration timeline_**

Enable Delta Sharing on Metastore window with some expiration timeline. Without any timeline set, it’s defaulted to indefinite time-period. Refer _Fig-4_ above.

**_Step #2 Enable Audit for Delta Sharing_**

Configure audit for Delta sharing activities like create, modify, update or delete a share or a recipient, when a recipient access the data or when recipient accesses an activation link and downloads the credential etc.

Launch the workspace from Databricks Account Admin portal and go to **Admin Console →Workspace** settings to turn on Verbose Audit Logs

![](https://miro.medium.com/v2/resize:fit:1400/1*Yq5Czogf8VFj3_AzuL8Oug.png)

_Fig-8_

![](https://miro.medium.com/v2/resize:fit:1400/1*-Wv8Iw4HGr4VY1XtewCVyQ.png)

![](https://miro.medium.com/v2/resize:fit:1400/1*B5u4UBRgb6LQ12oPYBsNkA.png)

_Fig-9_

Then go to Databricks service from Azure portal and click on Diagnostic Settings and select the logs/events and destination where you want them to redirect to.

Note — I’m not going into details how the events can be analysed from this point onwards using Log Analytics or other tools.

![](https://miro.medium.com/v2/resize:fit:1400/1*Ton7XnwkwIjl5kLj09zK3Q.png)

_Fig-10_

![](https://miro.medium.com/v2/resize:fit:1400/1*NVrxKUuf1j60YyNBCZbbFg.png)

_Fig-11_

**Step #3 Create share on the provider end**

Once audit is enabled, go to your Databricks workspace and click **Data** and navigate to **Delta Sharing** menu and select **Shared by me**

Create Shares (Navigate **Share Data →Name**)

![](https://miro.medium.com/v2/resize:fit:1400/1*8E0SCOIW7VvesbiGW0RdQg.png)

_Fig-12_

And then add tables under it which you want to share by navigating to **Add/Edit tables** page — select the catalog and database that contain the table, then select the table(s).

![](https://miro.medium.com/v2/resize:fit:1400/1*GNWckAin5qrCEFMxoah7qg.png)

_Fig-13_

**Step #4 Create recipient on the provider end**

Create Recipient (Navigate **Add New Recipien →Name**) and then link the same with **Add Recipient** option.

Please note that you do not use the sharing identifier for open sharing recipient.

![](https://miro.medium.com/v2/resize:fit:1400/1*_syiHg-gYIn3pXzQfZECGg.png)

_Fig-14_

Once a recipient is created you will receive a pop-up as below

![](https://miro.medium.com/v2/resize:fit:1400/1*BgzeruMKn6QTyIdKpuud0A.png)

_Fig-15_

Copy the URL and paste it in browser to download the credential file

![](https://miro.medium.com/v2/resize:fit:1400/1*tAXAzvQqoobRXVCJR_0TYQ.png)

_Fig-16_

Please note that this Download option would be available only once.

Once the file is downloaded the token is activated. On recipient details page, you can expire the token immediately or after a time duration.

![](https://miro.medium.com/v2/resize:fit:1400/1*DrHcrWPNuOzcqmRC2w9BNQ.png)

_Fig-17_

![](https://miro.medium.com/v2/resize:fit:1400/1*B9Tpj6xy03B4MDBP6dV5SA.png)

_Fig-18_

**Step #7 Construct the Delta sharing (“open”) recipient/client**

Once Delta share setup is complete, it’s now time to write client. Here I would show a simple Python (Pandas) client to access the share(data).

Once the credential file (config.share) is downloaded — use the same and use Pandas API to retrieve the data as shown below but please note that before you write your client you need to download the delta-sharing library.

![](https://miro.medium.com/v2/resize:fit:1400/1*cPUjNvKPP4sLF1BGnjwGFw.png)

_Fig-19_

**2.1.1.2 Scenario 2: Databricks to Databricks Sharing — Detailed Steps**

If you want to share data with users who don’t have access to your Unity Catalog metastore, you can use Databricks-to-Databricks Delta Sharing, as long as the recipients have access to a Databricks workspace that is [enabled for Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/enable-workspaces.html).

The advantage of this scenario is that the share recipient doesn’t need a token to access the share, and the provider doesn’t need to manage recipient tokens. The security of the sharing connection — including all identity verification, authentication, and auditing — is managed entirely through Delta Sharing and the Databricks platform

In this article, we would demonstrate how delta sharing can be made between two Databricks accounts — provider (hosted on Azure) and recipient (hosted on AWS).

**Step #1 Request the recipient sharing identifier**

On your recipient Databricks workspace, click **Data** and then navigate to **Delta SharingàShared with me** and then from Providers tab, click the **Sharing identifier** copy icon

![](https://miro.medium.com/v2/resize:fit:1400/1*UUEqO0pJt5Ewd-sz2W4nCA.png)

_Fig-20_

Please note that recipient workspace must also be Unity Catalog/Metastore enabled (you can follow the steps as done in first workspace)

**Step #2 Create recipient on provider workspace**

This is same as previous Scenario 1 Step #3 above except the fact that for Databricks to Databricks sharing you have to provide the recipient sharing identifier that you copied from previous step.

![](https://miro.medium.com/v2/resize:fit:1400/1*tk97WzYPzD0KtzDL_ot-Aw.png)

_Fig-21_

Since our provider account is on Azure and recipient one in AWS, that immediately gets reflected in this screen as soon as sharing identifier is accommodated.

Once you create the recipient, immediately that gets listed under recipient list with Authentication Type as Databricks (for Open Sharing same was Token) and you can view recipient details once you click on any particular recipient.

![](https://miro.medium.com/v2/resize:fit:1400/1*VJ1bHoFwAMhuPCsexoS1KA.png)

_Fig-22_

![](https://miro.medium.com/v2/resize:fit:1400/1*YL1H_8I0WvUqShutsnEPPw.png)

_Fig-23_

**Step #3 Create Share on Provider workspace**

Once Databricks recipient is added, it’s time to create Share and for that follow same steps as shown in Step #3 under Scenario 1.

![](https://miro.medium.com/v2/resize:fit:1400/1*TS-uTy7N10_HSY4gWiBFfQ.png)

_Fig-24_

![](https://miro.medium.com/v2/resize:fit:1400/1*bRqm0lVFEvkCkzwEjebS1Q.png)

_Fig-25_

**Step #4 Create catalog from the share created on recipient side**

Finally to access the tables in a share, a metastore admin or [privileged user](https://docs.databricks.com/data-sharing/read-data-databricks.html#access-data) must create a catalog from the share on the recipient Databricks workspace.

To do that go **Delta Sharing** menu and follow the navigation **Shared with me →Providers→Shares** (select particular share on top of which you want to create the new catalog)→**Create catalog**

Then enter a name for the catalog and optional comment to finish creating the catalog.

![](https://miro.medium.com/v2/resize:fit:1400/1*WlU89ZNeS14bqCMJgklGxw.png)

_Fig-26_

![](https://miro.medium.com/v2/resize:fit:1400/1*RCBfbREsEgRbbgGLkno2YA.png)

_Fig-27_

![](https://miro.medium.com/v2/resize:fit:1400/1*yrrlB2FcCNtPDZc7MCyoUA.png)

_Fig-28_

**Step #5 Access data using the catalog created on recipient workspace**

Once catalog is created on the recipient Databricks workspace, you can view the table (data) from Data tab as well as from Notebook if you query using <catalog>.<schema>.<table> qualifier

![](https://miro.medium.com/v2/resize:fit:1400/1*Kxq4SWaSzSCgFbrTrTScJA.png)

_Fig-29_

![](https://miro.medium.com/v2/resize:fit:1400/1*b47DTRL_pTbLJYVIx83tCg.png)

_Fig-30_

Thanks for reading. In case you want to share your case studies or want to connect, please ping me via [LinkedIn](https://www.linkedin.com/in/sandiproyofficial/)