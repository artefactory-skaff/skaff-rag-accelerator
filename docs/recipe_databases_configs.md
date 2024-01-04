The database config is the "easiest" as it only requires a database URL.

So far, `sqlite`, `mysql`, and `postgresql` are supported.

CloudSQL on GCP, RDS on AWS, or Azure Database will allow you to deploy `mysql`, and `postgresql` database instances. 

!!! warning
    If using `mysql` or `postgresql` you will need to also create a database, typically named `rag`, to be able to use it. 
    
    You will also need to create a user, and get its password. Make sure there are no spacial characters in the password.


As the database URL contains a username and password, we don't want to have it directly in the `config.yaml`.

Instead, we have:
```yaml
DatabaseConfig: &DatabaseConfig
  database_url: {{ DATABASE_URL }}
```

And `DATABASE_URL` is coming from an environment variable. 

The connection strings are formated as follows:

- **SQLite:** `sqlite:///database/rag.sqlite3`
```shell
export DATABASE_URL=sqlite:///database/rag.sqlite3
```

- **mySQL:** `mysql://<username>:<password>@<host>:<port>/rag`
```shell
# The typical port is 3306 for mySQL
export DATABASE_URL=mysql://username:abcdef12345@123.45.67.89:3306/rag
```

- **postgreSQL:** `postgresql://<username>:<password>@<host>:<port>/rag`
```shell
# The typical port is 5432 for postgreSQL
export DATABASE_URL=postgresql://username:abcdef12345@123.45.67.89:5432/rag 
```

When first testing the RAG locally, `sqlite` is the best since it requires no setup as the database is just a file on your machine. However, if you're working as part of a team, or looking to industrialize, you will need to deploy a `mysql`, or `postgresql` instance.
