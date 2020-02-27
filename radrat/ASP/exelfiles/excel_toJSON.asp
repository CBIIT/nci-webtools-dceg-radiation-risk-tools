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
Set responseObject("smoking_history") = jsObject()
Set responseObject("dose_units") = jsObject()
Set responseObject("advanced") = jsObject()
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
intCount = mySmartUpload.Save("/REB/RadRAT/excelfiles")
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

    Dim objFileSys
    set objFileSys = Server.CreateObject("Scripting.FileSystemObject")
    excelDirectory = Server.MapPath("./") '& "\excelfiles"
    ObjFileSys.CopyFile excelDirectory&"\"&excelfile, excelDirectory&"\savedfile.xls"
    ' delete the file that was just copied to savedfile.xls
    ObjFileSys.DeleteFile excelDirectory&"\"&excelfile

    Set objConn = Server.CreateObject("ADODB.Connection")
    objConn.Open "nci_radrat"

    Set objRS = Server.CreateObject("ADODB.Recordset")
    objRS.ActiveConnection = objConn
    objRS.CursorType = 3 'Static cursor.
    objRS.LockType = 2 'Pessimistic Lock.

    objRS.Source = "Select * from General_info"
    objRS.Open
    responseObject("personal")("gen_choice") = objRS.Fields.Item(1).Value
    responseObject("personal")("by") = objRS.Fields.Item(2).Value
    objRS.Close

    objRS.Source = "Select * from SmokingHistory"
    objRS.Open
    if objRS.Fields.Item(0).Value = "Yes" then
        responseObject("smoking_history")("include_history") = "on"
    else
        responseObject("smoking_history")("include_history") = ""
    end if
    responseObject("smoking_history")("cpd_intensity_inp") = objRS.Fields.Item(1).Value
    responseObject("smoking_history")("start_smk_yr_inp") = objRS.Fields.Item(2).Value
    responseObject("smoking_history")("quit_smk_p_inp") = objRS.Fields.Item(3).Value
    objRS.Close

    objRS.Source = "Select * from NumberExp"
    objRS.Open
    responseObject("dose_exposure")("dose_-TOTAL_FORMS") = objRS.Fields.Item(0).Value
    responseObject("dose_exposure")("dose_-MAX_NUM_FORMS") = ""
    responseObject("dose_exposure")("dose_-INITIAL_FORMS") = 0
    objRS.Close

    objRS.Source = "Select * from DoseUnits" 
    objRS.Open 
    responseObject("dose_units")("dose_units") = objRS.Fields.Item(0).Value
    objRS.Close
    'default dose units in case this is an older template    
    if isEmpty(responseObject("dose_units")("dose_units")) then
        responseObject("dose_units")("dose_units") = "mGy"
    end if

    Sub remapOrganType(index, value)
      val = value
        if value = "Uterus" then
            val = "Female Genitalia (less ovary)"
        elseif value = "Prostate" then
            val = "All Male Genitalia"
        elseif value = "Kidney" then
            val = "Urinary organs (less bladder)"
        else
            val = value    
        end if
      responseObject("dose_exposure")("dose_-" & index & "-organ") = val
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

    Sub remapDoseType(section, fieldname, value)
      val = value
        if value = "Constant" or Trim(value) = "" then
            val = "Fixed Value"
        end if
      responseObject(section)(fieldname) = val
    End Sub

    objRS.Source = "Select * from DoseInfo"
    objRS.Open
    for i = 1 to responseObject("dose_exposure")("dose_-TOTAL_FORMS")
        responseObject("dose_exposure")("dose_-" & i-1 & "-yoe") = objRS.Fields.Item(1).Value
        remapDoseType "dose_exposure", "dose_-" & i-1 & "-dosetype", objRS.Fields.Item(3).Value
        responseObject("dose_exposure")("dose_-" & i-1 & "-doseparm1") = objRS.Fields.Item(4).Value
        responseObject("dose_exposure")("dose_-" & i-1 & "-doseparm2") = objRS.Fields.Item(5).Value
        responseObject("dose_exposure")("dose_-" & i-1 & "-doseparm3") = objRS.Fields.Item(6).Value
        remapExposureRate i-1, objRS.Fields.Item(7).Value
        responseObject("dose_exposure")("dose_-" & i-1 & "-event") = objRS.Fields.Item(0).Value
        remapOrganType i-1, objRS.Fields.Item(2).Value
        objRS.MoveNext
    Next
    objRS.Close

    objRS.Source = "Select * from SimInfo"
    objRS.Open
    responseObject("advanced")("sample_size") = objRS.Fields.Item(0).Value
    responseObject("advanced")("random_seed") = objRS.Fields.Item(1).Value
    ' TODO: year_today missing from template -- responseObject("advanced")("year_today") = objRS.Fields.Item(2).Value
    responseObject("advanced")("year_today") = year(date)
    objRS.Close

    objRS.Source = "Select * from UserDistr"
    objRS.Open
    remapDoseType "advanced", "ududtype", objRS.Fields.Item(0).Value
    responseObject("advanced")("ududparm1") = objRS.Fields.Item(1).Value
    responseObject("advanced")("ududparm2") = objRS.Fields.Item(2).Value
    responseObject("advanced")("ududparm3") = objRS.Fields.Item(3).Value
    objRS.Close

    ' leukemia and thyroid models are not exposed on website and Excel template
    responseObject("advanced")("leukemia_choice") = "BEIR VII"
    responseObject("advanced")("thyroid_choice") = "BEIR VII"

    objRS.Source = "Select * from Baseline_info" 
    objRS.Open 
    ' remap value for Django form
    value = objRS.Fields.Item(0).Value
    if value = "U.S. 2000-2005 White" then
    	responseObject("personal")("baseline") = "usseer00_05w"
    elseif value = "U.S. 2000-2005 Black" then
    	responseObject("personal")("baseline") = "usseer00_05b"
    elseif value = "France 2003-2007" then
    	responseObject("personal")("baseline") = "france03_07"
    elseif value = "Spain 2003-2007" then
    	responseObject("personal")("baseline") = "spain03_07"
    elseif value = "England 2011-2012" then
    	responseObject("personal")("baseline") = "england11_12"
    elseif value = "Japan 2010" then
        responseObject("personal")("baseline") = "japan10"
    elseif value = "Korea 2010" then
        responseObject("personal")("baseline") = "korea10"
    elseif value = "Brazil 2001-2005" then
        responseObject("personal")("baseline") = "brazil01_05"
    else 'value = "U.S. 2000-2005"
  		responseObject("personal")("baseline") = "usseer00_05"
    end if   
    objRS.Close
    'default baseline in case this is an older template    
    if isEmpty(responseObject("personal")("baseline")) then
        responseObject("personal")("baseline") = "U.S. 2000-2005"
    end if

    'ADO Object clean up.
    Set objRS = Nothing
    objConn.Close
    Set objConn = Nothing

    'ObjFileSys.DeleteFile excelDirectory&"\"&excelfile
End If

'flush response object
responseObject.Flush
%>
