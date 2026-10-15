WACCPD 2026 presentation draft
=============================

15-minute slot: **16 main slides (including title), 14:30 of planned speech,
0:30 margin**, plus six vertical backup slides under the conclusion.
Speaker notes and elapsed-time cues are in ``slides.txt`` (reStructuredText).

View and edit
-------------

.. code-block:: sh

   make serve

Open http://localhost:8000. Press **S** for speaker view, **Esc** for the
overview, **Right/Space** for the main talk, and **Down** at the conclusion for
backups. Speaker view requires HTTP serving and permission to open its popup.
For PDF printing, open http://localhost:8000/?print-pdf and print landscape
with backgrounds enabled. Backup slides are included in the printout.

Edit ``slides.txt``, then run ``make``. Build requirements: Pandoc, Python 3.13
(as used in CI), the packages in ``requirements.txt``, D2 (0.9.0 in CI),
Asymptote, dvisvgm, and
LaTeX with its recommended packages/fonts, plus a local Reveal.js installation
in ``reveal.js/``. Liberation fonts are used for plots where available.
Reveal.js is not tracked in Git; the deployment workflow downloads version 5.2.1.
Viewing the built presentation needs no CDN.

For a fresh local checkout, install the system dependencies above, then:

.. code-block:: sh

   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install -r requirements.txt
   mkdir -p reveal.js
   curl -fsSL https://github.com/hakimel/reveal.js/archive/refs/tags/5.2.1.tar.gz \
     | tar -xz --strip-components=1 -C reveal.js
   make serve

``make figures`` regenerates just the seven generated SVGs. ``make clean``
removes those SVGs and the HTML, but preserves static assets and source data.

Deployment
----------

``.github/workflows/deploy.yml`` builds on pushes to ``main`` and can also be
started manually. It installs the plotting and diagram dependencies, downloads
the pinned Reveal.js release, generates figures from the local sources and
recorded timing logs, and stages the presentation under ``public/waccpd26/``.
Neither the build nor deployment needs neighboring manuscript repositories or
a GPU.

The workflow publishes to ``marshallward/marshallward.github.io`` on branch
``master``, preserving the site's other files. Configure the repository secret
``PAGES_DEPLOY_KEY`` with a deploy key authorized to write to that repository,
as in the September developer talk. The resulting URL is
https://marshallward.org/waccpd26/.

Generated HTML, figure SVGs, the Reveal.js installation, and deployment output
are ignored. Three static assets under ``img/`` are retained in Git:
``bg_gfdl.jpg``, ``gyre.png``, and ``corad_blocks.svg``.
The old ``figures/*.pdf`` copies are no longer build inputs; any existing
local copies are left untouched and ignored.

Figure generation
-----------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Output
     - Committed inputs
   * - Main-loop and module timings
     - ``runs/gen_plot.py`` and CPU/GH200 ``*.out`` logs
   * - Multi-GPU dynamic-core speedup
     - ``runs/plot_dycore_scaling.py`` and H100 ``*.out`` logs
   * - Multi-GPU module timings
     - ``runs/gen_plot.py`` and H100 ``*.out`` logs
   * - Block-shape diagram
     - ``asy/block_shapes.asy``
   * - Animated block traversal
     - ``scripts/gen_block_loop_title.py``
   * - FMS/MPI communication diagram
     - ``d2/fms_mpi.d2`` (copied from the NRL presentation)

The plotting scripts and timing logs are copied snapshots from the manuscript,
not live references. See ``runs/README.rst`` for provenance and configuration
selection. Python dependencies are pinned in ``requirements.txt``. Matching
numerical results does not imply byte-identical SVGs across systems: timestamps,
font availability, and diagram tool versions can affect output.

All generated performance plots use sans-serif fonts, including math labels,
with DejaVu Sans preferred. Both plotting scripts use ``--dark`` for white
text on a transparent outer background with white plot panels. Slide 14
reproduces the paper's fixed-domain speedup versus GPU count, with three
domain-size curves and an ideal-scaling reference. The H100 module plots
still show time per step against domain area, one curve per GPU count.
``plot_module_scaling.py`` remains an unused reference; a replacement
module-level speedup view is deferred.

The older blocking comparison remains static until its generator and original
data are recovered. Background and gyre image also remain static.

Sources and scope
-----------------

- Manuscript: ``~/manuscripts/waccpd/waccpd26.txt``. The requested
  ``~/manuscripts/waccpd26`` directory was absent.
- Theme and template: ``~/presentations/nrl2026``, with the same short-heading,
  figure-led approach used in ``~/presentations/sewg2026``.
- Blocking traversal animation, before/after plot, and implementation details:
  ``~/presentations/mom6-gpu-2026-09-14``. The earlier blocking experiment is
  explicitly distinguished from the manuscript's current GH200 measurements.
- Plot generators, recorded logs, and block-shape source:
  ``~/manuscripts/waccpd/``. Animation generator:
  ``~/presentations/mom6-gpu-2026-09-14/scripts/``. Background, gyre image,
  and FMS diagram come from NRL.
- Single-device results are **one GH200 GPU vs one 96-core Genoa socket**;
  fixed-domain scaling uses **H100 GPUs**. These should not be conflated.
- Bitwise validation is for NVIDIA CPU/GPU builds in the tested cases. The
  timing baseline uses Intel CPU compilation; the CPU regression test is a
  separate, matched comparison of production and GPU-enabled codebases.
- The draft does not claim a completed whole-model or cross-vendor GPU port.

Before presenting
-----------------

- Confirm event metadata and whether the 15-minute slot includes questions.
- Rehearse the notes; the timing is a draft budget, not a measured delivery.
- If questions must fit inside 15 minutes, omit the traversal animation and
  shorten the module breakdown. The blocking animation illustrates coverage,
  not serial execution of concurrent iterations. Serve over HTTP so the SVG
  object's script can run; PDF exports capture only a static frame.
- Confirm hardware, compiler settings, and the meaning of the shaded bands
  before making quantitative claims from the older ``corad_blocks.svg`` plot.
- The regenerated module figure's title now uses the plotted 64×64 reference
  rather than the old manuscript title's 32×32 lower bound. This label-only
  correction does not change data or domain selection.
- Review plot readability at the actual projection size. All six module
  panels are retained to match the paper; narration focuses on two contrasts.

Reveal.js licensing is retained in ``reveal.js/LICENSE`` and included in the
deployment output.
