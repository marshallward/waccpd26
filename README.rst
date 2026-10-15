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

Edit ``slides.txt``, then run ``make``. Build requirements: Pandoc and Poppler's
``pdftocairo``, plus a local Reveal.js installation in ``reveal.js/``.
Reveal.js is not tracked in Git; the deployment workflow downloads version 5.2.1.
Viewing the built presentation needs no CDN.

For a fresh local checkout, install Reveal.js before building:

.. code-block:: sh

   mkdir -p reveal.js
   curl -fsSL https://github.com/hakimel/reveal.js/archive/refs/tags/5.2.1.tar.gz \
     | tar -xz --strip-components=1 -C reveal.js
   make serve

Deployment
----------

``.github/workflows/deploy.yml`` builds on pushes to ``main`` and can also be
started manually. It installs Pandoc and Poppler, downloads the pinned Reveal.js
release, generates SVGs from ``figures/*.pdf``, and stages the presentation under
``public/waccpd26/``.

The workflow publishes to ``marshallward/marshallward.github.io`` on branch
``master``, preserving the site's other files. Configure the repository secret
``PAGES_DEPLOY_KEY`` with a deploy key authorized to write to that repository,
as in the September developer talk. The resulting URL is
https://marshallward.org/waccpd26/.

Generated HTML, figure SVGs, the Reveal.js installation, and deployment output
are ignored. Five existing static assets under ``img/`` are retained in Git.
For now, the figure PDFs are committed inputs; regenerating those PDFs from
plotting scripts and recorded timing data is not yet part of this build.

Sources and scope
-----------------

- Manuscript: ``~/manuscripts/waccpd/waccpd26.txt``. The requested
  ``~/manuscripts/waccpd26`` directory was absent.
- Theme and template: ``~/presentations/nrl2026``, with the same short-heading,
  figure-led approach used in ``~/presentations/sewg2026``.
- Blocking traversal animation, before/after plot, and implementation details:
  ``~/presentations/mom6-gpu-2026-09-14``. The earlier blocking experiment is
  explicitly distinguished from the manuscript's current GH200 measurements.
- Paper figures: copied into ``figures/`` and converted to browser-friendly SVG
  by the Makefile. Background, gyre image, and FMS diagram come from NRL.
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
- The manuscript module figure's embedded title says “32×32 to 1024×1024”,
  while its discussion and area scale use a 64×64 reference. The figure is
  preserved unchanged; reconcile that label in the manuscript's plotting
  source before finalizing.
- Review plot readability at the actual projection size. All six module
  panels are retained to match the paper; narration focuses on two contrasts.

Reveal.js licensing is retained in ``reveal.js/LICENSE`` and included in the
deployment output.
