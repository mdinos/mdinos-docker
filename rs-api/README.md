# rs-api

Flask API which:

```
GET
/api/healthcheck
```

Returns `{'ok': true}`

```
GET
/api/file?user=<rs username>&date=YYYY-MM-DD
```

Find S3 file key from username and date.

```
GET
/api/data?filekey=<s3 file key>
```

Get file contents.

```
PUT
/api/newtrackingrequest?username<rs username>
```

Add a new username to the list to track in s3.

To run locally, add your AWS credentials in rs_api.py as per https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#method-parameters

and then
```
./rs_api.py

curl -G http://0.0.0.0:3000/api/healthcheck
```

or using `aws-profile`, there's no need to add your credentials.
```shell
aws-profile -p <your profile> ./rs_api.py
```
or build and run the docker container like so:

```
 docker build -t rs_api:latest .

```

```
docker run -d -p 3000:3000 rs_api:latest
```