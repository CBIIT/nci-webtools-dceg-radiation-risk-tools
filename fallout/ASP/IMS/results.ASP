<!-- #INCLUDE FILE="utils.asp" -->
<!-- #INCLUDE FILE="parameters_get.asp" -->
<!-- #INCLUDE FILE="JSON_2.0.4.asp"-->
<%
' timeout this script after so many seconds
server.ScriptTimeout=summary_rpt_timeout

' This page shows the user a summary of results
Dim responseObject
Set responseObject = jsObject()
Set responseObject("messages") = jsArray()

set ade = CreateObject("ADE" & ade_version & ".CAEngine")
model = OpenModel(ade, Server.MapPath("../FC5.ana"))

' set last entry to 
entry_data(1, numentries+1) = 12
entry_data(2, numentries+1) = 1982

redim move_month(30)
for i=1 to 30
	move_month(i) = entry_data(1,i)
next

redim move_year(30)
for i=1 to 30
	move_year(i) = entry_data(2,i)
next

redim location(30)
for i=1 to 30
	location(i) = "'"+entry_data(4,i)+", "+entry_data(3,i)+"'"
next

redim milk_source(30)
for i=1 to 30
	milk_source(i) = "'"+entry_data(5,i)+"'"
next

redim milk_amount(30)
for i=1 to 30
	milk_amount(i) = "'"+entry_data(6,i)+"'"
next

	
' the following are the ActiveX calls to the Analytica application

' Submit variables to Analytica
' --------------------------------------

call setobjectattribute(ade, "Gender", "definition", "'"+gender+"'")
'set obj=ade.getobjectbyname("gender")
'bool=obj.setattribute("definition", gender)

call setobjectattribute(ade, "web_flag", "definition", web_flag)
'set obj=ade.getobjectbyname("web_flag")
'bool=obj.setattribute("definition", web_flag)

call setobjectattribute(ade, "Number_of_residences", "definition", numentries)
'set obj=ade.getobjectbyname("Number_of_residences")
'bool=obj.setattribute("definition", numentries)

call setobjectattribute(ade, "Birthdate", "definition", bdate)
'set obj=ade.getobjectbyname("Birthdate")
'bool=obj.setattribute("definition", bdate)

call setobjectattribute(ade, "Hours_outdoors", "definition", hours_outdoors)
'set obj=ade.getobjectbyname("Hours_outdoors")
'bool=obj.setattribute("definition", hours_outdoors)

call setobjectattribute(ade, "Mothers_milk_toggle", "definition", "'"+mothers_milk_toggle+"'")
'set obj=ade.getobjectbyname("Mothers_milk_toggle")
'bool=obj.setattribute("definition", mothers_milk_toggle)

call getobject_deftable_putsafearray(ade, "move_month", move_month)
'set obj=ade.getobjectbyname("move_month")
'set t_obj=obj.deftable
'bool=t_obj.putsafearray(move_month)
't_obj.update

call getobject_deftable_putsafearray(ade, "move_year", move_year)
'set obj=ade.getobjectbyname("move_year")
'set t_obj=obj.deftable
'bool=t_obj.putsafearray(move_year)
't_obj.update

call getobject_deftable_putsafearray(ade, "location", location)
'set obj=ade.getobjectbyname("location")
'set t_obj=obj.deftable
'bool=t_obj.putsafearray(location)
't_obj.update

call getobject_deftable_putsafearray(ade, "milk_source", milk_source)
'set obj=ade.getobjectbyname("milk_source")
'set t_obj=obj.deftable
'bool=t_obj.putsafearray(milk_source)
't_obj.update

call getobject_deftable_putsafearray(ade, "milk_amount", milk_amount)
'set obj=ade.getobjectbyname("milk_amount")
'set t_obj=obj.deftable
'bool=t_obj.putsafearray(milk_amount)
't_obj.update

call setobjectattribute(ade, "samplesize", "definition", sample_size)
'set obj=ade.getobjectbyname("samplesize")
'bool=obj.setattribute("definition", sample_size)

call setobjectattribute(ade, "randomseed", "definition", randomseed)
'set obj=ade.getobjectbyname("randomseed")
'bool=obj.setattribute("definition", randomseed)

call setobjectattribute(ade, "gender", "definition", "'"+gender+"'")

call setobjectattribute(ade, "today", "definition", datediff("d", "1/1/1904", date))
'set obj=ade.getobjectbyname("today")
'bool=obj.setattribute("definition", datediff("d", "1/1/1904", date))

call setobjectattribute(ade, "diag_year", "definition", diag_year)
'set obj=ade.getobjectbyname("diag_year")
'bool=obj.setattribute("definition", diag_year)

' Return results from Analytica
' --------------------------------------

Milk_source_res = getobject_resulttable_getsafearray(ade, "Milk_source_res")
'set obj=ade.getobjectbyname("Milk_source_res")
'Milk_source_res=obj.resulttable.getsafearray

Milk_amount_res = getobject_resulttable_getsafearray(ade, "Milk_amount_res")
'set obj=ade.getobjectbyname("Milk_amount_res")
'Milk_amount_res=obj.resulttable.getsafearray

FIPS_WEB = getobject_resulttable_getsafearray(ade, "FIPS_WEB")
'set obj=ade.getobjectbyname("FIPS_WEB")
'FIPS_WEB=obj.resulttable.getsafearray

Number_of_residences = getobject_result(ade, "Number_of_residences")
'set obj=ade.getobjectbyname("Number_of_residences")
'Number_of_residences=obj.result

Move_month_web_res = getobject_resulttable_getsafearray(ade, "Move_month_web_res")
'set obj=ade.getobjectbyname("Move_month_web_res")
'Move_month_web_res=obj.resulttable.getsafearray

Move_year_web_res = getobject_resulttable_getsafearray(ade, "Move_year_web_res")
'set obj=ade.getobjectbyname("Move_year_web_res")
'Move_year_web_res=obj.resulttable.getsafearray

Web_flag_returned = getobject_result(ade, "Web_flag")
'set obj=ade.getobjectbyname("Web_flag")
'Web_flag_returned=obj.result

Depo_summ = getobject_resulttable_getsafearray(ade, "Depo_summary")
'set obj=ade.getobjectbyname("Depo_summary")
'Depo_summ=obj.resulttable.getsafearray

Depo95 = getobject_result(ade, "Depo_95")
'set obj=ade.getobjectbyname("Depo_95")
'Depo95=obj.result

Temp = getobject_result(ade, "Temp_result")
'set obj=ade.getobjectbyname("Temp_result")
'Temp=obj.result

Va3 = getobject_resulttable_getsafearray(ade, "Va3")
'set obj=ade.getobjectbyname("Va3")
'Va3=obj.resulttable.getsafearray

NTS_Global = getobject_resulttable_getsafearray(ade, "Nts_global_web")
'set obj=ade.getobjectbyname("Nts_global_web")
'NTS_Global=obj.resulttable.getsafearray

Pathway_dose = getobject_resulttable_getsafearray(ade, "Pathway_Dose_WEB")
'set obj=ade.getobjectbyname("Pathway_Dose_WEB")
'Pathway_dose=obj.resulttable.getsafearray

Pathway_Dose_nts = getobject_resulttable_getsafearray(ade, "Pathway_Dose_nts")
'set obj=ade.getobjectbyname("Pathway_Dose_nts")
'Pathway_Dose_nts=obj.resulttable.getsafearray

Pathway_Dose_global = getobject_resulttable_getsafearray(ade, "Pathway_Dose_global")
'set obj=ade.getobjectbyname("Pathway_Dose_global")
'Pathway_Dose_global=obj.resulttable.getsafearray

total_lifetime = getobject_resulttable_getsafearray(ade, "tr_lifetime_per")
'set obj=ade.getobjectbyname("tr_lifetime_per")
'total_lifetime=obj.resulttable.getsafearray

total_future = getobject_resulttable_getsafearray(ade, "tr_future_per")
'set obj=ade.getobjectbyname("tr_future_per")
'total_future=obj.resulttable.getsafearray

baseline_lifetime = getobject_resulttable_getsafearray(ade, "baseline_life_per")
'set obj=ade.getobjectbyname("baseline_life_per")
'baseline_lifetime=obj.resulttable.getsafearray

baseline_future = getobject_resulttable_getsafearray(ade, "baseline_future_per")
'set obj=ade.getobjectbyname("baseline_future_per")
'baseline_future=obj.resulttable.getsafearray

pc = getobject_resulttable_getsafearray(ade, "pc_per")
'set obj=ade.getobjectbyname("pc_per")
'pc=obj.resulttable.getsafearray

excess_lifetime = getobject_resulttable_getsafearray(ade, "Ter_lifetime_per")
'set obj=ade.getobjectbyname("Ter_lifetime_per")
'excess_lifetime=obj.resulttable.getsafearray

Set responseObject("NTS_Global") = jsArray()
for i=1 to 9
    responseObject("NTS_Global")(Null) = NTS_Global(i)
next

Set responseObject("Pathway_Dose") = jsArray()
for i=1 to 24
    responseObject("Pathway_Dose")(Null) = Pathway_Dose(i)
next

Set responseObject("Pathway_Dose_nts") = jsArray()
for i=1 to 24
    responseObject("Pathway_Dose_nts")(Null) = Pathway_Dose_nts(i)
next

Set responseObject("Pathway_Dose_global") = jsArray()
for i=1 to 24
    responseObject("Pathway_Dose_global")(Null) = Pathway_Dose_global(i)
next

Set responseObject("FIPS_WEB") = jsArray()
for i=1 to numentries
    responseObject("FIPS_WEB")(Null) = FIPS_WEB(i)
next

Set responseObject("total_future") = jsArray()
for i=1 to 4
    responseObject("total_future")(Null) = total_future(i)
next

Set responseObject("baseline_future") = jsArray()
for i=1 to 4
    responseObject("baseline_future")(Null) = baseline_future(i)
next

Set responseObject("pc") = jsArray()
for i=1 to 4
    responseObject("pc")(Null) = pc(i)
next

'flush response object
responseObject.Flush
%>
