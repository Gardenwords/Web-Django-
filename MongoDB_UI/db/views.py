from django.shortcuts import render,redirect
import pymongo
import datetime
import pandas as pd
# Create your views here.

def toPage(request, pageName):
    return render(request, pageName)

def masg(request):
    return render(request,'masg.htm')

def login(request):
    if request.method == "GET":
        return render(request, 'login.htm')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = myclient["resources"]
        collection = db["user"]
        u = request.POST.get("userAccount")
        p = request.POST.get("userPassword")

        for i in collection.find({"usrAccount": u}):
            if i['usrPassword'] == p:
                request.session['usrerAccount'] = u
                myclient.close()
                return redirect("../page/main.htm")
            else:
                myclient.close()
                return render(request,'login.htm', {'msg':'用户名或密码不正确'})

def main(request):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["resources"]
    collection = db["usrMsg"]
    if request.method == "GET":
        cnt = 0
        for i in collection.find().sort("usrNegative_comment", 1):
            if cnt == 0:
                request.session['username'] = i['usrName']
                request.session['usersex'] = i['usrSex']
                request.session['userage'] = i['usrAge']
                request.session['userability'] = i['usrAbility']
                request.session['salary'] = i['usrSalary']
                request.session['usertransaction'] = i['usrTransaction_number']
                request.session['usernegative'] = i['usrNegative_comment']
                cnt = cnt + 1
            else:
                break
        myclient.close()
        return render(request,'main.htm')
    else:
        data = pd.DataFrame(list(collection.find({},{"_id":0})))
        data.head()
        # 保存为csv格式
        data.to_csv('user_information.csv', encoding='gbk')
        return render(request,'main.htm')

def submit(request):
    if request.method == "GET":
        return render(request,'submit.htm')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = myclient["resources"]
        collection = db["user"]
        u = request.POST.get("userAccount")
        p = request.POST.get("userPassword")

        for i in collection.find({"usrAccount": u}):
            if i['usrAccount'] == u:
                return render(request,'login.htm', {'msg':'账户已存在'})
        mydict = {"usrAccount":u,"usrPassword":p}
        x = collection.insert_one(mydict)
        myclient.close()
        return render(request, 'masg.htm')

def userMsg(request):
    if request.method == "GET":
        return render(request,'userMsg.htm')
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["resources"]
    collection = db["usrMsg"]
    #获取数据
    usrName = request.POST.get("usrName")
    usrSex = request.POST.get("usrSex")
    usrAge = request.POST.get("usrAge")
    usrAbility = request.POST.get("usrAbility")
    usrWork_time =request.POST.getlist("usrWork_time")
    usrSalary = request.POST.get("usrSalary")

    Account = request.session['usrerAccount']
    mydict = {"usrAccount":Account,"usrName":usrName,"usrSex":usrSex,"usrAge":usrAge,"usrAbility":usrAbility,
              "usrWork_time":usrWork_time,"usrSalary":usrSalary,"usrTransaction_number":0,"usrNegative_comment":0}
    x = collection.insert_one(mydict)
    myclient.close()
    return redirect("../page/main.htm")
    

def search(request):
    if request.method == "GET":
        return render(request,'search.htm')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = myclient["resources"]
        collection1 = db["usrMsg"]
        #获得查询条件
        usrAbility = request.POST.get("usrAbility")
        status = request.POST.get("order")
        if status == "下单":
            print(request.session['orderTime'])
            usrerAccount = request.session['usrerAccount']  # 雇主账号
            usreeAccount = request.session['usreeAccount']  # 应聘账号
            usreeName = request.session['usrName']           # 应聘姓名
            usrTime = (datetime.date.today() - request.session['orderTime']).days
            usrPrice = usrTime * request.session['usrSalary']
            collection = db["usrConnection"]
            connection = {"usrerAccount": usrerAccount, "usreeAccount": usreeAccount, 'usreeName': usreeName,
                          "usrTime": usrTime, "usrPrice": usrPrice}
            action = collection.insert_one(connection)
            return render(request, "main.htm")
        else:
            x = []
            cnt = 0
            for i in collection1.find({'usrAbility': usrAbility},
                                      {"_id": 0, "usrAccount": 1, "usrName": 1, "usrSex": 1, "usrAge": 1, "usrAbility": 1,
                                       "usrWork_time": 1, "usrSalary": 1}).sort("usrSalary", 1):
                if (cnt == 0):
                    request.session['usrName'] = i['usrName']
                    request.session['usrSalary'] = i["usrSalary"]
                    request.session['usreeAccount'] = i['usrAccount']
                    request.session['orderTime'] = datetime.date.today()
                    cnt += 1
                    x.append(i)

                else:
                    break
                cnt = cnt + 1
        myclient.close()
        return render(request,"search.htm",{'x':x})

def employment(request):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["resources"]
    collection = db["usrConnection"]
    collection_Msg = db['usrMsg']
    usrerAccount = request.session['usrerAccount']  #雇主账号
    usreeAccount = request.session['usreeAccount']  # 应聘账号
    usreeName = request.session['usrName']           # 应聘姓名
    m = collection.find({"$or": [{"usrerAccount": usrerAccount}, {"usreeAccount": usrerAccount}]},
                        {"_id": 0, "usrerAccount": 1, "usreeAccount": 1, "usreeName": 1, "usrTime": 1, "usrPrice": 1})
    x = []
    for i in m:
        x.append(i)
    if request.method == "GET":
        myclient.close()
        return render(request,"employment.html",{'x':x})
    else:
        status = request.POST.get("complete")
        negative = request.POST.get("usrNegative_comment")
        if status == "完成" and negative == "是":
            collection.delete_one({"usrerAccount": usrerAccount})
            collection_Msg.update_one({"$and": [{"usrAccount": usreeAccount}, {"usrName": usreeName}]},
                                      {"$inc": [{"usrTransaction_number": 1}, {"usrNegative_comment: 1"}]})
        else:
            collection.delete_one({"usrerAccount": usrerAccount})
            collection_Msg.update_one({"$and": [{"usrAccount": usreeAccount}, {"usrName": usreeName}]},
                                      {"$inc": {"usrTransaction_number": 1}})
            myclient.close()
            return render(request, 'op_masg.htm')
