from libdyn import *
from irpar import *
from BlockPrototypes import *
from TraverseGraph import *
from Signal import *
from ExecutionCommands import *
from CodeGenTemplates import *

from colorama import init,  Fore, Back, Style
init(autoreset=True)



class CompileResults(object):
    """
        compilation results for one system
        (excluding subsystems)
    """
    
    def __init__(self, manifest, commandToExecute):
        self._commandToExecute = commandToExecute
        self._manifest = manifest

    @property
    def manifest(self):
        return self._manifest

    @property
    def commandToExecute(self):
        return self._commandToExecute 



class CompileDiagram:

    def __init__(self):

        self._manifest = None
        self._compleResults = None

    @property
    def compileResults(self):
        return self._compleResults


    
    # TODO: for all subsystems in the simulation:
    #       - compile these subsystems first.
    #       - add their system embeddeds (e.g. if-subsystem)
    
    
    def traverseSubSystems(self, system : Simulation, level):
        print("-- List of subsystems --")

        for subSystem in system.subsystems:
            print(" level %d - %s" % (level, subSystem.name ) )

            self.traverseSubSystems(subSystem, level=level+1)


        #
        print("Now compiling: " + system.name )

        if system.name == 'if_subsystem':
            print('compiling if_subsystem')

        # compile the system
        compileResult = compileSystem( system )

        # store the compilation result in the system's structure
        system.compilationResult = compileResult

        if system.UpperLevelSim is not None:
            # means the compiled system is a subsystem

            # TODO: in the upper-level system: place a new block embeddeding 'system' and re-connect the
            # in- and outputs to the new block compiled replace the 

            embeddedingBlockPrototype = system.embeddedingBlockPrototype

            # set the manifest and the compile results describing the embedded subsystem
            embeddedingBlockPrototype.set_manifest( compileResult.manifest )
            embeddedingBlockPrototype.set_compile_result(compileResult)

            # TODO: in the upper-level system 'system.UpperLevelSim' connect the inputs 
            # using embeddedingBlockPrototype.set_inputSignals(  )

            # # get the inputs to the embedded system
            # i_o = compileResult.commandToExecute.API_functions['calculate_output'].inputSignals
            # i_r = compileResult.commandToExecute.API_functions['reset'].inputSignals
            # i_s = compileResult.commandToExecute.API_functions['state_update'].inputSignals

            # # join into sets
            # input_signals = set(( i_o ))
            # input_signals.update( i_r )
            # input_signals.update( i_s )
            # input_signals = list( input_signals )


            # connect these inputs to the embeddedingBlockPrototype
            # note these signals must be order somehow

            embeddedingBlockPrototype.set_inputSignals( compileResult.inputSignals )

            #
            embeddedingBlockPrototype.init(sim=system.UpperLevelSim)

            # initialize the datatypes of the signals yielded by embeddedingBlockPrototype
            # (copy this information)


            # make all outputs coming from embeddedingBlockPrototype
            # make the original connections to phantom connections (or vice versa)

            # o_o = compileResult.commandToExecute.API_functions['calculate_output'].outputSignals
            # o_r = compileResult.commandToExecute.API_functions['reset'].outputSignals
            # o_s = compileResult.commandToExecute.API_functions['state_update'].outputSignals

            # output_signals = set(( o_o ))
            # output_signals.update( o_r )
            # output_signals.update( o_s )

            # TODO: stopped here 3.10.19
            # embeddedingBlockPrototype.embeddedSystemsOutputs

            # get the output signals of the embedded system (returned by the function 'calculate_output')
            output_signals = system.primaryOutputs

            # iterate over all ouputs given by the calculate_outputs function
            portNum = 0
            for s in compileResult.outputSignals:
                s.sourcePort_inEmbeddedSystem = s.sourcePort
                s.sourceBlock_inEmbeddedSystem = s.sourceBlock

                # s.redefine_source(embeddedingBlockPrototype.block, portNum)
                s.redefine_source(sourceBlock=embeddedingBlockPrototype.block, sourcePort=portNum)

                portNum += 1


        else:
            # this system is the top-level system
            self._compleResults = compileResult



    def compile(self, system):
        #
        # The datatypes of all signals must be determined here
        #

        if system.UpperLevelSim is not None:
            raise BaseException("given system is not a top-level system (but dispite a sub-system of sth.)")

        self.traverseSubSystems(system, level = 0)

        if self._compleResults is None:
            raise BaseException("failed to obtain the compilation results")

        
        # self._compleResults = compileSystem(system)

        return self._compleResults



def compileSystem(sim):

    # the primary output signals are the outputs of the compiled system
    outputSignals = sim.primaryOutputs

    # prepare (input filter of the given signals)
    resolveUndeterminedSignals(outputSignals)

    #
    # compile the diagram: turn the blocks and signals into a tree-structure of commands to execute
    # at runtime.
    #



    #
    # create execution path builder that manages the graph of the diagram and markings of the graph nodes.
    #

    E=BuildExecutionPath()


    print()
    print(Style.BRIGHT + "-------- Find dependencies for calcularing the outputs  --------")
    print()


    # collect all execution lines with:
    executionLineToCalculateOutputs = ExecutionLine( [], [], [], [], [] )

    # for all requested output singals
    for s in outputSignals:
        elForOutputS = E.getExecutionLine( s )
        elForOutputS.printExecutionLine()

        # merge all lines into one
        executionLineToCalculateOutputs.appendExecutionLine( elForOutputS )




    print()
    print(Style.BRIGHT + "-------- Build all execution paths  --------")
    print()

    # look into executionLineToCalculateOutputs.dependencySignals and use E.getExecutionLine( ) for each
    # element. Also collect the newly appearing dependency signals in a list and also 
    # call E.getExecutionLine( ) on them. Stop until no further dependend signal appear.
    # finally concatenare the execution lines

    # 

    # start with following signals to be computed
    dependencySignals = executionLineToCalculateOutputs.dependencySignals
    dependencySignalsSimulationInputs = executionLineToCalculateOutputs.dependencySignalsSimulationInputs
    blocksToUpdateStates = executionLineToCalculateOutputs.blocksToUpdateStates
    dependencySignalsThroughStates = executionLineToCalculateOutputs.dependencySignalsThroughStates




    # get the simulation-input signals in dependencySignals
    # NOTE: these are only the simulation inputs that are needed to calculate the output y


    # TODO: stopped here: investigate missmatch between those two
    simulationInputSignalsToCalculateOutputs = dependencySignalsSimulationInputs



    simulationInputSignalsToCalculateOutputs = []
    for s in dependencySignals:
        if isinstance(s, SimulationInputSignal):
            simulationInputSignalsToCalculateOutputs.append(s)

    # counter for the order (i.e. step through all delays present in the system)
    order = 0


    # execution line per order
    commandToCalcTheResultsToPublish = CommandCalculateOutputs(executionLineToCalculateOutputs, outputSignals, defineVarsForOutputs = True)

    #
    # cache all signals that are calculated so far
    # TODO: make a one-liner e.g.  signalsToCache = removeInputSignals( executionLineToCalculateOutputs.signalOrder )
    #

    signalsToCache = []
    for s in executionLineToCalculateOutputs.signalOrder:

        if isinstance(s, UndeterminedSignal):
            raise BaseException("found anonymous signal during compilation")

        if isinstance(s, BlockOutputSignal):

            # only implement caching for intermediate computaion results.
            # I.e. exclude the simulation input signals

            signalsToCache.append( s )

    commandToCacheIntermediateResults = CommandCacheOutputs( signalsToCache )

    # build the API function calcPrimaryResults() that calculates the outputs of the simulation.
    # Further, it stores intermediate results
    commandToPublishTheResults = PutAPIFunction("calcResults_1", 
                                                inputSignals=simulationInputSignalsToCalculateOutputs,
                                                outputSignals=outputSignals, 
                                                executionCommands=[ commandToCalcTheResultsToPublish, commandToCacheIntermediateResults ] )

    # Initialize the list of commands to execute to update the states
    commandsToExecuteForStateUpdate = []

    # restore the cache of output signals to update the states
    commandsToExecuteForStateUpdate.append( CommandRestoreCache(commandToCacheIntermediateResults) )

    # the simulation intputs needed to perform the state update
    #
    # TODO: 6.10.19: use sets for this to collect
    #
    simulationInputSignalsToUpdateStates = []

    # the list of blocks that are updated. Note: So far this list is only used to prevent
    # double uodates.
    blocksWhoseStatesToUpdate_All = []

    while True:

        print("--------- Computing order "+ str(order) + " --------")
        print("dependent sources:")
            
        for s in dependencySignals:
            print(Fore.YELLOW + "  - " + s.toStr() )


        # collect all executions lines build in this order in:
        executionLinesForCurrentOrder = []

        # backwards jump over the blocks that compute dependencySignals through their states.
        # The result is dependencySignals__ which are the inputs to these blocks
        print(Style.DIM + "These sources are translated to (through their blocks via state-update):")




        # find out which singnals must be further computed to allow a state-update of the blocks
        dependencySignals__ = []
        for s in dependencySignalsThroughStates + dependencySignals:

            if isinstance(s, SimulationInputSignal):
                simulationInputSignalsToUpdateStates.append(s)

            elif not E.isSignalAlreadyComputable(s):   # TODO: if s is a simulation input no need to add to dependencySignals__ ?
                dependencySignals__.append(s)

            else:
                print(Style.DIM + "    This signal is already computable (no futher execution line is calculated to this signal)")




        # TODO: check whether to abort in case of len(dependencySignals__) == 0






        # print the list of signals
        print("-- dependency signals __ --")
        for s in dependencySignals__:
            print("  - " + s.name)



        # iterate over all needed input signals and find out how to compute each signal
        for s in dependencySignals__:

            # get execution line to calculate s
            executionLineForS = E.getExecutionLine(s)

            # store this execution line
            executionLinesForCurrentOrder.append(executionLineForS)


        # merge all lines temporarily stored in 'executionLinesForCurrentOrder' into one 'executionLineForCurrentOrder'
        executionLineForCurrentOrder = ExecutionLine( [], [], [], [], [] )
        for e in executionLinesForCurrentOrder:

            # append execution line
            executionLineForCurrentOrder.appendExecutionLine( e )


        # create a command to calcurate executionLineForCurrentOrder and append to the
        # list of commands for state update: 'commandsToExecuteForStateUpdate'
        
        #
        # TODO: ensure somehow that variables are reserved for the inputs to the blocks
        #       whose states are updated
        #

        commandsToExecuteForStateUpdate.append( CommandCalculateOutputs(executionLineForCurrentOrder, dependencySignals__, defineVarsForOutputs = False) )

        #
        # find out which blocks need a call to update their states:
        # create commands for the blocks that have dependencySignals as outputs
        #

        print("state update of blocks that yield the following output signals:")



        # TODO: rework this loop
        # blocksToUpdateStates Is already computed

        blocksWhoseStatesToUpdate = []

        for blk in blocksToUpdateStates:

            if not blk in blocksWhoseStatesToUpdate_All:
                # only add once (e.g. to prevent multiple state-updates in case two or more signals in 
                # dependencySignals are outputs of the same block)
                blocksWhoseStatesToUpdate.append( blk )
                blocksWhoseStatesToUpdate_All.append( blk )

                print("    (added) " + blk.toStr())
            else:
                print("    (already added) " + blk.toStr())




        # create state update command and append to the list of commnds to execute for state-update
        sUpCmd = CommandUpdateStates( blocksWhoseStatesToUpdate )
        commandsToExecuteForStateUpdate.append( sUpCmd )

        #print("added command(s) to perform state update:")
        #sUpCmd.printExecution()

        # get the dependendy singals of the current order
        # TODO important: remove the signals that are already computable from this list
        dependencySignals = executionLineForCurrentOrder.dependencySignals
        blocksToUpdateStates = executionLineForCurrentOrder.blocksToUpdateStates
        dependencySignalsThroughStates = executionLineForCurrentOrder.dependencySignalsThroughStates

        # iterate
        order = order + 1
        if len(dependencySignals__) == 0:
            print(Fore.GREEN + "All dependencies are resolved")

            break

        if order == 1000:
            print(Fore.GREEN + "Maxmimum iteration limit reached -- this is likely a bug or your simulation is very complex")
            break




    # Build API to update the states: e.g. c++ function updateStates()
    commandToUpdateStates = PutAPIFunction( nameAPI = 'updateStates', 
                                            inputSignals=simulationInputSignalsToUpdateStates, 
                                            outputSignals=[], 
                                            executionCommands=commandsToExecuteForStateUpdate )

    # code to reset add blocks in the simulation
    # TODO: only add blocksWhoseStatesToUpdate_All
    commandsToExecuteForStateReset = CommandResetStates( blockList=sim.getBlocksArray() )

    # create an API-function resetStates()
    commandToResetStates = PutAPIFunction( nameAPI = 'resetStates', 
                                            inputSignals=[], 
                                            outputSignals=[], 
                                            executionCommands=[commandsToExecuteForStateReset] )


    # define the interfacing class
    commandToExecute_simulation = PutSimulation(    simulation = sim,
                                                    resetCommand = commandToResetStates, 
                                                    updateCommand = commandToUpdateStates,
                                                    outputCommand = commandToPublishTheResults
                                                )

    # collect all (needed) inputs to this system
    
    # simulationInputSignalsToUpdateStates
    # simulationInputSignalsToCalculateOutputs

    allinputs = set(( simulationInputSignalsToUpdateStates ))
    allinputs.update( simulationInputSignalsToCalculateOutputs )
    allinputs = list(allinputs)

    # output signals
    # outputSignals



    # build the manifest for the compiled system
    manifest = SystemManifest( commandToExecute_simulation )

    compleResults = CompileResults( manifest, commandToExecute_simulation)

    compleResults.inputSignals = allinputs
    compleResults.simulationInputSignalsToUpdateStates = simulationInputSignalsToUpdateStates
    compleResults.simulationInputSignalsToCalculateOutputs = simulationInputSignalsToCalculateOutputs
    compleResults.outputSignals = outputSignals

    

    #
    return compleResults

