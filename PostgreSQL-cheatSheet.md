# PostGreSQL cheat sheet
1. Start and stopping PostGreSQL:
    - Start: `brew services start postgresql`
    - Stop: `brew services stop postgresql`
    - Restart: `brew services restart postgresql`
2. Accessing PostGreSQL:
    - Enter PostGreSQL prompt: `psql postgres`
    - Connect to a specific database: `psql -d database_name`
3. Creating a Database:
    - From terminal: `createdb database_name`
    - From psql prompt: `CREATE DATABASE database_name;`
4. Listing Databases:
    - From psql prompt: \l or \\list
5. Connecting to a Database:
    - From psql prompt: `\c database_name`
6. Creating a Table:
    ```
       CREATE TABLE table_name (
        column1 datatype,
     column2 datatype,
     ...
   );
    ```
7. Listing Tables:
    - From psql prompt: \dt 
8. Describing a Table:
    - From psql prompt: \d table_name