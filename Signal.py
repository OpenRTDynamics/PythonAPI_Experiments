from typing import Dict, List
from colorama import init,  Fore, Back, Style
init(autoreset=True)

#from Block import * 


class Signal:
    def __init__(self, sim, datatype = None, sourceBlock = None, sourcePort = None):
        self.sim = sim
        self.datatype = datatype
        self.sourceBlock = sourceBlock
        self.sourcePort = sourcePort  # counting starts at zero
        self.name = "--"

        # the list of destinations this signals goes to
        self.destinationBlocks = []
        self.destinationPorts = []

        # link to myself by defaul
        self.linkedSignal = self

        #if sourceBlock == None:
            # create a signal without any specified origin


        # used by TraverseGraph as a helper variable to perform a marking of the graph nodes
        self.linkedSignal.graphTraversionMarker = -1
        # self.graphTraversionMarker = -1


    def graphTraversionMarkerReset(self):
        self.linkedSignal.graphTraversionMarker = -1

    def graphTraversionMarkerMarkVisited(self, level):
        if level < 0:
            raise BaseException("level cannot be < 0")

        #print(Fore.RED + "-setmark- " + self.toStr() )

        self.linkedSignal.graphTraversionMarker = level
    
    def graphTraversionMarkerMarkIsVisited(self):
        #print(Fore.RED + "-checkmark- " + self.toStr() + " " + str(self.linkedSignal.graphTraversionMarker))

        # check of this node was marked on level or a level below
        #return not (self.linkedSignal.graphTraversionMarker == -1) # and self.linkedSignal.graphTraversionMarker <= level
        return self.linkedSignal.graphTraversionMarker >= 0

    def graphTraversionMarkerMarkIsVisitedOnLevel(self, onLevel):
        # check of this node was marked on level or a level below
        return self.linkedSignal.graphTraversionMarker == onLevel


    # set the name of this signal
    def setName(self, name):
        self.linkedSignal.name = name

        return self

    def getName(self):
        return self.linkedSignal.name

    def toStr(self):
        ret = ''
        ret += self.linkedSignal.name

        if self.linkedSignal.datatype is not None:
            ret += " (" + self.linkedSignal.datatype.toStr() + ")"

        else:
            ret += " (undef datatype)"

        return ret
        

    def addDestination(self, block , port : int):
        # add this destination to the list
        self.linkedSignal.destinationBlocks.append( block )
        self.linkedSignal.destinationPorts.append( port )

    def getDestinationBlocks(self):
        return self.linkedSignal.destinationBlocks

    def getSourceBlock(self):
        return self.linkedSignal.sourceBlock

    def setequal(self, to):
        # build a link to the already existing signal 'to'
        print("== Created a signal link " +  to.getName() + " == "+   self.getName() +  "")

        # merge the list of detination blocks
        for b in self.destinationBlocks:
            to.destinationBlocks.append(b)

        # merge self.destinationBlocks into to.destinationBlocks
        for p in self.destinationPorts:
            to.destinationPorts.append(p)

        # overwrite self
        self.linkedSignal = to

    # @property
    # def datatype(self):
    #     return self.linkedSignal.datatype

    # TODO remove this
    def getDatatype(self):
        return self.linkedSignal.datatype

    def setDatatype(self, datatype  ):
        self.linkedSignal.datatype = datatype

    def setNameOfOrigin(self, name):
        if not self.linkedSignal.sourceBlock is None:
            self.linkedSignal.sourceBlock.setName(name)

        return self


    def ShowOrigin(self):
        if not self.linkedSignal.sourcePort is None and not self.linkedSignal.sourceBlock is None:
            print("Signal >" + self.name + "< origin: port " + str(self.linkedSignal.sourcePort) + " of block #" + str(self.linkedSignal.sourceBlock.getId()) )

        else:
            print("Signal >" + self.name + "< origin not defined (so far)")





class BlockOutputSignal(Signal):
    """
        A signal that is the output of a block (normal case)

        TODO: implement and remove code from 'Signal' above
    """

    def __init__(self, sim, port : int, datatype = None):
        pass



class SimulationInputSignal(Signal):
    """
        A special signal that markes an input to a simulation.
    """

    def __init__(self, sim, port : int, datatype = None):
        
        self.port = port

        Signal.__init__(self, sim, datatype=datatype)

