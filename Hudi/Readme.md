# Hudi

## Hudi Overview

- Open-source data management framework used to simplify incremental data processing and data pipeline development by providing record-level insert, update, upsert, and delete capabilities. 
- Hudi is integrated with Apache Spark, Apache Hive, and Presto. In Amazon EMR release versions 6.1.0 and later, Hudi is also integrated with Trino (PrestoSQL). 
- With Amazon EMR release version 5.28.0 and later, EMR installs Hudi components by default when Spark, Hive, Presto, or Flink are installed. You can use Spark or the Hudi DeltaStreamer utility to create or update Hudi datasets.
- You can use Hive, Spark, Presto, or Flink to query a Hudi dataset interactively or build data processing pipelines using incremental pull. (Incremental pull refers to the ability to pull only the data that changed between two actions.)
- These features make Hudi suitable for the following use cases:
  1. Working with streaming data from sensors and other Internet of Things (IoT) devices that require specific data insertion and update events. 
  2. Complying with data privacy regulations in applications where users might choose to be forgotten or modify their consent for how their data can be used. 
  3. Implementing a change data capture (CDC) system that allows you to apply changes to a dataset over time. 


## How Hudi Works
- You can write data to the dataset using the Spark Data Source API or the Hudi DeltaStreamer utility. Hudi organizes a dataset into a partitioned directory structure under a basepath that is similar to a traditional Hive table. The specifics of how the data is laid out as files in these directories depend on the dataset type that you choose. You can choose either Copy on Write (CoW) or Merge on Read (MoR). 
- Regardless of the dataset type, each partition in a dataset is uniquely identified by its partitionpath relative to the basepath. Within each partition, records are distributed into multiple data files. 
- Each action in Hudi has a corresponding commit, identified by a monotonically increasing timestamp known as an Instant. Hudi keeps a series of all actions performed on the dataset as a timeline. Hudi relies on the timeline to provide snapshot isolation between readers and writers, and to enable roll back to a previous point in time.


## Understanding dataset storage types: Copy on write vs. merge on read
- Copy on Write (CoW) – Data is stored in a columnar format (Parquet), and each update creates a new version of files during a write. CoW is the default storage type. 
- Merge on Read (MoR) – Data is stored using a combination of columnar (Parquet) and row-based (Avro) formats. Updates are logged to row-based delta files and are compacted as needed to create new versions of the columnar files. 

With CoW datasets, each time there is an update to a record, the file that contains the record is rewritten with the updated values. With a MoR dataset, each time there is an update, Hudi writes only the row for the changed record. MoR is better suited for write- or change-heavy workloads with fewer reads. CoW is better suited for read-heavy workloads on data that changes less frequently. 

- Hudi provides three logical views for accessing the data:
  - Read-optimized view – Provides the latest committed dataset from CoW tables and the latest compacted dataset from MoR tables. When you query the read-optimized view, the query returns all compacted data but does not include the latest delta commits. Querying this data provides good read performance but omits the freshest data.
  - Incremental view – Provides a change stream between two actions out of a CoW dataset to feed downstream jobs and extract, transform, load (ETL) workflows.
  - Real-time view – Provides the latest committed data from a MoR table by merging the columnar and row-based files inline. When you query the real-time view, Hudi merges the compacted data with the delta commits on read. The freshest data is available to query, but the computational overhead of merging makes the query less performant. 

The ability to query either compacted data or real-time data allows you to choose between performance and flexibility when you query. 

- Hudi creates two tables in the Hive metastore for MoR: a table with the name that you specified, which is a read-optimized view, and a table with the same name appended with _rt, which is a real-time view. You can query both tables. 


## Considerations and limitations for using Hudi on Amazon EMR
- Record key field cannot be null or empty – The field that you specify as the record key field cannot have null or empty values. 
- Schema updated by default on upsert and insert – Hudi provides an interface, HoodieRecordPayload that determines how the input DataFrame and existing Hudi dataset are merged to produce a new, updated dataset. Hudi provides a default implementation of this class, OverwriteWithLatestAvroPayload, that overwrites existing records and updates the schema as specified in the input DataFrame. To customize this logic for implementing merge and partial updates, you can provide an implementation of the HoodieRecordPayload interface using the DataSourceWriteOptions.PAYLOAD_CLASS_OPT_KEY parameter. 
- Deletion requires schema – When deleting, you must specify the record key, the partition key, and the pre-combine key fields. Other columns can be made null or empty, but the full schema is required. 
- MoR table limitations – MoR tables do not support savepointing. You can query MoR tables using the read-optimized view or the real-time view (tablename_rt) from Spark SQL, Presto, or Hive. Using the read-optimized view only exposes base file data, and does not expose a merged view of base and log data. 


## Source
- https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-hudi.html
- https://hudi.apache.org/docs/concepts/



# Hudi Setup

## To use Hudi with Amazon EMR Notebooks

- Connect to the master node of the cluster using SSH and then copy the jar files from the local filesystem to HDFS as shown in the following examples. In the example, we create a directory in HDFS for clarity of file management. You can choose your own destination in HDFS, if desired.
```
hdfs dfs -mkdir -p /apps/hudi/lib
```
```
hdfs dfs -copyFromLocal /usr/lib/hudi/hudi-spark-bundle.jar /apps/hudi/lib/hudi-spark-bundle.jar
```
```
hdfs dfs -copyFromLocal /usr/lib/spark/external/lib/spark-avro.jar /apps/hudi/lib/spark-avro.jar
```

- Open the notebook editor, enter the code from the following example, and run it. 
```
%%configure
{ "conf": {
            "spark.jars":"hdfs:///apps/hudi/lib/hudi-spark-bundle.jar,hdfs:///apps/hudi/lib/spark-avro.jar",
            "spark.serializer":"org.apache.spark.serializer.KryoSerializer",
            "spark.sql.hive.convertMetastoreParquet":"false"
          }}
```

## To open the Spark shell on the master node
```
spark-shell \
--conf "spark.serializer=org.apache.spark.serializer.KryoSerializer" \
--conf "spark.sql.hive.convertMetastoreParquet=false" \
--jars /usr/lib/hudi/hudi-spark-bundle.jar,/usr/lib/spark/external/lib/spark-avro.jar
```

## To submit a Spark application that uses Hudi
```
spark-submit \
--conf "spark.serializer=org.apache.spark.serializer.KryoSerializer"\
--conf "spark.sql.hive.convertMetastoreParquet=false" \
--jars /usr/lib/hudi/hudi-spark-bundle.jar,/usr/lib/spark/external/lib/spark-avro.jar
```
