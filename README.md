# fhlibrary


## What is in the box?
This is a small collection of diverse code snippets written in python and R from years of scripting in computational biology. The entire collection is significantly larger, handles blast queries, alignments, phylogenetic trees and more but is at this moment not usefull for the public without investing more time in particular on documentation and setup. If you are a beginner in python/R you should not start with this code - you will very likely not understand the purpose of the code and will give up before getting anywhere. If you are a intermediate level scripter maybe you find some interesting code snippets and concepts or solutions and I hope they turn out to be usefull for your project. If you are an expert scripter you might see it as challenge to fix various problems but more likely just simply smile and move on.

## What is not in the box?
If you find a package for python/R that does the job for you don't waste time looking at the code here - it lacks documentation and at the moment it will likely not run out of the box. Furthermore basically the code snippets here are mainly wrappers around many of those packages which I generated to combine these into more complex workflows in computational biology.

## What are things that the code could do if only I figure out how to deal with the dependencies and structure?
I use the code provided here as basic tool for:
- SQLite database management from/to python (SQLitebase.py,fhutils.py)
- simple Table object to read/write/filter/loop tables (fhutils.py)
- plot from python using python > rpy2 > R > ggplot2 (plot_rengine.py,fhstats.py,rfhstats.R,plotting_routines.R)
- statistics such as anova, aggregating tables, error propagation, outlier detection from python using python > rpy2 > R (fhstats.py, rfhstats.R) 
- logging in python (fhutils.py)
- execute/pipe commands in terminal with error handling (fhutils.py)
- creat/invert dictionaries handling non-unique keys, flatten lists (fhutils.py)
- venndiagram wrappers using python > rpy2 > R (venndiagram.py, graph_venn.R)

## Where should I start to try things out?
If you decided to get things running and not simply copying code start looking at the pytest folder and the tests scripts there. By setting up the python path and R environment as needed these tests are the most easy start i.e. if you get those running you will have a rough idea what functionality is included. The following hints provide some help on this path:

- Clone the repository into a directory of your choice.
- Change into this directory that now contains the fhlibrary folder, generate a virtualenv "gitpy" and activate it.
- Change into the fhlibrary>pytest>dbtools folder and use pip to install the packages listed in the requirements.txt
- run the test_dbtools.py script. This should generate an SQLite database file and a text file. Looking at the test script and the generated database you can see what the code is doing. Note at this stage only the test_dbtools.py should work.



