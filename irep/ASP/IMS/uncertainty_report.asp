
<!-- #INCLUDE FILE="utils.asp" -->
<!-- #INCLUDE FILE="parameters_get.asp" -->
<!-- #INCLUDE FILE="../excelfiles/JSON_2.0.4.asp"-->

<%
' This page shows the user two uncertainty analyses
Dim responseObject
Set responseObject = jsObject()
Set responseObject("messages") = jsArray()

set ade = CreateObject("ADE" & ade_version & ".CAEngine")
model = OpenModel(ade, Server.MapPath("../irep.ana"))

redim d_tab(7,200), r_tab(6,100), ud_tab(4)
for i=1 to num
	d_tab(1,i) = dose_table(1,i)
	d_tab(2,i) = "'"+dose_table(2,i)+"'"
	d_tab(3,i) = dose_table(3,i)
	d_tab(4,i) = dose_table(4,i)
	d_tab(5,i) = dose_table(5,i)
	d_tab(6,i) = "'"+dose_table(6,i)+"'"
	d_tab(7,i) = "'"+dose_table(7,i)+"'"
next
' fill out defaults
if num<200 then
	for i=num+1 to 200
		d_tab(1,i) = 1970
		d_tab(2,i) = "'Lognormal'"
		d_tab(3,i) = 3
		d_tab(4,i) = 1.3
		d_tab(5,i) = 0
		d_tab(6,i) = "'a'"
		d_tab(7,i) = "'e1'"
	next
end if
for i=1 to numradon
	r_tab(1,i) = radon_table(1,i)
	r_tab(2,i) = "'"+radon_table(2,i)+"'"
	r_tab(3,i) = radon_table(3,i)
	r_tab(4,i) = radon_table(4,i)
	r_tab(5,i) = radon_table(5,i)
	r_tab(6,i) = "'"+radon_table(6,i)+"'"
next
' fill out defaults
if numradon<100 then
	for i=numradon+1 to 100
		r_tab(1,i) = 1970
		r_tab(2,i) = "'Lognormal'"
		r_tab(3,i) = 3
		r_tab(4,i) = 1.3
		r_tab(5,i) = 0
		r_tab(6,i) = "'annual'"
	next
end if
ud_tab(1) = "'"+udud_table(1)+"'"
ud_tab(2) = udud_table(2)
ud_tab(3) = udud_table(3)
ud_tab(4) = udud_table(4)

can = "'"+cancer_choice+"'"
gen = "'"+gen_choice+"'"
smk = "'"+smoking_history+"'"
eth = "'"+ethnic+"'"
expsrc = "'"+exposure_source+"'"

' the following are the ActiveX calls to the Analytica application
call setobjectattribute(ade, "By", "definition", by)
call setobjectattribute(ade, "Number_of_exposures", "definition", num)
' the following is evaluated so that the variably-sized arrays are all available for later use
per_ind = getobject_resulttable_getsafearray(ade, "exp_period_index")
call setobjectattribute(ade, "cancer_choice", "definition", can)
call setobjectattribute(ade, "ethnic_origin", "definition", eth)
call setobjectattribute(ade, "dod", "definition", dod)
call getobject_deftable_putsafearray(ade, "dose_table_in", d_tab)
call setobjectattribute(ade, "gen_choice", "definition", gen)
call setobjectattribute(ade, "smoking_history", "definition", smk)
call setobjectattribute(ade, "exposure_source", "definition", expsrc)
call setobjectattribute(ade, "samplesize", "definition", sample_size)
call setobjectattribute(ade, "randomseed", "definition", randomseed)
call setobjectattribute(ade, "No_of_exposure_radon", "definition", numradon)
call getobject_deftable_putsafearray(ade, "wlm_table_in", r_tab)
call getobject_deftable_putsafearray(ade, "udud_inputs", ud_tab)
summ_tab = getobject_resulttable_getsafearray(ade, "summary_table")
sumidx_tab = getobject_resulttable_getsafearray(ade, "summary_index")

'Retrieve results
unc_pc_tab = getobject_resulttable_getsafearray(ade, "level_1")
unc_pc_idx_tab = getobject_resulttable_getsafearray(ade, "level_1_index")
' check to see if uncertainty values make sense.  If sum of squares is not
' a number, then values must be set to zero to avoid unusual results
sumofsq2 = getobject_result(ade, "sum_of_squares2")
if Not(IsNumeric(sumofsq2)) then
	for i=1 to 3
		unc_pc_tab(i)=0
	next
end if
Set responseObject("unc_pc_tab") = jsArray()	
for i=1 to 3
	Set responseObject("unc_pc_tab")(Null) = jsObject()
	responseObject("unc_pc_tab")(Null)("unc_pc_tab") = formatpercent(unc_pc_tab(i))
	responseObject("unc_pc_tab")(Null)("unc_pc_idx_tab") = unc_pc_idx_tab(i)
next

' retrieve the following set when exposure_source is anything but "Radon"
if exposure_source <> "Radon" then
	abs_dose_tab = getobject_resulttable_getsafearray(ade, "absorbed_dose_out")
	rbe_tab = getobject_resulttable_getsafearray(ade, "applicable_rbe_out")
	err_tab = getobject_resulttable_getsafearray(ade, "err_out")
	Set responseObject("abs_dose_tab") = jsArray()	
	Set responseObject("rbe_tab") = jsArray()	
	Set responseObject("err_tab") = jsArray()	
	for i=1 to num
    	Set responseObject("abs_dose_tab")(Null) = jsArray()  	
    	Set responseObject("rbe_tab")(Null) = jsArray()  	
    	Set responseObject("err_tab")(Null) = jsArray()
    	for c=1 to 3  	
    		responseObject("abs_dose_tab")(Null)(Null) = formatnumber(abs_dose_tab(i,c),2)
    		responseObject("rbe_tab")(Null)(Null) = formatnumber(rbe_tab(c,i),2)
    		responseObject("err_tab")(Null)(Null) = formatnumber(err_tab(c,i),4)
		next	
	next
	
	unc_shr_tab = getobject_resulttable_getsafearray(ade, "dosevserr")
	unc_shr_idx_tab = getobject_resulttable_getsafearray(ade, "dose_err_index")
	' check to see if uncertainty values make sense.  If sum of squares is not
	' a number, then values must be set to zero to avoid unusual results
	sumofsq = getobject_result(ade, "sum_of_squares")
	if Not(IsNumeric(sumofsq)) then
		for i=1 to 3
			unc_shr_tab(i)=0
		next
	end if
	Set responseObject("unc_shr_tab") = jsArray()	
	for i=1 to 3
		Set responseObject("unc_shr_tab")(Null) = jsObject()
		responseObject("unc_shr_tab")(Null)("unc_shr_tab") = formatpercent(unc_shr_tab(i))
		responseObject("unc_shr_tab")(Null)("unc_shr_idx_tab") = unc_shr_idx_tab(i)
	next	

	unc_errsv_tab = getobject_resulttable_getsafearray(ade, "components_err_sv")
	unc_errsv_idx_tab = getobject_resulttable_getsafearray(ade, "err_comp_index")
	' check to see if uncertainty values make sense.  If sum of squares is not
	' a number, then values must be set to zero to avoid unusual results
	sumofsq1 = getobject_result(ade, "sum_of_squares1")
	if Not(IsNumeric(sumofsq1)) then
		for i=1 to 5
			unc_errsv_tab(i)=0
		next
	end if
	Set responseObject("unc_errsv_tab") = jsArray()	
	for i=1 to 5
		Set responseObject("unc_errsv_tab")(Null) = jsObject()
		responseObject("unc_errsv_tab")(Null)("unc_errsv_tab") = formatpercent(unc_errsv_tab(i))
		responseObject("unc_errsv_tab")(Null)("unc_errsv_idx_tab") = unc_errsv_idx_tab(i)
	next
end if

' retrieve the following set when exposure_source is anything but "Other Sources"
if exposure_source <> "Other Sources" then
	wlm_latency_tab = getobject_resulttable_getsafearray(ade, "wlm_latency_out")
	Set responseObject("wlm_latency_tab") = jsArray()	
	for i=1 to numradon
    	Set responseObject("wlm_latency_tab")(Null) = jsArray()
    	for c=2 to 4  	
    		responseObject("wlm_latency_tab")(Null)(Null) = formatnumber(wlm_latency_tab(c,i),2)
		next	
	next
	err_radon_tab = getobject_resulttable_getsafearray(ade, "err_radon_out")
	Set responseObject("err_radon_tab") = jsArray()	
	for i=2 to 4
		responseObject("err_radon_tab")(Null) = formatnumber(err_radon_tab(i),2)
	next
	
	unc_rad_tab = getobject_resulttable_getsafearray(ade, "level_2r")
	unc_rad_idx_tab = getobject_resulttable_getsafearray(ade, "level_2r_index")
	' check to see if uncertainty values make sense.  If sum of squares is not
	' a number, then values must be set to zero to avoid unusual results
	sumofsq3 = getobject_result(ade, "sum_of_squares3")
	if Not(IsNumeric(sumofsq3)) then
		for i=1 to 3
			unc_rad_tab(i)=0
		next
	end if
	Set responseObject("unc_rad_tab") = jsArray()	
	for i=1 to 3
		Set responseObject("unc_rad_tab")(Null) = jsObject()
		responseObject("unc_rad_tab")(Null)("unc_rad_tab") = formatpercent(unc_rad_tab(i))
		responseObject("unc_rad_tab")(Null)("unc_rad_idx_tab") = unc_rad_idx_tab(i)
	next
end if
'flush response object
responseObject.Flush
%>