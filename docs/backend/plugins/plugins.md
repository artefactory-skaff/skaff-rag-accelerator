Plugins are used to add functionalities to the API as you need them.

We provide a few plugins out of the box in `backend/api_plugins`, and you will also be able to create your own. If you write a useful plugin, don't hesitate to open a PR!

A plugin takes the form of a function that wraps all the FastAPI routes it introduces.

### Data model

Plugins may need special database tables to properly function. You can bundle a SQL script that will add this table if it dosen't exist when the plugin is instantiated. For example, the authentication plugins adds a table that stores users.

`users_tables.sql`:
```sql
CREATE TABLE IF NOT EXISTS "users" (
    "email" VARCHAR(255) PRIMARY KEY,
    "password" TEXT
);
```
```python
def authentication_routes(app, dependencies=List[Depends]):
    from backend.database import Database
    with Database() as connection:
        connection.run_script(Path(__file__).parent / "users_tables.sql")

    # rest of the plugin
```

### Dependencies

Plugins should allow for dependency injection. In practice that means the wrapper function should accept a list of FastAPI `Depends` object and pass it to all the wrapped routes. For example, the sessions plugin takes an unspecified list of dependencies that may be needed in the future, and an explicit auth dependency to link sessions to users. [Learn more about FastAPI dependencies here.](https://fastapi.tiangolo.com/tutorial/dependencies/)
