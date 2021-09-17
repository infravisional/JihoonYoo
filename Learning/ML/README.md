## ML Workflow
Every ML-based software includes three main artifacts:<br>
* Data engineering: data acquisition & data preparation
* ML model engineering: ML model training & serving
* Code engineering: integrating ML model into the final product.

#### Data Engineering
The Data Engineering pipeline includes a sequence of operations on the available data that leads to supplying training and testing datasets for the machine learning algorithms:
1. Data Ingestion – Collecting data by using various frameworks and formats, such as Spark, HDFS, CSV, etc. This step might also include synthetic data generation or data enrichment.
2. Exploration and Validation – Includes data profiling to obtain information about the content and structure of the data. The output of this step is a set of metadata, such as max, min, avg of values. Data validation operations are user-defined error detection functions, which scan the dataset in order to spot some errors.
3. Data Wrangling (Cleaning) – The process of re-formatting particular attributes and correcting errors in data, such as missing values imputation.
4. Data Labeling – The operation of the Data Engineering pipeline, where each data point is assigned to a specific category.
5. Data Splitting – Splitting the data into training, validation, and test datasets to be used during the core machine learning stages to produce the ML model.



