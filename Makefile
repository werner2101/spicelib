

MODEL_LIBDIR="model_library"
MODEL_SIGDIR="model_signatures"
TEMPDIR="tmp"



all:
	echo "target all not defined"

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

unpack_nxp: unpack_nxp_bipolar

unpack_nxp_bipolar: downloads/nxp/SST.zip
	rm -rf $(TEMPDIR)/nxp/bipolar
	mkdir -p $(TEMPDIR)/nxp/bipolar
	md5sum downloads/nxp/SST.zip > $(MODEL_SIGDIR)/nxp_bipolar.md5sum
	- unzip -d $(TEMPDIR)/nxp/bipolar downloads/nxp/SST.zip
	md5sum $(TEMPDIR)/nxp/bipolar/* >>$(MODEL_SIGDIR)/nxp_bipolar.md5sum

create_nxp_bipolar:
	rm -rf $(MODEL_LIBDIR)/nxp/bipolar
	mkdir -p $(MODEL_LIBDIR)/nxp/bipolar
	scripts/fix_trailing_newline.py $(TEMPDIR)/nxp/bipolar/*
	cp $(TEMPDIR)/nxp/bipolar/* $(MODEL_LIBDIR)/nxp/bipolar
	md5sum $(MODEL_LIBDIR)/nxp/bipolar/* >$(MODEL_SIGDIR)/nxp_bipolar_lib.md5sum
