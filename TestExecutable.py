

from libdyn import *
from irpar import *
from BlockPrototypes import *
from TraverseGraph import *
from Signal import *


@contextmanager
def ld_subsim(sim):
    print("create triggered subsimulation" )

    nestedsim = Simulation(sim, 'IFsub')

    yield nestedsim

    nestedsim.FinishSimulation()

    inlist = nestedsim.GetInputInterface()

    print("--- The following inputs go to the nested simulation ---")

    for i in inlist:

        print(  i  )

    # create new block with the inputs in inlist

    # -- Just store which type of subsimulation block to create:
    #
    # if / for / ...
    #
    # and then do later during export of the schematic
    #
    # In general, think about something to store an abstract representation of each block
    # and do all the work of parameter creation on export
    #
    # Maybe use classes for each block, instead of functions (def:)
    # class functions could be __init__ (collect parameters), check IO, export()
    #
    #
    # (This way, different backends can be supported)
    #



    print("finish triggered subsimulation")



# @contextmanager
# def ld_IF(sim, ConditionSignal):
#     print("create triggered subsimulation" )

#     nestedsim = Simulation(sim, 'IFsub')

#     yield nestedsim

#     print("finish triggered subsimulation")



# new simulation
sim = Simulation(None, 'main')


c1 = dyn_const(sim, 1.123)

c2 = dyn_const(sim, 10)

print()
print('origin of c1')
c1.ShowOrigin()
print()

u = dyn_add(sim, [c1, c2], [1,-1])

# open feedback loop
u2_feedback = Signal(sim)

u2 = dyn_add(sim, [u, u2_feedback], [1,1])

u2_delayed = dyn_delay(sim, u2 )

u2_feedback.setequal( u2_delayed )



#dyn_printf(sim, u, "sum value is")






# with ld_IF(sim, condition) as sim:
#     #pass
#     print("define simulation triggered by if")





# test 
sim.ShowBlocks()


print()
print("-------- Traverse --------")
print()
 # sim.getBlocksArray()
T = TraverseGraph()
T.forwardTraverse( c1.getSourceBlock() )


print()
print("-------- Compile connections --------")
print()
sim.CompileConnections()

# finish
#sim.export_ortdrun('RTMain')
#sim.ShowBlocks()


















