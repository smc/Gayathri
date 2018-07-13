#!/usr/bin/make -f

NAME=BD
FONTS=Regular Bold Thin
INSTALLPATH=/usr/share/fonts/opentype/malayalam
PY=python3
version=`cat VERSION`
TOOLDIR=tools
SRCDIR=sources
webfontscript=$(TOOLDIR)/webfonts.py
designspace=$(SRCDIR)/BDProject.designspace
tests=tests/tests.txt
BLDDIR=build
default: otf
all: clean lint otf ttf webfonts test
OTF=$(FONTS:%=$(BLDDIR)/$(NAME)-%.otf)
TTF=$(FONTS:%=$(BLDDIR)/$(NAME)-%.ttf)
WOFF2=$(FONTS:%=$(BLDDIR)/$(NAME)-%.woff2)
PDF=$(FONTS:%=$(BLDDIR)/$(NAME)-%.pdf)

$(BLDDIR)/%.otf: $(SRCDIR)/%.ufo
	@echo "  BUILD    $(@F)"
	@fontmake -S --verbose=WARNING -o otf --output-dir $(BLDDIR) -u $<

$(BLDDIR)/%.ttf: $(SRCDIR)/%.ufo
	@echo "  BUILD    $(@F)"
	@fontmake --verbose=WARNING -o ttf --output-dir $(BLDDIR) -u $<

$(BLDDIR)/%.woff2: $(BLDDIR)/%.otf
	@echo "WEBFONT    $(@F)"
	@$(PY) $(webfontscript) -i $<

$(BLDDIR)/%.pdf: $(BLDDIR)/%.otf $(tests)
	@echo "   TEST    $(@F)"
	@hb-view $< --font-size 14 --margin 100 --line-space 1.5 \
		--foreground=333333 --text-file $(tests) \
		--output-file $(BLDDIR)/$(@F);

ttf: $(TTF)
otf: $(OTF)
webfonts: $(WOFF2)
lint: ufolint
ufo: glyphs ufonormalizer lint

ufolint: $(SRCDIR)/*.ufo
	$@ $^
ufonormalizer: $(SRCDIR)/*.ufo
	@for variant in $^;do \
		ufonormalizer -m $$variant;\
	done;
install: otf
	@mkdir -p ${DESTDIR}${INSTALLPATH}
	install -D -m 0644 $(BLDDIR)/*.otf ${DESTDIR}${INSTALLPATH}/

test: otf $(PDF)

glyphs:
	@for variant in $(FONTS);do \
		for svg in `ls sources/design/$$variant/A*.svg`;do \
			$(PY) tools/import-svg-to-ufo.py -c "sources/design/config/$$variant-svg-glif-mapping.yaml" $$svg;\
		done;\
	done;

clean:
	@rm -rf $(BLDDIR)
