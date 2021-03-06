import csv
import json
import os.path
import subprocess
import sys
import webbrowser
from datetime import datetime
from glob import glob

import docker

filename = ".gradingstatus"
assert (len(sys.argv) > 1), "You need an argument for the location of your assigned students"
assigned_filename = sys.argv[1]
grades_filename = ".gradedata"
global grades
grades = {}
PORT = 8000
firstrun = True
regrade = False
times = []
deleteall = False
is_hw5 = False


def process_argv():
    global regrade
    global deleteall
    global is_hw5
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if (arg == "--deleteall"):
                deleteall = True
            elif (arg == "--regrade"):
                regrade = True
            elif (arg == "--hw5"):
                is_hw5 = True


def parse_regrades(student):
    grades = []
    notes = ""
    if os.path.isfile('regrades.csv'):
        with open('regrades.csv') as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                if row[0] == student:
                    for idx, val in enumerate(row[1:]):
                        try:
                            if int(val)==int(val):
                                grades.append(val)
                        except:
                            notes = val
    return (grades, notes)




def readassigned(current):
    # If the file exists
    assert (os.path.isfile(assigned_filename))
    # Read file
    with open(assigned_filename) as f:
        content = f.readlines()
    f.close()
    for idx in range(len(content)):
        content[idx] = content[idx].strip()

    assert (len(content) != 0)
    if not int(current) < len(content):
        return -1

    return content[int(current)]


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
    if (len(content) == 0):
        return ""

    retval = json.loads(content)

    if not type(retval) == dict:
        retval = {}
    return retval


def readcurrent(grades):
    with open(assigned_filename) as f:
        content = f.readlines()
    f.close()

    for idx, var in enumerate(content):

        if not (var.strip() in grades):
            print(var)
            return idx

    return -1


# Found this online
def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


def prompt(grades):
    global is_hw5
    global regrade
    scores = {}
    notes = {}
    

    if is_hw5:
        if regrade:
            for idx, grade in enumerate(grades):
                scoreString = ''
                notesString = ''
                objString = ''
                if idx==1:
                    scoreString = 'obj2/3Score'
                    notesString = 'obj2/3Notes'
                    objString = 'Objectives 2/3'
                elif idx==2:
                    scoreString = 'obj4Score'
                    notesString = 'obj4Notes'
                    objString = 'Objective 4'
                else:
                    scoreString = f'obj{idx+1}Score'
                    notesString = f'obj{idx+1}Notes'
                    objString = f'Objective {idx+1}'
                if int(grade) == 3:
                    scores[scoreString] = 3
                    notes[notesString] = ''
                else:
                    scores[scoreString] = (input(f'Prev score: {grade}\nScore for {objString}:\n'))
                    if scores[scoreString].strip() == '':
                        print(f'Giving original grade of {grade}')
                        scores[scoreString] = grade
                    notes[notesString] = (input(f'Notes for {objString}:\n'))
            scores['bonusScore'] = 0
            notes['bonusNotes'] =  ''
            notes['overallNotes'] = (input("Overall notes:\n"))
        else:
            scores['obj1Score'] = (input("Score for Obj1:\n"))
            notes['obj1Notes'] = (input("Notes for Obj1:\n"))
            scores['obj2/3Score'] = (input("Score for Obj2/3:\n"))
            notes['obj2/3Notes'] = (input("Notes for Obj2/3:\n"))
            scores['obj4Score'] = (input("Score for Obj4:\n"))
            notes['obj4Notes'] = (input("Notes for Obj4:\n"))
            scores['bonusScore'] = (input("Score for bonus:\n"))
            notes['bonusNotes'] = (input("Notes for the bonus:\n"))
            notes['overallNotes'] = (input("Overall notes:\n"))
    else:
        if regrade:
            for idx, grade in enumerate(grades):
                if int(grade) == 3:
                    scores[f'obj{idx+1}Score'] = 3
                    notes[f'obj{idx+1}Notes'] = ''
                else:
                    scores[f'obj{idx+1}Score'] = (input(f'Prev score: {grade}\nScore for Obj{idx+1}:\n'))
                    if scores[f'obj{idx+1}Score'].strip() == '':
                        print(f'Giving original grade of {grade}')
                        scores[f'obj{idx+1}Score'] = grade
                    notes[f'obj{idx+1}Notes'] = (input(f'Notes for Obj{idx+1}:\n'))
            scores['bonusScore'] = 0
            notes['bonusNotes'] =  ''
            notes['overallNotes'] = (input("Overall notes:\n"))
        else:
            scores['obj1Score'] = (input("Score for Obj1:\n"))
            notes['obj1Notes'] = (input("Notes for Obj1:\n"))
            scores['obj2Score'] = (input("Score for Obj2:\n"))
            notes['obj2Notes'] = (input("Notes for Obj2:\n"))
            scores['obj3Score'] = (input("Score for Obj3:\n"))
            notes['obj3Notes'] = (input("Notes for Obj3:\n"))
            scores['obj4Score'] = (input("Score for Obj4:\n"))
            notes['obj4Notes'] = (input("Notes for Obj4:\n"))
            scores['bonusScore'] = (input("Score for bonus:\n"))
            notes['bonusNotes'] = (input("Notes for the bonus:\n"))
            notes['overallNotes'] = (input("Overall notes:\n"))

    return {"scores": scores, "notes": notes}


def get_notes(notes):
    global is_hw5
    notesString = ''

    # Iterate through the notes
    for key in notes:
        if len(notes[key]) > 0:
            if notesString == "":
                notesString = "\""
            # Add delimiter per discrete note
            if len(notesString) > 0 and notesString != "\"":
                notesString += "\\n"
                # Replace double quotes with single quotes
                notes[key] = notes[key].replace("\"", "\'")

            # Handle specific notes
            if is_hw5:
                if key == "obj1Notes":
                    notesString += ("Objective 1: " + notes['obj1Notes'])
                elif key == "obj2/3Notes":
                    notesString += ("Objective 2/3: " + notes['obj2/3Notes'])
                elif key == "obj4Notes":
                    notesString += ("Objective 4: " + notes['obj4Notes'])
                elif key == "bonusNotes":
                    notesString += ("Notes for the bonus: " + notes['bonusNotes'])
                elif key == "overallNotes":
                    notesString += ("Overall notes: " + notes['overallNotes'])
            else:
                if key == "obj1Notes":
                    notesString += ("Objective 1: " + notes['obj1Notes'])
                elif key == "obj2Notes":
                    notesString += ("Objective 2: " + notes['obj2Notes'])
                elif key == "obj3Notes":
                    notesString += ("Objective 3: " + notes['obj3Notes'])
                elif key == "obj4Notes":
                    notesString += ("Objective 4: " + notes['obj4Notes'])
                elif key == "bonusNotes":
                    notesString += ("Notes for the bonus: " + notes['bonusNotes'])
                elif key == "overallNotes":
                    notesString += ("Overall notes: " + notes['overallNotes'])
    if (notesString != ""):
        notesString = notesString + "\""
    return notesString


def get_csv():
    retval = ""
    with open(assigned_filename) as f:
        content = f.readlines()
    f.close()
    for idx in range(len(content)):
        content[idx] = content[idx].strip()
    # Print order
    fLine = "Order: "
    for key in content:
        fLine += (key + ", ")
    retval += (fLine[:len(fLine) - 2] + "\n")
    # Actually make the csv
    for key in content:
        if key not in grades:
            break
        line = ""
        scores = grades[key]["scores"]
        notes = grades[key]["notes"]
        notesVal = get_notes(notes)

        for idx, key2 in enumerate(scores):
            if (regrade and key2 != 'bonusScore') or not regrade:
                line += f'{scores[key2]},'
            elif regrade:
                line += ','
        if (regrade):
            line = line[:len(line) - 1]

        # if not regrade:
        line += notesVal
        # if regrade:
        if notesVal == "":
            line += "\"\""
        line += "\n"
        retval += line
    return retval


def nomore_students():
    print("You've run out of student to grade! Crashing and printing csv...")
    print(
        "Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
    print("If you have any troubles, make sure to be splitting by comma")
    print("------------")
    print(get_csv())
    print("------------")


def print_report(current_student, report_location):
    try:
        # They might have a report, if so print it
        if (len(report_location) > 1):
            print("------------")
            print(f'{current_student} has more than 1 reports')
            for num, report in enumerate(report_location):
                print(num, report)
            idx = int(input("Enter the index of the report location you like the best!\n"))
            assert (idx >= 0 and idx < len(report_location)), "Crashing because you entered a bad index!!"
            report_location = [report_location[idx]]
            print("------------")

        if (len(report_location) == 1):
            print(f'{current_student}\'s Report:\n' + "------------")

            with open(report_location[0], encoding='utf-8') as f:
                content = f.readlines()
            f.close()

            for line in content:
                print(line.strip())
            if (len(content) == 0):
                print("Empty report!")
            print("------------")
        else:
            print("------------")
            print(f'Appears {current_student} does not have a report.txt...')
            print("------------")
    except:
        print(f'{current_student} has a broken report!?')


def handle_dockerfiles(dockerfile_location, current_student):
    print("UHOH\n------------")
    print(f'{current_student} has more than 1 dockerfile or compose!?!?')
    for num, dockerfile in enumerate(dockerfile_location):
        print(num, dockerfile)
    idx = int(input("Enter the index of the dockerfile/compose location you like the best!\n"))
    assert (idx >= 0 and idx < len(dockerfile_location)), "Crashing because you entered a bad index!!"
    dockerfile_location = [dockerfile_location[idx]]
    print("------------")
    return dockerfile_location


def compose_restart(compose_location):
    process = subprocess.Popen(f'docker-compose -f \"{os.path.realpath(compose_location)}\" restart')
    process.wait()


# One unit of grading
def grading_unit():
    global grades
    global firstrun
    global regrade
    global deleteall
    grades = readgrades()
    # Get the index of the student currently being graded
    current = readcurrent(grades)
    current_student = readassigned(current)
    # Get the ubid of that student

    if current == -1:
        nomore_students()
        return False
    try:
        current_student_dir = glob(f'.\\{current_student}\\')[0]
        student_exists = True
    except:
        print(f'{current_student} does not have a submission in this directory!')
        student_exists = False

    if student_exists:
        # Recursively search for their report
        report_location = glob(current_student_dir + "\\**\\*report*", recursive=True)

        # print report
        print_report(current_student, report_location)

        # Recursively search for their dockerfile
        dockerfile_location = glob(current_student_dir + "\\**\\[Dd]ockerfile", recursive=True)

        try:
            compose_location = glob(current_student_dir + "\\**\\docker-compose.yml", recursive=True)
            if (len(compose_location) > 1):
                compose_location = handle_dockerfiles(compose_location, current_student)[0]
            else:
                compose_location = compose_location[0]
            PORT = 8080
            has_compose = True
        except:
            PORT = 8000
            has_compose = False

        # Handle multiple dockerfiles
        if (not has_compose and len(dockerfile_location) > 1):
            dockerfile_location = handle_dockerfiles(dockerfile_location)
            
        if (not has_compose and len(dockerfile_location) == 0):
            print(f'{current_student} does not have a dockerfile?')
            input('Check if there are any hidden (i.e. starting with a .) directories and unhide them')

        if (not has_compose and len(dockerfile_location) == 0):
            print('Unable to find dockerfile')
        else:
            # This step isn't necessary anymore
            dockerfile_location = dockerfile_location[0]
            # If we're in windows, open the path of the dockerfile
            if os.name == 'nt':
                subprocess.Popen(f'explorer /select,\"{os.path.realpath(dockerfile_location)}\"')

            print(f'Killing containers, building and running container on port {PORT}...')
            # Kill all docker containers
            client = docker.from_env()
            for container in client.containers.list():
                container.stop()
                if (deleteall):
                    container.remove()

            buildAndRun = True
            while buildAndRun:
                try:
                    if has_compose and os.name == 'nt':
                        process = subprocess.Popen(
                            f'docker-compose --log-level ERROR -f \"{os.path.realpath(compose_location)}\" up --build --detach')
                        process.wait()
                        if firstrun:
                            webbrowser.open(f'http://localhost:8080/')
                            firstrun = False
                    else:
                        # We don't have a docker-compose
                        # Build the container
                        dcontainer = client.images.build(path=os.path.realpath(os.path.dirname(dockerfile_location)),
                                                         dockerfile=os.path.realpath(dockerfile_location),
                                                         tag="student")
                        # docker_build_output = run(f'docker build -t student -f {dockerfile_location} {os.path.dirname(dockerfile_location)}')
                        # Open path in explorer

                        # Run the container
                        container = client.containers.run('student', ports={f'{PORT}/tcp': 8000},
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
                    while tryAgain != "y" and tryAgain != "n":
                        tryAgain = input("Try building/running again? y/n")
                    if (tryAgain == "n"):
                        buildAndRun = False
                        exitVar = input("Exit? y/n")
                        while exitVar != "y" and exitVar != "n":
                            exitVar = input("Exit? y/n")
                        if (exitVar == "y"):
                            sys.exit("Crashing because dockerfile is broken")
                        else:
                            print("Going onto grading...")
    # Print time and # of students graded
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    print("Time: ", current_time)
    times.append(current_time)
    print(f'You have graded {len(grades)} students')
    print(f'Now grading: {current_student}')
    if regrade:
        prev_grades,notes = parse_regrades(current_student)
        print(notes)
    else:
        prev_grades = [0,0,0,0]

    print("------------")
    grades[current_student] = prompt(prev_grades)
    print("\nYour input:")
    print(grades[current_student])
    print("------------")
    prompt_text = "q to quit, c to continue, r to redo grading data entry, j to print csv output, " \
                  "d for docker-compose restart\n "

    u_input = ""

    while (u_input != "q" and u_input != "c"):
        if u_input == "r":
            print("------------")
            grades[current_student] = prompt(prev_grades)
            print("\nYour input:")
            print(grades[current_student])
            print("------------")
        elif u_input == "j":
            print(
                "Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
            print("If you have any troubles, make sure to be splitting by comma")
            print("------------")
            print(get_csv())
            print("------------")
        elif u_input == "d":
            if not has_compose:
                print("no compose file found!")
            else:
                # Restart
                compose_restart(compose_location)
        u_input = input(prompt_text)

    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    times.append(current_time)
    print("Time: ", current_time)

    save = ""
    while save != "y" and save != "n" and u_input != "c":
        save = input("save? y/n")
    if save == "y" or u_input == "c":
        writegrades()
        current = int(current) + 1
        writecurrent(str(current))

    if u_input == "q":
        return False
    elif u_input == "c":
        return True


process_argv()

if not os.path.isfile(filename) or not os.path.isfile(grades_filename):
    print("Local data files do not exist. Rewriting...")
    grades = {}
    writegrades()
    writecurrent("0")
else:
    grades = readgrades()
    prompt_text = "Enter y to reset data or j to print csv output. Otherwise press enter to start!\n"
    print(f'You have graded {len(grades)} students')

    reset = input(prompt_text)

    while reset.strip() != "":
        if (reset == "y"):
            print("Resetting...")
            grades = {}
            writegrades()
            writecurrent(str(0))
        elif reset == "j":
            print(
                "Copy and paste in results into first obj column in google sheets, click on data in the top bar and press split text to columns")
            print("If you have any troubles, make sure to be splitting by comma")
            print("------------")
            print(get_csv())
            print("------------")
        reset = input(prompt_text)

while grading_unit():
    print("Grading loop...")
print("Killing remaining container...please wait...")
print(times)
client = docker.from_env()
for container in client.containers.list():
    container.stop()
if (deleteall):
    run("docker ps -a -q | % { docker rm $_ }")
