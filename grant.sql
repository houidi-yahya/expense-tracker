grant select,insert,delete,update on users,expenses to expense_user;
GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO expense_user;
