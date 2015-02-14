
# builds a fresh template file
template:
	cd .. && xgettext -cTRANSLATORS -Lpython -o po/londonlaw.pot london-admin london-client london-server common/*.py server/*.py guiclient/*.py

# compiles all .po files to binary .mo
mo:
	find . -name "*.po" -print -execdir msgfmt -o londonlaw.mo {} \;


# arch-tag: DO_NOT_CHANGE_c66eeffc-53c4-4e51-965e-7a2d56aebcf6 
