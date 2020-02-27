<!-- #INCLUDE FILE="utils.asp" -->
<!-- #INCLUDE FILE="parameters_get.asp" -->
<!-- #INCLUDE FILE="../excelfiles/JSON_2.0.4.asp"-->
<%
' timeout this script after so many seconds
server.ScriptTimeout=summary_rpt_timeout

' This page shows the user a summary of results
Dim responseObject
Set responseObject = jsObject()
Set responseObject("messages") = jsArray()

set ade = CreateObject("ADE" & ade_version & ".CAEngine")
model = OpenModel(ade, Server.MapPath("../radrat_411.ANA"))

redim d_tab(8,200), ud_tab(4), base_rate_tab(19,19), base_se_tab(19,19), surv_tab(121)
for i=1 to num
  d_tab(1,i) = dose_table(1,i)
  d_tab(2,i) = "'"+dose_table(2,i)+"'"
  d_tab(3,i) = dose_table(3,i)
  d_tab(4,i) = getvalueOrDefault(dose_table(4,i),0)
  d_tab(5,i) = getvalueOrDefault(dose_table(5,i),0)
  d_tab(6,i) = "'"+dose_table(6,i)+"'"
  d_tab(7,i) = dose_table(7,i)
  d_tab(8,i) = "'"+dose_table(8,i)+"'"
next
' fill out defaults
if num<200 then
  for i=num+1 to 200
    d_tab(1,i) = 0
    d_tab(2,i) = 0
    d_tab(3,i) = 0
    d_tab(4,i) = 0
    d_tab(5,i) = 0
    d_tab(6,i) = 0
    d_tab(7,i) = 0
    d_tab(8,i) = 0
  next
end if

ud_tab(1) = "'"+udud_table(1)+"'"
ud_tab(2) = udud_table(2)
ud_tab(3) = getvalueOrDefault(udud_table(3),0)
ud_tab(4) = getvalueOrDefault(udud_table(4),0)

' Translate the baseline parameter into a variable that the Analytica model is expecting. 
public popname
If baseline="usseer00_05" Then
    popname="U.S. 2000-2005"
elseif baseline="usseer00_05w" Then
    popname="U.S. 2000-2005 White"
elseif baseline="usseer00_05b" Then
    popname="U.S. 2000-2005 Black"
elseif baseline="france03_07" Then
    popname="France 2003-2007"
elseif baseline="spain03_07" Then
    popname="Spain 2003-2007"
elseif baseline="england11_12" Then
    popname="England 2011-2012" 
elseif baseline="japan10" Then
    popname="Japan 2010" 
elseif baseline="korea10" Then
    popname="Korea 2010" 
elseif baseline="brazil01_05" Then
    popname="Brazil 2001-2005"
else
    Response.Write("Error: Unknown baseline population " & baseline)
    Response.End
end if
base = "'"+popname+"'"

gen = "'"+gen_choice+"'"
units = "'"+dose_units+"'"
leuk = "'"+leukemia_choice+"'"
thyr = "'"+thyroid_choice+"'"

' Translate the include_history parameter into variable that the Analytica model is expecting.
if include_history = "" then
   lung = "'BEIR VII'"
else
   lung = "'FURUKAWA'"
end if

' Translate the start_smk_yr_inp and quit_smk_p_inp parameter into variable that the Analytica model is expecting.
If include_history <> "" And Not isnumeric(start_smk_yr_inp) Then 
   start_smk_yr_inp = "'Never'"
end if
If include_history <> "" And Not isnumeric(quit_smk_p_inp) Then 
   quit_smk_p_inp = "'Never'"
end if

' the following are the ActiveX calls to the Analytica application
call setobjectattribute(ade, "gen_choice", "definition", gen)
call setobjectattribute(ade, "By", "definition", by)
call setobjectattribute(ade, "dose_units", "definition", units)
call getobject_deftable_putsafearray(ade, "baselinerate", baselinerate)
call getobject_deftable_putsafearray(ade, "baseline_se", baseline_se)
call getobject_deftable_putsafearray(ade, "survivalweb", survivalfunction)
' TODO: I can't find this vairable defined anywhere: call setobjectattribute(ade, "dod", "definition", dod)
call setobjectattribute(ade, "Number_of_exposures", "definition", num)
call getobject_deftable_putsafearray(ade, "Dose_table_in_web", d_tab)
call setobjectattribute(ade, "samplesize", "definition", sample_size)
call setobjectattribute(ade, "randomseed", "definition", randomseed)
call setobjectattribute(ade, "baseline_rate_choice", "definition", base)
call setobjectattribute(ade, "year_today", "definition", year_today)
call getobject_deftable_putsafearray(ade, "udud_inputs", ud_tab)

call setobjectattribute(ade, "start_smk_yr_inp", "definition", start_smk_yr_inp)
call setobjectattribute(ade, "quit_smk_p_inp", "definition", quit_smk_p_inp)
call setobjectattribute(ade, "cpd_intensity_inp", "definition", cpd_intensity_inp)

call setobjectattribute(ade, "leukemia_model", "definition", leuk)
call setobjectattribute(ade, "thyroid_model", "definition", thyr)
call setobjectattribute(ade, "lung_model", "definition", lung)

risk_tab = getobject_resulttable_getsafearray(ade, "risk_output")
elr_organ_tab = getobject_resulttable_getsafearray(ade, "elr_organ_output")
eflr_organ_tab = getobject_resulttable_getsafearray(ade, "eflr_organ_output")
bflr_organ_tab = getobject_resulttable_getsafearray(ade, "bflr_organ_output")

base_test = getobject_resulttable_getsafearray(ade, "baseline_test")
base_se_test = getobject_resulttable_getsafearray(ade, "baseline_se_test")
surv_test = getobject_resulttable_getsafearray(ade, "survivalwebtest")

Set responseObject("risk_tab") = jsArray()
for i=1 to 28
    responseObject("risk_tab")(Null) = risk_tab(i)
next

Set responseObject("elr_organ_tab") = jsArray()
for i=1 to 57
    responseObject("elr_organ_tab")(Null) = elr_organ_tab(i)
next

Set responseObject("eflr_organ_tab") = jsArray()
for i=1 to 57
    responseObject("eflr_organ_tab")(Null) = eflr_organ_tab(i)
next

Set responseObject("bflr_organ_tab") = jsArray()
for i=1 to 57
    responseObject("bflr_organ_tab")(Null) = bflr_organ_tab(i)
next

' these values are for debug only
Set responseObject("base_test_row1") = jsArray()
for i=1 to 19
    responseObject("base_test_row1")(Null) = base_test(i, 1)
next
Set responseObject("base_test_row19") = jsArray()
for i=1 to 19
    responseObject("base_test_row19")(Null) = base_test(i, 19)
next
Set responseObject("base_se_test_row1") = jsArray()
for i=1 to 19
    responseObject("base_se_test_row1")(Null) = base_se_test(i, 1)
next
Set responseObject("base_se_test_row19") = jsArray()
for i=1 to 19
    responseObject("base_se_test_row19")(Null) = base_se_test(i, 19)
next
' select survival data - debug only
Set responseObject("surv_test") = jsArray()
responseObject("surv_test")(Null) = surv_test(1)
responseObject("surv_test")(Null) = surv_test(6)
responseObject("surv_test")(Null) = surv_test(11)
responseObject("surv_test")(Null) = surv_test(121)

'flush response object
responseObject.Flush
%>