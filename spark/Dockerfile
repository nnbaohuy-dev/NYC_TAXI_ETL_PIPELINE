# ============================================================
# Stage 1: Download Delta Lake and Hadoop S3A dependencies
# ============================================================
FROM maven:3.9-eclipse-temurin-21 AS dependencies

WORKDIR /build

RUN cat > pom.xml <<'EOF'
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>local.project</groupId>
    <artifactId>spark-runtime-dependencies</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>org.apache.hadoop</groupId>
            <artifactId>hadoop-aws</artifactId>
            <version>3.5.0</version>
        </dependency>
        <dependency>
            <groupId>io.delta</groupId>
            <artifactId>delta-spark_4.2_2.13</artifactId>
            <version>4.4.0</version>
        </dependency>
    </dependencies>
</project>
EOF

RUN mvn -B dependency:copy-dependencies \
    -DincludeScope=runtime \
    -DoutputDirectory=/build/jars \
 && ls -1 /build/jars


# ============================================================
# Stage 2: Build the custom Spark image
# ============================================================
FROM spark:4.2.0

USER root

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY jars/postgresql-42.7.13.jar /opt/spark/jars/

# Hadoop S3A + AWS SDK v2 + analytics accelerator
COPY --from=dependencies /build/jars/hadoop-aws-3.5.0.jar /opt/spark/jars/
COPY --from=dependencies /build/jars/bundle-*.jar /opt/spark/jars/
COPY --from=dependencies /build/jars/analyticsaccelerator-s3-*.jar /opt/spark/jars/

# Delta Lake
COPY --from=dependencies /build/jars/delta-spark_4.2_2.13-4.4.0.jar /opt/spark/jars/
COPY --from=dependencies /build/jars/delta-storage-4.4.0.jar /opt/spark/jars/

RUN mkdir -p /opt/spark/conf \
 && printf '%s\n' \
    'spark.sql.extensions io.delta.sql.DeltaSparkSessionExtension' \
    'spark.sql.catalog.spark_catalog org.apache.spark.sql.delta.catalog.DeltaCatalog' \
    >> /opt/spark/conf/spark-defaults.conf

USER spark