import sys
import csv
import os

def main():

    testDir = sys.argv[1]
    with open(sys.argv[2], 'w') as ouputFile:
        csvWriter = csv.writer(ouputFile, delimiter=',')
        
        # Add the header
        csvWriter.writerow(['FOLDER','FILE','ALG','DFS','P2P'])
        
        # Add all tests files to the output
        csvFoldersPaths = os.listdir(testDir)
        for i in range(len(csvFoldersPaths)):
            currFolderPath = os.path.join(testDir, csvFoldersPaths[i])
            currFilesPaths = [file for file in os.listdir(currFolderPath) if file[-3:] == "csv"]
            if currFilesPaths:
                for file in currFilesPaths:
                    with open(os.path.join(currFolderPath, file)) as currFile:
                        currReader = csv.reader(currFile, delimiter=',')
                        for row in currReader:
                            if not row[0] == "alg":
                                newRow = [os.path.basename(currFolderPath), file]
                                newRow.extend(row)
                                csvWriter.writerow(newRow)
                            
if __name__ == "__main__":
    main()