import project as proj
import sys


line = raw_input("Input BeginYear BeginQtr EndYear EndQtr\n")
beginYear, beginQtr, endYear, endQtr = line.split(" ")

endQtr = endQtr.rstrip("\n")
beginYear = int(beginYear)
beginQtr = int(beginQtr)
endYear = int(endYear)
endQtr = int(endQtr)

print "Begin downloading..."

dl = proj.Form10Fetcher()
dl.downloadBatch(beginYear,beginQtr,endYear,endQtr)
