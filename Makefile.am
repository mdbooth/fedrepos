dist_bin_SCRIPTS = fedrepos
dist_man1_MANS = fedrepos.1

fedrepos.1: fedrepos.1.txt
	$(A2X) --doctype manpage --format manpage $<

EXTRA_DIST = fedrepos.1.txt

CLEANFILES = $(dist_man1_MANS)
