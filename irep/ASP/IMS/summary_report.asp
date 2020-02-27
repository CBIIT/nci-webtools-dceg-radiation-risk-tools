<!-- #INCLUDE FILE="utils.asp" -->
<!-- #INCLUDE FILE="parameters_get.asp" -->
<!-- #INCLUDE FILE="../excelfiles/JSON_2.0.4.asp"-->
<%
' This page shows the user a summary of results
Dim responseObject
Set responseObject = jsObject()
Set responseObject("messages") = jsArray()

set ade = CreateObject("ADE" & ade_version & ".CAEngine")
model = OpenModel(ade, Server.MapPath("../irep.ana"))

redim d_tab(199,6), r_tab(99,5), ud_tab(4)
for i=0 to num-1
  d_tab(i,0) = dose_table(1,i+1)
  d_tab(i,1) = "'"+dose_table(2,i+1)+"'"
  d_tab(i,2) = dose_table(3,i+1)
  d_tab(i,3) = getvalueOrDefault(dose_table(4,i+1),0)
  d_tab(i,4) = getvalueOrDefault(dose_table(5,i+1),0)
  d_tab(i,5) = "'"+dose_table(6,i+1)+"'"
  d_tab(i,6) = "'"+dose_table(7,i+1)+"'"
next
' fill out defaults
if num<199 then
  for i=num to 199
    d_tab(i,0) = 1970
    d_tab(i,1) = "'Lognormal'"
    d_tab(i,2) = 3
    d_tab(i,3) = 1.3
    d_tab(i,4) = 0
    d_tab(i,5) = "'a'"
    d_tab(i,6) = "'e1'"
  next
end if
for i=0 to numradon-1
  r_tab(i,0) = radon_table(1,i+1)
  r_tab(i,1) = "'"+radon_table(2,i+1)+"'"
  r_tab(i,2) = radon_table(3,i+1)
  r_tab(i,3) = getvalueOrDefault(radon_table(4,i+1),0)
  r_tab(i,4) = getvalueOrDefault(radon_table(5,i+1),0)
  r_tab(i,5) = "'"+radon_table(6,i+1)+"'"
next
' fill out defaults
if numradon<99 then
  for i=numradon to 99
    r_tab(i,0) = 1970
    r_tab(i,1) = "'Lognormal'"
    r_tab(i,2) = 3
    r_tab(i,3) = 1.3
    r_tab(i,4) = 0
    r_tab(i,5) = "'annual'"
  next
end if
ud_tab(1) = "'"+udud_table(1)+"'"
ud_tab(2) = udud_table(2)
ud_tab(3) = getvalueOrDefault(udud_table(3),0)
ud_tab(4) = getvalueOrDefault(udud_table(4),0)

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

Set responseObject("summ_tab") = jsArray()
responseObject("summ_tab")(Null) = formatnumber(summ_tab(11),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(12),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(13),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(14),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(15),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(16),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(17),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(18),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(19),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(20),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(21),3)
responseObject("summ_tab")(Null) = formatnumber(summ_tab(22),3)
Set responseObject("sumidx_tab") = jsArray()
responseObject("sumidx_tab")(Null) = sumidx_tab(11)
responseObject("sumidx_tab")(Null) = sumidx_tab(12)
responseObject("sumidx_tab")(Null) = sumidx_tab(13)
responseObject("sumidx_tab")(Null) = sumidx_tab(14)
responseObject("sumidx_tab")(Null) = sumidx_tab(15)
responseObject("sumidx_tab")(Null) = sumidx_tab(16)
responseObject("sumidx_tab")(Null) = sumidx_tab(17)
responseObject("sumidx_tab")(Null) = sumidx_tab(18)
responseObject("sumidx_tab")(Null) = sumidx_tab(19)
responseObject("sumidx_tab")(Null) = sumidx_tab(20)
responseObject("sumidx_tab")(Null) = sumidx_tab(21)

'flush response object
responseObject.Flush
%>