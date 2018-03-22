# elb-log-analyzer
A tool set to analyze AWS elb access log

## Prerequisites
- Java 7 / Java 8
- Elasticsearch
- Logstash


### Java

```
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get -y install oracle-java8-installer
```


### Elasticsearch

#### Install
We're targeting elasticsearch at version 6.2.x. Please see [here](https://www.elastic.co/guide/en/elasticsearch/reference/6.2/_installation.html) for the installation guide. Or, you can run elasticsearch on [Docker](https://www.elastic.co/guide/en/elasticsearch/reference/6.2/docker.html).


#### Configuration
- [Reference 1](https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elk-stack-on-ubuntu-14-04)
- [Reference 2](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-14-04)
- If only one instance, we can set only one shard no replica in `/etc/elasticsearch/elasticsearch.yml`

    ```
    index.number_of_shards: 1
    index.number_of_replicas: 0
    ```


### Logstash

#### Install
We're targeting logstash at version 6.2.x. Please see [here](https://www.elastic.co/guide/en/logstash/6.2/installing-logstash.html) for the installation guide. Or, you can run logstash on [Docker](https://www.elastic.co/guide/en/logstash/6.2/docker.html).

#### Configuration
- Install `logstash-filter-railsroutes 0.2.0` plugin

    ```
    cd /opt/logstash/bin
    sudo ./plugin install logstash-filter-railsroutes
    ```
- Set up `/etc/logstash/conf.d/logstash.conf`
    - output
        - elasticsearch
            - `user`: use `logstash` user created in shield
            - `password`: use `logstash` user created in shield
- Put `routes_spec` in appropriate place
- Put `sincedb` of `logstash-input-s3` in appropriate place


## Scripts
### archive_s3_log.py
- Archive access log stored in S3 of a date.
- `python archive_s3_log.py [-h] [-d DATE]`
- optional arguments:
    - `-h`, `--help`: show this help message and exit
    - `-d DATE`, `--date DATE`: Specify what date (`%Y-%m-%d`) to archive. Default is yesterday.


### delete_old_logs.py
- Dispose old access log.
- `python delete_old_logs.py [-h] [-d DATE]`
- optional arguments:
    - `-h`, `--help`: show this help message and exit
    - `-d DATE`, `--date DATE`: Specify what date (`%Y-%m-%d`) to delete. Default is 30 days ago.


### server_error_alarm.py
- Find all server error events and report via slack.
- `python server_error_alarm.py [-h] [-b BEGIN] [-e END]`
- optional arguments:
    - `-h`, `--help`: show this help message and exit
    - `-b BEGIN`, `--begin BEGIN`: Specify when (`%Y-%m-%dT%H:%M:%S`) to scan. Default is 10 minutes ago.
    - `-e END`, `--end END`: Specify when (`%Y-%m-%dT%H:%M:%S`) to stop scanning. Default is 5 minutes ago.

### hourly_report.py
- Dump hourly report.
- `python hourly_report.py [-h] [-b BEGIN] [-e END]`
- optionsal arguments:
    - `-h`, `--help`: show this help message and exit
    - `-b BEGIN`, `--begin BEGIN`: Specify when (`%Y-%m-%dT%H:%M:%S`) to scan. Default is 1 hour before the top of this hour.
    - `-e END`, `--end END`: Specify when (`%Y-%m-%dT%H:%M:%S`) to stop scanning. Default is the top of this hour.

### daily_report.py
- Dump daily report.
- `python daily_report.py [-h] [-d DATE]`
- optional arguments:
    - `-h`, `--help`: show this help message and exit
    - `-d DATE`, `--date DATE`: Specify which date (%Y-%m-%d) to make report. Default is yesterday.
