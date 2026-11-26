from datetime import*
import ast
from tkinter import*
from tkinter import messagebox
from tkinter import ttk

##barebones

def makeSchedule(custname, custaddress,yyyy,mm,dd,hour,minute):
    sched=datetime(yyyy,mm,dd,hour,minute)

    sch= {"name": custname,"address":custaddress,"year":yyyy,"month":mm,"day":dd,"hour":hour,"minute":minute}
    ##print(sch)
    return sch
    0

def getDateTime(sch):
    if isinstance(sch, dict):
        return datetime(sch["year"],sch["month"],sch["day"],sch["hour"],sch["minute"],0).strftime("%Y-%m-%d %H:%M")

    else:
        print("Error: not dictionary type")
        0

def getTime(sch):
    if isinstance(sch, dict):
        return time(sch["hour"],sch["minute"],0).strftime("%H:%M")

    else:
        print("Error: not dictionary type")
        0

def getDate(sch):
    if isinstance(sch, dict):
        return date(sch["year"],sch["month"],sch["day"])

    else:
        print("Error: not dictionary type")
        0

def storeSchedule(sch):
    sch=str(sch)
    sch=sch+"\n"


    with open("SchedulesData.txt","r") as file:
        lines=file.readlines()
        lastlineSlashN=lines[-1].endswith("\n") #detects if the last line has a \n missing, if it is missing two schedules will be saved to the same line and the formatting will have issues and break
        if str(sch) in lines:
            print("already in file")
        else:
            with open("SchedulesData.txt","a") as file:
                if lastlineSlashN==False:
                    file.write("\n")
                file.write(sch)
            0

def findinfo(category,info):
    l=[]
    ##enter all orleave category blank in order to get all schedules into a list
    if info=="all" or category=="" or info=="" or category=="all":
        with open("SchedulesData.txt","r") as file:
                for line in file:
                    l.append(ast.literal_eval(line))
    else:
        with open("SchedulesData.txt","r") as file:
            for line in file:
                if info == ast.literal_eval(line)[category]:
                    l.append(ast.literal_eval(line))
    return l
    0

def deleteinfo(sch):
    sch=str(sch)
    print(sch)

    with open("SchedulesData.txt","r") as file:
        lines=file.readlines()
    with open("SchedulesData.txt","w") as file:
        for line in lines:
            if line.strip("\n") != sch:
                file.write(line)

def editinfo(sch,newsch):
    sch=str(sch)
    print(sch)

    with open("SchedulesData.txt","r") as file:
        lines=file.readlines()
        lastlineSlashN=lines[-1].endswith("\n") #detects if the last line has a \n missing, if it is missing two schedules will be saved to the same line and the formatting will have issues and break
    with open("SchedulesData.txt","w") as file:
        for line in lines:
            
            if line.strip("\n") != sch:
                file.write(line)
            elif line.strip("\n") == sch:
                file.write(str(newsch))
        if lastlineSlashN==False:
                file.write("\n")

def formatting(sch):
    return sch["name"]+" "+sch["address"]+" "+str(getDateTime(sch))

#sch=makeSchedule("name","place3",1979,9,1,9,16)
#storeSchedule(sch)
##print(findinfo("address","place2"))
##deleteinfo(sch)
##print(sorted(findinfo("address","all"),key=lambda x: x["name"]))
##print(sorted(findinfo("address","all"),key=lambda x: (x["year"],x["month"],x["day"])))  



#now=datetime.now().ctime()
#adate=time(2026,2,2,12,46,0)
#print(adate)




def windowmaker():

    def enterSchedinfo():
        try:
            if nameEnt.get()=="" or addressEnt.get()=="":
                if messagebox.showinfo(title="Error", message="Must have name or address"):
                    0
            else:
                sch=makeSchedule(nameEnt.get(),addressEnt.get(),int(yearEnt.get()),int(monthEnt.get()),int(dayEnt.get()),int(hourEnt.get()),int(minuteEnt.get()))
                print(sch)
                storeSchedule(sch)
                schedString=formatting(sch)
                pointSchedDict[schedString]=str(sch)
                listbox.insert(listbox.size(),schedString)
        except Exception as e:
            if messagebox.showinfo(title="Error", message=f"Error has occurerd: \n {e}"):
                0
        0
    def delete():
        text=listbox.get(listbox.curselection())
        if messagebox.askokcancel(title="Are you sure", message="Are you sure you want to delete Schedule:\n"+text):
            sch=pointSchedDict[text]
            deleteinfo(sch)
            listbox.delete(listbox.curselection())


    def makelistbox():
        schList=findinfo("","")
        for i in range(0, len(schList)):
            d=ast.literal_eval(str(schList[i]))
            print(d["name"])
            schedString=formatting(d)
            pointSchedDict[schedString]=str(d)
            listbox.insert(i,schedString)

    def sortSchedule():
        val=combo.get()
        if val not in sortval:
                if messagebox.showinfo(title="Error", message="No sort value selected"):
                    0
        else:
            listbox.delete(0,END)
            sort1="all"
            sort2="all"
            if combo2.get()=="Any Customer":
                sort1="all"
                sort2="all"
            else:
                sort1="name"
                sort2=combo2.get()

            if val=="Name":
                sch=sorted(findinfo(sort1,sort2),key=lambda x: x["name"])
            elif val=="Address":
                sch=sorted(findinfo(sort1,sort2),key=lambda x: x["address"])
            elif val=="Date and Time":
                sch=sorted(findinfo(sort1,sort2),key=lambda x: (x["year"],x["month"],x["day"]))
            print(sch)
            for i in range(0, len(sch)):
                d=ast.literal_eval(str(sch[i]))
                print(d["name"])
                schedString=formatting(d)
                pointSchedDict[schedString]=str(d)
                listbox.insert(i,schedString)


    
    def edit_window():
        text=listbox.get(listbox.curselection())
        sch=pointSchedDict[listbox.get(listbox.curselection())]  
        
        def enter():
            try:
                
                newsch=makeSchedule(nameEnt.get(),addressEnt.get(),int(yearEnt.get()),int(monthEnt.get()),int(dayEnt.get()),int(hourEnt.get()),int(minuteEnt.get()))
                if messagebox.askokcancel(title="Are you sure", message="Are you sure you want to edit this Schedule:\n"+text+"\n to \n"+formatting(newsch)):
                    editinfo(sch,newsch)
                    listbox.delete(0,END)
                    schList=findinfo("","")
                    for i in range(0, len(schList)):
                                        d=ast.literal_eval(str(schList[i]))
                                        print(d["name"])
                                        schedString=formatting(d)
                                        pointSchedDict[schedString]=str(d)
                                        listbox.insert(i,schedString)
                    newwindow.destroy()
            except Exception as e:
                if messagebox.showinfo(title="Error", message=f"Error has occurerd: \n {e}"):
                    0



        newwindow=Toplevel()
        newwindow.geometry("720x420")
        eframe=Frame(newwindow)
        eframe.grid(row=0,column=0)

        infoCust = Label(eframe,text="Customer information: ").grid(row=0,column=0,columnspan=2)

        nameLabel = Label(eframe,text="Name: ").grid(row=1,column=0)
        nameEnt=Entry(eframe)
        nameEnt.grid(row=1,column=1)

        addressLabel = Label(eframe,text="Address: ").grid(row=2,column=0)
        addressEnt=Entry(eframe)
        addressEnt.grid(row=2,column=1)

        infoSched = Label(eframe,text="Date of schedule: ").grid(row=3,column=0,columnspan=2)

        yearLabel = Label(eframe,text="Year(yyyy): ").grid(row=4,column=0)
        yearEnt=Entry(eframe)
        yearEnt.grid(row=4,column=1)

        monthLabel = Label(eframe,text="Month(mm): ").grid(row=5,column=0)
        monthEnt=Entry(eframe)
        monthEnt.grid(row=5,column=1)

        dayLabel = Label(eframe,text="Day(dd): ").grid(row=6,column=0)
        dayEnt=Entry(eframe)
        dayEnt.grid(row=6,column=1)

        timeLabel = Label(eframe,text="Time of day ").grid(row=7,column=0,columnspan=2)


        hourLabel = Label(eframe,text="Hours: ").grid(row=8,column=0)
        hourEnt=Entry(eframe)
        hourEnt.grid(row=8,column=1)

        hourLabel = Label(eframe,text="Minutes: ").grid(row=9,column=0)
        minuteEnt=Entry(eframe)
        minuteEnt.grid(row=9,column=1)

        nameEnt.insert(0,ast.literal_eval(sch)["name"])
        addressEnt.insert(0,ast.literal_eval(sch)["address"])
        yearEnt.insert(0,ast.literal_eval(sch)["year"])
        monthEnt.insert(0,ast.literal_eval(sch)["month"])
        dayEnt.insert(0,ast.literal_eval(sch)["day"])
        hourEnt.insert(0,ast.literal_eval(sch)["hour"])
        minuteEnt.insert(0,ast.literal_eval(sch)["minute"])


        enterbutton= Button(eframe,text="Enter",command=enter).grid(row=10,column=0,columnspan=2)


    
    window=Tk()
    window.geometry("720x500")
    frame=Frame(window)
    frame.grid(row=0,column=0)

    infoCust = Label(frame,text="Add Customer Information: ").grid(row=0,column=0,columnspan=2)

    nameLabel = Label(frame,text="Name: ").grid(row=1,column=0)
    nameEnt=Entry(frame)
    nameEnt.grid(row=1,column=1)

    addressLabel = Label(frame,text="Address: ").grid(row=2,column=0)
    addressEnt=Entry(frame)
    addressEnt.grid(row=2,column=1)

    infoSched = Label(frame,text="Date of schedule: ").grid(row=3,column=0,columnspan=2)

    yearLabel = Label(frame,text="Year(yyyy): ").grid(row=4,column=0)
    yearEnt=Spinbox(frame,from_=1,to=float('inf'), increment=1)
    yearEnt.grid(row=4,column=1)

    monthLabel = Label(frame,text="Month(mm): ").grid(row=5,column=0)
    monthEnt=Spinbox(frame,from_=1,to=12, increment=1)
    monthEnt.grid(row=5,column=1)

    dayLabel = Label(frame,text="Day(dd): ").grid(row=6,column=0)
    dayEnt=Spinbox(frame,from_=1,to=31, increment=1)
    dayEnt.grid(row=6,column=1)

    timeLabel = Label(frame,text="Time of day ").grid(row=7,column=0,columnspan=2)


    hourLabel = Label(frame,text="Hours: ").grid(row=8,column=0)
    hourEnt=Spinbox(frame,from_=0,to=23, increment=1)
    hourEnt.grid(row=8,column=1)

    hourLabel = Label(frame,text="Minutes: ").grid(row=9,column=0)
    minuteEnt=Spinbox(frame,from_=1,to=59, increment=1)
    minuteEnt.grid(row=9,column=1)

    enterbutton= Button(frame,text="Enter",command=enterSchedinfo).grid(row=10,column=0,columnspan=2)

    ##list of schedules
    frame2=Frame(window)
    frame2.grid(row=1,column=0)
    listbox=Listbox(frame2,width=30)
    listbox.grid(row=1,column=0)
    schList=findinfo("","")
    pointSchedDict={}

    makelistbox()

    
    deletebutton= Button(frame2,text="delete",command=delete).grid(row=2,column=0)
    ##editbutton= Button(frame2,text="edit",command=edit).grid(row=2,column=1)

    editbutton= Button(frame2,text="edit",command=edit_window).grid(row=2,column=1)


    frame3=Frame(window)
    frame3.grid(row=1,column=1)
    sortbutton=Button(frame3,text="Select how to Sort",command=sortSchedule).grid(row=1,column=2)
    sortval=["Name","Address","Date and Time"]
    combo=ttk.Combobox(frame3,values=sortval,state="readonly")
    combo.set("Sort By")
    combo.grid(row=2,column=2)


    sortvalueStr=[cust for cust in pointSchedDict.values()]
    sortval2=["Any Customer"]
    for cust in sortvalueStr:
        sortval2.append(ast.literal_eval(cust)["name"])
    combo2=ttk.Combobox(frame3,values=sortval2,state="readonly")
    combo2.set("Any Customer")
    combo2.grid(row=4,column=2)


    window.mainloop()

windowmaker()
