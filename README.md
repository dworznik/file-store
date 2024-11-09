## Development environment

### Prerequisites

* [Python](https://www.python.org)
* [Poetry](https://python-poetry.org)
* [GCP account](https://cloud.google.com/docs/get-started)
* [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)

### Python project, poetry, virtual env

Run `poetry install` to install the dependencies and create a virtual Python env.

### GCP account and project

Log in into your GCP account
```
gcloud auth login
```

Select the default project (you may need to create a new project first)
```
gcloud config set project
```

Set up [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to
)
```
gcloud auth application-default login
```

### GCP service account configuration

https://console.cloud.google.com/iam-admin/serviceaccounts

Add keys and choose the default JSON format


### DB schema and migrations

Init Alembic migrations in a new db
```
poetry run alembic init migrations
```

Run all the migrations
```
poetry run alembic upgrade head
```

Roll back the last migration

```
poetry run alembic downgrade -1
```

### Google Drive access configuration


## CLI

TODO: token, expiration date

```
poetry run drive --service-account-file <account key file> watch --webhook-url <webhook url> --folder-id <google drive folder id>
```


```
poetry run drive --service-account-file <account key file> changes
```

```
poetry run drive --service-account-file <account key file>> info --folder-id <google drive folder id>
```

### Sources

* https://www.emptor.io/blog/demystifying-the-google-drive-changes-api/
* https://medium.com/the-team-of-future-learning/integrating-google-drive-api-with-python-a-step-by-step-guide-7811fcd16c44
* https://developers.google.com/drive/api/guides/push
* https://developers.google.com/drive/api/guides/manage-changes
