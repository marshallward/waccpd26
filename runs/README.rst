Recorded performance data
=========================

These are copies of the manuscript's recorded MOM6 timing logs and plotting
scripts, originally in ``~/manuscripts/waccpd/runs/``. The build reads these
logs; it does not execute MOM6 or require a GPU. Only the ``*.out`` inputs
needed by the plotting scripts are included, not scheduler error logs.

Single-device comparison
------------------------

``c6_96pe_avx512/``
   Fixed-resource baseline: one 96-core AMD EPYC 9654 socket.

``arm_20260809/``
   One GH200 GPU.

``gen_plot.py`` generates the main-loop and six-module figures. Configuration
numbers encode horizontal area relative to 32 × 32. The Makefile excludes
configurations below 4 and divides the displayed scale by 4, so the plotted
reference is 64 × 64 and the largest displayed area factor is 256.
Vertical resolution is 100 levels. The main-loop figure includes speedup;
module panels report time per step. Plot options and sizes follow the
manuscript's Makefile, with the module title corrected to the plotted range.

Multi-GPU timing curves
----------------------

``h100_p1_20260725/``, ``h100_p2_20260725/``, ``h100_p4_20260725/``,
``h100_p8_20260725/``, and ``h100_p10_20260725/`` contain runs using one,
two, four, eight, and ten H100 GPUs respectively. There are two GPUs per node.
As in the single-device figures, configurations below 4 are omitted and the
displayed area scale is divided by 4, giving a 64 × 64 reference grid.

``gen_plot.py`` generates the module timing curves with white text around
white plot panels on a transparent outer background (``--dark``). The x-axis
is global horizontal domain area; each curve fixes the GPU count. Comparing
curves at a fixed x value compares the same global problem on different GPU
counts.

``plot_dycore_scaling.py`` reproduces the paper's dynamic-core strong-scaling
figure: speedup relative to one GPU versus GPU count, with fixed domains of
256 × 256, 512 × 512, and 1024 × 1024 (configurations 64, 256, and 1024).
It includes an ideal-scaling line and uses the same sans-serif fonts and
``--dark`` styling as the timing curves.

``plot_module_scaling.py`` remains an unused publication reference; a
module-level speedup view is deferred. The CPU/GH200 main-loop figure retains
its existing speedup subplot.
These runs use GPU-aware MPI with host-staged communication, not NVLink or
GPUDirect RDMA.

Limitations and maintenance
--------------------------

The copied scripts retain the manuscript's parsing and statistical methods.
The logs and pinned Python dependencies are build inputs; updating them can
change figures and should be reviewed as a scientific-results change.
The separate historical blocking comparison, ``img/corad_blocks.svg``, does
not come from these inputs. Its original generator/data have not been located
and it remains a static asset.
