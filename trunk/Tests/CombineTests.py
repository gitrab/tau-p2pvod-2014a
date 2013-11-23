import sys
import csv
import os
import fnmatch

def getCsvFiles(path):
    csvFiles = []
    for root, dirnames, filenames in os.walk(path):
      for filename in fnmatch.filter(filenames, '*.csv'):
          csvFiles.append(os.path.join(root, filename))
    
    return csvFiles

def main():

    print 'Starting...'

    testsDir = sys.argv[1]
    outputFile = open(sys.argv[2], 'w')
    csvWriter = csv.writer(outputFile, delimiter=',')
        
    # Add the header
    csvWriter.writerow(['PATH','T','ALG','DFS','P2P'])
    
    # Run on all csv files in the tests directory and add them to output
    csvFiles = getCsvFiles(testsDir)
    for csvFilePath in csvFiles:
        print "Adding: %s" % csvFilePath
        with open(csvFilePath) as currFile:
            currReader = csv.reader(currFile, delimiter=',')
            rowindex = 0
            for row in currReader:
                if not row[0] == "alg":
                    rowindex += 1
                    newRow = [csvFilePath, rowindex]
                    newRow.extend(row)
                    csvWriter.writerow(newRow)
    
    outputFile.close()    
    
    print 'Done. %d files added.' % len(csvFiles)
                            
if __name__ == "__main__":
    main()