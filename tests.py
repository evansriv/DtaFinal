import sys
import traceback

import network
import utils
   
IS_MISSING = -1

def approxEqual(value, target, tolerance):
   if (abs(target) <= tolerance ): return abs(value) <= tolerance
   return abs(float(value) / target - 1) <= tolerance
   
def check(name, value, target, tolerance):
   if approxEqual(value, target, tolerance):
      return True
   else:
      print("\nWrong %s: your value %f, correct value %f"
               % (name, value, target))
      return False

def checkExact(name, value, target):
   if value == target:
      return True
   else:
      print("\nWrong %s: your value %s, correct value %s"
               % (name, value, target))
      return False

def TDSP(testFileName):
  
   print("Running TDSP test: " + str(testFileName) + "...", end='')
   
   try:
      with open(testFileName, "r") as testFile:
         # Read test information
         try:
            fileLines = testFile.read().splitlines()
            pointsPossible = IS_MISSING
            networkFile = IS_MISSING
            origin = IS_MISSING
            departureTime = IS_MISSING
            correctCost = IS_MISSING
            travelTimes = dict()
            correctBacklink = IS_MISSING
            for line in fileLines:
               # Ignore comments and blank lines
               if len(line.strip()) == 0 or line[0] == '#':
                  continue
                   
               # Set points possible
               if pointsPossible == IS_MISSING:
                  pointsPossible = int(line)
                  continue
                  
               # Set network file
               if networkFile == IS_MISSING:
                  networkFile = line
                  testNetwork = network.Network(networkFile)
                  continue
                  
               # Set origin/departure time
               if origin == IS_MISSING:
                  inputs = line.split(",")
                  origin = int(inputs[0])
                  departureTime = int(inputs[1])
                  continue
                  
               # Set time-dependent travel times
               if len(travelTimes) < testNetwork.numLinks:
                  inputs = line.split(",")
                  testNetwork.links[inputs[0]].travelTime = [int(x) for x in inputs[1:]]
                  travelTimes[inputs[0]]  = True
                  continue
               
               # Set correct cost labels   
               if correctCost == IS_MISSING:
                  inputs = line.split(",")
                  correctCost = [int(x) for x in inputs]
                  continue
                        
               # Set correct backlink labels   
               if correctBacklink == IS_MISSING:
                  inputs = line.split(",")
                  correctBacklink = inputs
                  continue
                  
         except:
            print("\nError running test %s, attempting to continue with remaining tests.  Exception details: " % testFileName)
            traceback.print_exc(file=sys.stdout)
            return 0, 0
            
         # Now run the actual test
         try:
            (studentCost, studentBacklink) = testNetwork.TDSP(origin - 1, departureTime)
            numCorrect = 0
            for i in range(testNetwork.numNodes):
               numCorrect += 1 if check("Node %d cost" % (i+1), studentCost[i], correctCost[i], 0.01)  else 0
               numCorrect += 1 if checkExact("Node %d backlink" % (i+1), studentBacklink[i], correctBacklink[i]) else 0
         except utils.NotYetAttemptedException:
            print("...not yet attempted")
            return 0, pointsPossible
         except:
            print("\nException raised, attempting to continue:")
            traceback.print_exc(file=sys.stdout)                     
            print("\n...fail")
            return 0, pointsPossible

         if numCorrect < 2 * testNetwork.numNodes:               
            print("...fail")
         else:            
            print("...pass")
         return pointsPossible * (numCorrect / float(2 * testNetwork.numNodes) ), pointsPossible

         
   except IOError:
      print("\nError running test %s, attempting to continue with remaining tests.  Exception details: " % testFileName)
      traceback.print_exc(file=sys.stdout) 
      return 0, 0
   


def convexCombo(testFileName):
  
   print("Running convex combinations test: " + str(testFileName) + "...", end='')
   
   try:
      with open(testFileName, "r") as testFile:
         # Read test information
         try:
            fileLines = testFile.read().splitlines()
            pointsPossible = IS_MISSING
            networkFile = IS_MISSING
            stepSize = IS_MISSING
            originalPathFlows = dict()
            targetPathFlows = dict()
            correctPathFlows = dict()
            for line in fileLines:
               # Ignore comments and blank lines
               if len(line.strip()) == 0 or line[0] == '#':
                  continue
                   
               # Set points possible
               if pointsPossible == IS_MISSING:
                  pointsPossible = int(line)
                  continue
                  
               # Set network file
               if networkFile == IS_MISSING:
                  networkFile = line
                  testNetwork = network.Network(networkFile)
                  continue
                  
               # Set step size
               if stepSize == IS_MISSING:
                  stepSize = float(line)
                  continue
                  
               # Set original path flows
               if len(originalPathFlows) < sum(len(OD.paths) for OD in testNetwork.ODs):
                  inputs = line.split(",")
                  path = tuple(inputs[:-testNetwork.timeHorizon])
                  flows = inputs[-testNetwork.timeHorizon:]
                  testNetwork.pathFlows[path] = [float(x) for x in flows]
                  originalPathFlows[path]  = True
                  continue
               
               # Set target path flows
               if len(targetPathFlows) < sum(len(OD.paths) for OD in testNetwork.ODs):
                  inputs = line.split(",")
                  path = tuple(inputs[:-testNetwork.timeHorizon])
                  flows = inputs[-testNetwork.timeHorizon:]
                  targetPathFlows[path] = [float(x) for x in flows]
                  continue
                                          
               # Set correct path flows   
               if len(correctPathFlows) < sum(len(OD.paths) for OD in testNetwork.ODs):
                  inputs = line.split(",")
                  path = tuple(inputs[:-testNetwork.timeHorizon])
                  flows = inputs[-testNetwork.timeHorizon:]
                  correctPathFlows[path] = [float(x) for x in flows]
                  continue
                  
         except:
            print("\nError running test %s, attempting to continue with remaining tests.  Exception details: " % testFileName)
            traceback.print_exc(file=sys.stdout)
            return 0, 0
            
         # Now run the actual test
         try:
            testNetwork.updatePathFlows(targetPathFlows, stepSize)
            numCorrect = 0
            for path in targetPathFlows:
               for t in range(testNetwork.timeHorizon):
                  numCorrect += 1 if check("Path %s flow at time %d" % (path, t), testNetwork.pathFlows[path][t], correctPathFlows[path][t], 0.01)  else 0
         except utils.NotYetAttemptedException:
            print("...not yet attempted")
            return 0, pointsPossible
         except:
            print("\nException raised, attempting to continue:")
            traceback.print_exc(file=sys.stdout)                     
            print("\n...fail")
            return 0, pointsPossible

         if numCorrect < len(targetPathFlows) * testNetwork.timeHorizon:               
            print("...fail")
         else:            
            print("...pass")
         return pointsPossible * (numCorrect / float(len(targetPathFlows) * testNetwork.timeHorizon) ), pointsPossible

         
   except IOError:
      print("\nError running test %s, attempting to continue with remaining tests.  Exception details: " % testFileName)
      traceback.print_exc(file=sys.stdout) 
      return 0, 0
   

