Title: debrfstats software for RFS statistics
Date: 2014-09-23 11:35
Tags: debian, python
Category: Debian
Slug: debrfstats-software-for-rfs-statistics

[Last time](|filename|statistics-of-rfs-bugs.md) I told that I would release software I used to make
RFS stats plots. You can find it in my github repo -
[github.com/tdi/debrfstats](https://github.com/tdi/debrfstats). 

The software contains small class to get data needed to generate plots, as well as for doing
some simple bug analysis. The software also contains an R script to make plots from a CSV file. For
now debrfstats uses SOAP interface to Debbugs but I am now working on adding a UDD data source.

The software is written in Python 2 (SOAPpy does not come in 3 flavour), some usage examples are in
the `main.py` file in the repository.  

If you have any questions or wishes for debrfstats do not hesitate to contact me. 




