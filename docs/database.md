The backend in stateless, it does not retain information about previous requests. There is no stored knowledge of, or reference to past transactions in the backend itself. Instead all this state knowledge is handled by a database.

In the medium/long term, stateless backends are a much simpler paradigm. They are much easier to develop, test, and debug since all requests are self-contained, with all the side effects are stored on the DB. They also scale to multiple instances much better since any query can be responded to by any instance of the backend.

### Choosing the right Database backend.

This accelerator supports `SQLite`, `Postgres`, and `MySQL`

This section focuses on architecture descision making. you will find implementation details and recipes [here in the cookbook.](cookbook/configs/databases_configs.md)

#### SQLite

!!! success "Pick this if"
    - You only want to do small scale prototyping
    - You are working alone
    - This is the very beginning of the project


SQLite is the default option. It is a minimalist SQL database stored as a single `.sqlite` file. This is suitable for local development and prototyping, but not for industrialization.

As the data is only persisted locally, this also means you can not easily share it with the rest of the dev team in your project. If that is something you need, consider using cloud-based Postgres or MySQL backends.

!!! info "Visualizing the DB in your IDE"
    In VSCode/cursor, the `SQLite Viewer` extension is very useful for dev and debug as it allows you to open and explore the `.sqlite` database file.

#### Postgres

!!! success "Pick this if"
    - You have multiple people working with you
    - Your project will require some form of industrialization
    - You also want to use Postgres as your vector store (using `pgvector`)

Postgres is the preferred choice for any project that has the ambition to go beyond a simple POC. All clouds offer a managed Postgres so it is usually pretty easy and cheap to deploy and use.

This centralized database can be queried from anywhere by any backend instance provided they have access. Very useful for working as a team and sharing data such as chat sessions, feedbacks, or other. Mandatory to serve a service that will scale beyond 10 users.

By using Postgres you can kill two birds with one stone as it can also be used as your vector store. That way, you essentially get a production-grade vector store for free as you need a SQL backend anyways.

!!! info "Visualizing the DB in your IDE"
    In VSCode/cursor, the `PostgresSQL` extension is very useful for dev and debug as it allows you to open and explore the remote database.

#### MySQL

!!! success "Pick this if"
    - You can not use Postgres or if you already have a MySQL database
    - You have multiple people working with you
    - Your project will require some form of industrialization

This is essentially the same as postgres, but without the possibility of doubling as a vector store. Unless there is a very project-specific reason to use it, just prefer other options.

### Interacting with the database

Only the backend interacts with the database, **not** the frontend.

![](3t_architecture.png)

All the databases interactions should go through the `Database` helper class at [backend/database.py](https://github.com/artefactory/skaff-rag-accelerator/blob/main/backend/database.py)

This class abstracts away the underlying database and allows you to run SQL queries while handling connections securely and efficiently in the background.

For example: fetching a user by email can be done like this:
```python
from backend.database import Database

with Database() as connection:
    user_row = connection.fetchone("SELECT * FROM users WHERE email = ?", (email,))
```

### Database data model

The minimal database for the RAG only has one table, `message_history`. It is meant to be extended by plugins to add functionalities as they are needed. See the the [plugins documentation](backend/plugins/plugins.md) for more info.
