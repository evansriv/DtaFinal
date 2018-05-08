import node
import nodeModel
import network
import link
import linkModel

from network import INFINITY

if __name__ == '__main__':
   network = network.Network('tests/daganzo.txt')

   # By default link capacities are the same at upstream and downstream end.  We really just want to constrain outflow, not inflow.
   network.links['Bottom'].upstreamCapacity = INFINITY
   
   network.DTA()
   print("Link data for first 20 time steps: ")
   for ij in network.links:
      print("LINK: ", ij)
      print("-----------")
      print("Travel time: ", network.links[ij].travelTime[1:min(20,network.timeHorizon)])
      print("Upstream count: ", ["%.2f" % network.links[ij].upstreamCount(t) for t in range(min(20,network.timeHorizon))])
      print("Downstream count: ", ["%.2f" % network.links[ij].downstreamCount(t) for t in range(min(20,network.timeHorizon))])
   print("TSTT is ", network.calculateTSTT())
   

