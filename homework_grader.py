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
times = []


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
    scores = {}
    notes = {}
    
    scores['obj1Score']=(input("Score for Obj1:\n"))
    notes['obj1Notes']=(input("Notes for Obj1:\n"))
    scores['obj2Score']=(input("Score for Obj2:\n"))
    notes['obj2Notes']=(input("Notes for Obj2:\n"))
    scores['obj3Score']=(input("Score for Obj3:\n"))
    notes['obj3Notes']=(input("Notes for Obj3:\n"))
    scores['obj4Score']=(input("Score for Obj4:\n"))
    notes['obj4Notes']=(input("Notes for Obj4:\n"))
    scores['bonusScore']=(input("Score for bonus:\n"))
    notes['bonusNotes']=(input("Notes for the bonus:\n"))
    notes['overallNotes']=(input("Overall notes:\n"))
    
    return {"scores":scores,"notes":notes}

def get_notes(notes):
    notesString = ""
    
    #Iterate through the notes
    for key in notes:
        if len(notes[key])>0:
            #Add delimiter per discrete note
            if len(notesString)>0:
                notesString += "\\n "
                #Replace double quotes with single quotes
                notes[key].replace("\"","\'")
            
            #Handle specific notes
            if key=="obj1Notes":
                notesString += ("Objective 1: " + notes['obj1Notes'])
            elif key=="obj2Notes":
                notesString += ("Objective 2: " + notes['obj2Notes'])
            elif key == "obj3Notes":
                notesString += ("Objective 3: " + notes['obj3Notes'])
            elif key == "obj4Notes":
                notesString += ("Objective 4: " + notes['obj4Notes'])
            elif key == "bonusNotes":
                notesString += ("Notes for the bonus: " + notes['bonusNotes'])
            elif key == "overallNotes":
                notesString += ("Overall notes: " + notes['overallNotes'])
    return notesString
              

def get_csv():
    retval = ""
    #Print order
    fLine = "Order: "
    for key in grades:
        fLine += (key+", ")
    retval += (fLine[:len(fLine)-2]+"\n")
    #Actually make the csv
    for key in grades:
        line = ""
        scores = grades[key]["scores"]
        notes = grades[key]["notes"]
        notesVal = get_notes(notes)
        
        for idx,key2 in enumerate(scores):
            if not (regrade and key2=='bonusScore'):
                line+=scores[key2]
                if (idx<len(scores)-1):
                    line+=", "
        if not regrade:
            line+=f', {notesVal}'
        if regrade:
            line = line[:len(line)-2]
        line += "\n"
        retval += line
    return retval
    
def nomore_students():
    print("You've run out of student to grade! Crashing and printing csv...")
    print("Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
    print("If you have any troubles, make sure to be splitting by comma")
    print("------------")
    print(get_csv())
    print("------------")

def print_report(current_student,report_location):
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

def handle_dockerfiles(dockerfile_location):
    print("UHOH\n------------")
    print(f'{current_student} has more than 1 dockerfile!?!?')
    for num,dockerfile in enumerate(dockerfile_location):
        print(num,dockerfile)
    idx = int(input("Enter the index of the dockerfile location you like the best!\n"))
    assert(idx>=0 and idx<len(dockerfile_location)),"Crashing because you entered a bad index!!"
    dockerfile_location = [dockerfile_location[idx]]
    print("------------")
    return dockerfile_location

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
        regradeStr = input("Regrade? y/n\n")
        if regradeStr == "y":
            regrade = True
        nomore_students()
        return False
    try:
        current_student_dir = glob(f'.\\{current_student}\\')[0]
    except:
        nomore_students()
        return False
    #Recursively search for their report
    report_location = glob(current_student_dir+"\\**\\*report*",recursive=True)
    
    #print report
    print_report(current_student,report_location)
    
    #Recursively search for their dockerfile
    dockerfile_location = glob(current_student_dir+"\\**\\[Dd]ockerfile",recursive=True)
    
    try:
        compose_location = glob(current_student_dir+"\\**\\docker-compose.yml",recursive=True)[0]
        PORT = 8080
        has_compose = True
    except:
        PORT = 8000
        has_compose = False
    
            
    #Handle multiple dockerfiles
    if (not has_compose and len(dockerfile_location)>1):
        dockerfile_location = handle_dockerfiles(dockerfile_location)
    
    
    if (not has_compose and len(dockerfile_location)==0):
        print(f'{current_student} does not have a dockerfile? Initiating manual grading...')    
    else:
        #This step isn't necessary anymore
        dockerfile_location = dockerfile_location[0]
        #If we're in windows, open the path of the dockerfile
        if os.name == 'nt':
            subprocess.Popen(f'explorer /select,\"{os.path.realpath(dockerfile_location)}\"')
        
        print(f'Killing containers, building and running container on port {PORT}...')
        #Kill all docker containers
        client = docker.from_env()
        for container in client.containers.list():
            container.stop()
            if (len(sys.argv)>2 and sys.argv[2]=="--deleteall"):
                container.remove()
            
        buildAndRun = True
        while buildAndRun:
            try:
                if has_compose and os.name=='nt':
                    process = subprocess.Popen(f'docker-compose --log-level ERROR -f \"{os.path.realpath(compose_location)}\" up --detach')
                    process.wait()
                    if firstrun:
                        webbrowser.open(f'http://localhost:8080/')
                        firstrun = False
                else:
                    #We don't have a docker-compose
                    #Build the container
                    dcontainer = client.images.build(path=os.path.realpath(os.path.dirname(dockerfile_location)),dockerfile=os.path.realpath(dockerfile_location),tag="student")
                    #docker_build_output = run(f'docker build -t student -f {dockerfile_location} {os.path.dirname(dockerfile_location)}')
                    #Open path in explorer
                    
                    #Run the container
                    container = client.containers.run('student',ports={f'{PORT}/tcp':8000},
                                                      detach=True)
                    if firstrun:
                        webbrowser.open(f'http://localhost:{PORT}/')
                        firstrun = False
                buildAndRun = False
                print("Done!")
                
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
    #Print time and # of students graded
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    print("Time: ", current_time)
    times.append(current_time)
    print(f'You have graded {len(grades)} students')
    
    print("------------")
    grades[current_student] = prompt()
    print("\nYour input:")
    print(grades[current_student])
    print("------------")
    prompt_text = "q to quit, c to continue, r to redo grading data entry, j to print csv output, d for docker-compose restart\n"
    
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
        elif u_input == "d":
            if not has_compose:
                print("no compose file found!")
            else:
                process = subprocess.Popen(f'docker-compose -f \"{os.path.realpath(compose_location)}\" restart')
                process.wait()
        u_input = input(prompt_text)
    
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    times.append(current_time)
    print("Time: ", current_time)
    
    
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
print(times)   
client = docker.from_env()
for container in client.containers.list():
    container.stop()
if (len(sys.argv)>2 and sys.argv[2]=="--deleteall"):
    run("docker ps -a -q | % { docker rm $_ }")


    

