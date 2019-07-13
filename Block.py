from typing import Dict, List

from Signal import *
from Datatypes import *





# move to BlockInterface.py
class BlockPrototype:
    """
        This is a base class to be deviated from each block type.
        It contains logic to handle the input/ output types and
        the parameters.
    """

    def __init__(self, block):
        self.block = block

    # def __init__(self):

    #     block = Block(sim, self, None, blockname = '')
    #     block.configOutputSignals([ Signal(sim) ])

    #     self.block = block

    def getUniqueVarnamePrefix(self):
        # return a variable name prefix unique in the simulation
        # to be used for code generation 
        return "" + self.block.getName() +  "_" + str(self.block.getBlockId())


    #
    # The derived classes shall use these shortcuts to access the I/O signals
    #

    # get a signal of a specific output port
    def outputSignal(self, port):
        #return self.block.getOutputSignals()[port]
        return self.block.getOutputSignal(port)

    # get a signal of a specific input port
    def inputSignal(self, port):
        return self.block.getInputSignal(port)


    #
    # Standard functions that should be re-implemented
    #

    def configDefineOutputTypes(self, inputTypes):
        raise BaseException("configDefineOutputTypes not implemented")

    # function to generate code
    def codeGen(self, language, flag):
        # raise BaseException("code generation not implemented")

        # This is to show what could be implemented
        lines = ''

        if language == 'c++':

            if flag == 'defStates':
                lines = ''

            elif flag == 'localvar':
                lines = ''

            elif flag == 'constructor':
                lines = ''

            elif flag == 'destructor':
                lines = ''

            elif flag == 'output':
                lines = ''

            elif flag == 'update':
                lines = ''

            elif flag == 'reset':
                lines = ''

        return lines

    def codeGen_defStates(self, language):
        return ''

    def codeGen_localvar(self, language):
        return ''
        
    def codeGen_constructor(self, language):
        return ''
        
    def codeGen_destructor(self, language):
        return ''
        
    def codeGen_output(self, language):
        return ''
        
    def codeGen_update(self, language):
        return ''
        
    def codeGen_reset(self, language):
        return ''
        
        



class Block:
    """
        This decribes a block that is part of a Simulation
     
        BlockPrototype - describes the block's prototype implementation
                         that defined IO, parameters, ...
    """

    def __init__(self, sim, blockPrototype : BlockPrototype, inputSignals : List[Signal], blockname : str):
        print("Creating new block " + blockname)

        self.sim = sim

        # create a new unique block id 
        self.id = sim.getNewBlockId()

        # default names
        if blockname is None:
            blockname = 'block'

        self.blocknameShort =  blockname + '_bid' + str( self.id )   # variable name
        self.blockname = blockname + '_bid' + str( self.id )  # description

        # add myself to the given simulation
        self.sim.addBlock(self)

        # The blocks prototype function. e.g. to determine the port sizes and types
        # and to define the parameters
        self.blockPrototype = blockPrototype

        # The input singals in form of a list
        self.inputSignals = []

        if not inputSignals is None:
            # store the list of input signals
            self.inputSignals = inputSignals # array of Signal

            # update the input signals to also point to this block
            for port in range(0, len( self.inputSignals ) ):
                self.inputSignals[port].addDestination( self, port )


        # initialize the empty list of output signals
        self.OutputSignals = []

        # used by TraverseGraph as a helper variable to perform a marking of the graph nodes
        self.graphTraversionMarker = False


    def graphTraversionMarkerReset(self):
        self.graphTraversionMarker = False

    def graphTraversionMarkerMarkVisited(self):
        self.graphTraversionMarker = True
    
    def graphTraversionMarkerMarkIsVisited(self):
        return self.graphTraversionMarker
    
    # TODO remove soon 13.7.19
    def configAddOutputSignal(self):
        # add an output signals to this block typically called by the block prototypes
        # NOTE: This just reservates that there will be an output
        #       the type is undefined at this point

        print("---------------------------- obsolet function configAddOutputSignal ------------------------")

        portNumber = len(self.OutputSignals)
        newSignal = Signal(self.sim, None, self, portNumber )

        self.OutputSignals.append( newSignal )

        return self

    def configOutputSignals(self, signals):
        self.OutputSignals = signals


    def configDefineOutputTypes(self):
        # ask the block's prototype class instance to define the output types given
        # the input types by calling the prototype's function 'configDefineOutputTypes' 
        # 
        # Please note that the input types are define by other blocks
        # whose outputs are connected to this block.
        #
        # It might happen that the datatypes of these signals are not already determined.
        # Eventually a proposal for a datatype is available. In any case, based on the available
        # information, the prototype is asked to provide information on the types of the outputs.
        #


        # build a list of input signals types for this block
        inputSignalTypes = []

        for s in self.inputSignals:

            if s.getDatatype() is not None:
                # this input's datatype is already fixed 
                inputSignalTypes.append(s.getDatatype() )
            else:
                # check for the proposed datatype
                if s.getProposedDatatype() is not None:
                    inputSignalTypes.append(s.getProposedDatatype() )
                else:
                    # no info on this input signal is available -- just put None and let the blocks propotype
                    # 'configDefineOutputTypes' function deceide what to do.
                    inputSignalTypes.append(None)


        # ask prototype to define output types (this might just be a proposal for datatypes; they are fixed later)
        proposedOutputSingalTypes = self.blockPrototype.configDefineOutputTypes( inputSignalTypes )

        # update all signals accordingly
        for i in range(0, len(self.OutputSignals)):

            signal = self.OutputSignals[i]
            signal.setProposedDatatype(  proposedOutputSingalTypes[i]  )

        return


    def getName(self):
        return self.blocknameShort

    def setName(self, name):
        self.blockname = name
        return self

    def toStr(self):
        return self.blockname + ' (' + self.blocknameShort + ')'

    def getBlockPrototype(self):
        return self.blockPrototype

    def getBlockId(self):
        return self.id # a unique id within the simulation the block is part of

    def getInputSignals(self):
        return self.inputSignals

    def getOutputSignals(self):
        return self.OutputSignals

    def getOutputSignal(self, port):
        if port < 0:
            raise Exception('port < 0')

        if port >= len(self.OutputSignals): 
            raise Exception('port out of range')

        return self.OutputSignals[port]

    def getInputSignal(self, port):
        if port < 0:
            raise Exception('port < 0')

        if port >= len(self.inputSignals): 
            raise Exception('port out of range')

        return self.inputSignals[port]
    













