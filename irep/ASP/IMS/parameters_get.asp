<%
' This page shows the user a summary of results

'For Each item In Request.Form
'    response.AppendToLog "Key: " & item & " - Value: " & Request.Form(item) & "<BR />"
'Next


public ade_version
ade_version = Trim(Request("ade_version"))
public irep_version
irep_version = Trim(Request("irep_version"))
public by
by = cint(Trim(Request("by")))
public cancer_choice
cancer_choice = Trim(Request("cancer_choice"))
public dod
dod = cint(Trim(Request("dod")))

public num 
num = cint(Trim(Request("dose_-TOTAL_FORMS")))
'Error check -- number of dose forms is hard capped at 200
if num > 200 then
	Response.Write("Error: Number of dose records exceeds limit of 200. Received indication of " & num & " records.")
	Response.End
end if

public dose_table(7,200)
for i=1 to num
	dose_table(1,i) = Trim(Request("dose_-" & i-1 & "-yoe"))
	dose_table(2,i) = Trim(Request("dose_-" & i-1 & "-dosetype"))
	dose_table(3,i) = Trim(Request("dose_-" & i-1 & "-doseparm1"))
	dose_table(4,i) = Trim(Request("dose_-" & i-1 & "-doseparm2"))
	dose_table(5,i) = Trim(Request("dose_-" & i-1 & "-doseparm3"))
	dose_table(6,i) = Trim(Request("dose_-" & i-1 & "-exprate"))
	dose_table(7,i) = Trim(Request("dose_-" & i-1 & "-radtype"))
next

public numradon
numradon = cint(Trim(Request("radon_-TOTAL_FORMS")))
'Error check -- number of dose forms is hard capped at 200
if numradon > 100 then
	Response.Write("Error: Number of radon records exceeds limit of 100. Received indication of " & numradon & " records.")
	Response.End
end if

public radon_table(6,100)
for i=1 to numradon
	radon_table(1,i) = Trim(Request("radon_-" & i-1 & "-yoe"))
	radon_table(2,i) = Trim(Request("radon_-" & i-1 & "-dosetype"))
	radon_table(3,i) = Trim(Request("radon_-" & i-1 & "-doseparm1"))
	radon_table(4,i) = Trim(Request("radon_-" & i-1 & "-doseparm2"))
	radon_table(5,i) = Trim(Request("radon_-" & i-1 & "-doseparm3"))
	radon_table(6,i) = Trim(Request("radon_-" & i-1 & "-exptype"))
next

public udud_table(4)
udud_table(1) = Trim(Request("ududtype"))
udud_table(2) = Trim(Request("ududparm1"))
udud_table(3) = Trim(Request("ududparm2"))
udud_table(4) = Trim(Request("ududparm3"))

public gen_choice 
gen_choice = Trim(Request("gen_choice"))
public exposure_source 
exposure_source = Trim(Request("exposure_source"))
public smoking_history 
smoking_history = Trim(Request("smoking_history"))
public ethnic 
ethnic = Trim(Request("ethnic"))
public ethnic_output 
ethnic_output = ethnic
public sample_size 
sample_size = Trim(Request("sample_size"))
public randomseed 
randomseed = Trim(Request("random_seed"))
%>