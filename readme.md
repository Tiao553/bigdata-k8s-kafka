<h1 align="center"> 
	Challenge: Event-Driven Architecture in kubernetes
</h1>

> You need to make unified data available from the union of three tables that are essential to your customer's business. Your area manager has started a migration project to make this data available in real time. You will be responsible for building a Real-time pipeline to make this data available in the Data Warehouse. You will need to perform the processing using appropriate tools and make the data available for queries from business users and BI analysts. In addition, you need to make the data available to data scientists.

To fit the needs of the business, the following architecture was proposed as a solution:
--

# <center><img src='img/architeture_kafka_k8s.png'></center>

As this work is a test case we are going to instantiate in kubernetes both banks presented in the architecture, but we are going to isolate them as microservices and use kafka connect to collect the data. That said, we can think about how we are going to manage the kafka configurations.

---
# Settup  Kafka.

In talking to the manager we came to the conclusion that kafka will need to deliver all messages. Thus ensuring the durability of using kafka. **Basically, durability is all about reducing the chance of a message getting lost.** 

The most important feature that allows durability is **replication**, which ensures that messages are copied to multiple brokers. If one broker has a failure, the data is available from at least one other broker. Topics with high durability requirements should have a configuration parameter that will ensure that the cluster can handle a loss of two Brokers without losing data.

To meet these requirements we need to design and configure kafka in all its layers, to make it easier we will divide the configuration per layer. As a comparison we will demonstrate how it is shown as the default configuration and which one we should use to guarantee durability, this way we have:

---
## 1. Producer 

These are responsible for delivering the events to kafka, in this layer some options are used to validate how the event is being delivered to kafka, some of the main ones are (1) ACKS(acknowledge), (2) Idempontence and (3) connection requests.

- ACKS : This is how it will validate the delivery of the message. When $0$ it does not want to get this return, when $1$ it wants to get the return from the leader partition, when $-1$ or $all$ it means that it needs to verify that the message was delivered to the leader and its replicas called *followers*.

- IDEMPOTENCE: Even if a message is sent several times, this character guarantees that it has the same effect as if it was sent only once. That is, if there are retries, the same message will not be written again. Each message will contain a sequence number that the broker will use to dedicate any duplicate submissions.
  
- REQUIRES : A numerical value to allow retries without message reordering. So, consider that if kafka is configured with `max.in.flight.requests.per.connection = 1`, which is the requests config, this will ensure that only one request can be sent to the broker at a time. 

Now that we have the introduction of the concepts, we can get back to the business requirements. It is desirable that the architecture has durable characteristics, for this we must configure the characteristics shown as follows:


<center>

| Producer                              | Value | Default |
|---------------------------------------|-------|---------|
| ACKS                                  | ALL   | 1       |
| Enable.Idempotence                    | True  | False   |
| Max.In.Flight.Requests.per.Connection | 1     | 5       |
</center>

---
## 2. Stream

This stage is where we worry about how we are going to save the events in kafka's topics. At this point we are concerned with (1) the **guarantee of delivery of messages** to topics and (2) the **replication factor of each topic**.

Below are the settings for each of the two configurations:


<center>

|              Streams              	| Value  	|    Default    	|
|:---------------------------------:	|:------:	|:-------------:	|
| Replication Factor Configuration  	|   3    	|       1       	|
|      Exactly Once Semantics       	|  True  	| At Least Once 	|

</center>

> I won't go into the merits of the guaranteed message delivery system, but I suggest this link as reading: 
	> [ACCESS](https://medium.com/@andy.bryant/processing-guarantees-in-kafka-12dd2e30be0e)

---
## 3. Brokers

The **brokers** they are the clusters in which kafka is acting, in this case not considering the zookeeper clusters. In this layer we will also be concerned with how the message will be saved, however now at the topic level. To achieve the proposed needs, the table below shows the values to be set as a solution:

<center>

|              Broker             	| Value  	| Default 	|
|:-------------------------------:	|:------:	|:-------:	|
|  Default.Replication.Factor    	|   3    	|    1    	|
|    Auto.Create.Topics.Enable    	|  False 	|   True  	|
|       Min.InSync.Replicas       	|   2    	|    1    	|
| Unclean.Leader.Election.Enable  	| False  	|  False  	|
| Log.Flush.Interval Message & MS 	|   Low  	|    OS   	|
</center>

 1) **Replication factor** refers to the number of follower's created, in this case think similar to a backup. 

 2) The **Auto create topics** is the default option in kafka that creates topics automatically to ensure scalability automatically.

 3) The third option is the configuration of the **synchronism of the replicas**, with 3 replicas by default kafka guarantees that at least 1 replica is in sync. Thinking about the solution to meet the client's requests if two brokers fail, one of the replicas may be out-of-sync that means they are missing data. This way durability is compromised, **so we need all replicas to stay in sync.**
	> For more information access: [Link](https://www.cloudkarafka.com/blog/what-does-in-sync-in-apache-kafka-really-mean.html)

4) In the fourth option we want to emphasize the fact that we must not let kafka elect a leader out-of-sync because that means we will lose data.

5) The way to force this recording is to call the fsync system call (see man fsync) and this is where *-log.flush.interval.messages* and *-log.flush.interval.ms* come into play. With these settings, you can tell Kafka exactly when to do this flushing (after a certain number of messages or period of time). So, to ensure the greatest effectiveness for durability we have to leave this at a low value.

---
## 4. Consumer

In this layer we will be concerned with how we are going to get the messages from kafka's topics. As in all other layers we should worry about the process and how to configure it to meet the client's need to have a durable architecture.

Below we have a table with the default values of kafka and what values we should set so that we meet the client's needs.

<center>

|      Consumer      	|        Value        	| Default 	|
|:------------------:	|:-------------------:	|:-------:	|
| Enable.Auto.Commit 	|        False        	|   True  	|
|   Isolation.Level  	| Read Committed[EOS] 	|   NONE  	|
</center>

1) The consumer does a `pull()` on kafka which checks what *offset* is stored in the consumer and asynchronously or synchronously the consumer reads these messages. Problems happen, and the broker may crash and it may be a problem to commit the *offset* value. The first setting is related to this fact. When this is set to `False` it does the synchronous commit, but this can also generate failures because throughtput is limited. 

2) This is why this second config comes in, it makes sure that we don't need to do both commits (synchronous and asynchronous). This method we are going to give a set it isolates the commits by adding this asynchronous portion.


## *Next steps*

Now we need to describe the kubernetes configuration for the architecture. 

---
---

# Settup Kubernetes

We will detail it in future updates

|          Services         	| Nodes 	|                         Storage                        	|               Memory               	| CPU 	|
|:-------------------------:	|:-----:	|:------------------------------------------------------:	|:----------------------------------:	|:---:	|
|      Apache Zookeeper     	|   3   	| Transactional Log = 256 GB Storage - 1x 1 TB [RAID 10] 	|                16 GB               	| 2~4 	|
|        Kafka Broker       	|   3   	|                    6x1 TB [RAID 10]                    	|               32 GB +              	|  6  	|
| Confluent Schema Registry 	|   2   	|                    Installation Only                   	|           1 GB Heap Size           	| 2~4 	|
|       Kafka Connect       	|   2   	|                    Installation Only                   	|           2 GB Heap Size           	| 2~4 	|
|    Confluent Rest Proxy   	|   2   	|                    Installation Only                   	| Producer = 512 MB Consumer = 16 MB 	|  16 	|
|      Confluent KSQLDB     	|   2   	|                      128 GB [SSD]                      	|                10 GB               	|  2  	|
|    Database postgreSQL    	|   1   	|                                                        	|                                    	|  2  	|
|      Database mongoDB     	|   1   	|                                                        	|                                    	|  2  	|
|        Apache Pinot       	|   3   	|                                                        	|                                    	| 2~4 	|
|           Minio           	|   2   	|                                                        	|                                    	|  2  	|
|           Lenses           	|   2   	|                                                        	|                                    	|  2  	|

