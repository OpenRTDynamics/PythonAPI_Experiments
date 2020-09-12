

# from BlockPrototypes import Operator1
from typing import Dict, List

from . import lang as dy
from . import BlockPrototypes as block_prototypes

from .CodeGenHelper import *
from . import SignalInterface as si

from .Signal import Signal, UndeterminedSignal, BlockOutputSignal, SimulationInputSignal



class sub:
    def __init__(self, subsystem_name = None ):

        if subsystem_name is not None:
            self._subsystem_name = subsystem_name
        else:
            self._subsystem_name = dy.generate_subsystem_name()

        self._outputs_inside_subsystem = []
        self._outputs_of_embedding_block = []

    def add_output(self, output_signal : dy.SignalUserTemplate):

        self._outputs_inside_subsystem.append(output_signal)


        # use SubsystemOutputLink to generate a new signal to be used outside of the subsystem
        # This creates a link output_signal_of_embedding_system --> output_signal
        output_signal_of_embedding_system = dy.SubsystemOutputLinkUser( dy.get_simulation_context().UpperLevelSim, output_signal )

        # inherit datatype from output_signal
        output_signal_of_embedding_system.inherit_datatype( output_signal )


        self._outputs_of_embedding_block.append( output_signal_of_embedding_system.unwrap )

        return output_signal_of_embedding_system

    def set_outputs(self, signals):
        """
            connect the list of outputs
        """
        return_signals = []

        for s in signals:
            return_signals.append( self.add_output( s ) )

        return return_signals




    def __enter__(self):

        print("enterq subsystem " + self._subsystem_name )
        dy.enter_subsystem(self._subsystem_name )

        return self


    def __exit__(self, type, value, traceback):

        print("leave subsystem " + self._subsystem_name )

        # set the outputs of the system
        dy.get_simulation_context().set_primary_outputs( dy.unwrap_list( self._outputs_inside_subsystem ) )

        # Please note: in case it is really necessary to specify a system != None here, use the upper-level system
        # not the embedded one.

        # store an embeeder prototype (as generated by dy.GenericSubsystem) into the date structure of the subsystem
        embeddedingBlockPrototype = dy.GenericSubsystem( sim=dy.get_simulation_context().UpperLevelSim, 
                                                        inputSignals=None, manifest=None, 
                                                        additionalInputs=None )

        dy.get_simulation_context().embeddedingBlockPrototype = embeddedingBlockPrototype

        #
        # Link output_signal_of_embedding_system to the outputs created by dy.GenericSubsystem
        #

        embeddedingBlockPrototype.set_anonymous_output_signal_to_connect(   self._outputs_of_embedding_block  )


        # TODO: add a system wrapper/embedded (e.g. this if-block) to leave_system
        dy.leave_system()









class sub_if:
    """

        NOTE: in case the if condition is false, the outputs are hold. Eventally uninitialized.
    """


    def __init__(self, condition_signal : dy.SignalUserTemplate, subsystem_name = None, prevent_output_computation = False ):

        if subsystem_name is not None:
            self._subsystem_name = subsystem_name
        else:
            self._subsystem_name = dy.generate_subsystem_name()

        self._condition_signal = condition_signal
        self._prevent_output_computation = prevent_output_computation

        self._outputs_inside_subsystem = []
        self._outputs_of_embedding_block = []

    def add_output(self, output_signal : dy.SignalUserTemplate):

        self._outputs_inside_subsystem.append(output_signal)

        # use SubsystemOutputLink to generate a new signal to be used outside of the subsystem
        # This creates a link output_signal_of_embedding_system --> output_signal
        output_signal_of_embedding_system = dy.SubsystemOutputLinkUser( dy.get_simulation_context().UpperLevelSim, output_signal )

        # inherit datatype from output_signal
        output_signal_of_embedding_system.inherit_datatype( output_signal )

        self._outputs_of_embedding_block.append( output_signal_of_embedding_system.unwrap )

        return output_signal_of_embedding_system


    def __enter__(self):

        print("enter triggered subsystem " + self._subsystem_name )
        dy.enter_subsystem(self._subsystem_name )

        return self


    def __exit__(self, type, value, traceback):

        print("leave triggered subsystem " + self._subsystem_name )

        # set the outputs of the system
        dy.get_simulation_context().set_primary_outputs( dy.unwrap_list( self._outputs_inside_subsystem ) )

        # Please note: in case it is really necessary to specify a system != None here, use the upper-level system
        # not the embedded one.

        # store an embeeder prototype (as generated by dy.GenericSubsystem) into the date structure of the subsystem
        embeddedingBlockPrototype = dy.TruggeredSubsystem( sim=dy.get_simulation_context().UpperLevelSim, 
            inputSignals=None, 
            N_outputs=len(self._outputs_inside_subsystem),
            manifest=None, 
            trigger=self._condition_signal.unwrap,
            prevent_output_computation=self._prevent_output_computation )

        
        for i in range(0, len( embeddedingBlockPrototype.outputs )):
            embeddedingBlockPrototype.outputs[i].inherit_datatype_from_signal( self._outputs_inside_subsystem[i].unwrap() )

        #dy.get_simulation_context().embeddedingBlockPrototype = embeddedingBlockPrototype

        #
        # Link output_signal_of_embedding_system to the outputs created by dy.GenericSubsystem
        #

        #embeddedingBlockPrototype.set_anonymous_output_signal_to_connect(   self._outputs_of_embedding_block  )


        # TODO: add a system wrapper/embedded (e.g. this if-block) to leave_system
        dy.leave_system()











#
# new stuff
#





class SwitchPrototype:
    """
        a switch for subsystems that are implemented by SwitchedSubsystemPrototype (class to be derived)

        switch_subsystem_name        - the name of the switch
        number_of_additional_outputs - the number of system outputs in addition to the embedded systems outputs
                                       i.e. control outputs of a switch/statemaching/...

        - member variables -

        self._switch_output_links    - overwrite by derived class when calling on_exit()
        self.outputs                 - a list of output signals as defined by self._switch_output_links

        - methods to be defined -

        on_exit(subsystem_prototypes)  - callback once all subsystems were defined
                                         during this callback self._switch_output_links must be defined

    """

    # NOTE: in case of an exception, nothing happens just __exit__ is called silently which then aborts

    def __init__(self, switch_subsystem_name, number_of_additional_outputs=0):

        self._switch_subsystem_name = switch_subsystem_name
        self._total_number_of_subsystem_outputs = None
        self._switch_output_links = None
        self._switch_system = None
        self._number_of_additional_outputs = number_of_additional_outputs
        self._number_of_switched_outputs = None

        # List [ dy.GenericSubsystem ]
        self._subsystem_prototypes = None

        # List [ switch_single_sub ]
        self._subsystem_list = None


    def new_subsystem(self, subsystem_name = None):
        raise BaseException("to be implemented")

    def __enter__(self):

        self._subsystem_list = []
        self._subsystem_prototypes = []

        return self

    def on_exit(self, subsystem_prototypes):
        """
            called when all subsystems have been added to the switch

            subsystem_prototypes - the list of subsystem block prototypes of type dy.GenericSubsystem
        """
        raise BaseException("to be implemented")

    def __exit__(self, type, value, traceback):
        # collect all prototyes thet embedd the subsystems
        for system in self._subsystem_list:
            self._subsystem_prototypes.append( system.subsystem_prototype )

        # analyze the default subsystem (the first) to get the output datatypes to use
        for subsystem in [ self._subsystem_list[0] ]:

            # get the outputs that will serve as reference points for datatype inheritance
            number_of_normal_outputs = len( subsystem.outputs ) - self._number_of_additional_outputs
            self._reference_outputs = subsystem.outputs[0:number_of_normal_outputs]
            self._total_number_of_subsystem_outputs = len(subsystem.outputs)

            self._number_of_switched_outputs = self._total_number_of_subsystem_outputs - self._number_of_additional_outputs

        self.on_exit( self._subsystem_prototypes )

    @property
    def outputs(self):

        if self._switch_output_links is None:
            BaseException("Please close the switch subsystem before querying its outputs")
        
        return self._switch_output_links
    


class SwitchedSubsystemPrototype:
    """
        A single subsystem as part of a switch (implemented by SwitchPrototype) inbeween multiple subsystems

        - methods to called by the user -

        set_switched_outputs(signals)  - connect a list of signals to the output of the switch
    """

    # NOTE: in case of an exception, nothing happens just __exit__ is called silently which then aborts

    def __init__(self, subsystem_name = None ):

        if subsystem_name is not None:
            self._subsystem_name = dy.generate_subsystem_name() + '_' + subsystem_name
        else:        
            self._subsystem_name = dy.generate_subsystem_name()

        self._outputs_inside_subsystem = None

        self._system = None
        self._anonymous_output_signals = None
        self._embeddedingBlockPrototype = None

    @property
    def system(self):
        return self._system

    @property
    def name(self):
        return self._subsystem_name

    @property
    def outputs(self):
        return self._outputs_inside_subsystem

    def set_switched_outputs(self, signals):
        """
            connect a list of outputs to the switch that switches between multple subsystems of this kind

            use self.set_switched_outputs_prototype in the derived classes to set this
        """
        
        BaseException("to be implemented")

    def set_switched_outputs_prototype(self, signals):
        """
            connect a list of outputs to the switch that switches between multple subsystems of this kind
        """

        if self._outputs_inside_subsystem is None:
            self._outputs_inside_subsystem = signals.copy()
        else:
            raise BaseException("tried to overwrite previously set outputs")





    def __enter__(self):

        #print("enter system " + self._subsystem_name)
        self._system = dy.enter_subsystem(self._subsystem_name )

        return self


    def __exit__(self, type, value, traceback):
        embedded_subsystem = dy.get_simulation_context()

        #
        number_of_subsystem_ouputs = len(self._outputs_inside_subsystem)

        # set the outputs of the system
        embedded_subsystem.set_primary_outputs( dy.unwrap_list( self._outputs_inside_subsystem ) )

        # create generic subsystem block prototype
        self._embeddedingBlockPrototype = dy.GenericSubsystem( sim=embedded_subsystem.UpperLevelSim, 
                                                    manifest=None, inputSignals=None, 
                                                    embedded_subsystem=embedded_subsystem,
                                                    N_outputs=number_of_subsystem_ouputs )

        # leave the context of the subsystem
        dy.leave_system()

    @property
    def subsystem_prototype(self):
        return self._embeddedingBlockPrototype


##
##
## Derivatives of SwitchedSubsystemPrototype
##
##




#
# Switch among subsystems i.e. similar to select/case
#

class SwitchedSubsystem(SwitchedSubsystemPrototype):
    """
        A single subsystem as part of a switch (implemented by SwitchPrototype) inbeween multiple subsystems

        - methods to be called by the user -

        set_switched_outputs(signals)  - connect a list of signals to the output of the switch
    """
    def __init__(self, subsystem_name = None ):

        SwitchedSubsystemPrototype.__init__(self, subsystem_name)


    def set_switched_outputs(self, signals):
        """
            connect a list of outputs to the switch that switches between multple subsystems of this kind
        """

        self.set_switched_outputs_prototype(signals)

        # if self._outputs_inside_subsystem is None:
        #     self._outputs_inside_subsystem = signals.copy()
        # else:
        #     raise BaseException("tried to overwrite previously set outputs")



class sub_switch(SwitchPrototype):
    def __init__(self, switch_subsystem_name, select_signal : dy.SignalUserTemplate ):

        self._select_signal = select_signal
        SwitchPrototype.__init__(self, switch_subsystem_name, number_of_additional_outputs=0)

    def new_subsystem(self, subsystem_name = None):

        system = SwitchedSubsystem(subsystem_name=subsystem_name)
        self._subsystem_list.append(system)

        return system


    def on_exit(self, subsystem_prototypes):

        # create the  embeeder prototype
        embeddedingBlockPrototype = dy.SwichSubsystems( sim=dy.get_simulation_context(), 
                control_input=self._select_signal.unwrap, 
                subsystem_prototypes=subsystem_prototypes, 
                reference_outputs=  si.unwrap_list( self._reference_outputs ) )

        # connect the normal outputs via links
        self._switch_output_links = si.wrap_signal_list( embeddedingBlockPrototype.subsystem_switch_outouts )

        # connect the additional (control) outputs
        # -- None --



#
# State machines
#

class state_sub(SwitchedSubsystemPrototype):
    """
        A single subsystem as part of a state machine (implemented by sub_statemachine)

        - methods to called by the user -

        set_switched_outputs(signals, state_signal)  - connect a list of signals to the output of the state machine
    """

    def __init__(self, subsystem_name = None ):
        SwitchedSubsystemPrototype.__init__(self, subsystem_name)

        self._output_signals = None
        self._state_signal = None


    def set_switched_outputs(self, signals, state_signal):
        """
            set the output signals of a subsystem embedded into the state machine

            - signals      - normal system output that are forwarded using a switch
            - state_signal - control signal indicating the next state the state machine enters
        """
        self._output_signals = signals
        self._state_signal = state_signal

        # SwitchedSubsystemPrototype.set_switched_outputs(self, signals +  [state_signal] )

        self.set_switched_outputs_prototype( signals +  [state_signal] )

    @property
    def state_control_output(self):
         return self._state_signal

    @property
    def subsystem_outputs(self):
        return self._output_signals



class sub_statemachine(SwitchPrototype):
    """
        A state machine subsystem

        - properties -

        self.state - status signal of the state machine (available after 'with sub_statemachine' has findished)
    """
    def __init__(self, switch_subsystem_name):
        number_of_additional_outputs = 1 # add one control output to inform about the current state

        SwitchPrototype.__init__(self, switch_subsystem_name, number_of_additional_outputs )

        # state output signal undefined until defined by on_exit() 
        self._state_output = None

    @property
    def state(self):

        return self._state_output

    def new_subsystem(self, subsystem_name = None):

        system = state_sub(subsystem_name=subsystem_name)
        self._subsystem_list.append(system)

        return system

    def on_exit(self, subsystem_prototypes):

        # create the embeeder prototype
        embeddedingBlockPrototype = dy.StatemachineSwichSubsystems( sim=dy.get_simulation_context(), 
                subsystem_prototypes=subsystem_prototypes, 
                reference_outputs=  si.unwrap_list( self._reference_outputs ) )

        # connect the normal outputs via links
        self._switch_output_links = si.wrap_signal_list( embeddedingBlockPrototype.subsystem_switch_outouts )

        # connect the additional (control) outputs
        self._state_output = si.wrap_signal( embeddedingBlockPrototype.state_output )

