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
  description text,
  venue text,
  eventdate DATETIME,
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
cid integer not null,
name text not null,
instructions text not null,
rating integer,
cook_time integer not null,
servings integer not null,
foreign key(cid) references category(cid)
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
quantity text,
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


drop table if exists my_saved_bag;
create table my_saved_bag (
mid integer,
rid integer,
ingredient text not null,
foreign key(mid) references users(mid),
foreign key(rid) references recipes(rid),
primary key(mid,rid,ingredient)
);

drop table if exists my_shared_bag;
create table my_shared_bag (
mid_assignee integer,
mid_assignor integer,
rid integer,
gid integer,
ingredient text not null,
foreign key(mid_assignee) references users(mid),
foreign key(mid_assignor) references users(mid),
foreign key(rid) references recipes(rid),
foreign key(gid) references groups(gid),
primary key(mid_assignee,mid_assignor,rid, gid, ingredient)
);

