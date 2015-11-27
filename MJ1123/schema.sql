drop table if exists entries;
drop table if exists Member;

create table Member (
	id string primary key,
	passwd string not null
);
create table entries (
	id integer primary key autoincrement,
	title string not null,
	text string not null,
	userid string not null,
	FOREIGN KEY ('userid') REFERENCES 'Member' ('userid')
);