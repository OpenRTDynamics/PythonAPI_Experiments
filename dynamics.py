from libdyn import *
from Signal import *
from Block import *
from BlockPrototypes import *
from ExecutionCommands import *
from CodeGenTemplates import *
from CompileDiagram import *
from SimulationContext import *
from CompileDiagram import *
from SignalInterface import *

print("-- RTDynamics II loaded --")

def signal():
    return SignalUser(get_simulation_context())

def system_input(datatype):
    return SimulationInputSignal(get_simulation_context(), datatype)
    