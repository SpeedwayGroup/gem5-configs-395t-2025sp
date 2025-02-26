"""
Sample FS config script to run multi-threaded GAP and Parsec benchmarks
with a switchable CPU, booting the OS in KVM and then switching to a simple
TIMING processor with a 3-level classic cache hierarchy
"""

import time

from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

import util.simarglib as simarglib
from components.cache_hierarchies.three_level_classic import ThreeLevelClassicHierarchy
from components.processors.custom_x86_switchable_processor import (
    CustomX86SwitchableProcessor,
)
from util.event_managers.roi.simple import SimpleROIManager
from workloads.fs.gap_and_parsec import GapAndParsecFS

# Parse all command-line args
simarglib.parse()

# Create a processor
# NOTE: using a timing processor, NOT the detailed O3 model!
requires(isa_required=ISA.X86)

# kvm start core, timing switch core recommended
processor = CustomX86SwitchableProcessor()

# Create a cache hierarchy
cache_hierarchy = ThreeLevelClassicHierarchy()

# Create some DRAM
memory = DualChannelDDR4_2400(size="3GB")

# Create a board
board = X86Board(
    clk_freq="3GHz", processor=processor, cache_hierarchy=cache_hierarchy, memory=memory
)

# Set up the workload
workload = GapAndParsecFS()
board.set_workload(workload)

# Set up the simulator
# (including any event management)
manager = SimpleROIManager()
simulator = Simulator(board=board, on_exit_event=manager.get_event_handlers())

# Run the simulation
starttime = time.time()
print("***Beginning simulation!")
simulator.run()

totaltime = time.time() - starttime
print(
    f"***Exiting @ tick {simulator.get_current_tick()} because {simulator.get_last_exit_event_cause()}."
)
print(f"Total wall clock time: {totaltime:.2f} s = {(totaltime/60):.2f} min")
