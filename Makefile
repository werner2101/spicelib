
NAME=spicelib
VERSION=0.0.2
INSTALLDIR=/store


MODEL_LIBDIR=model_library
MODEL_SIGDIR=model_checksums
MODEL_PATCHDIR=model_patches
TESTDIR=model_tests
TEMPDIR=unpack




all:	mkdirs download unpack create index

mkdirs:
	mkdir -p $(MODEL_SIGDIR)

download: download_nxp download_ti

unpack: unpack_nxp unpack_ti

create: create_nxp create_ti

index: 
	scripts/testlibrary.py -i indexfiles/*index

test:
	scripts/testlibrary.py -t indexfiles/*index


# nxp models downloaded from URL:
# http://www.nxp.com/models/index.html  --> Spice and S-parameters
download_nxp:
	rm -rf downloads/nxp
	mkdir -p downloads/nxp
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/fet.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/power.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/wideband.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/SBD.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/SST.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/diodes.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/mmics.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/varicap.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/basestations.zip
	wget -P downloads/nxp http://www.nxp.com/models/spicespar/zip/complex_discretes.zip


unpack_nxp: unpack_nxp_bipolar unpack_nxp_diodes

create_nxp: create_nxp_diodes create_nxp_bipolar

unpack_nxp_bipolar: downloads/nxp/SST.zip
	rm -rf $(TEMPDIR)/nxp/bipolar
	mkdir -p $(TEMPDIR)/nxp/bipolar
	md5sum downloads/nxp/SST.zip > $(MODEL_SIGDIR)/nxp_bipolar.md5sum
	- unzip -d $(TEMPDIR)/nxp/bipolar downloads/nxp/SST.zip
	md5sum $(TEMPDIR)/nxp/bipolar/* >>$(MODEL_SIGDIR)/nxp_bipolar.md5sum

unpack_nxp_diodes: downloads/nxp/diodes.zip
	rm -rf $(TEMPDIR)/nxp/diodes
	mkdir -p $(TEMPDIR)/nxp/diodes
	md5sum downloads/nxp/diodes.zip > $(MODEL_SIGDIR)/nxp_diodes.md5sum
	- unzip -d $(TEMPDIR)/nxp/diodes downloads/nxp/diodes.zip
	md5sum $(TEMPDIR)/nxp/diodes/* >>$(MODEL_SIGDIR)/nxp_diodes.md5sum

create_nxp_bipolar:
	rm -rf $(MODEL_LIBDIR)/nxp/bipolar
	mkdir -p $(MODEL_LIBDIR)/nxp/bipolar
	cp $(TEMPDIR)/nxp/bipolar/* $(MODEL_LIBDIR)/nxp/bipolar
	scripts/fix_trailing_newline.py $(MODEL_LIBDIR)/nxp/bipolar/*
	scripts/replace_string.py BC327-25 BC327_25 $(MODEL_LIBDIR)/nxp/bipolar/BC327-25.prm
	scripts/replace_string.py BC327-40 BC327_40 $(MODEL_LIBDIR)/nxp/bipolar/BC327-40.prm
	scripts/replace_string.py QBC337-16 QBC337_16 $(MODEL_LIBDIR)/nxp/bipolar/BC337-16.prm
	scripts/replace_string.py QBC337-25 QBC337_25 $(MODEL_LIBDIR)/nxp/bipolar/BC337-25.prm
	scripts/replace_string.py QBC337-40 QBC337_40 $(MODEL_LIBDIR)/nxp/bipolar/BC337-40.prm
	scripts/replace_string.py QBC807-25 QBC807_25 $(MODEL_LIBDIR)/nxp/bipolar/BC807-25.prm
	scripts/replace_string.py QBC807-25W QBC807_25W $(MODEL_LIBDIR)/nxp/bipolar/BC807-25W.prm
	scripts/replace_string.py QBC807-40 QBC807_40 $(MODEL_LIBDIR)/nxp/bipolar/BC807-40.prm
	scripts/replace_string.py QBC807-40W QBC807_40W $(MODEL_LIBDIR)/nxp/bipolar/BC807-40W.prm
	scripts/replace_string.py QBC817-16 QBC817_16 $(MODEL_LIBDIR)/nxp/bipolar/BC817-16.prm
	scripts/replace_string.py QBC817-16W QBC817_16W $(MODEL_LIBDIR)/nxp/bipolar/BC817-16W.prm
	scripts/replace_string.py QBC817-25 QBC817_25 $(MODEL_LIBDIR)/nxp/bipolar/BC817-25.prm
	scripts/replace_string.py QBC817-25W QBC817_25W $(MODEL_LIBDIR)/nxp/bipolar/BC817-25W.prm
	scripts/replace_string.py QBC817-40 QBC817_40 $(MODEL_LIBDIR)/nxp/bipolar/BC817-40.prm
	scripts/replace_string.py QBC817-40W QBC817_40W $(MODEL_LIBDIR)/nxp/bipolar/BC817-40W.prm
	scripts/replace_string.py QBCP54-16 QBCP54_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP54-16.prm
	scripts/replace_string.py QBCP55-16 QBCP55_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP55-16.prm
	scripts/replace_string.py QBCP56-16 QBCP56_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP56-16.prm
	md5sum $(MODEL_LIBDIR)/nxp/bipolar/* >$(MODEL_SIGDIR)/nxp_bipolar_lib.md5sum

create_nxp_diodes:
	rm -rf $(MODEL_LIBDIR)/nxp/diodes
	mkdir -p $(MODEL_LIBDIR)/nxp/diodes
	cp $(TEMPDIR)/nxp/diodes/* $(MODEL_LIBDIR)/nxp/diodes
	scripts/fix_trailing_newline.py $(MODEL_LIBDIR)/nxp/diodes/*
	scripts/replace_string.py BZX384-B BZX384B $(MODEL_LIBDIR)/nxp/diodes/BZX384-B*.prm
	scripts/replace_string.py BZX585-B BZX585B $(MODEL_LIBDIR)/nxp/diodes/BZX585-B*.prm
	scripts/replace_string.py BZX884-B BZX884B $(MODEL_LIBDIR)/nxp/diodes/BZX884-B*.prm
	md5sum $(MODEL_LIBDIR)/nxp/diodes/* >$(MODEL_SIGDIR)/nxp_diodes_lib.md5sum

test_nxp_bipolar:
	rm -rf $(TESTDIR)/nxp/bipolar
	mkdir -p $(TESTDIR)/nxp/bipolar
	scripts/testlibrary.py -t indexfiles/nxp_bipolar.index

test_nxp_diodes:
	rm -rf $(TESTDIR)/nxp/diodes
	mkdir -p $(TESTDIR)/nxp/diodes
	scripts/testlibrary.py -t indexfiles/nxp_diodes.index


## texas instruments models

create_ti: create_ti_opamps

download_ti:
	rm -rf downloads/ti
	mkdir -p downloads/ti
	wget -P downloads/ti http://focus.ti.com/packaged_lits/pspice_files/ti_pspice_models.zip
	wget -P downloads/ti http://focus.ti.com/packaged_lits/pspice_files/ti_pspice_models_index.txt

unpack_ti:
	rm -rf $(TEMPDIR)/ti
	mkdir -p $(TEMPDIR)/ti
	md5sum downloads/ti/ti_pspice_models.zip > $(MODEL_SIGDIR)/ti_all.md5sum
	md5sum downloads/ti/ti_pspice_models_index.txt >> $(MODEL_SIGDIR)/ti_all.md5sum
	unzip -d $(TEMPDIR)/ti downloads/ti/ti_pspice_models.zip
	find $(TEMPDIR)/ti/ -type f -exec md5sum {} \; >xxx.txt
	cat xxx.txt | sort -k 2 >>$(MODEL_SIGDIR)/ti_all.md5sum
	# unzip all archives that are inside the above zip and remove the zips
	find $(TEMPDIR)/ti/ -name "*zip" -exec unzip -d {}_d {} \;

create_ti_opamps:
	rm -rf $(MODEL_LIBDIR)/ti/opamps
	mkdir -p $(MODEL_LIBDIR)/ti/opamps
	# copy models, don't copy TINA models and test circuits, don't copy PSpice libs and schematics
	find $(TEMPDIR)/ti/pspice_models/opa* -type f -name "*mod" -exec cp {} $(MODEL_LIBDIR)/ti/opamps \;
	find $(TEMPDIR)/ti/pspice_models/opa* -type f -name "*MOD" -exec cp {} $(MODEL_LIBDIR)/ti/opamps \;
	find $(TEMPDIR)/ti/pspice_models/opa* -type f -name "*txt" -exec cp {} $(MODEL_LIBDIR)/ti/opamps \;
	find $(TEMPDIR)/ti/pspice_models/opa* -type f -name "*sub" -exec cp {} $(MODEL_LIBDIR)/ti/opamps \;
	# remove the accidently copied Readme and disclaimer file
	rm $(MODEL_LIBDIR)/ti/opamps/Readme.txt $(MODEL_LIBDIR)/ti/opamps/disclaimer.txt
	md5sum $(MODEL_LIBDIR)/ti/opamps/* >$(MODEL_SIGDIR)/ti_opamps_lib.md5sum

test_ti_opamps:
	rm -rf $(TESTDIR)/ti/opamps
	mkdir -p $(TESTDIR)/ti/opamps
	scripts/testlibrary.py -t indexfiles/ti_opamps.index



#### install all models to an extra directory
#### this installation should be used by the users

install:
	rm -rf $(INSTALLDIR)/$(NAME)
	mkdir -p $(INSTALLDIR)/$(NAME)
	mkdir -p $(INSTALLDIR)/$(NAME)/scripts
	cp -a scripts/gedaparts $(INSTALLDIR)/$(NAME)/scripts
	cp -a indexfiles $(INSTALLDIR)/$(NAME)
	cp -a model_library $(INSTALLDIR)/$(NAME)
	cp -a model_tests $(INSTALLDIR)/$(NAME)
	cp -a symbol_templates $(INSTALLDIR)/$(NAME)
	cp -a doc $(INSTALLDIR)/$(NAME)
	cp -a testcircuits $(INSTALLDIR)/$(NAME)

