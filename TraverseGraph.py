from Signal import *
from Block import *

from typing import Dict, List
from colorama import init,  Fore, Back, Style
init(autoreset=True)

class Node:
    def __init__(self, block : Block):
        self.block = block

    # return a list of linked nodes
    def getLinks(self):  
        pass


            




class TraverseGraph:
    # TODO: rename to TraverseBlocks

    # NOTE: THis is currently not needed but might be userd in the future for sth...

    def __init__(self): #blockList : List[ Block ]

        # # build a list of nodes
        # self.nodeList = []

        # for block in blockList:

        #     self.nodeList.append( Node(block) )

        # the list of reachable blocks
        self.reachableBlocks = []




    # Start forward traversion starting from the given startBlock
    def forwardTraverse(self, startBlock : Block):
        self.reachableBlocks = []

        # fill in self.reachableBlocks
        self.forwardTraverse__(startBlock, depthCounter = 0)

        # reset graph traversion markers
        for block in self.reachableBlocks:
            block.graphTraversionMarkerReset()

        return self.reachableBlocks

    # Start forward traversion starting from the given startBlock
    def forwardTraverse__(self, startBlock : Block, depthCounter : int):
        
        tabs = ''
        for i in range(0, depthCounter):
            tabs += '   '

        # print(tabs + "....... depth " + str( depthCounter )  )

        #
        if startBlock.graphTraversionMarkerMarkIsVisited():
            print(tabs + "*** visited *** "  + startBlock.getName() + " (" + str( startBlock.id ) + ") ****")  ## TODO investigtare: why is this never reached?
            return

        # store this block as it is reachable
        self.reachableBlocks.append( startBlock )

        # make the node as visited
        startBlock.graphTraversionMarkerMarkVisited()

        print(tabs + "-- " + startBlock.getName() + " (" + str( startBlock.id ) + ") --" )



        # find out the links to other blocks
        for signal in startBlock.getOutputSignals():
            # for each output signal

            print(tabs + "-> S " + signal.getName() )

            if len( signal.getDestinationBlocks() ) == 0:
                print(tabs + '-- none --')

            for destinationBlock in signal.getDestinationBlocks():
                # destinationBlock is a link to a connected block

                print( tabs + "*", destinationBlock.getName(), "(", destinationBlock.id, ")"  )

            #for destinationBlock in signal.getDestinationBlocks():
                # destinationBlock is a link to a connected block

                # recursion
                self.forwardTraverse__( destinationBlock, depthCounter = depthCounter + 1 )












    # Start backward traversion starting from the given startBlock
    #
    # Note this is not fully tested 
    # DELETE SOON, if it is not needed
    #
    def backwardTraverseExec(self, startBlock : Block):
        self.reachableBlocks = []

        # fill in self.reachableBlocks
        self.backwardTraverseExec__(startBlock, depthCounter = 0)

        # reset graph traversion markers
        for block in self.reachableBlocks:
            block.graphTraversionMarkerReset()

        return self.reachableBlocks


    # Start backward traversion starting from the given startBlock
    def backwardTraverseExec__(self, startBlock : Block, depthCounter : int):
        
        tabs = ''
        for i in range(0, depthCounter):
            tabs += '   '

        #print(tabs + "....... depth " + str( depthCounter )  )

        #
        if startBlock.graphTraversionMarkerMarkIsVisited():
            print(tabs + "*** visited *** "  + startBlock.getName() + " (" + str( startBlock.id ) + ") ****")  ## TODO investigtare: why is this never reached?
            return

        # check of the block 'startBlock'
        #if returnDependingInputs( signal )

        # store this block as it is reachable
        self.reachableBlocks.append( startBlock )

        # make the node as visited
        startBlock.graphTraversionMarkerMarkVisited()

        print(tabs + "--- " + startBlock.getName() + " (" + str( startBlock.id ) + ") --" )



        # find out the links to other blocks
        for signal in startBlock.getInputSignals():
            # for each output signal


            print(tabs + "-> S " + signal.getName() )

            if signal.getSourceBlock() is None:
                print(tabs + '-- ERROR: no input signal defined for this block! --')
                
            else:

                print( tabs + "*", signal.getSourceBlock().getName(), "(", signal.getSourceBlock().id, ")"  )

                self.forwardTraverse__( signal.getSourceBlock(), depthCounter = depthCounter + 1 )








class ExecutionLine():
    """
        contains a list 'signalOrder' of signals to be computed in the given order.
        The computation of these signals depends on a list of signals given by
        'dependencySignals'.
    """

    def __init__(self, signalOrder : List[ Signal ] , dependencySignals : List[ Signal ], dependencySignalsSimulationInputs : List[ Signal ], blocksToUpdateStates : List[ Block ], dependencySignalsThroughStates : List[ Signal ] ):
        self.signalOrder = signalOrder
        self.dependencySignals = dependencySignals
        self.dependencySignalsSimulationInputs = dependencySignalsSimulationInputs
        self.blocksToUpdateStates = blocksToUpdateStates
        self.dependencySignalsThroughStates = dependencySignalsThroughStates

    def printExecutionLine(self):
        print("------ print of execution line -----")

        print(Fore.RED + "dependent sources:")

        for s in self.dependencySignals:
            print("  - " + s.getName() )

        print(Fore.RED + "dependent sources (simulation inputs):")
                
        for s in self.dependencySignalsSimulationInputs:
            print("  - " + s.getName() )

        print(Fore.RED + "dependent sources (through state-dependend blocks):")
        
        for s in self.dependencySignalsThroughStates:
            print("  - " + s.getName() )

        print(Fore.GREEN + "execution order:")

        for s in self.signalOrder:
            print("  - " + s.getName() )

        print(Fore.GREEN + "blocks whose states must be updated:")

        for block in self.blocksToUpdateStates:
            print("  - " + block.getName() )


    def getSignalsToExecute(self):
        l = []

        #l.extend( self.dependencySignals )
        l.extend( self.signalOrder )

        return l


    def appendExecutionLine(self, executionLineToAppend):

        # merge dependencySignals: only add the elements of executionLineToAppend.dependencySignals
        # to self.dependencySignals that are not part of self.dependencySignals or self.signalOrder

        # TODO: use sets to merge..

        for s in executionLineToAppend.dependencySignals:
            if not s in self.dependencySignals and not s in self.signalOrder:
                self.dependencySignals.append(s)


        for s in executionLineToAppend.dependencySignalsSimulationInputs:
            if not s in self.dependencySignalsSimulationInputs and not s in self.signalOrder:
                self.dependencySignalsSimulationInputs.append(s)

        
        for s in executionLineToAppend.dependencySignalsThroughStates:
            if not s in self.dependencySignalsThroughStates and not s in self.signalOrder:
                self.dependencySignalsThroughStates.append(s)

        

        for s in executionLineToAppend.signalOrder:
            # TODO: (for optimization purposes) 
            # check if there comcon blocks in the list. (only in case a block has more than one
            # output signals and one of these signals is in the list executionLineToAppend.signalOrder
            # and another one in self.signalOrder  )

            # just append the 
            self.signalOrder.append( s )

        for s in executionLineToAppend.blocksToUpdateStates:
            # TODO: (for optimization purposes) 
            # check if there comcon blocks in the list. 

            # just append the 
            self.blocksToUpdateStates.append( s )










class BuildExecutionPath:
    """
        Find out the order in which signals have to be computed such that a given signal
        'signalToCalculte'can be calculated. This means finding out all dependencies of
        'signalToCalculte'. For each callc to 'getExecutionLine' only the signals that
        were not already marked as a dependeny in previous calls are returned.
        Each call to 'getExecutionLine' gives an instance 'ExecutionLine'
    """
    def __init__(self): #blockList : List[ Block ]

        # list of signals the computation depends on (the tips of the execution tree)
        self.dependencySignals = []

        self.dependencySignalsThroughStates = []

        # the list of reachable signals
        self.reachableSignals = []

        # For each signgal self.reachableSignals there might be a blocks that
        # has an internal memory. It is required to build a list of those blocks
        # that need a state update after their output(s) are calculated.
        self.blocksToUpdateStates = []

        # list of marked signals (important to reset their visited flags)
        self.markedSignals = []

        # number of calls to getExecutionLine()
        self.level = 0

    def __del__(self):
        self.resetMarkers()


    def getExecutionLine(self, signalToCalculte : Signal):
        # get the order of computation steps and their order that have
        # to be performed to compute 'signalToCalculte'
        #
        # For each call to this function, a list is generated that does not contain
        # signals that are already part of a previous list (that are already computed)
        #
        # This function can be called multiple times and returns only the necessaray 
        # computations. Computations already planned in previous calls of this function
        # are not listed again. (until resetMarkers() is called)
        #   

        # TODO: dependency signals should stay as theiy are but reachableSignals should not contain signals
        #       that already have been calculated. Further, reachableSignals shall also contain dependency if they 
        #       were not already calculated

        print("getExecutionLine on level " + str(self.level) )

        # reset the lists
        self.reachableSignals = []
        self.dependencySignals = []
        self.dependencySignalsThroughStates = []
        self.dependencySignalsSimulationInputs = []
        self.blocksToUpdateStates = []

        # search within this system
        self.system = signalToCalculte.sim

        # compute by traversing the tree
        self.backwardTraverseSignalsExec__(startSignal=signalToCalculte, depthCounter = 0)

        # reverse of the list of reacheable signals gives the order of calculating the individual signals
        self.reachableSignals.reverse()

        # the iteration level
        self.level = self.level + 1

        return ExecutionLine( self.reachableSignals, self.dependencySignals, self.dependencySignalsSimulationInputs, self.blocksToUpdateStates, self.dependencySignalsThroughStates )

    def printExecutionLine(self):
        pass

    def resetMarkers(self):
        # reset graph traversion markers
        for signal in self.markedSignals:
            signal.graphTraversionMarkerReset()

        # reset status variables
        self.markedSignals = []
        self.level = 0

    def isSignalAlreadyComputable(self, signal : Signal):
        return signal.graphTraversionMarkerMarkIsVisited()

    # Start backward traversion starting from the given startSignal
    def backwardTraverseSignalsExec__(self, startSignal : Signal, depthCounter : int):
        
        tabs = ''
        for i in range(0, depthCounter):
            tabs += '   '


        if not (isinstance(startSignal, SimulationInputSignal) or isinstance(startSignal, BlockOutputSignal)):
            
            # this case must be an error..                  
            raise BaseException('not implemented or internal error: unexpected type of signal' + startSignal.getName())


        if startSignal.graphTraversionMarkerMarkIsVisitedOnLevel(self.level):
            # startSignal was already computed at this level


            # it might be an algeraic loop, but does not have to be
            #
            # TODO: investigate if this is able to find all algebraic loops, i.e. also in case
            #       of multiple levels
            #
            #print(tabs + "algebraic loop detected at signal " + startSignal.toStr())
            #raise BaseException("algebraic loop detected at signal " + startSignal.toStr())

            #
            # move startSignal to an upper level in the execution linst
            #

            # remove from its current position
            self.reachableSignals.remove( startSignal )

            # put to the front
            self.reachableSignals.append( startSignal )

            print(Style.DIM + tabs + "moved to the current head of the execution list")
            
            return


        #
        if startSignal.graphTraversionMarkerMarkIsVisited():
            # - a previously computed signal has been reached

            print(Style.DIM + tabs + "has already been calculated in a previous traversion") 

            self.dependencySignals.append( startSignal )


            return

        # mark the node visited
        startSignal.graphTraversionMarkerMarkVisited(self.level)
        self.markedSignals.append(startSignal)

        #
        # store startSignal as reachable (put it on the exeution list)
        # NOTE: if startSignal is the tip of the tree (no dependingSignals) it is excluded
        #       from this list. However, it is still in the list of dependencySignals.
        #

        print(Style.DIM + tabs + "added " + startSignal.toStr())
        self.reachableSignals.append( startSignal )




        # check if the signal is a system input signal
        if isinstance(startSignal, SimulationInputSignal):
            # signal is an input to the simulation
            # add to the list of dependent inputs

            # startSignal is at the top of the tree, so add it to the dependiencies
            self.dependencySignals.append( startSignal )

            # also note down that this is a (actually used) simulation input
            self.dependencySignalsSimulationInputs.append( startSignal )

            return


        # when the system the signal belongs to changes we reached a boundary to a upperl-level system
        if startSignal.sim != self.system:
            print("detected a boundary to an upper-level system: " + startSignal.name + " is a signal from upper level.")

            self.dependencySignals.append( startSignal )

            # also note down that this is a (actually used) simulation input
            self.dependencySignalsSimulationInputs.append( startSignal )

            return



        # get the blocks prototype function to calculate startSignal
        block = startSignal.getSourceBlock()
        blocksPrototype = block.getBlockPrototype()

        # check if the block that yields startSignal uses internal-states to compute startSignal
        if blocksPrototype.returnInutsToUpdateStates( startSignal ) is not None:
            # 
            self.blocksToUpdateStates.append( block )

            # add the signals that are required to perform the state update
            self.dependencySignalsThroughStates.extend( blocksPrototype.returnInutsToUpdateStates( startSignal ) )

        # find out the links to other signals but only these ones that are 
        # needed to calculate 'startSignal'
        print(tabs + "--- signals needed for " + startSignal.getName() + " (" + ") --" )

        dependingSignals = blocksPrototype.returnDependingInputs(startSignal)

        if len(dependingSignals) == 0:
            # no dependencies to calculate startSignal (e.g. in case of const blocks or blocks without direct feedthrough)

            # block startSignal.getSourceBlock() --> startSignal is a starting point

            # startSignal is at the top of the tree, so add it to the dependiencies
            self.dependencySignals.append( startSignal )

            return




        # go through all signals needed to calculate startSignal
        for signal in dependingSignals:

            print(Fore.MAGENTA + tabs + "-> S " + signal.getName() )

            self.backwardTraverseSignalsExec__( signal, depthCounter = depthCounter + 1 )



