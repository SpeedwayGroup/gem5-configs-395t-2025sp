"""se_custom_binary_periodic.py

A sample SE config script to run custom binaries on a switchable CPU,
which uses KVM to fast-forward and O3 to simulate.
"""

import time
from typing import Final

from gem5.components.memory import DualChannelDDR4_2400
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from termcolor import colored, cprint

import util.simarglib as simarglib
from components.boards.custom_simple_board import CustomSimpleBoard
from components.cache_hierarchies.three_level_classic import ThreeLevelClassicHierarchy
from components.cpus.skylake_cpu import SkylakeCPU
from components.processors.custom_x86_switchable_processor import (
    CustomX86SwitchableProcessor,
)
from util.event_managers.event_manager import EventCoordinator
from util.event_managers.roi.periodic import PeriodicROIManager
from workloads.se.custom_binary import CustomBinarySE

# Parse all command-line args
simarglib.parse()

# Create a processor
requires(isa_required=ISA.X86)

# Start with a KVM CPU
# Switch to a SkylakeCPU (O3)
processor = CustomX86SwitchableProcessor(SwitchCPUCls=SkylakeCPU)

# Create a cache hierarchy
cache_hierarchy = ThreeLevelClassicHierarchy()

# Create some DRAM
memory = DualChannelDDR4_2400(size="3GiB")

# Create a board
board = CustomSimpleBoard(
    processor=processor, cache_hierarchy=cache_hierarchy, memory=memory
)

# Create event manager and event coordinator
#
# This specific event manager, PeriodicROIManager, handles the
# fast-forward, warmup, and simulation intervals / regions of interest.
#
# The coordinator manages one or more event managers to ensure multiple
# event managers can work together smoothly.
roi_manager = PeriodicROIManager()
coordinator = EventCoordinator([roi_manager])

# Set up the workload
workload = CustomBinarySE()

# Configure the board
board.set_workload(workload)

# Set up the simulator
simulator = Simulator(
    board=board,
    on_exit_event=coordinator.get_event_handlers(),
)
coordinator.register(simulator)

# Print information
print(
    colored(
        "***Fast-forward interval:",
        color="blue",
        attrs=["bold"],
    ),
    colored(
        f"{roi_manager._ff_interval:,} instructions",
        color="blue",
    ),
)
print(
    colored(
        "***Warmup interval      :",
        color="blue",
        attrs=["bold"],
    ),
    colored(
        f"{roi_manager._warmup_interval:,} instructions",
        color="blue",
    ),
)
print(
    colored(
        "***ROI interval         :",
        color="blue",
        attrs=["bold"],
    ),
    colored(
        f"{roi_manager._roi_interval:,} instructions",
        color="blue",
    ),
)
print(
    colored(
        "***Initial fast-forward :",
        color="blue",
        attrs=["bold"],
    ),
    colored(
        f"{roi_manager._init_ff_interval:,} instructions",
        color="blue",
    ),
)
print(
    colored(
        "***Maximum ROIs         :",
        color="blue",
        attrs=["bold"],
    ),
    colored(
        f"{roi_manager._num_rois or 'Unlimited'}",
        color="blue",
    ),
)
print(
    colored("***Continue simulation  :", color="blue", attrs=["bold"]),
    colored(
        f"{roi_manager._continue_sim}",
        color="blue",
    ),
)

# Run the simulation
start_wall_time: Final[float] = time.time()
cprint("***Beginning simulation!", color="blue", attrs=["bold"])
simulator.run()

elapsed_wall_time: Final[float] = time.time() - start_wall_time
elapsed_instructions = coordinator.get_current_time().instruction or 0
elapsed_ticks = simulator.get_current_tick()
print(
    colored(
        f"***Instruction {elapsed_instructions:,}, tick {elapsed_ticks:,}:",
        color="blue",
        attrs=["bold"],
    ),
    colored(
        f"Exiting because {simulator.get_last_exit_event_cause()}.",
        color="blue",
    ),
)
print(
    colored(
        "***Total wall clock time:",
        color="blue",
        attrs=["bold"],
    ),
    colored(
        f"{(elapsed_wall_time/60):.2f} min",
        color="blue",
    ),
)
