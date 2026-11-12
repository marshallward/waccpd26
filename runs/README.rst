Recorded performance data
=========================

These are copies of the manuscript's recorded MOM6 timing logs and plotting
scripts, originally in ``~/manuscripts/waccpd/runs/``. The build reads these
logs; it does not execute MOM6 or require a GPU. The plots read ``*.out``
inputs; scheduler error logs accompanying the November 11 runs are not used.

Single-device comparison
------------------------

``c6_96pe_avx512/``
   Fixed-resource baseline: one 96-core AMD EPYC 9654 socket.
   Retained as the CPU reference for comparison with November 11 GH200.
   The presenter reports repeated matched-flags tests support treating EPYC
   performance as unchanged; colleague confirmation is still pending.

``c6_96pe_avx512_20261111/``
   Updated EPYC runs, included only in the optional dated main-loop and
   module comparison figures. These replace the mismatched-flags first test
   in ``c6_96pe_20261111/`` (no longer plotted). The presenter reports the
   replacement runs use the same flags as the earlier CPU baseline.
   The main-loop plot shows them as a purple dashed
   timing curve, excluded from the GPU speedup panel using
   ``--timing-only-platform``. All GPU ratios still use the earlier baseline;
   the primary figures remain unchanged. At configuration 1024, the updated
   CPU main-loop time is 1597.216 ms/step, versus 1538.561 ms/step in the
   earlier baseline; these measurements do not yet demonstrate a CPU speedup.

``arm_20260809/``
   One GH200 GPU.

``gh200_p1_20261109/``
   One-GH200 run series supplied November 9, 2026, retained in the dated
   comparison figures. Its main-loop time at
   1024 × 1024 × 100 is 0.484 s/step (483.626 ms).

``gh200_p1_20261111/``
   One-GH200 run series supplied November 11, 2026. The reference for the
   primary main-loop and six-module figures, paired with the original EPYC
   baseline. Each primary
   figure has a vertical subslide overlaying all three GPU dates
   (August 9, November 9, November 11),
   with date-specific legend labels. All speedup curves use the same EPYC
   baseline, matching configuration numbers and the existing per-step
   normalization. At configuration 1024 (1024 × 1024 × 100), the main-loop
   times are 1538.561 ms for the CPU and 395.642 ms for November 11 GH200,
   giving a speedup of 3.889× (August 9: 2.743×; November 9: 3.181×).
   These ratios use the earlier recorded CPU series, retained after the
   presenter's repeat matched-flags CPU tests. Treating CPU performance as
   unchanged is the working assumption; colleague confirmation is pending.
   The absolute November 11 GPU result is
   0.396 s/step at the largest domain.
   Build/compiler/configuration equivalence
   between the GPU series has not been independently established here;
   do not attribute the difference to a particular optimization without review.

``gen_plot.py`` generates the main-loop and six-module figures. Configuration
numbers encode horizontal area relative to 32 × 32. The Makefile excludes
configurations below 4 and divides the displayed scale by 4, so the plotted
reference is 64 × 64 and the largest displayed area factor is 256 in the
module panels. The primary main-loop figure and August/November comparison
instead use ``--domain-sizes``: ticks label 64², 128², 256², 512², and 1024²,
with intermediate area-doubling ticks left unlabeled. This changes labels,
not the plotted x coordinates or data selection.
Vertical resolution is 100 levels in the original experiment. The main-loop
comparison includes a separate speedup curve for each GPU run series, while
the primary figure shows only November 11. Both speedup panels extend to at least 3.5×
and expand automatically to fit the largest measured speedup;
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
