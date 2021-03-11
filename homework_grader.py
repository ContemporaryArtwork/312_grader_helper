import os.path
from glob import glob
import subprocess
import threading
import json
import sys

filename = ".gradingstatus"
assert (len(sys.argv)>1), "You need an argument for the location of your assigned students"
assigned_filename = sys.argv[1]
grades_filename = ".gradedata"
global grades
grades = {}
PORT = 8000

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
    f = open(grades_filename, "w")
    
    f.write(json.dumps(grades))
    f.close()

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
    Obj1 = input("Score for Obj1:\n")
    Obj1Notes = input("Notes for Obj1:\n")
    Obj2 = input("Score for Obj2:\n")
    Obj2Notes = input("Notes for Obj2:\n")
    Obj3 = input("Score for Obj3:\n")
    Obj3Notes = input("Notes for Obj3:\n")
    Obj4 = input("Score for Obj4:\n")
    Obj4Notes = input("Notes for Obj4:\n")
    Bonus = input("Score for bonus:\n")
    return [Obj1,Obj2,Obj3,Obj4,Bonus,"Objective 1: "+Obj1Notes+"; Objective 2: "+Obj2Notes+"; Objective 3: "+Obj3Notes+"; Objective 4: "+Obj4Notes]

def get_csv():
    retval = ""
    fLine = "Order: "
    for key in grades:
        fLine += (key+", ")
    retval += (fLine[:len(fLine)-2]+"\n")
    for key in grades:
        line = ""
        for idx in range(len(grades[key])):
            line+=("\""+grades[key][idx]+"\"")
            if idx!=5:
                line+=", "  
        line += "\n"
        retval += line
    return retval
#One unit of grading
def grading_unit():
    global grades
    #Get the index of the student currently being graded
    current = readcurrent()
    
    #Get the ubid of that student
    current_student = readassigned(current)
    if current_student==-1:
        print("You've run out of student to grade! Crashing and printing csv...")
        print("Copy and paste in results, click on data in the top bar and press split text to columns")
        print(get_csv())
        return False
    try:
        current_student_dir = glob(f'./{current_student}/')[0]
    except:
        print("You've run out of student to grade in this directory! Crashing and printing csv...")
        print("Copy and paste in results, click on data in the top bar and press split text to columns")
        print(get_csv())
        return False
    #Recursively search for their dockerfile
    dockerfile_location = glob(current_student_dir+"/**/[Dd]ockerfile",recursive=True)
    #Recursively search for their report
    report_location = glob(current_student_dir+"/**/report.txt",recursive=True)
    #They must have a dockerfile
    assert(len(dockerfile_location)==1),f'{current_student_dir} does not have a dockerfile?'
    dockerfile_location = dockerfile_location[0]
    
    #They might have a report, if so print it
    if (len(report_location)>=1):
        with open(report_location[0]) as f:
                content = f.readlines()
        f.close()
        print(f'{current_student}\'s Report')
        for line in content:
            print(line.strip())
    else:
        print(f'Appears {current_student} does not have a report.txt...')
    print(f'\nKilling containers, building and running container on port {PORT}...')
    #Kill all docker containers
    kill = threading.Thread(target=run,
        args=('docker ps -q | % { docker stop $_ }',), 
    )
    kill.start()
    
    #Build the container
    docker_build_output = run(f'docker build -t student -f {dockerfile_location} {os.path.dirname(dockerfile_location)}')
    #Open path in explorer
    subprocess.Popen(f'explorer /select,\"{os.path.realpath(dockerfile_location)}\"')
    #Run the container
    kill.join()
    runT = threading.Thread(target=run,
        args=(f'docker container run --publish {PORT}:8000 --detach student',), 
    )
    runT.start()
    runT.join()
    print("Done!")
    
    
    
    grades[current_student] = prompt()
    prompt_text = "q to quit, c to continue, r to redo grading data entry, j to print csv output\n"
    
    u_input = input(prompt_text)
    
    while (u_input!="q" and u_input!="c" and u_input!="r" and u_input!="j"):
        u_input = input(prompt_text)
    while(u_input=="r"):
        grades[current_student] = prompt()
        u_input = input(prompt_text)
    writegrades()
    current = int(current) + 1
    writecurrent(str(current))
    if u_input == "q":
        return False
    elif u_input == "c":
        return True
    elif u_input == "j":
        print("Copy and paste in results, click on data in the top bar and press split text to columns")
        print(get_csv())
        return False
if not os.path.isfile(filename) or not os.path.isfile(grades_filename):
    print("Local data files do not exist. Rewriting...")
    grades = {}
    writegrades()
    writecurrent("0")
else: 
    reset = input("Enter y to reset data\n")
    if (reset=="y"):
        grades = {}
        writegrades()
        writecurrent("0")
    grades = readgrades()

while grading_unit():
    print("Grading loop...")
print("Killing remaining container...please wait...")   
kill = threading.Thread(target=run,
        args=('docker ps -q | % { docker stop $_ }',), 
    )
kill.start()
kill.join()
    

