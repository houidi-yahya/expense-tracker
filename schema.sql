create table users
(
  id serial primary key,
  email varchar(100) not null unique,
  hashed_pass text not null,
  created_at timestamp default now() not null
);
create table expenses
(
  id serial primary key,
  object text default 'not_specified',
  price numeric(10,2) not null,
  user_id integer not null,
  created_at timestamp default now() not null,
  category varchar(20) default 'other' not null,
  constraint fk1 FOREIGN KEY(user_id) REFERENCES users(id) on delete cascade
);
