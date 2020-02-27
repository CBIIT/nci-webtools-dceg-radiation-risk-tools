<%
' This page shows the user a summary of results
public ade_version
ade_version = Trim(Request("ade_version"))
public fallout_version
fallout_version = Trim(Request("fallout_version"))
public summary_rpt_timeout
summary_rpt_timeout = cint(Trim(Request("summary_rpt_timeout")))

public bda
bda = cint(Trim(Request("bda")))
public bmo
bmo = cint(Trim(Request("bmo")))
public byr
byr = cint(Trim(Request("byr")))
public gender 
gender = Trim(Request("gender"))
public hours_outdoors
hours_outdoors = Trim(Request("hours_outdoors"))
if hours_outdoors="Not sure" then
    hours_outdoors = "'Not sure'"
end if
public mothers_milk_toggle
mothers_milk_toggle = Trim(Request("mothers_milk_toggle"))
public diag_year
diag_year = Trim(Request("diag_year"))

public numentries 
numentries = cint(Trim(Request("location_-TOTAL_FORMS")))
'Error check -- number of locations is hard capped at 30
if numentries > 30 then
    Response.Write("Error: Number of locations exceeds limit of 30. Received indication of " & num & " records.")
    Response.End
end if

public entry_data(6,30)
for i=1 to 30
    entry_data(1,i) = 0
    entry_data(2,i) = 0
    entry_data(3,i) = ""
    entry_data(4,i) = ""
    entry_data(5,i) = ""
    entry_data(6,i) = ""
next
for i=1 to numentries
    entry_data(1,i) = Trim(Request("location_-" & i-1 & "-month"))
    entry_data(2,i) = Trim(Request("location_-" & i-1 & "-year"))
    entry_data(3,i) = Trim(Request("location_-" & i-1 & "-state"))
    if entry_data(3,i) = "OU" then
        entry_data(4,i) = "OU"
    else
        entry_data(4,i) = Trim(Request("location_-" & i-1 & "-county"))
    end if    
    entry_data(5,i) = Trim(Request("location_-" & i-1 & "-milksource"))
    entry_data(6,i) = Trim(Request("location_-" & i-1 & "-milkamount"))
next

' set last entry to
entry_data(1, numentries+1) = 12
entry_data(2, numentries+1) = 1982

public sample_size 
sample_size = Trim(Request("sample_size"))
public randomseed 
randomseed = Trim(Request("randomseed"))
public Web_flag 
Web_flag = Trim(Request("web_flag"))
dim bdate
bdate = bmo & "/" & bda & "/" & byr

%>