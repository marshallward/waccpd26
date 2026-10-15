THEME = gfdl
FLAGS = -s -f rst -t revealjs --slide-level=2 \
        -V revealjs-url=./reveal.js -V theme=$(THEME) \
        -V slideNumber=true -V width=1280 -V height=720 \
        -V transition=none --template=gfdl.revealjs --no-highlight

FIGURES = $(patsubst figures/%.pdf,img/%.svg,$(wildcard figures/*.pdf))

.PHONY: all serve clean
all: index.html

index.html: slides.txt gfdl.revealjs reveal.js/css/theme/gfdl.css $(FIGURES)
	pandoc $(FLAGS) $< -o $@

reveal.js/css/theme/gfdl.css: gfdl.css
	mkdir -p $(@D)
	cp $< $@

img/%.svg: figures/%.pdf
	pdftocairo -svg $< $@

serve: all
	python3 -m http.server 8000 --bind 127.0.0.1

clean:
	rm -f index.html
