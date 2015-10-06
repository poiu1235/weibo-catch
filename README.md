# weibo-catch

if you want to use this code running in your computer
you need a computer with a ubuntu operation system and mysql db management system

you need create database by use the create db code(in mysql)

you must create two project and put this code as a copy.
the one named weibo-catch(use to catch weibo profile),another named weibo-catch-user(use to catch follow),
then two program run together.

1 change the file 'WeiboCatch.py' findweibo(cls,sweb) like follows:

if your function is catch-follow then delete the "#" before t1 and append(t1) line

if your function is catch-profile then delete the "#" before t2 and append(t2) line

#----------------------

#t1 = threading.Thread(target=obj.catchfollow,args=("/"+userid+"/follow",))

#threads.append(t1)

t2 = threading.Thread(target=obj.catchprofile,args=("/"+userid+"/profile",))

threads.append(t2)

#---------------------- 

2 change the 'ConnSQL.py' def getuserid(self) and def setcompleteid(self,userid) like follows:

#----------------------
#if your function is catch-profile then use follow sql replace the code part 

#cursor.execute("SELECT * FROM weibocatch.w_user where (recon=0 or (recon=1 and color=0)) and flag=1 order by inserttime limit 1")

#if your function is catch-follow then use follow sql replace the code part

#cursor.execute("SELECT * FROM weibocatch.w_user where (recon=0 or (recon=1 and color=0)) and flag=0 order by inserttime limit 1")

#if your function is catch-profile then use follow sql replace the code part

#cursor.execute("UPDATE weibocatch.w_user SET flag = 2 WHERE wid = %s",(userid,))

#if your function is catch-follow then use follow sql replace the code part

#cursor.execute("UPDATE weibocatch.w_user SET flag = 1 WHERE wid = %s",(userid,))

#---------------------- 

why don't use multiprocess?

because at the beginning, many variable I have used have the same name. And at that time,
I overlook the suitable situation that the global variable should be used,if I want to use multiprocess this time,
I will have enormous work in all code reconstruction.

Don't worry, I will do this tough work in the future.
but here I must appologise, I can't. I only ensure the function can run correctly.

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

