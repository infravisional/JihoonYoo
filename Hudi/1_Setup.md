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
