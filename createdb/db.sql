create database weibocatch;

use weibocatch;
/*汉字和一个字母都是一个字符*/
create table w_user (
    wid char(10) primary key,
    wname varchar(100) not null,
    recon tinyint(1),
    color tinyint(1) default null,
    flag tinyint(2) default 0,
    inserttime timestamp default NOW()
);

create table w_error (
    wid char(10),
    exception varchar(2000),
	inserttime timestamp default NOW()
);

create table w_relation (
    wid char(10),
    wfriendid char(10)
);

create table w_conn (
    weiboid char(32),
    tag tinyint(1),
    atid varchar(150),
    atname varchar(100),
    primary key (weiboid , tag)
);
/*Date或DateTime类型是不能使用函数作为默认值的，所以改用timestamp类型*/
create table w_content (
    weiboid char(32) primary key,
    wid char(10),
    content varchar(1000),
    url varchar(1000),
    map varchar(200),
    label varchar(100),
    intime varchar(100),
    picid int,
    wfrom varchar(100),
    inserttime timestamp default NOW()
);
/*Date或DateTime类型是不能使用函数作为默认值的，所以改用timestamp类型*/
create table w_transfer (
    weiboid char(32) primary key,
    wid char(10),
    transferid char(10),
    content varchar(1000),
    remark varchar(1000),
    label varchar(100),
    url varchar(1000),
    intime varchar(100),
    picid int,
    wfrom varchar(100),
    inserttime timestamp default NOW()
);

create table pic_reg (
    id int primary key auto_increment,
    path varchar(3000),
    label1 varchar(100),
    label2 varchar(100),
    label3 varchar(100),
    title varchar(9000)
)  auto_increment=10000;

/*INSERT INTO weibocatch.w_user
(wid,wname,recon,color,flag)
VALUES
('2468833122','poiu1235',0,0,0);*/

INSERT INTO weibocatch.w_user
(wid,wname,recon,color,flag)
VALUES
('2430104687','江森开根号',0,0,0);

SHOW GLOBAL VARIABLES LIKE 'auto_incre%';-- 全局变量
select 
    *
from
    weibocatch.w_relation;
select NOW();
delete from weibocatch.pic_reg;
delete from weibocatch.w_transfer;

alter table weibocatch.pic_reg AUTO_INCREMENT=10000;
select 
    *
from
    weibocatch.w_user;
update weibocatch.w_user 
set 
    flag = 0
where
    wid = '2430104687';

select version();
show character set;
SHOW VARIABLES LIKE 'character%';
set names 'utf8mb4';

SHOW VARIABLES WHERE Variable_name LIKE 'character\_set\_%';
