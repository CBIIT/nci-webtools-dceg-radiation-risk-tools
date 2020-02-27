
<!-- #INCLUDE FILE="utils.asp" -->
<!-- #INCLUDE FILE="parameters_get.asp" -->
<!-- #INCLUDE FILE="../excelfiles/JSON_2.0.4.asp"-->
<%
' This page shows the user a summary of results
Dim responseObject
Set responseObject = jsObject()
Set responseObject("messages") = jsArray()

resultstype = Trim(Request("resultstype"))

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
summ_tab = getobject_resulttable_getsafearray(ade, resultstype)

Set responseObject("summ_tab") = jsArray()
for c=1 to num
    Dim a
    Set a = jsArray()    
    a(Null) = formatnumber(summ_tab(c,1),2)
    a(Null) = formatnumber(summ_tab(c,2),2)
    a(Null) = formatnumber(summ_tab(c,3),2)
    a(Null) = formatnumber(summ_tab(c,4),2)
    a(Null) = formatnumber(summ_tab(c,5),2)
    a(Null) = formatnumber(summ_tab(c,6),2)
    a(Null) = formatnumber(summ_tab(c,7),2)
    a(Null) = formatnumber(summ_tab(c,8),2)
    a(Null) = formatnumber(summ_tab(c,9),2)
    a(Null) = formatnumber(summ_tab(c,10),2)
    a(Null) = formatnumber(summ_tab(c,11),2)
	Set responseObject("summ_tab")(Null) = a
next
'flush response object
responseObject.Flush
%>
