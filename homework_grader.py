import os.path
from glob import glob
import subprocess
import threading
import json
import sys
import docker
import webbrowser
from datetime import datetime






filename = ".gradingstatus"
assert (len(sys.argv)>1), "You need an argument for the location of your assigned students"
assigned_filename = sys.argv[1]
grades_filename = ".gradedata"
global grades
grades = {}
PORT = 8000
firstrun = True
regrade = False



def readassigned(current):
    #If the file exists
    assert(os.path.isfile(assigned_filename))
    #Read file
    with open(assigned_filename) as f:
        content = f.readlines()
    f.close()
    for idx in range(len(content)):
        content[idx] = content[idx].strip()
    
    assert(len(content)!=0)
    if not int(current)<len(content):
        return -1
    
    return content[int(current)]
    
    
    

def readcurrent():
    #If the file exists
    if os.path.isfile(filename):
        #Read file
        with open(filename) as f:
            content = f.readlines()
        f.close()
        #Probably should do some check here
        assert(len(content)!=0)
        return content[0]
    else:
        #Get first subdir in dir
        return 0
def writecurrent(current):
    f = open(filename, "w")
    f.write(current)
    f.close()
    
def writegrades():
    with open(grades_filename, "w") as outfile:
        json.dump(grades, outfile, indent=2, separators=(',', ': '))
    

def readgrades():
    if not os.path.isfile(grades_filename):
        return ""
    with open(grades_filename) as f:
       content = f.read()
    f.close()
    if (len(content)==0):
        return ""
    
    retval = json.loads(content)
    
    if not type(retval) == dict:
        retval = {}
    return retval

#Found this online 
def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed
def prompt():
    userData = []
    userData.append(input("Score for Obj1:\n"))
    userData.append(input("Notes for Obj1:\n"))
    userData.append(input("Score for Obj2:\n"))
    userData.append(input("Notes for Obj2:\n"))
    userData.append(input("Score for Obj3:\n"))
    userData.append(input("Notes for Obj3:\n"))
    userData.append(input("Score for Obj4:\n"))
    userData.append(input("Notes for Obj4:\n"))
    userData.append(input("Score for bonus:\n"))
    userData.append(input("Notes for the bonus:\n"))
    userData.append(input("Overall notes:\n"))
    notesString = ""
    for idx in range(len(userData)):
        if len(userData[idx])>0:
            if (idx==1 or idx==3 or idx == 5 or idx == 7 or idx == 9 or idx==10) and len(notesString)>0:
                notesString += "; "
            
            if idx==1:
                notesString += ("Objective 1: " + userData[idx])
            elif idx==3:
                notesString += ("Objective 2: " + userData[idx])
            elif idx==5:
                notesString += ("Objective 3: " + userData[idx])
            elif idx==7:
                notesString += ("Objective 4: " + userData[idx])
            elif idx==9:
                notesString += ("Notes for the bonus: " + userData[idx])
            elif idx==10:
                notesString += ("Overall notes: " + userData[idx])
            
    if regrade:
        notesString = "Regrade: "+notesString
    assert(len(userData)>0),"You need to enter something!"            
    #notesString = "Objective 1: "+Obj1Notes+"; Objective 2: "+Obj2Notes+"; Objective 3: "+Obj3Notes+"; Objective 4: "+Obj4Notes+"; Bonus: "+BonusNotes+"; Other notes: "+MiscNotes
    return [userData[0],userData[2],userData[4],userData[6],userData[8],notesString]

def get_csv():
    retval = ""
    fLine = "Order: "
    for key in grades:
        fLine += (key+", ")
    retval += (fLine[:len(fLine)-2]+"\n")
    for key in grades:
        line = ""
        for idx in range(len(grades[key])):
            line+=("\""+grades[key][idx].replace("\"","\'")+"\"")
            if idx!=5:
                line+=","  
        line += "\n"
        retval += line
    return retval
#One unit of grading
def grading_unit():
    global grades
    global firstrun
    grades = readgrades()
    #Get the index of the student currently being graded
    current = readcurrent()
    
    #Get the ubid of that student
    current_student = readassigned(current)
    if current_student==-1:
        print("You've run out of student to grade! Crashing and printing csv...")
        print("Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
        print("If you have any troubles, make sure to be splitting by comma")
        print("------------")
        print(get_csv())
        print("------------")
        return False
    try:
        current_student_dir = glob(f'.\\{current_student}\\')[0]
    except:
        print("You've run out of student to grade in this directory! Crashing and printing csv...")
        print("Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
        print("If you have any troubles, make sure to be splitting by comma")
        print(get_csv())
        return False
    
    #Recursively search for their dockerfile
    dockerfile_location = glob(current_student_dir+"\\**\\[Dd]ockerfile",recursive=True)
    #Recursively search for their report
    report_location = glob(current_student_dir+"\\**\\*report*",recursive=True)
    #They must have a dockerfile
    #They might have a report, if so print it
    if (len(report_location)>1):
        print("------------")
        print(f'{current_student} has more than 1 reports')
        for num,report in enumerate(report_location):
            print(num,report)
        idx = int(input("Enter the index of the report location you like the best!\n"))
        assert(idx>=0 and idx<len(report_location)),"Crashing because you entered a bad index!!"
        report_location = [report_location[idx]]
        print("------------")
    
    if (len(report_location)==1):
        print(f'{current_student}\'s Report:\n'+"------------")
        
        with open(report_location[0],encoding='utf-8') as f:
                content = f.readlines()
        f.close()
        
        for line in content:
            print(line.strip())
        if (len(content)==0):
            print("Empty report!")
        print("------------")
    
    else:
        print("------------")
        print(f'Appears {current_student} does not have a report.txt...')
        print("------------")
            
    #Handle dockerfile stuff
    
        
        
    if (len(dockerfile_location)>1):
        print("UHOH\n------------")
        print(f'{current_student} has more than 1 dockerfile!?!?')
        for num,dockerfile in enumerate(dockerfile_location):
            print(num,dockerfile)
        idx = int(input("Enter the index of the dockerfile location you like the best!\n"))
        assert(idx>=0 and idx<len(dockerfile_location)),"Crashing because you entered a bad index!!"
        dockerfile_location = [dockerfile_location[idx]]
        print("------------")
    
    
    if (len(dockerfile_location)==0):
        print(f'{current_student} does not have a dockerfile? Initiating manual grading...')    
    else:
        dockerfile_location = dockerfile_location[0]
        if os.name == 'nt':
            subprocess.Popen(f'explorer /select,\"{os.path.realpath(dockerfile_location)}\"')
        
        print(f'Killing containers, building and running container on port {PORT}...')
        #Kill all docker containers
        '''
        kill = threading.Thread(target=run,
            args=('docker ps -q | % { docker stop $_ }',), 
        )
        kill.start()'''
        client = docker.from_env()
        for container in client.containers.list():
            container.stop()
            if (len(sys.argv)>2 and sys.argv[2]=="--deleteall"):
                container.remove()
            
        buildAndRun = True
        while buildAndRun:
            try:
                #Build the container
                dcontainer = client.images.build(path=os.path.realpath(os.path.dirname(dockerfile_location)),dockerfile=os.path.realpath(dockerfile_location),tag="student")
                #docker_build_output = run(f'docker build -t student -f {dockerfile_location} {os.path.dirname(dockerfile_location)}')
                #Open path in explorer
                
                #Run the container
                #kill.join()
                container = client.containers.run('student',ports={f'{PORT}/tcp':8000},
                                                  detach=True)
                if firstrun:
                    webbrowser.open(f'http://localhost:{PORT}/')
                    firstrun = False
                buildAndRun = False
                print("Done!")
                now = datetime.now()
                current_time = now.strftime("%I:%M %p")
                print("Current Time =", current_time)
            except Exception as e:
                print("Error!")
                print(e)
                tryAgain = input("Try building/running again? y/n")
                while tryAgain!="y" and tryAgain!="n":
                    tryAgain = input("Try building/running again? y/n")
                if (tryAgain=="n"):
                    buildAndRun = False
                    exitVar = input("Exit? y/n")
                    while exitVar!="y" and exitVar!="n":  
                        exitVar = input("Exit? y/n")
                    if (exitVar=="y"):
                        sys.exit("Crashing because dockerfile is broken") 
                    else:
                        print("Going onto grading...")
    
    print("------------")
    grades[current_student] = prompt()
    print("\nYour input:")
    print(grades[current_student])
    print("------------")
    prompt_text = "q to quit, c to continue, r to redo grading data entry, j to print csv output\n"
    
    u_input = ""
    
    while (u_input!="q" and u_input!="c"):
        if u_input=="r":
            print("------------")
            grades[current_student] = prompt()
            print("\nYour input:")
            print(grades[current_student])
            print("------------")
        elif u_input == "j":
            print("Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
            print("If you have any troubles, make sure to be splitting by comma")
            print("------------")
            print(get_csv())
            print("------------")
        u_input = input(prompt_text)
    
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    print("Time: ", current_time)
    print(f'You have graded {len(grades)} students')
    
    save = ""
    while save!="y" and save!="n" and u_input!="c":
        save = input("save? y/n")
    if save=="y" or u_input=="c":
        writegrades()
        current = int(current) + 1
        writecurrent(str(current))
            
    if u_input == "q":
        return False
    elif u_input == "c":
        return True
    



if not os.path.isfile(filename) or not os.path.isfile(grades_filename):
    print("Local data files do not exist. Rewriting...")
    grades = {}
    writegrades()
    writecurrent("0")
else:
    grades = readgrades()
    prompt_text = "Enter y to reset data or j to print csv output, or r to use regrade mode. Otherwise press enter to start!\n"
    print(f'You have graded {len(grades)} students')
    
    reset = input(prompt_text)
    
    while reset!="y" and reset!="j" and reset!="r" and reset.strip()!="":
        if (reset=="y"):
            print("Resetting...")
            grades = {}
            writegrades()
            writecurrent(str(0))
        elif reset=="j":
            print("Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
            print("If you have any troubles, make sure to be splitting by comma")
            print("------------")
            print(get_csv())
            print("------------")
        
    
    
    
    if reset=="r":
        print("Will signal that we are regrading in feedback column")
        regrade = True
while grading_unit():
    print("Grading loop...")
print("Killing remaining container...please wait...")   
client = docker.from_env()
for container in client.containers.list():
    container.stop()
if (len(sys.argv)>2 and sys.argv[2]=="--deleteall"):
    run("docker ps -a -q | % { docker rm $_ }")


    

