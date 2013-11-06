import sys
import csv
import os

ALGORITHM_INDEX = 0
DFS_INDEX = 1
P2P_INDEX = 2

class ComputeStatistics:
    

    
    def __init__(self, dirPath):
       self.dirPath = dirPath
       self.csvReaders = []
       self.algorithmType = None 
       
    
    def loadCSVFiles(self):
        csvFilesPaths = os.listdir(self.dirPath)
        for i in range(len(csvFilesPaths)):
            currCSVFile = open(os.path.join(self.dirPath, csvFilesPaths[i]))
            self.csvReaders.append(csv.reader(currCSVFile, delimiter=','))
            #advance each reader to it's first data row, in order to pass the headline
            self.csvReaders[-1].next()
            
    
    def closeCSVFiles(self):
        for i in range(len(self.csvReaders)):
            self.csvReaders[i].close()
            
    def computeAverage(self):
        dfsAverages = []
        p2pAverages = []
        averages = [dfsAverages, p2pAverages]
        while(1):
            try:
                dfsSum = 0
                p2pSum = 0
                length = 0
                for i in range(len(self.csvReaders)):
                    currRow = self.csvReaders[i].next()
                    dfsSum += int(currRow[DFS_INDEX])
                    p2pSum += int(currRow[P2P_INDEX])
                    length += 1
                    
                dfsAverages.append(float(dfsSum)/float(length))
                p2pAverages.append(float(p2pSum)/float(length))
            except:
                break
            
        return averages
    
    
def main():
    stats = ComputeStatistics(sys.argv[1])
    
    stats.loadCSVFiles()
    averageList = stats.computeAverage()
    print averageList
    #stats.closeCSVFiles()
    
   

if __name__ == '__main__':
    main()
        