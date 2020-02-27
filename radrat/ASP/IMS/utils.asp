<%
Function checkErrorCode(ade, objName)
    if ade.errorcode <> 0 then
        responseObject("messages")(Null) = "ADE Message for objName '" + objName + "' : " + ade.errortext + " (code " + cStr(ade.errorcode) + ") (OutputBuffer: "  + ade.OutputBuffer + ")"
    end if
End Function

Function OpenModel(ade, FileSpec)
    OpenModel = ade.OpenModel(FileSpec)
    call checkErrorCode(ade, "OpenModel")
End Function

Function getobjectbyname(ade, name)
    set getobjectbyname = ade.getobjectbyname("" & name)
    call checkErrorCode(ade, name)
End Function

Function setattribute(ade, obj, name, value)
    setattribute = obj.setattribute("" & name, value)
    call checkErrorCode(ade, name)
End Function

Function setobjectattribute(ade, objname, attributename, value)
    set obj = getobjectbyname(ade, objname)
    if ade.errorcode = 0 then
        call setattribute(ade, obj, attributename, value)
    end if  
End Function

Function getobject_resulttable_getsafearray(ade, objname)
    set obj = getobjectbyname(ade, "" & objname)
    if not IsNull(obj) then
        getobject_resulttable_getsafearray = obj.resulttable.getsafearray
        call checkErrorCode(ade, objname)
    end if  
End Function

Function getobject_resulttable_getsafearray_size(ade, objname)
    set obj = getobjectbyname(ade, "" & objname)
    if not IsNull(obj) then
        getobject_resulttable_getsafearray_size = obj.resulttable.numdims
        call checkErrorCode(ade, objname)
    end if  
End Function

Function getobject_deftable_putsafearray(ade, objname, table)
    set obj = getobjectbyname(ade, "" & objname)
    if not IsNull(obj) then
        set t_obj=obj.deftable
        t_obj.putsafearray(table)
        call checkErrorCode(ade, "" & objname)
        t_obj.update
        call checkErrorCode(ade, "" & objname)
    end if  
End Function

Function getobject_result(ade, objname)
    set obj = getobjectbyname(ade, "" & objname)
    if not IsNull(obj) then
        getobject_result = obj.result
        call checkErrorCode(ade, "" & objname)
    end if
End Function

Function getvalueOrDefault(value, default)
  if IsNull(value) Or value = "" then
    getvalueOrDefault = default
  else
    getvalueOrDefault = value
  end if
End Function
%>