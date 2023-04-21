Use DialogFlow;
CREATE TABLE question (
	qid int not null auto_increment, 
	text varchar(256), 
    primary key(qid)
);

CREATE TABLE leadsTo (
	parentQID int, 
    childQID int, 
    response varchar(256), 
    foreign key(parentQID) references question(qid),
    foreign key(childQID) references question(qid)
);

CREATE TABLE DFintent(
	iid int not null auto_increment, 
    resp_txt varchar(256), 
    inputCtx JSON, 
    outputCtx JSON, 
    params JSON, 
    primary key(iid)
);

CREATE TABLE DFleadsTo (
	parentIID int, 
    childIID int,
    foreign key(parentIID) references DFintent(iid),
    foreign key(childIID) references DFintent(iid)
);