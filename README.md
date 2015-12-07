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
```
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
sudo apt-get update
sudo apt-get -y install elasticsearch
```

#### Install shield
```
cd /usr/share/elasticsearch/bin
sudo ./plugin install license
sudo ./plugin install shield
```

- Create an admin user
    ```
    cd /usr/share/elasticsearch/bin/shield
    esusers useradd admin-user -r admin
    ```
- Create a logstash user so that he can write logstash data into elasticsearch
    ```
    cd /usr/share/elasticsearch/bin/shield
    esusers useradd logstash-user -r logstash
    ```
- Create a read-only role for logstash in `/etc/elasticsearch/shield/roles.yml`
    ```
    logstash_user:
      indices:
        'logstash-*':
          privileges: read
    ```
- Enable anonymous access for elasticsearch in `/etc/elasticsearch/elasticsearch.yml`
    ```
    shield.authc:
      anonymous:
        roles: logstash_user  # the read-only role
        authz_exception: true
    ```
- Make sure `elasticsearch` user can access user information data
    - Try `esusers list` using `elasticsearch` user identity

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
```
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/logstash/2.1/debian stable main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get -y install logstash
```

#### Configuration
- Install `logstash-filter-railsroutes` plugin
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
    - `-d DATE`, `--date DATE`: Specify what date (%Y-%m-%d) to archive. Default is yesterday.
