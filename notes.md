`part 1`
in step 1 i just created both tables users and expenses using the schema.sql file.
and putted on delete cascade because i want to delete the parallele tabs if the one is deleted
and than i used **GRANT** command to add access to the ***expence_user*** so he can create delete insert etc
and also than i do ***GRANT USAGE ON SEQUENCE users_id_seq, expenses_id_seq TO expense_user;*** so the  **expence_user**

`part 2`

ok so now we have : 
**database.py** : connect to postgres
**models.py** : pydantic models
**routes/** : endpoints
**main.py** : creates the app 

now we need to put the ***password*** inside another file and its **.env** so we dont have problems when publish it in github using *dotenv* and *os* 

i just studied *routers* which are things to seperate ur *API* in multiple files
than just import it like this
***from routes import router_name*** 
routes is the name of the folder that have the routers 
i also created the pydantic model for expenses and the default must match the default inside the sql 


inside the routes_expenses , i make an endpoint to call post test

i made the **delete** method , the return status is 204 and it raises a 404 error if the id dont exist

*Depends - Connection*
**jwt**

