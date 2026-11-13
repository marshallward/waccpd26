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

``c6_main/``
   Additional CPU run series shown as ``CPU (c6_main)`` in both optional
   comparison figures. Included as timing-only in the main-loop figure;
   GPU speedup ratios continue to use the earlier CPU baseline.
   Also shown in the primary main-loop figure as small hollow black circles
   behind the EPYC baseline, labeled ``CPU (production code)``. These production-code
   timings are 1.3–2.8 percent above the earlier CPU timings in the plotted sweep.

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

SCA27 barotropic loop-order case study
--------------------------------------

``sca27_barotropic_256k.csv`` supports the demo closing slide. It is extracted
from the same ``SCA27-paper-data`` snapshot as the continuity data below,
following ``scripts/barotropic_merged.py``, figure 3a and section 5.2.2 of the
paper. Configuration 64 is 512 × 512 × 100 in this experiment.

Each row stores one timing sample and its ``Ocean dynamics`` hit count.
The source path is ``data/raw/<source_directory>/<prefix>_064_r<repeat>.out``.
The value is 1000 times the per-rank mean ``tavg`` of
``(Ocean barotropic mode stepping)``, divided by dynamics hits / 2.
CPU uses the minimum of five 150-step runs on the 104-core Xeon node;
each MI250X GCD form has one unprofiled 20-step run. The differing repeat
counts are labeled on the figure; no confidence intervals are inferred.

The original AMD form is ``mi250x-bt-data/unsure/plain``, as used in the
paper's figure, not the distinct ``base`` directory. The alternative is
``mi250x-bt-data/jik/plain``, without ``nowait``. CPU uses
``cpu104-base-data`` and ``cpu104-bt-jik-data``. The whole-solver times are:

* CPU j-k-i: 45.28342 ms; j-i-k: 59.19762 ms (30.7% higher time).
* AMD j-k-i: 77.2182 ms; j-i-k: 36.2583 ms (2.13× lower time).

Bars are normalized independently to each platform's original form, with
absolute times annotated. These are source/compiler tradeoffs, not hardware
rankings. The rewrite changes the solver's 16 j-k-i reduction loops; it does
not mean every barotropic kernel is a vertical reduction. Both preserve the
ordered k sum. The paper has no matching NVIDIA j-i-k experiment, so no H200
pair is plotted. Its separate async/nowait experiments are not included.
AMD results describe a historical explicit-OpenMP component port and tested
compiler lowering; do not infer current-code or current-compiler behavior.

Normal builds read only the committed CSV. To verify the source extraction:

.. code-block:: sh

   python3 scripts/gen_barotropic_tradeoff.py \
     --import-data ~/presentations/SCA27-paper-data


SCA27 continuity-correction case study
-------------------------------------

``sca27_continuity_256k.csv`` is a small extracted snapshot from
``~/presentations/SCA27-paper-data`` at commit
``296e36a27387507442d026cb80a6f6d29665207d``. It supports the closing
portability-tradeoff visual, not the WACCPD main-loop or module figures.
Source: Yang et al., SCA27 manuscript, section 5.3 / figure 4.

Each row retains five per-step timing samples at configuration 64, meaning
512 × 512 columns with 100 layers in this study (its reference is 64 × 64,
not the WACCPD configuration convention). ``source_directory`` is relative
to that repository's ``data/raw``. The source files are
``<prefix>_064_r1.out`` through ``<prefix>_064_r5.out``.
Each sample is 1000 times the per-rank mean ``tavg`` of
``(Ocean continuity correction)``, divided by ``Ocean dynamics`` hits / 2.
The visual takes the minimum of the five samples, following the source script
``scripts/flux_adjust_jik_compare.py``.

Resources are a 104-core dual-socket Intel Xeon Platinum 8470Q node,
one NVIDIA H200, and one AMD MI250X GCD (not a full MI250X). The AMD component
is an experimental explicit-OpenMP port, not the complete dynamic core.
The column-wise rewrite also moves Newton iterations into each thread and
enables per-face early exit; it is not just loop interchange. This is a
compiler/source portability case study, not a controlled hardware ranking.

Ordinary builds read only the committed CSV. To verify or refresh the extract,
this command prints the CSV to stdout without modifying either repository:

.. code-block:: sh

   python3 scripts/gen_portability_tradeoff.py \
     --import-data ~/presentations/SCA27-paper-data


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
