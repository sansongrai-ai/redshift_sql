CREATE SCHEMA test;
 
 
 CREATE TABLE test.emp (id INT, name VARCHAR (15));



 insert into test.emp values (1 , 'ram');

SELECT * FROM test.emp;


create table test.listing(
	listid integer not null distkey,
	sellerid integer not null,
	eventid integer not null,
	dateid smallint not null  sortkey,
	numtickets smallint not null,
	priceperticket decimal(8,2),
	totalprice decimal(8,2),
	listtime timestamp);


copy test.listing 
from 's3://lambda-ouput-klr/redshift/input/listing_pipe.txt'
iam_role 'arn:aws:iam::445448907072:role/redshift-role';

SELECT * FROM test.listing;


unload ('select * from test.listing')
to 's3://lambda-ouput-klr/redshift/output/parquet/file'
iam_role 'arn:aws:iam::445448907072:role/redshift-role'
PARQUET;

unload ('select * from test.listing')
to 's3://lambda-ouput-klr/redshift/output/csv/file'
iam_role 'arn:aws:iam::445448907072:role/redshift-role'
csv;


create table test.listing_parquet(
	listid integer not null distkey,
	sellerid integer not null,
	eventid integer not null,
	dateid smallint not null  sortkey,
	numtickets smallint not null,
	priceperticket decimal(8,2),
	totalprice decimal(8,2),
	listtime timestamp);


copy test.listing_parquet 
from 's3://lambda-ouput-klr/redshift/output/parquet/file'
iam_role 'arn:aws:iam::445448907072:role/redshift-role'
format as parquet;

SELECT * FROM test.listing_parquet;


create table test.event(
	eventid integer not null distkey,
	venueid smallint not null,
	catid smallint not null,
	dateid smallint not null sortkey,
	eventname varchar(200),
	starttime timestamp);

copy test.event
from 's3://lambda-ouput-klr/redshift/input/events.txt' 
iam_role 'arn:aws:iam::445448907072:role/redshift-role'
removequotes
emptyasnull
blanksasnull
maxerror 5
delimiter '|'
timeformat 'YYYY-MM-DD HH:MI:SS';
 
SELECT * FROM test.event;

create table test.venue_new(
venueid smallint not null,
venuename varchar(100) not null,
venuecity varchar(30),
venuestate char(2),
venueseats integer not null default '1000');

copy test.venue_new(venueid, venuename, venuecity, venuestate) 
from 's3://lambda-ouput-klr/redshift/input/venue.txt' 
iam_role 'arn:aws:iam::445448907072:role/redshift-role'
delimiter '|';

SELECT * from test.venue_new;