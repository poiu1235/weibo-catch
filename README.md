# weibo-catch

if you want to use this code running in your computer
you need a computer with a ubuntu operation system and mysql db management system

you need create database by use the create db code(in mysql)

you need create a file named 'localconfig' used to record the account information
and its format like follows:
#------------------------------------
[weibo]
weibouser=xxxxxxxx
weibopwd=xxxxxxxx

[db]
dbsite=xxxxxxxx
dbuser=xxxxxxxx
dbpwd=xxxxxxxx

[email]
emailuser=xxxxxxxx
emailpwd=xxxxxxxx
emailhost=smtp.163.com #xxxxxxxx
emailrec=xxxxxxxx
#-------------------------------------
project describtion:
The weibo-catch is a kind of spider in Weibo(Sina).
I want to catch two kind of data from weibo:
one is follows,which is people interested in some people,cooperation,or field.
another is what he says,commits,conveys and shares.
so I keep two thread to do the two kind of jobs.

beacause of the enormous imformation of weibo creates everyday,
I always keep the program running.
and it will Loop traversal your follows list, and catch them information.

all my data are stored in mysql database.
I will give the table stacture and the creating code

in the future, I will catch them into other two kind of no-sql database
redis and mongodb, in order to compare their capacity in store big data.

finally I will import Hbase and hadoop to count or do some statistic at 
what i am interesting.

all this have done already, I will open one website to running this huge 
information for free.

finally my name is Luis, I come from China in Asia.
my e-mail is yuyi304738837@163.com or 304738837@qq.com,
I am a master candidate in HIT,
welcome to contact me and discuss.

