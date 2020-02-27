<!--#include file="JSON_2.0.4.asp"-->
<%
   On Error Resume Next
'  Variables
'  *********
Dim mySmartUpload
Dim intCount
Dim file
Dim responseObject
Set responseObject = jsObject()
Set responseObject("error") = jsObject()
Set responseObject("personal") = jsObject()
Set responseObject("advanced") = jsObject()
Set responseObject("skin_lung") = jsObject()
Set responseObject("radon_exposure") = jsObject()
Set responseObject("dose_exposure") = jsObject()

'  Object creation
'  ***************
Set mySmartUpload = Server.CreateObject("aspSmartUpload.SmartUpload")

'  Only allow txt or htm files
'  ***************************
mySmartUpload.AllowedFilesList = "xls"

'  DeniedFilesList can also be used :
' Allow all files except exe, bat and asp
' ***************************************
' mySmartUpload.DeniedFilesList = "exe,bat,asp"

'  Deny physical path
'  *******************
mySmartUpload.DenyPhysicalPath = True

'  Only allow files smaller than 100000 bytes
'  *****************************************
mySmartUpload.MaxFileSize = 100000

'  Deny upload if the total fila size is greater than 200000 bytes
'  ***************************************************************
mySmartUpload.TotalMaxFileSize = 200000

'  Upload
'  ******
mySmartUpload.Upload

'  Save the files with their original names in a virtual path of the web server
'  ****************************************************************************
intCount = mySmartUpload.Save("/REB/IREP/excelfiles")
' sample with a physical path
' intCount = mySmartUpload.Save("c:\temp\")

'  Trap errors
'  ***********
If Err Then
  responseObject("error")("message") = "" & Err.description
Else
  '  Display successful upload message
  For each file In mySmartUpload.Files
    excelfile = file.FileName
  Next
    ' reset default values for variables, this gets around session reset that occurs the first time cpshost.dll is run
    'session.Timeout=90
    Dim radon_table(6,100)
    Dim yoe(200), aae(200), tse(200), udud_table(4), yoe_r(100), diagnoses(2,6)

    Dim objFileSys
    set objFileSys = Server.CreateObject("Scripting.FileSystemObject")
    excelDirectory = Server.MapPath("./") '& "\excelfiles"
    ObjFileSys.CopyFile excelDirectory&"\"&excelfile, excelDirectory&"\savedfile.xls"
    ' delete the file that was just copied to savedfile.xls
    ObjFileSys.DeleteFile excelDirectory&"\"&excelfile

    Set objConn = Server.CreateObject("ADODB.Connection")
    objConn.Open "irep_nih"

    Set objRS = Server.CreateObject("ADODB.Recordset")
    objRS.ActiveConnection = objConn
    objRS.CursorType = 3 'Static cursor.
    objRS.LockType = 2 'Pessimistic Lock.

    objRS.Source = "Select * from PersonalInfo"
    objRS.Open
    responseObject("personal")("gen_choice") = objRS.Fields.Item(2).Value
    responseObject("personal")("by") = objRS.Fields.Item(3).Value
    responseObject("personal")("dod") = objRS.Fields.Item(4).Value
    responseObject("personal")("cancer_choice") = objRS.Fields.Item(5).Value
    objRS.Close

    objRS.Source = "Select * from NumberExp"
    objRS.Open
    responseObject("dose_exposure")("dose_-TOTAL_FORMS") = objRS.Fields.Item(0).Value
    responseObject("dose_exposure")("dose_-MAX_NUM_FORMS") = ""
    responseObject("dose_exposure")("dose_-INITIAL_FORMS") = 0
    objRS.Close

    Sub remapRadiationType(index, value)
      val = value
	    if value = "electrons E<15keV" then
		    val = "e1"
	    elseif value = "electrons E>15keV" then
		    val = "e2"
	    elseif value = "photons E<30keV" then
		    val = "p1"
	    elseif value = "photons E=30-250keV" then
		    val = "p2"
	    elseif value = "photons E>250keV" then
		    val = "p3"
	    elseif value = "neutrons E<10keV" then
		    val = "n1"
	    elseif value = "neutrons E=10-100keV" then
		    val = "n2"
	    elseif value = "neutrons E=100keV-2MeV" then
		    val = "n3"
	    elseif value = "neutrons E=2-20MeV" then
		    val = "n4"
	    elseif value = "neutrons E>20MeV" then
		    val = "n5"
	    elseif value = "alpha" then
	        val = "a"
	    end if
      responseObject("dose_exposure")("dose_-" & index & "-radtype") = val
    End Sub

    Sub remapExposureRate(index, value)
      val = value
	    if value = "chronic" then
		    val = "c"
	    elseif value = "acute" then
	        val = "a"
	    end if
      responseObject("dose_exposure")("dose_-" & index & "-exprate") = val
    End Sub

    objRS.Source = "Select * from DoseInfo"
    objRS.Open
    for i = 1 to responseObject("dose_exposure")("dose_-TOTAL_FORMS")
    	responseObject("dose_exposure")("dose_-" & i-1 & "-yoe") = objRS.Fields.Item(1).Value
	    remapExposureRate i-1, objRS.Fields.Item(2).Value
        remapRadiationType i-1, objRS.Fields.Item(3).Value
	    responseObject("dose_exposure")("dose_-" & i-1 & "-dosetype") = objRS.Fields.Item(4).Value
	    responseObject("dose_exposure")("dose_-" & i-1 & "-doseparm1") = objRS.Fields.Item(5).Value
	    responseObject("dose_exposure")("dose_-" & i-1 & "-doseparm2") = objRS.Fields.Item(6).Value
	    responseObject("dose_exposure")("dose_-" & i-1 & "-doseparm3") = objRS.Fields.Item(7).Value
	    objRS.MoveNext
    Next
    objRS.Close

    objRS.Source = "Select * from SimInfo"
    objRS.Open
    responseObject("advanced")("sample_size") = objRS.Fields.Item(0).Value
    responseObject("advanced")("random_seed") = objRS.Fields.Item(1).Value
    objRS.Close

    objRS.Source = "Select * from UserDistr"
    objRS.Open
    responseObject("advanced")("ududtype") = objRS.Fields.Item(0).Value
    responseObject("advanced")("ududparm1") = objRS.Fields.Item(1).Value
    responseObject("advanced")("ududparm2") = objRS.Fields.Item(2).Value
    responseObject("advanced")("ududparm3") = objRS.Fields.Item(3).Value
    objRS.Close

    Sub remapEthnicOrigin(value)
      val = value
      if value = "American Indian or Alaska Native" then
        val = "American Indian"
      elseif value = "Asian or Native Hawaiian or Other Pacific Islander" then
        val = "Asian"
      elseif value = "White-Hispanic" then
        val = "Hispanic"
      elseif value = "White-Non-Hispanic" then
        val = "White-non-hispanic"
      elseif value = "All races/race not specified" then
        val = "US Population"
      elseif value = "Black" then
        val = "Black"
      end if
      responseObject("skin_lung")("ethnic") = val
    End Sub

    objRS.Source = "Select * from Skin"
    objRS.Open
    remapEthnicOrigin objRS.Fields.Item(0).Value
    objRS.Close

    objRS.Source = "Select * from Lung"
    objRS.Open
    responseObject("skin_lung")("exposure_source") = objRS.Fields.Item(0).Value
    responseObject("skin_lung")("smoking_history") = objRS.Fields.Item(1).Value
    objRS.Close

    objRS.Source = "Select * from NumRadon"
    objRS.Open
    responseObject("radon_exposure")("radon_-TOTAL_FORMS") = objRS.Fields.Item(0).Value
    responseObject("radon_exposure")("radon_-MAX_NUM_FORMS") = ""
    responseObject("radon_exposure")("radon_-INITIAL_FORMS") = 0
    objRS.Close

    objRS.Source = "Select * from RadonInfo"
    objRS.Open
    for i = 1 to responseObject("radon_exposure")("radon_-TOTAL_FORMS")
      responseObject("radon_exposure")("radon_-" & i-1 & "-yoe") = objRS.Fields.Item(1).Value
      responseObject("radon_exposure")("radon_-" & i-1 & "-exptype") = "annual" 'objRS.Fields.Item(2).Value      
      responseObject("radon_exposure")("radon_-" & i-1 & "-dosetype") = objRS.Fields.Item(3).Value      
      responseObject("radon_exposure")("radon_-" & i-1 & "-doseparm1") = objRS.Fields.Item(4).Value
   	  responseObject("radon_exposure")("radon_-" & i-1 & "-doseparm2") = objRS.Fields.Item(5).Value
	  responseObject("radon_exposure")("radon_-" & i-1 & "-doseparm3") = objRS.Fields.Item(6).Value
	  objRS.MoveNext
    Next
    objRS.Close

    'ADO Object clean up.
    Set objRS = Nothing
    objConn.Close
    Set objConn = Nothing

    'ObjFileSys.DeleteFile excelDirectory&"\"&excelfile
End If

'flush response object
responseObject.Flush
%>
