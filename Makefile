THEME = gfdl
PYTHON = python3
ASY = asy
D2 = d2
export MPLBACKEND = Agg
FLAGS = -s -f rst -t revealjs --slide-level=2 \
        -V revealjs-url=./reveal.js -V theme=$(THEME) \
        -V slideNumber=true -V width=1280 -V height=720 \
        -V transition=slide --template=gfdl.revealjs --no-highlight

CPU_RUN = runs/c6_96pe_avx512
GPU_RUN = runs/arm_20260809
H100_RUNS = runs/h100_p1_20260725 runs/h100_p2_20260725 \
            runs/h100_p4_20260725 runs/h100_p8_20260725 runs/h100_p10_20260725
SINGLE_DEVICE_DATA = $(wildcard $(CPU_RUN)/*.out $(GPU_RUN)/*.out)
H100_DATA = $(foreach run,$(H100_RUNS),$(wildcard $(run)/*.out))
FIGURES = img/block_shapes.svg img/block_loop_title.svg img/fms_mpi.svg \
          img/dycore_and_main.svg img/module_scaling.svg \
          img/dycore_speedup.svg img/h100_module_timings.svg
STATIC_ASSETS = img/bg_gfdl.jpg img/gyre.png img/corad_blocks.svg

.PHONY: all figures serve clean
all: index.html

figures: $(FIGURES)

index.html: slides.txt Makefile gfdl.revealjs reveal.js/css/theme/gfdl.css $(FIGURES) $(STATIC_ASSETS)
	pandoc $(FLAGS) $< -o $@

reveal.js/css/theme/gfdl.css: gfdl.css
	mkdir -p $(@D)
	cp $< $@

img/block_shapes.svg: asy/block_shapes.asy Makefile | img
	$(ASY) -f svg $< -o $(basename $@)

img/block_loop_title.svg: scripts/gen_block_loop_title.py Makefile | img
	$(PYTHON) $< -o $@ --n 32 --block 8,4 --frame-ms 48

img/fms_mpi.svg: d2/fms_mpi.d2 Makefile | img
	$(D2) $< $@ --pad 2

img/dycore_and_main.svg: runs/gen_plot.py $(SINGLE_DEVICE_DATA) requirements.txt Makefile | img
	$(PYTHON) $< $(CPU_RUN) $(GPU_RUN) -o $@ \
	  -l "AMD EPYC 9654,GH200" --figsize 3.5,3.0 --dark \
	  --regions "Main loop" --with-speedup --min-config 4 --xscale-factor 4 \
	  --title "Time per step (ms) for the MOM6 timestep"

img/module_scaling.svg: runs/gen_plot.py $(SINGLE_DEVICE_DATA) requirements.txt Makefile | img
	$(PYTHON) $< $(CPU_RUN) $(GPU_RUN) -o $@ \
	  -l "AMD EPYC 9654,GH200" --figsize 7.2,3.8 --dark \
	  --min-config 4 --xscale-factor 4 \
	  --title "Time per step (ms) from 64×64 to 1024×1024"

img/dycore_speedup.svg: runs/plot_dycore_scaling.py $(H100_DATA) requirements.txt Makefile | img
	$(PYTHON) $< $(H100_RUNS) -o $@ -q speedup --configs 64,256,1024 \
	  --platform-label "1,2,4,8,10" --figsize 3.5,2.8 --dark

img/h100_module_timings.svg: runs/gen_plot.py $(H100_DATA) requirements.txt Makefile | img
	$(PYTHON) $< $(H100_RUNS) -o $@ \
	  -l "1 H100,2 H100s,4 H100s,8 H100s,10 H100s" --figsize 7.2,4.2 --dark \
	  --min-config 4 --xscale-factor 4 \
	  --title "Module time per step (ms); 1× = 64×64 cells"

img:
	mkdir -p $@

serve: all
	$(PYTHON) -m http.server 8000 --bind 127.0.0.1

clean:
	rm -f index.html $(FIGURES)
