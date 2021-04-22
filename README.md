# 312 Grader Helper
Arguments:  
```python {name of grader} {file where students to be graded are separated by newlines} {--deleteall} {--regrade}```

## --deleteall:
  Delete all docker containers after finishing. Cleans up some clutter.
## --regrade:
  Set the script to regrade mode.  
  If you want, in the same directory as the grader you can put a CSV file called "regrades.csv" which should be organized like this:  
  ```UBIT,obj1grade,...{,optionally you can put notes here}```  
  This will make regrading easier at will display any objectives where the student did not achieve a 3, along with your notes if you included them.
