
NAME=spicelib
VERSION=0.0.3
INSTALLDIR=/store


MODEL_LIBDIR=model_library
MODEL_SIGDIR=model_checksums
MODEL_PATCHDIR=model_patches
TESTDIR=model_tests
TEMPDIR=unpack
SYMBOLDIR=symbol_library




all:	mkdirs download unpack create index

mkdirs:
	mkdir -p $(MODEL_SIGDIR)

download: download_nxp download_ti download_ltc download_national

unpack: unpack_nxp unpack_ti unpack_ltc unpack_national

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
	patch -d $(MODEL_LIBDIR)/nxp/bipolar/ -p1 < $(MODEL_PATCHDIR)/BCP68.patch
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
	if test ! -z `ls $(MODEL_LIBDIR)/ti/opamps | head -n 1` ; then md5sum $(MODEL_LIBDIR)/ti/opamps/* >$(MODEL_SIGDIR)/ti_opamps_lib.md5sum; else touch $(MODEL_SIGDIR)/ti_opamps_lib.md5sum; fi

test_ti_opamps:
	rm -rf $(TESTDIR)/ti/opamps
	mkdir -p $(TESTDIR)/ti/opamps
	scripts/testlibrary.py -t indexfiles/ti_opamps.index



## National semiconductor models from http://www.national.com/analog/amplifiers/spice_models
download_national: download_national_opamps
download_national_opamps: downloads/national/opamps/spice_models
downloads/national/opamps/spice_models:
	mkdir -p downloads/national/opamps
	cd downloads/national/opamps ;\
  wget http://www.national.com/analog/amplifiers/spice_models ;\
	for url in `awk -F '"' '/href.*javascript.*href.*\.MOD/ {print $$6; next} /href.*\.MOD/ {print $$4}' spice_models | sort | uniq ` ;\
	do wget $$url ;\
	done

unpack_national: unpack_national_opamps
unpack_national_opamps:
	rm -rf $(TEMPDIR)/national/opamps
	mkdir -p $(TEMPDIR)/national/opamps
	md5sum downloads/national/opamps/*.MOD > $(MODEL_SIGDIR)/national_opamps.md5sum
	cp downloads/national/opamps/*.MOD $(TEMPDIR)/national/opamps/
	md5sum $(TEMPDIR)/national/opamps/* >> $(MODEL_SIGDIR)/national_opamps.md5sum

create_national: create_national_opamps
create_national_opamps:
	rm -rf $(MODEL_LIBDIR)/national/opamps
	mkdir -p $(MODEL_LIBDIR)/national/opamps
	cp $(TEMPDIR)/national/opamps/*.MOD $(MODEL_LIBDIR)/national/opamps
	scripts/fix_name_has_slash.py $(MODEL_LIBDIR)/national/opamps/*.MOD
	#Individual file fixes
	subckt_rename() { \
		#Rename '.SUBCKT $2' to '.SUBCKT $3' in file $1 \
		TMPFILE=`mktemp -p $$(dirname $$1)` ;\
		sed "s/\.SUBCKT *$$2/.SUBCKT $$3/" $$1 > $$TMPFILE;\
		mv $$TMPFILE $$1 ; } ;\
	subckt_rename $(MODEL_LIBDIR)/national/opamps/LMH6619.MOD LMH6618 LMH6619;\
	subckt_rename $(MODEL_LIBDIR)/national/opamps/LMP7702.MOD LMP7701 LMP7702;\
	subckt_rename $(MODEL_LIBDIR)/national/opamps/LMP7704.MOD LMP7701 LMP7704;\
	subckt_rename $(MODEL_LIBDIR)/national/opamps/LMP7709.MOD LMP7707 LMP7709;\
	subckt_rename $(MODEL_LIBDIR)/national/opamps/LMP7712.MOD LMP7711 LMP7712;\
	subckt_rename $(MODEL_LIBDIR)/national/opamps/LMV552.MOD LMV551 LMV552;\
	subckt_rename $(MODEL_LIBDIR)/national/opamps/LMV652.MOD LMV651 LMV652;\
	md5sum $(MODEL_LIBDIR)/national/opamps/* >$(MODEL_SIGDIR)/national_opamps_lib.md5sum

test_national_opamps:
	rm -rf $(TESTDIR)/national/opamps
	mkdir -p $(TESTDIR)/national/opamps
	scripts/testlibrary.py -t indexfiles/national_opamps.index


## Linear Technology models from http://www.linear.com/designtools/software/spice_models.jsp
download_ltc: downloads/ltc/LTC.zip
downloads/ltc/LTC.zip:
	wget -P `dirname $@` http://ltspice.linear.com/software/LTC.zip

unpack_ltc:
	rm -rf $(TEMPDIR)/ltc
	mkdir -p $(TEMPDIR)/ltc
	md5sum downloads/ltc/LTC.zip > $(MODEL_SIGDIR)/ltc_all.md5sum
	unzip -d $(TEMPDIR)/ltc downloads/ltc/LTC.zip
	scripts/ltcsplit.py -d $(TEMPDIR)/ltc $(TEMPDIR)/ltc/LTC.lib

create_ltc: create_ltc_opamps

all_ltc_opamps=LT1001.MOD LT1002.MOD LT1006.MOD LT1007.MOD LT1008.MOD LT1010.MOD LT1012.MOD LT1013.MOD LT1014.MOD LT1022.MOD LT1024.MOD LT1028.MOD LT1037.MOD LT1055.MOD LT1056.MOD LT1057.MOD LT1058.MOD LT1077.MOD LT1078.MOD LT1079.MOD LT1097.MOD LT1101.MOD LT1102.MOD LT1112.MOD LT1113.MOD LT1114.MOD LT1115.MOD LT1122.MOD LT1124.MOD LT1125.MOD LT1126.MOD LT1127.MOD LT1128.MOD LT1167.MOD LT1168.MOD LT1169.MOD LT1178.MOD LT1179.MOD LT1187.MOD LT1189.MOD LT1190.MOD LT1191.MOD LT1192.MOD LT1193.MOD LT1194.MOD LT1195.MOD LT1203.MOD LT1204.MOD LT1205.MOD LT1206.MOD LT1207.MOD LT1208.MOD LT1209.MOD LT1210.MOD LT1211.MOD LT1212.MOD LT1213.MOD LT1214.MOD LT1215.MOD LT1216.MOD LT1217.MOD LT1218.MOD LT1218L.MOD LT1219.MOD LT1219L.MOD LT1220.MOD LT1221.MOD LT1222.MOD LT1223.MOD LT1224.MOD LT1225.MOD LT1226.MOD LT1227.MOD LT1228.MOD LT1229.MOD LT1230.MOD LT1251.MOD LT1252.MOD LT1253.MOD LT1254.MOD LT1256.MOD LT1259.MOD LT1260.MOD LT1351.MOD LT1352.MOD LT1353.MOD LT1354.MOD LT1355.MOD LT1356.MOD LT1357.MOD LT1358.MOD LT1359.MOD LT1360.MOD LT1361.MOD LT1362.MOD LT1363.MOD LT1364.MOD LT1365.MOD LT1366.MOD LT1367.MOD LT1368.MOD LT1369.MOD LT1395.MOD LT1396.MOD LT1397.MOD LT1398.MOD LT1399.MOD LT1399HV.MOD LT1413.MOD LT1457.MOD LT1462.MOD LT1463.MOD LT1464.MOD LT1465.MOD LT1466L.MOD LT1467L.MOD LT1468.MOD LT1468-2.MOD LT1469.MOD LT1469-2.MOD LT1490A.MOD LT1491A.MOD LT1492.MOD LT1493.MOD LT1494.MOD LT1495.MOD LT1496.MOD LT1497.MOD LT1498.MOD LT1499.MOD LT1630.MOD LT1631.MOD LT1632.MOD LT1633.MOD LT1635.MOD LT1636.MOD LT1637.MOD LT1638.MOD LT1639.MOD LT1672.MOD LT1673.MOD LT1674.MOD LT1675.MOD LT1675-1.MOD LT1677.MOD LT1678.MOD LT1679.MOD LT1722.MOD LT1723.MOD LT1724.MOD LT1739.MOD LT1782.MOD LT1783.MOD LT1784.MOD LT1787.MOD LT1787HV.MOD LT1789-1.MOD LT1789-10.MOD LT1792.MOD LT1793.MOD LT1794.MOD LT1795.MOD LT1797.MOD LT1800.MOD LT1801.MOD LT1802.MOD LT1803.MOD LT1804.MOD LT1805.MOD LT1806.MOD LT1807.MOD LT1809.MOD LT1810.MOD LT1812.MOD LT1813.MOD LT1813HV.MOD LT1814.MOD LT1815.MOD LT1816.MOD LT1817.MOD LT1818.MOD LT1819.MOD LT1880.MOD LT1881.MOD LT1882.MOD LT1884.MOD LT1885.MOD LT1886.MOD LT1920.MOD LT1969.MOD LT1970.MOD LT1990.MOD LT1991.MOD LT1993-10.MOD LT1993-2.MOD LT1993-4.MOD LT1994.MOD LT1995.MOD LT1996.MOD LT2078.MOD LT2079.MOD LT2178.MOD LT2179.MOD LT5514.MOD LT5524.MOD LT5554.MOD LT6000.MOD LT6001.MOD LT6002.MOD LT6003.MOD LT6004.MOD LT6005.MOD LT6010.MOD LT6011.MOD LT6012.MOD LT6013.MOD LT6014.MOD LT6100.MOD LT6106.MOD LT6107.MOD LT6200.MOD LT6200-10.MOD LT6200-5.MOD LT6201.MOD LT6202.MOD LT6203.MOD LT6204.MOD LT6205.MOD LT6206.MOD LT6207.MOD LT6210.MOD LT6211.MOD LT6220.MOD LT6221.MOD LT6222.MOD LT6230.MOD LT6230-10.MOD LT6231.MOD LT6232.MOD LT6233.MOD LT6233-10.MOD LT6234.MOD LT6235.MOD LT6300.MOD LT6301.MOD LT6402-12.MOD LT6402-20.MOD LT6402-6.MOD LT6411.MOD LT6550.MOD LT6551.MOD LT6552.MOD LT6553.MOD LT6554.MOD LT6555.MOD LT6556.MOD LT6557.MOD LT6558.MOD LT6559.MOD LT6600-10.MOD LT6600-15.MOD LT6600-2.5.MOD LT6600-20.MOD LT6600-5.MOD LT6604-10.MOD LT6604-15.MOD LT6604-2.5.MOD LT6604-5.MOD LTC1047.MOD LTC1049.MOD LTC1050.MOD LTC1051.MOD LTC1052.MOD LTC1053.MOD LTC1100.MOD LTC1150.MOD LTC1151.MOD LTC1152.MOD LTC1250.MOD LTC1541.MOD LTC1542.MOD LTC1564.MOD LTC1992.MOD LTC2050.MOD LTC2050HV.MOD LTC2051.MOD LTC2051HV.MOD LTC2052.MOD LTC2052HV.MOD LTC2053.MOD LTC2053-SYNC.MOD LTC2054.MOD LTC2054HV.MOD LTC2055.MOD LTC2055HV.MOD LTC4151.MOD LTC6078.MOD LTC6079.MOD LTC6081.MOD LTC6082.MOD LTC6084.MOD LTC6085.MOD LTC6087.MOD LTC6088.MOD LTC6101.MOD LTC6101HV.MOD LTC6102.MOD LTC6102HV.MOD LTC6103.MOD LTC6104.MOD LTC6240.MOD LTC6240HV.MOD LTC6241.MOD LTC6241HV.MOD LTC6242.MOD LTC6242HV.MOD LTC6244.MOD LTC6244HV.MOD LTC6400-14.MOD LTC6400-20.MOD LTC6400-26.MOD LTC6400-8.MOD LTC6401-14.MOD LTC6401-20.MOD .MOD LTC6401-26.MOD LTC6401-8.MOD LTC6403-1.MOD LTC6404-1.MOD LTC6404-2.MOD LTC6404-4.MOD LTC6405.MOD LTC6406.MOD LTC6410-6.MOD LTC6412.MOD LTC6416.MOD LTC6420-20.MOD LTC6421-20.MOD LTC6601-1.MOD LTC6601-2.MOD LTC6602.MOD LTC6603.MOD LTC6605-10.MOD LTC6605-14.MOD LTC6605-7.MOD LTC6800.MOD LTC6910-1.MOD LTC6910-2.MOD LTC6910-3.MOD LTC6911-1.MOD LTC6911-2.MOD LTC6912-1.MOD LTC6912-2.MOD LTC6915.MOD
create_ltc_opamps:
	rm -rf $(MODEL_LIBDIR)/ltc/opamps
	mkdir -p $(MODEL_LIBDIR)/ltc/opamps
	cd $(TEMPDIR)/ltc; cp $(all_ltc_opamps) ../../$(MODEL_LIBDIR)/ltc/opamps 2>/dev/null; true
	md5sum $(MODEL_LIBDIR)/ltc/opamps/* > $(MODEL_SIGDIR)/ltc_opamps_lib.md5sum

test_ltc_opamps:
	rm -rf $(TESTDIR)/ltc/opamps
	mkdir -p $(TESTDIR)/ltc/opamps
	scripts/testlibrary.py -t indexfiles/ltc_opamps.index

### dump all symbols to a directory. This creates a static symbol library
dump_symbols:
	rm -rf $(SYMBOLDIR)
	mkdir -p $(SYMBOLDIR)
	scripts/gedaparts -d $(SYMBOLDIR) -s ti_opamps.index
	scripts/gedaparts -d $(SYMBOLDIR) -s nxp_diodes.index
	scripts/gedaparts -d $(SYMBOLDIR) -s nxp_bipolar.index
	scripts/gedaparts -d $(SYMBOLDIR) -s ltc_opamps.index


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

#### Clean out all downloaded and generated files
clean:
	rm -rf downloads unpack model_library model_checksums
