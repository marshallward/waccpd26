WACCPD 2026 presentation draft
=============================

15-minute slot: **18 main slides (including title), 14:30 of planned speech,
0:30 margin**, plus optional August/November comparisons beneath the main
timing and module slides, and six vertical backup slides under the conclusion.
Speaker notes and elapsed-time cues are in ``slides.txt`` (reStructuredText).

View and edit
-------------

.. code-block:: sh

   make serve

Open http://localhost:8000. Press **S** for speaker view, **Esc** for the
overview, **Right** for the main talk, and **Down** for vertical comparison or
backup slides. **Space** traverses vertical slides too. Speaker view requires
HTTP serving and permission to open its popup.
For PDF printing, open http://localhost:8000/?print-pdf and print landscape
with backgrounds enabled. Backup slides are included in the printout.

Edit ``slides.txt``, then run ``make``. Build requirements: Pandoc, Python 3.13
(as used in CI), the packages in ``requirements.txt``, D2 (0.9.0 in CI),
Asymptote, dvisvgm, curl, tar, and
LaTeX with its recommended packages/fonts. Liberation fonts are used for plots
where available. The Makefile downloads Reveal.js into ``reveal.js/`` if
``reveal.js/dist/reveal.js`` is missing, using version 5.2.1 pinned in
``REVEAL_VERSION``. Local builds and deployment use the same rule.
Reveal.js is not tracked in Git; an existing installation is reused.
Viewing the built presentation needs no CDN.

The ocean-flow video is cached in ``media/mom6_relvort.mp4`` and ignored by
Git. On a fresh build, the Makefile downloads the approximately 49 MiB file
from https://marshallward.org/sewg2026/media/mom6_relvort.mp4; local previews
can instead reuse the identical file from the SEWG presentation. Override
``MOM6_VIDEO_URL`` if its hosting location changes. Deployment includes the
cached file, so playback is local to the deployed talk rather than streamed
from the older presentation. Cached media is preserved by ``make clean``.
The video is muted and loops on its slide; controls allow manual playback
if autoplay is blocked. Budget about thirty seconds, not the full movie.

For a fresh local checkout, install the system dependencies above, then:

.. code-block:: sh

   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install -r requirements.txt
   make serve

``make figures`` regenerates the thirteen generated SVGs. ``make clean``
removes those SVGs and the HTML, but preserves static assets and source data.
It also preserves Reveal.js, so subsequent builds can work offline. To install
a different Reveal.js version, remove ``reveal.js/`` and rebuild with
``make REVEAL_VERSION=<version>``.

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
are ignored. Four static assets under ``img/`` are retained in Git:
``bg_gfdl.jpg``, ``gyre.png``, ``corad_blocks.svg``, and ``mom6_regional.png``.
The regional image is copied unchanged from the GTC poster's
``assets/mom6_regional.png``: Gulf Stream and eddies in the 5 km Northwest
Atlantic configuration. It provides scientific context on ``What is MOM6?``;
it is not the timing benchmark or evidence of a GPU-validated production run.
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
   * - Layer, column, and slice solver diagrams
     - ``scripts/gen_kernel_types.py``, adapted from the GTC poster
   * - Moving ocean-layer schematic
     - ``scripts/gen_ocean_layers.py``, adapted from the GTC poster
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

The ``Solvers of MOM6`` overview reuses the schematic geometry and teal/orange
colors from ``~/presentations/gtc2026/scripts/kernel_types.py``. Its local
adaptation exports SVGs rather than poster PDFs/PNGs, with sans-serif labels
and a transparent outer background. These illustrate dependency patterns,
not literal ocean data or GPU thread layouts. The slice is one useful pattern
within mixed solvers, not a complete depiction of all their phases. No GTC
performance datasets or results are imported into this talk.
The ocean sketch above the diagrams comes from the poster's
``scripts/ocean_layers.py``. It schematically depicts moving ALE layers,
not simulation output; the branching layout relates the ocean domain to
computational views rather than indicating a sequence of solver execution.
The local SVG animates the interfaces on a six-second loop. The column's left
and right walls stay fixed horizontally, while its internal layer boundaries
and top follow the surrounding waves; the seabed remains stationary. The generator checks
that interfaces never cross. Click the picture (or focus it and press Enter)
to pause/resume; reduced-motion preferences pause it automatically. Use
``python3 scripts/gen_ocean_layers.py --static -o /tmp/opencode/ocean_layers.svg``
for a still export. No animation library or video file is required.

RST slide transitions
---------------------

The two ``Solvers of MOM6`` slides use Reveal.js Auto-Animate. The first
shows the ocean sketch large and centered; on the next advance it moves up
and shrinks while the three solver diagrams fade in. This uses the existing
solver explanation's timing budget rather than adding speaking time.

``scripts/reveal_attributes.lua`` converts RST classes into Reveal attributes
during the Pandoc build, without editing generated HTML. Mark adjacent slide
headings like this::

   .. class:: auto-animate animate-group-solvers

   Solvers of MOM6
   ===============

``auto-animate`` enables the effect; matching ``animate-group-NAME`` classes
restrict it to that sequence. Containers with matching ``animate-id-NAME``
classes receive matching ``data-id`` values. Raw embedded elements can use
``data-id`` directly, as the animated ocean SVG objects do. Position and size
differences are authored in ``gfdl.css``; the filter sets a one-second
ease-in-out transition. Other slides retain the normal sliding effect.

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
