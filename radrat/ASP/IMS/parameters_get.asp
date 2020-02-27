<%
' This page shows the user a summary of results
public ade_version
ade_version = Trim(Request("ade_version"))
public radrat_version
radrat_version = Trim(Request("radrat_version"))
public gen_choice 
gen_choice = Trim(Request("gen_choice"))
public by
by = cint(Trim(Request("by")))
public include_history
include_history = Trim(Request("include_history"))
public cpd_intensity_inp
cpd_intensity_inp = Trim(Request("cpd_intensity_inp"))
public start_smk_yr_inp
start_smk_yr_inp = Trim(Request("start_smk_yr_inp"))
public quit_smk_p_inp
quit_smk_p_inp = Trim(Request("quit_smk_p_inp"))
public summary_rpt_timeout
summary_rpt_timeout = cint(Trim(Request("summary_rpt_timeout")))
public dose_units 
dose_units = Trim(Request("dose_units"))
public baseline
baseline = Trim(Request("baseline"))
public leukemia_choice
leukemia_choice = Trim(Request("leukemia_choice"))
public thyroid_choice
thyroid_choice = Trim(Request("thyroid_choice"))

public num 
num = cint(Trim(Request("dose_-TOTAL_FORMS")))
'Error check -- number of dose forms is hard capped at 200
if num > 200 then
    Response.Write("Error: Number of dose records exceeds limit of 200. Received indication of " & num & " records.")
    Response.End
end if

public dose_table(8,200)
for i=1 to num
    dose_table(1,i) = Trim(Request("dose_-" & i-1 & "-yoe"))
    dose_table(2,i) = Trim(Request("dose_-" & i-1 & "-dosetype"))
    dose_table(3,i) = Trim(Request("dose_-" & i-1 & "-doseparm1"))
    dose_table(4,i) = Trim(Request("dose_-" & i-1 & "-doseparm2"))
    if dose_table(4,i) = "" then
       dose_table(4,i) = "0"
    end if
    dose_table(5,i) = Trim(Request("dose_-" & i-1 & "-doseparm3"))
    if dose_table(5,i) = "" then
       dose_table(5,i) = "0"
    end if
    dose_table(6,i) = Trim(Request("dose_-" & i-1 & "-exprate"))
    dose_table(7,i) = Trim(Request("dose_-" & i-1 & "-event"))
    dose_table(8,i) = Trim(Request("dose_-" & i-1 & "-organ"))
next

public udud_table(4)
udud_table(1) = Trim(Request("ududtype"))
udud_table(2) = Trim(Request("ududparm1"))
udud_table(3) = Trim(Request("ududparm2"))
if udud_table(3) = "" then
  udud_table(3) = "0"
end if
udud_table(4) = Trim(Request("ududparm3"))
if udud_table(4) = "" then
  udud_table(4) = "0"
end if

public sample_size 
sample_size = Trim(Request("sample_size"))
public randomseed 
randomseed = Trim(Request("random_seed"))
public year_today
year_today = Trim(Request("year_today"))

' New methodology for reading baseline data from a text file. 
' IMS: This code was provided by Oakridge and used as-is (in large part).
' Create local variables for extracting data from file
public baselinerate(19,19)
public baseline_se(19,19)
dim colskip(19)
dim objFileSys
dim TheTextStream
dim Gen_line_se
dim Gen_line_rate
If gen_choice="Male" Then Gen_line_rate=1 Else Gen_line_rate=41 End If 'The following if statement determines how many rows to skip in the text file.

'Read baseline rate from text file (Males=rows 3 to 21, Females=rows 43 to 61)
dim getbaselines
getbaselines = Server.MapPath("../baselines/" & baseline & ".txt")
Set objFileSys = Server.CreateObject("Scripting.FileSystemObject")
For j = 1 to 19
	For i = 1 to 19
		set TheTextStream = objFileSys.OpenTextFile(getbaselines)
	    For m=1 to Gen_line_rate
			TheTextStream.SkipLine
		next
		For k=1 to j
			TheTextStream.SkipLine
		next
		colskip(i) = (i*11)
		TheTextStream.Skip(colskip(i))
		baselinerate(i,j) = TheTextStream.Read(10)
		TheTextStream.Close
	next	
next

'Read baseline standard error from text file (Males=rows 23 to 41, Females=rows 63 to 81)
If gen_choice="Male" Then Gen_line_se=21 Else Gen_line_se=61 End If 'The following if statement determines how many rows to skip in the text file.
Set objFileSys = Server.CreateObject("Scripting.FileSystemObject")
For j = 1 to 19
	For i = 1 to 19
		set TheTextStream = objFileSys.OpenTextFile(getbaselines)
	  	For m=1 to Gen_line_se
			TheTextStream.SkipLine
		next
		For k=1 to j
			TheTextStream.SkipLine
		next
		colskip(i) = (i*11)
		TheTextStream.Skip(colskip(i))
		baseline_se(i,j) = TheTextStream.Read(10)
		TheTextStream.Close
	next	
next

'Read survival functions from text file (data for males begins in column 12, females begin in column 23)
public survivalfunction(121)
dim getsurvival
dim gencolumn
If gen_choice="Male" Then gencolumn=11 Else	gencolumn=22 End If

getsurvival = Server.MapPath("../survival/sf_" & baseline & ".txt")
Set objFileSys = Server.CreateObject("Scripting.FileSystemObject")
For i = 1 to 121
	set TheTextStream = objFileSys.OpenTextFile(getsurvival)
	TheTextStream.SkipLine
	TheTextStream.SkipLine
	For j = 1 to i
		TheTextStream.SkipLine
	next
	TheTextStream.Skip(gencolumn)
	survivalfunction(i) = TheTextStream.Read(10)
	TheTextStream.Close
Next
%>