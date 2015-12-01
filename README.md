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

#### Configuration
```
sudo vim /etc/elasticsearch/elasticsearch.yml
```
- [Reference 1](https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elk-stack-on-ubuntu-14-04)
- [Reference 2](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-14-04)


### Logstash

#### Install
- Download [logstash](https://www.elastic.co/downloads/logstash)
- Configure `config.ini`

