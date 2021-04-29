# 312 Grader Helper
Python file must be placed in directory of student submissions.
Arguments:  
```python homework_grader.py  {file where students to be graded are separated by newlines} {--deleteall} {--regrade} {--hw5}```

## --deleteall:
  Delete all docker containers after finishing. Cleans up some clutter.
## --regrade:
  Set the script to regrade mode.  
  If you want, in the same directory as the grader you can put a CSV file called "regrades.csv" which should be organized like this:  
  ```UBIT,obj1grade,...{,optionally you can put notes here}```  
  This will make regrading easier at will display any objectives where the student did not achieve a 3, along with your notes if you included them.
## --hw5:
  Use this flag if you are grading homework 5.
