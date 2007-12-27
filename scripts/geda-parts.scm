;                                                         -*-Scheme-*-
; add a library with the command backend
; Syntax:
; (component-library-command "[listcommand]" "[getcommand]" "[name]")
;
(component-library-command 
 "/home/werner/oss/geda/spicelib/scripts/gedaparts -l nxp_bipolar.index" 
 "/home/werner/oss/geda/spicelib/scripts/gedaparts -p nxp_bipolar.index" 
 "NXP bipolar transistors")
(component-library-command 
 "/home/werner/oss/geda/spicelib/scripts/gedaparts -l nxp_diodes.index" 
 "/home/werner/oss/geda/spicelib/scripts/gedaparts -p nxp_diodes.index" 
 "NXP diodes")
(component-library-command 
 "/home/werner/oss/geda/spicelib/scripts/gedaparts -l ti_opamps.index" 
 "/home/werner/oss/geda/spicelib/scripts/gedaparts -p ti_opamps.index" 
 "TI opamps")

;(component-library-command 
; "/store/spicelib/scripts/gedaparts nxp_bipolar.index" 
; "/store/spicelib/scripts/gedaparts nxp_bipolar.index" 
; "1_NXP bipolar transistors")
;(component-library-command 
; "/store/spicelib/scripts/gedaparts nxp_diodes.index" 
; "/store/spicelib/scripts/gedaparts nxp_diodes.index" 
; "1_NXP diodes")
;(component-library-command 
; "/store/spicelib/scripts/gedaparts ti_opamps.index" 
; "/store/spicelib/scripts/gedaparts ti_opamps.index" 
; "1_TI opamps")
