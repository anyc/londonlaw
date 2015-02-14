# London Law documentation makefile
all: manual.pdf manual.html post-build-cleanup

manual.ps: manual.dvi
	dvips -tletterSize -Ppdf -G0 manual.dvi

manual.dvi: manual.tex
	latex manual.tex
	latex manual.tex

manual.pdf: manual.ps
	ps2pdf13 manual.ps

manual.html: manual.tex
	hevea manual.tex

post-build-cleanup: manual.pdf manual.html
	rm -f *.aux *.log *.dvi *.ps

clean:
	rm -f *.aux *.log *.dvi *.ps *.pdf *.html




# arch-tag: DO_NOT_CHANGE_7fb16864-342a-429b-83ed-6a12821406fe 
