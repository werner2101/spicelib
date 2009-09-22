
NAME=spicelib
VERSION=0.0.3
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

release:
	git archive --format=tar --prefix=$(NAME)-$(VERSION)/ $(VERSION) |gzip >$(NAME)-$(VERSION).tar.gz

# nxp models downloaded from URL:
# http://www.nxp.com/models/index.html  --> Spice and S-parameters
NXP_FILES=fet.zip power.zip wideband.zip SBD.zip SST.zip diodes.zip mmics.zip varicap.zip basestations.zip complex_discretes.zip
NXP_DOWNLOADS=$(foreach file,$(NXP_FILES), downloads/nxp/$(file))
download_nxp: $(NXP_DOWNLOADS)
$(NXP_DOWNLOADS):
	wget -P `dirname $@` http://www.nxp.com/models/spicespar/zip/`basename $@`

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
	## individual file fixes
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
	scripts/replace_string.py QBCP52-16 QBCP52_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP52-16.prm
	scripts/replace_string.py QBCP53-16 QBCP53_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP53-16.prm
	scripts/replace_string.py QBCP54-16 QBCP54_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP54-16.prm
	scripts/replace_string.py QBCP55-16 QBCP55_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP55-16.prm
	scripts/replace_string.py QBCP56-16 QBCP56_16 $(MODEL_LIBDIR)/nxp/bipolar/BCP56-16.prm
	scripts/replace_string.py "QTR1" "TR1" $(MODEL_LIBDIR)/nxp/bipolar/2PB709ART.prm
	scripts/replace_string.py "1 BCX56 NPN" "1 BCX56" $(MODEL_LIBDIR)/nxp/bipolar/BCX56.prm
	scripts/replace_string.py "*.SUBCKT" ".SUBCKT" $(MODEL_LIBDIR)/nxp/bipolar/PBSS8110AS.prm
	scripts/replace_string.py "LE 3 333" "LE 3 33" $(MODEL_LIBDIR)/nxp/bipolar/BCV47.prm
	scripts/replace_string.py "1 PBSS4540X" "1 PB4540X" $(MODEL_LIBDIR)/nxp/bipolar/PBSS4540X.prm
	scripts/replace_string.py "*.MODEL" ".MODEL" $(MODEL_LIBDIR)/nxp/bipolar/PBSS5160K.prm
	scripts/replace_string.py "*.MODEL" ".MODEL" $(MODEL_LIBDIR)/nxp/bipolar/PBSS5160U.prm
	scripts/replace_string.py "TC2233Y" "TC223Y" $(MODEL_LIBDIR)/nxp/bipolar/PDTC123YT.prm
	scripts/replace_string.py "LE 3 333" "LE 3 33" $(MODEL_LIBDIR)/nxp/bipolar/PXTA14.prm
	## general newline fix for the End of the file
	scripts/fix_trailing_newline.py $(MODEL_LIBDIR)/nxp/bipolar/*
	## general fix for wrong .ENDS statements
	scripts/fix_ends_without_subcircuit.py $(MODEL_LIBDIR)/nxp/bipolar/*

	## md5sums for the created models
	md5sum $(MODEL_LIBDIR)/nxp/bipolar/* >$(MODEL_SIGDIR)/nxp_bipolar_lib.md5sum

create_nxp_diodes:
	rm -rf $(MODEL_LIBDIR)/nxp/diodes
	mkdir -p $(MODEL_LIBDIR)/nxp/diodes
	cp $(TEMPDIR)/nxp/diodes/* $(MODEL_LIBDIR)/nxp/diodes
	## remove duplicate model files
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/BZX384-B*prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/BZB84-B*prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/BZV49-C12.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PDZ4V7B.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU2.4*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU2.7*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU3.0*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU3.3*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU3.6*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU3.9*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU4.3*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU4.7*.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU5.1B*A.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU5.1DB2.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU5.6B*A.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU5.6DB2.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU6.2B*A.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU6.2DB2.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU6.8B*A.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU6.8DB2.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU7.5B*A.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU7.5DB2.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU8.2B*A.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU8.2DB2.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU9.1B*A.prm
	rm -rf $(MODEL_LIBDIR)/nxp/diodes/PZU9.1DB2.prm

	## individual file fixes
	scripts/replace_string.py "*.MODEL" ".MODEL" $(MODEL_LIBDIR)/nxp/diodes/PESD3V3L1BA.prm
	scripts/replace_string.py ".END" ".ENDS" $(MODEL_LIBDIR)/nxp/diodes/1N4148.prm
	scripts/replace_string.py ".MODEL BZX100A" ".MODEL BZX100A D" $(MODEL_LIBDIR)/nxp/diodes/BZX100A.prm



	## general newline fix for the End of the file
	scripts/fix_trailing_newline.py $(MODEL_LIBDIR)/nxp/diodes/*
	## general fix for wrong .ENDS statements
	scripts/fix_ends_without_subcircuit.py $(MODEL_LIBDIR)/nxp/diodes/*

	## md5sums for the created models
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

download_ti: downloads/ti/ti_pspice_models.zip downloads/ti/ti_pspice_models_index.txt

downloads/ti/ti_pspice_models.zip:
	wget -P `dirname $@` http://focus.ti.com/packaged_lits/pspice_files/ti_pspice_models.zip

downloads/ti/ti_pspice_models_index.txt:
	wget -P `dirname $@` http://focus.ti.com/packaged_lits/pspice_files/ti_pspice_models_index.txt

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
	rm -f $(MODEL_LIBDIR)/ti/opamps/Readme.txt $(MODEL_LIBDIR)/ti/opamps/disclaimer.txt
	if test ! -z `ls $(MODEL_LIBDIR)/ti/opamps` ; then md5sum $(MODEL_LIBDIR)/ti/opamps/* >$(MODEL_SIGDIR)/ti_opamps_lib.md5sum; fi

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

