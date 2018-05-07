from copy import copy
from node import Node

class WrongNodeTypeException(Exception):
   pass
   
class SeriesNode(Node):

   def __init__(self, upstreamLinks, downstreamLinks):
      if len(upstreamLinks) != 1 or len(downstreamLinks) != 1:
         raise WrongNodeTypeException
      Node.__init__(self, upstreamLinks, downstreamLinks)
   
   def calculateTransitionFlows(self, sendingFlow, receivingFlow, proportion):
      transitionFlows = dict()
      for inLink in self.upstreamLinks:
         transitionFlows[inLink] = dict()
        
      upLink = self.upstreamLinks[0]
      downLink = self.downstreamLinks[0]
     
      transitionFlows[upLink][downLink] = min(sendingFlow[upLink], receivingFlow[downLink])
      return transitionFlows
      
class DivergeNode(Node):

   def __init__(self, upstreamLinks, downstreamLinks):
      if len(upstreamLinks) != 1 or len(downstreamLinks) < 1:
         raise WrongNodeTypeException
      Node.__init__(self, upstreamLinks, downstreamLinks)
   
   def calculateTransitionFlows(self, sendingFlow, receivingFlow, proportion):
      transitionFlows = dict()  
      for inLink in self.upstreamLinks:
         transitionFlows[inLink] = dict()
      
      inLink = self.upstreamLinks[0]
      
      movingFraction = 1
      for outLink in self.downstreamLinks:
         try:
            movingFraction = min(movingFraction, receivingFlow[outLink] / (sendingFlow[inLink] * proportion[inLink][outLink] ))
         except ZeroDivisionError:
            pass
            
      for outLink in self.downstreamLinks:
         transitionFlows[inLink][outLink] = movingFraction * proportion[inLink][outLink] * sendingFlow[inLink]            
      
      return transitionFlows
      
  
class MergeNode(Node):

   # For a merge node, also need to include the relative priority values for each node
   def __init__(self, upstreamLinks, downstreamLinks, priority):
      if len(upstreamLinks) < 1 or len(downstreamLinks) != 1:
         raise WrongNodeTypeException
      Node.__init__(self, upstreamLinks, downstreamLinks)
      self.priority = priority
      if min(priority.values()) <= 0:
         print("Merge nodes must have strictly positive priority values for incoming links.")
         raise WrongNodeTypeException
   
   def calculateTransitionFlows(self, sendingFlow, receivingFlow, proportion):
      transitionFlows = dict()   
      for inLink in self.upstreamLinks:
         transitionFlows[inLink] = dict()
      
      outLink = self.downstreamLinks[0]      
      
      for inLink in self.upstreamLinks:
         transitionFlows[inLink][outLink] = 0
         
      activeLinks = copy(self.upstreamLinks)
      while len(activeLinks) > 0 and receivingFlow[outLink] > 0:
         totalPriority = 0
         for inLink in activeLinks:
            totalPriority += self.priority[inLink]
         flowMovedThisIteration = 0
         inactivatedLinks = list()
         for inLink in activeLinks:
            additionalFlow = min(sendingFlow[inLink], self.priority[inLink] / float(totalPriority) * receivingFlow[outLink])
            transitionFlows[inLink][outLink] += additionalFlow
            flowMovedThisIteration += additionalFlow
            sendingFlow[inLink] -= additionalFlow
            if sendingFlow[inLink] == 0: 
               inactivatedLinks.append(inLink)
         receivingFlow[outLink] -= flowMovedThisIteration
         for inLink in inactivatedLinks:
            activeLinks.remove(inLink)
      
      return transitionFlows
      
class OriginNode(Node):

   def __init__(self, upstreamLinks, downstreamLinks):
      if len(upstreamLinks) != 0:
         raise WrongNodeTypeException
      Node.__init__(self, upstreamLinks, downstreamLinks)
      self.isCentroid = True      

class DestinationNode(Node):
   
   def __init__(self, upstreamLinks, downstreamLinks):
      if len(downstreamLinks) != 0:
         raise WrongNodeTypeException
      Node.__init__(self, upstreamLinks, downstreamLinks)
      self.isCentroid = True
      self.isDestination = True
    

