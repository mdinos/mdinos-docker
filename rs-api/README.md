# rs-api

Flask API which:

```
/api/healthcheck
```

Returns `{'ok': true}`

```
/api/file?user=<rs username>&date=YYYY-MM-DD
```

Find S3 file key from username and date.

```
/api/data?filekey=<s3 file key>
```

Get file contents.

To run locally, add your AWS credentials in rs_api.py as per https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#method-parameters

and then
```
python rs_api.py

curl -G http://0.0.0.0:5000/api/healthcheck
```

or build and run the docker container.