# Checkpoint VPN Troubleshooter


Description goes here



## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Configuration

Use `settings.yaml` to populate a drop-down menu of Management servers

#### Example

```
management_servers:
  test1:
    hostname: myserver.mydomain.com
    port: 443
  test2:
    hostname: 10.10.3.21
    port: 8443

google_maps_api_key: xxxxxxxxx
```
### Configuring From Files

## Usage

Run via quart:

```
python app.py
```

or 

```
quart run
```

For increased performance, run via hypercorn:

```
hypercorn --access-logfile '-' app:app
```

### Running in Docker

```

docker build -t checkpoint-vpn .

docker run -p 8000:8000 --name checkpoint-vpn checkpoint-vpn 

```

## Reference

CheckPoint Documentation

- [R81.20 Management API Reference](https://sc1.checkpoint.com/documents/latest/APIs/index.html#introduction~v1.9.1%20)
- [R81.10 Management API Reference](https://sc1.checkpoint.com/documents/latest/APIs/index.html#introduction~v1.8.1%20)

[Getting Started with CheckPoint Management API](https://layer77.net/2023/06/03/getting-started-with-checkpoint-r81-10-management-api/)


## Changelog

- Version 0.1 : initial upload
