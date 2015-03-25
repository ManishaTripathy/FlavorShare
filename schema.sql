drop table if exists users;
create table users (
  mid integer primary key autoincrement,
  name text not null,
  email text unique not null,
  password text not null
);

drop table if exists groups;
create table groups (
  gid integer primary key autoincrement,
  name text not null,
  admin_id integer not null,
  foreign key(admin_id) references users(mid)
);

drop table if exists group_members;
create table group_members (
  gid integer,
  mid integer,
  foreign key(gid) references groups(gid),
foreign key(mid) references users(mid),
primary key(gid,mid)
);

drop table if exists recipes;
create table recipes (
rid integer primary key autoincrement,
category text not null,
name text not null,
instructions text not null,
rating integer,
cook_time integer not null,
servings integer not null
);

drop table if exists ingredients;
create table ingredients (
iid integer primary key autoincrement,
name text not null
);

drop table if exists recipe_ingredients;
create table recipe_ingredients (
rid integer,
iid integer,
foreign key(rid) references recipes(rid),
foreign key(iid) references ingredients(iid),
primary key(rid,iid)
);

drop table if exists category;
create table category (
cid integer primary key autoincrement,
name text not null
);

drop table if exists group_category;
create table group_category (
gid integer,
cid integer,
no_of_items integer not null,
foreign key(gid) references groups(gid),
foreign key(cid) references category(cid),
primary key(gid,cid)
);

drop table if exists group_category_recipes;
create table group_category_recipes (
gid integer,
cid integer,
rid integer,
mid integer,
foreign key(gid) references groups(gid),
foreign key(cid) references category(cid),
foreign key(rid) references recipes(rid),
foreign key(mid) references users(mid),
primary key(gid,cid,rid,mid)
);

drop table if exists my_bag;
create table my_bag (
mid_assignee integer,
mid_assignor integer,
iid integer,
gid integer,
quantity integer,
foreign key(mid_assignee) references users(mid),
foreign key(mid_assignor) references users(mid),
foreign key(iid) references ingredients(iid),
foreign key(gid) references users(mid),
primary key(mid_assignee,mid_assignor,iid)
);

