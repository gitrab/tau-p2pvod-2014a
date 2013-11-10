import sys
import csv
import os
import math

ALGORITHM_INDEX = 0
DFS_INDEX = 1
P2P_INDEX = 2

class ComputeStatistics:
    

    
    def __init__(self, dirPath):
       self.dirPath = dirPath
       self.dataFilesAsLists = []
       self.algorithmType = None 
       
    
    def loadCSVFilesToLists(self):
        csvFoldersPaths = os.listdir(self.dirPath)
        for i in range(len(csvFoldersPaths)):
            currFolderPath = os.path.join(self.dirPath, csvFoldersPaths[i])
            currFilesPaths = os.listdir(currFolderPath)
            for j in range(len(currFilesPaths)):
                self.dataFilesAsLists.append([])
                with open(os.path.join(currFolderPath, currFilesPaths[j])) as currCSVFile: 
                    currReader = csv.reader(currCSVFile, delimiter=',')
                    for row in currReader:
                        #discard headlines
                        if(row[0]!='alg'):
                            self.dataFilesAsLists[(i*len(currFilesPaths))+j].append(row)

            
    def computeAverages(self):
        
        dfsAverages = [0.0] * len(self.dataFilesAsLists[0])
        p2pAverages = [0.0] * len(self.dataFilesAsLists[0])
        averages = {"DFS" : dfsAverages, "P2P" : p2pAverages}
        
        for i in range(len(self.dataFilesAsLists[0])):
            for j in range(len(self.dataFilesAsLists)):
                dfsAverages[i] += float(self.dataFilesAsLists[j][i][DFS_INDEX])
                p2pAverages[i] += float(self.dataFilesAsLists[j][i][P2P_INDEX])
            
            p2pAverages[i] /= len(self.dataFilesAsLists)
            dfsAverages[i] /= len(self.dataFilesAsLists)

            
        return averages
    
    def computeVariances(self, averages):
        
        dfsVariances = [0.0] * len(self.dataFilesAsLists[0])
        p2pVariances = [0.0] * len(self.dataFilesAsLists[0])
        variances = {"DFS" : dfsVariances, "P2P" : p2pVariances}
        
        for i in range(len(self.dataFilesAsLists[0])):
            for j in range(len(self.dataFilesAsLists)):
                dfsVariances[i] += (float(self.dataFilesAsLists[j][i][DFS_INDEX]) - averages["DFS"][i]) ** 2
                p2pVariances[i] += (float(self.dataFilesAsLists[j][i][P2P_INDEX]) - averages["P2P"][i]) ** 2
            
            dfsVariances[i] /= len(self.dataFilesAsLists)
            p2pVariances[i] /= len(self.dataFilesAsLists)
        
        return variances
    
    #TODO: accumulated DFS (as in the graphs xlxs)
    
def main():
    
    stats = ComputeStatistics(sys.argv[1])
    stats.loadCSVFilesToLists()
    averages = stats.computeAverages()
    variances = stats.computeVariances(averages)
    
    #Takes the square root of the variances to get the standard daviations
    for i in range(len(variances.values())):
        for j in range(len(variances.values()[i])):
           variances.values()[i][j] = math.sqrt(variances.values()[i][j])
    
    print averages["DFS"][-1]
    print variances["DFS"][-1]
    
   

if __name__ == '__main__':
    main()
        