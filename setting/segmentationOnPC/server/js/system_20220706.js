var _api_importSystemFile = "/api/system/file";
var _api_uploadOTAFile = "/api/system/ota";
var _api_workStates = "/api/work/state"
var _api_sysSetting = "/api/system/config";
var _api_sysTime = "/api/system/time";
var _api_sysClear = "/api/system/clear/local";
var _api_sysClearMem = "/api/system/clear/mem";
var _api_sysReboot = "/api/system/boot/reboot";
var _apOldPw = null;
var _oldForm = null;
var _focusRefresh=false;

function topBarCallback(){
    showLoading();
    loadSystemSetting(false,function(data){
        if(data!=null)
            loadInputBox(data);
        _oldForm = getForm();
        //console.log(_oldForm);
        $(".title").click();
        hideLoading();
    });
}

window.onbeforeunload=function(e){
    var nowData = getForm();
    if(! compareObject(nowData,_oldForm) && !_focusRefresh){
        console.log(nowData);
        console.log(_oldForm);
        var e=window.event||e;
        //e.returnValue=("There are forms that have not been saved. Are you sure to leave the page?");
        e.returnValue=(_language.check_left_page);
    }
    
}


$(document).on("change","input[name='lanSetting']",function(){
    var status = $("input[name='lanSetting']:checked").val();
    if(status=="auto"){
        $('.lanInput').attr('disabled', true);
        $('.lanInput').css('opacity', "0.5");

    }
    else{
        $('.lanInput').attr('disabled', false);
        $('.lanInput').css('opacity', "1");
    }
});


$(document).on("change","input[name='lan2Setting']",function(){
    var status = $("input[name='lan2Setting']:checked").val();
    if(status=="auto"){
        $('.lan2Input').attr('disabled', true);
        $('.lan2Input').css('opacity', "0.5");

    }
    else{
        $('.lan2Input').attr('disabled', false);
        $('.lan2Input').css('opacity', "1");
    }
});


$(document).on("change","input[name='wifiSetting']",function(){
    var status = $("input[name='wifiSetting']:checked").val();
    if(status=="auto"){
        $('.wifiInput').attr('disabled', true);
        $('.wifiInput').css('opacity', "0.5");

    }
    else{
        $('.wifiInput').attr('disabled', false);
        $('.wifiInput').css('opacity', "1");
    }
});

$(document).on("click","#ImportSubmit",function(){
    //if(confirm("This operation will overwrite the original setting. Are you sure to execute？")){
    if(confirm(_language.check_over_setting)){
        $("#ImportSubmitSelect").val(null);
        $("#ImportSubmitSelect").click();
    }
});

$(document).on("click","#OTASubmit",function(){
    //if(confirm("This operation will overwrite the original setting. Are you sure to execute？")){
    if(confirm(_language.check_over_setting)){
        $("#OTASubmitSelect").val(null);
        $("#OTASubmitSelect").click();
    }
});


$(document).on("click","#webSubmit",function(){
    var ip = $("#webIp").val();
    var states = $("input[name='uploadData2Server']:checked").val();
    var proxy = $("#webProxy").val();
    var type = "0";
    
    if(! isURL(ip) && ip!=""){
        alert("Server hostname format error.");
        return;
    }
    if(! isURL(proxy) && proxy!=""){
        alert("Server proxy format error.");
        return;
    }
    if(states=="enable")
        type = "1";
    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "server":{
                "ip":ip,
                "type":type,
                "proxy":proxy
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            alert("Server setting req error: "+response.msg);
        }
        else{
            alert("Setting successfully.");
            _oldForm.server.ip=ip;
            _oldForm.server.type=type;
            _oldForm.server.proxy=proxy;
        }
        hideLoading();
    }).error(function(e){
        alert("Server setting error." + e.statusText);
        hideLoading();
    });
});



$(document).on("click","#statusSubmit",function(){
    var ip = $("#statusIp").val();
    var proxy = $("#statusProxy").val();
    
    if(! isURL(ip) && ip!=""){
        //alert("Status server hostname format error.");
        alert(_language.system.status_server_host_err);
        return;
    }
    if(! isURL(proxy) && proxy!=""){
        //alert("Server proxy format error.");
        alert(_language.system.status_server_proxy_err);
        return;
    }
    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "status":{
                "ip":ip,
                "proxy":proxy
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Server setting req error: "+response.msg);
            alert(_language.system.status_server_set_err+response.msg);
        }
        else{
            //alert("Setting successfully.");
            alert(_language.system.status_server_set_OK);
            _oldForm.status.ip=ip;
            _oldForm.status.proxy=proxy;
        }
        hideLoading();
    }).error(function(e){
        //alert("Server setting error." + e.statusText);
        alert(_language.system.status_server_req_err + e.statusText);
        hideLoading();
    });
});


$(document).on("click","#clearSubmit",function(){
    showLoading();
    var settings = {
        "url": _api_sysClear,
        "type": "GET",
        "timeout": 0
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Clear req error: "+response.msg);
            alert(_language.system.clear_file_err+response.msg);
        }
        else{
            //alert("Clear successfully.");
            alert(_language.system.clear_file_OK);
            $(".localCount").html(_language.form.localCount + "0");
        }
        hideLoading();
    }).error(function(e){
        //alert("Clear error." + e.statusText);
        alert(_language.system.clear_file_req_err + e.statusText);
        hideLoading();
    });
});



$(document).on("click","#clearMemorySubmit",function(){
    showLoading();
    var settings = {
        "url": _api_sysClearMem,
        "type": "GET",
        "timeout": 0
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Clear RAM error: "+response.msg);
            alert(_language.system.clear_queue_err+response.msg);
        }
        else{
            //alert("Clear RAM successfully.");
            alert(_language.system.clear_queue_OK);
            $(".memoryCount").html(_language.form.memoryCount + "0");
        }
        hideLoading();
    }).error(function(e){
        //alert("Clear RAM error." + e.statusText);
        alert(_language.system.clear_queue_req_err + e.statusText);
        hideLoading();
    });
});

$(document).on("click","#sgSubmit",function(){
    
    var obj = [$("#sgIp"),$("#sgPort"),$("#sgTopic"),$("#sgUser")];
    var checkFunc = [isHostname,isInt,null,isＷord];
    var allowEmpty = [false,false,false,true];
    var objName=["hostname","port","topic","user name"];
    var ip = $("#sgIp").val();
    var port = $("#sgPort").val();
    var topic = $("#sgTopic").val();
    var name = $("#sgUser").val();
    var pw = $("#sgUserpw").val();
    if(ip!=""){
        for(var i=0;i<obj.length;i++){
            if(obj[i].val().length==0 && !allowEmpty[i]){
                //alert("Smart Grid (MQTT) Server "+objName[i]+" can't empty.");
                alert(_language.system.smart_grid+objName[i]+_language.system.smart_grid_empty);
                obj[i].focus();
                return;
            }
            console.log(typeof(checkFunc[i]));
            if(typeof(checkFunc[i])==="function" && obj[i].val().length>0)
                if(!checkFunc[i](obj[i].val())){
                    //alert("Smart Grid (MQTT) Server "+objName[i]+" format error.");
                    alert(_language.system.smart_grid+objName[i]+_language.system.smart_grid_format);
                    obj[i].focus();
                    return;
                }
        }
    }
    else{
        ip="";
        port="";
        topic="";
        name="";
        pw="";
        $("#sgPort").val("");
        $("#sgTopic").val("");
        $("#sgUser").val("");
        $("#sgUserpw").val("");
    }
    
    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "mqtt":{
                "ip":ip,
                "port":port,
                "topic":topic,
                "name":name,
                "passwd":pw
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Smart Grid (MQTT) Server setting req error: "+response.msg);
            alert(_language.system.smart_grid_err+response.msg);
        }
        else{
            //alert("Smart Grid (MQTT) Setting successfully.");
            alert(_language.system.smart_grid_OK);
            _oldForm.mqtt.ip=ip;
            _oldForm.mqtt.port=port;
            _oldForm.mqtt.topic=topic;
            _oldForm.mqtt.name=name;
            _oldForm.mqtt.passwd=pw;
        }
        hideLoading();
    }).error(function(e){
        //alert("Smart Grid (MQTT) setting error." + e.statusText);
        alert( + e.statusText);
        hideLoading();
    });
});

$(document).on("click","#ntpSubmit",function(){
    var ip = $("#ntpIp").val();
    var proxy = $("#ntpProxy").val();
    if(! isHostname(ip) && ip!=""){
        //alert("NTP IP address format error.");
        alert(_language.system.NTP_format);
        return;
    }
    if(! isURL(proxy) && proxy!=""){
        //alert("NTP proxy format error.");
        alert(_language.system.NTP_proxy);
        return;
    }

    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "ntp":{
                "proxy":proxy,
                "ip":ip
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("NTP setting req error: "+response.msg);
            alert(_language.system.NTP_err+response.msg);
        }
        else{
            //alert("Setting successfully.");
            alert(_language.system.NTP_OK);
            _oldForm.ntp.ip=ip;
            _oldForm.ntp.proxy=proxy;
        }
        hideLoading();
    }).error(function(e){
        //alert("NTP setting error." + e.statusText);
        alert(_language.system.NTP_req_err + e.statusText);
        hideLoading();
    });
});


$(document).on("click","#ftpSubmit",function(){
    var dataType = $(".uploadFTPType").val();
    var ip = $("#ftpIp").val();
    var name = $("#ftpUsername").val();
    var proxy = $("#ftpProxy").val();
    var pw = $("#ftpUserpw").val();
    if(! isHostname(ip) && ip!="" && dataType!="0"){
        //alert("FTP IP address format error.");
        alert(_language.system.FTP_format);
        return;
    }
    if(! isURL(proxy) && proxy!=""){
        //alert("FTP proxy format error.");
        alert(_language.system.FTP_proxy);
        return;
    }

    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "ftp":{
                "ip":ip,
                "name":name,
                "pwd":pw,
                "proxy":proxy,
                "type":dataType
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("FTP setting req error: "+response.msg);
            alert(_language.system.FTP_err+response.msg);
        }
        else{
            //alert("FTP Setting successfully.");
            alert(_language.system.FTP_OK);
            _oldForm.ftp.ip=ip;
            _oldForm.ftp.name=name;
            _oldForm.ftp.pwd=pw;
            _oldForm.ftp.type=dataType;
            _oldForm.ftp.proxy=proxy;
        }
        hideLoading();
    }).error(function(e){
        //alert("FTP setting error." + e.statusText);
        alert(_language.system.FTP_req_err + e.statusText);
        hideLoading();
    });
});


$(document).on("click","#pinSubmit",function(){
    var newPwd = $("#pinNewPw").val();
    var checkPwd = $("#pinCheckPw").val();
    
    if(newPwd != checkPwd){
        //alert("New password and check password are difference.");
        alert(_language.system.pin_format_valida);
        return;
    }
    if(!isInt(newPwd)){
        //alert("The password only accepts numbers.");
        alert(_language.system.pin_format_num);
        return;
    }
    if(newPwd.length<4){
        //alert("The password length cannot be less than 4.");
        alert(_language.system.pin_format_min_len);
        return;
    }
    if(newPwd.length>20){
        //alert("The password length cannot be more than 20.");
        alert(_language.system.pin_format_max_len);
        return;
    }

    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "pin":{
                "pwd":newPwd
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("PIN setting req error: "+response.msg);
            alert(_language.system.pin_err+response.msg);
        }
        else{
            //alert("Setting successfully.");
            alert(_language.system.pin_OK);
        }
        hideLoading();
    }).error(function(e){
        //alert("PIN setting error." + e.statusText);
        alert(_language.system.pin_req_err + e.statusText);
        hideLoading();
    });
});

$(document).on("click","#langSubmit",function(){
    var lang = $("select[name='changeLanguage']").val();
    
    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "language":{
                "value":lang
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Language setting req error: "+response.msg);
            alert(_language.system.lang_set_err+response.msg);
            hideLoading();
        }
        else{
            //alert("Language setting successfully.");
            alert(_language.system.lang_set_OK);
            cookieAdd("language",lang,999999999);
            window.location.reload(); 
        }
    }).error(function(e){
        //alert("Language setting error." + e.statusText);
        alert(_language.system.lang_req_err + e.statusText);
        hideLoading();
    });
});

$(document).on("click","#rebootSubmit",function(){
    //if(!confirm("The operation will force reboot device. Do you want to continue?"))
    if(!confirm(_language.system.reboot_check))
        return;
    showLoading();
    var settings = {
        "url": _api_sysReboot,
        "type": "PUT",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({})
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Reboot req error: "+response.msg);
            alert(_language.system.reboot_err+response.msg);
        }
        else{
            //alert("Reboot req successfully. Please wait.");
            alert(_language.system.reboot_OK);
        }
        hideLoading();
    }).error(function(e){
        //alert("Reboot error." + e.statusText);
        alert(_language.system.reboot_check + e.statusText);
        hideLoading();
    });
});

$(document).on("click","#apSubmit",function(){
    var name = $("#apName").val();
    if(name.length==0){
        //alert("The ap name cannot be empty.");
        alert(_language.system.AP_SSID_empty);
        return;
    }
    if(!isＷord(name)){
        //alert("The ap name only accepts symbol, English and numbers.");
        alert(_language.system.AP_SSID_format);
        return;
    }
    var oldPwd = $("#apOldPw").val();
    var newPwd = $("#apNewPw").val();
    var checkPwd = $("#apCheckPw").val();
    if(oldPwd!="" || newPwd!="" || checkPwd!=""){
        if(oldPwd != _apOldPw){
            //alert("Old password input error.");
            alert(_language.system.AP_passwd_err);
            return;
        }
        if(newPwd != checkPwd){
            //alert("New password and check password are difference.");
            alert(_language.system.AP_passwd_valida);
            return;
        }
        if(!isNumEnglish(newPwd)){
            //alert("The password only accepts English and numbers.");
            alert(_language.system.AP_passwd_format);
            return;
        }
        if(newPwd.length<8){
            //alert("The password length cannot be less then 8.");
            alert(_language.system.AP_passwd_len);
            return;
        }
    }
    else{
        newPwd=_apOldPw;
    }

    showLoading();
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 180000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "ap":{
                "name":name,
                "passwd":newPwd
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("AP setting req error: "+response.msg);
            alert(_language.system.AP_err+response.msg);
        }
        else{
            //alert("Setting successfully. Please wait moment to take effect.");
            alert(_language.system.AP_OK);
        }
        hideLoading();
    }).error(function(e){
        //alert("AP setting error." + e.statusText);
        alert(_language.system.AP_req_err + e.statusText);
        hideLoading();
    });
});

$(document).on("click","#lanSubmit",function(){
    updateIPsetting("lan",function(ip,mask,getway){
            _oldForm.lan.ip=ip;
            _oldForm.lan.mask=mask;
            _oldForm.lan.getway=getway;
    });
});
$(document).on("click","#lan2Submit",function(){
    updateIPsetting("lan2",function(ip,mask,getway){
            _oldForm.lan2.ip=ip;
            _oldForm.lan2.mask=mask;
            _oldForm.lan2.getway=getway;
    });
});
$(document).on("click","#wifiSubmit",function(){
    updateIPsetting("wifi",function(ip,mask,getway){
            _oldForm.wifi.ip=ip;
            _oldForm.wifi.mask=mask;
            _oldForm.wifi.getway=getway;
    });
});

function updateIPsetting(name,callback){
    if($("input[name='"+name+"Setting']:checked").val() == "manual"){
        var ip = getIP(name+"Ip");
        var mask = getIP(name+"Mk");
        var getway = getIP(name+"Gw");
        if(! isIP(ip)){
            //alert("IP address format error.");
            alert(_language.system.IP_format);
            return;
        }
        if(! isIP(mask)){
            //alert("Subnet mask IP address format error.");
            alert(_language.system.IP_mask_format);
            return;
        }
        if(! isIP(getway)){
            //alert("Default getway IP address format error.");
            alert(_language.system.IP_gw_format);
            return;
        }
    }
    else{
        var ip = "...";
        var mask = "...";
        var getway = "...";
    }

    showLoading();
    var obj = {}
    obj[name]={
        "ip": ip,
        "mask": mask,
        "getway": getway
    }
    var settings = {
        "url": _api_sysSetting,
        "type": "PUT",
        "timeout": 180000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify(obj),
    };
    console.log(settings);
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("IP setting req error: "+response.msg);
            alert(_language.system.IP_err+response.msg);
        }
        else{
            //alert("Setting successfully.");
            alert(_language.system.IP_OK);
            if(typeof(callback)=="function")
                callback(ip,mask,getway);
        }
        hideLoading();
    }).error(function(e){
        //alert("IP setting error." + e.statusText);
        alert(_language.system.IP_req_err + e.statusText);
        hideLoading();
    });
    
}


$(document).on("click","#timeSubmit",function(){
    var timeDate = $("#timeSetting").val();
    //alert(timeDate);
    try{
        Date.parse(timeDate);
    }
    catch(e){
        //alert("Date format error. Follow: yyyy-MM-dd hh:mm:ss");
        alert(_language.system.time_format);
        return;
    }
    
    if(timeDate==""){
        //alert("Please select time.")
        alert(_language.system.time_empty)
        return;
    }
    showLoading();
    var settings = {
        "url": _api_sysTime,
        "type": "PUT",
        "timeout": 180000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "time":{
                "value": timeDate
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Time setting req error: "+response.msg);
            alert(_language.system.time_err+response.msg);
        }
        else{
            //alert("Setting successfully.");
            alert(_language.system.time_OK);
        }
        hideLoading();
    }).error(function(e){
        //alert("Time setting error." + e.statusText);
        alert(_language.system.time_req_err + e.statusText);
        hideLoading();
    });
});
$(document).on("click","#enableSubmit",function(){
    var select=$("input[name='enableSample']:checked").val();
    var val = "0";
    if(select=="enable")
        val="1";
    
    showLoading();
    var settings = {
        "url": _api_workStates,
        "type": "PUT",
        "timeout": 30000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "work":{
                "enable":val
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("work state change req error: "+response.msg);
            alert(_language.system.work_err+response.msg);
            hideLoading();
        }
        else{
            //alert("Request sent successfully. Waiting for device processing");
            alert(_language.system.work_OK);
            setTimeout(waitWorkStates,1000,val,function(){
                hideLoading();
            });
        }

    }).error(function(e){
        //alert("work state change error." + e.statusText);
        alert(_language.system.work_req_err + e.statusText);
        hideLoading();
    });
});


function waitWorkStates(target,callback){
    var settings = {
        "url": _api_workStates,
        "type": "GET",
        "timeout": 5000
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("wait work state change req error: "+response.msg);
            alert(_language.system.work_wait_err+response.msg);
            if(typeof(callback)==="function")
                callback();
        }
        else{
            if(response.data.environment.work_task_state==target){
                //alert("Process successfully.");
                alert(_language.system.work_wait_OK);
                if(typeof(callback)==="function")
                    callback();
            }
            else{
                setTimeout(waitWorkStates,3000,target,callback);
            }
        }

    }).error(function(e){
        //alert("wait work state change error." + e.statusText);
        alert(_language.system.work_wait_req_err + e.statusText);
        if(typeof(callback)==="function")
            callback();
    });
}

function importFiles(e){
    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        showLoading();
        var data=event.target.result.split("base64,")[1];
        //console.log(data);
        //console.log(atob(data));
        var settings = {
            "url": _api_importSystemFile,
            "type": "POST",
            "timeout": 0,
            "cache":false,
            "headers": {
                "Content-Type": "text/plain"
            },
            "data": atob(data),
        };
        $.ajax(settings).success(function (response) {
            if(response.state!=200){
                //alert("import file req error: "+response.msg);
                alert(_language.system.import_err+response.msg);
            }
            else{
                //alert("Request sent successfully.");
                alert(_language.system.import_OK);
                window.location.reload(); 
            }
    
            hideLoading();
        }).error(function(e){
            console.log(e);
    
            hideLoading();
        });
    });
    reader.readAsDataURL(e[0]);
}

function importOTA(e){
    const reader = new FileReader();
    showLoading();
    reader.addEventListener('load', (event) => {
        var data=event.target.result.split("base64,")[1];
        //var buffer = event.target.result;
        //var uint8Arr=new Uint8Array(buffer);
        //var data=new Blob([uint8Arr],{type:'audio/mp3'});
        //var md5_str =  md5(data);
        var md5_str =  md5(data);
        //console.log(data);
        //console.log(md5_str);
        var settings = {
            "url": _api_uploadOTAFile,
            "type": "POST",
            "timeout": 0,
            "cache":false,
            "headers": {
                "Content-Type": "text/plain",
                "md5": md5_str
            },
            "data": data
        };
        
        $.ajax(settings).success(function (response) {
            if(response.state!=200){
                //alert("Update req error: "+response.msg);
                alert(_language.system.OTA_err+response.msg);
                hideLoading();
            }
            else{
                //alert("Request sent successfully. Please wait upload FW.");
                alert(_language.system.OTA_req_OK);
                OTAcheck(false);
            }
    
        }).error(function(e){
            console.log("Update error.");
            console.log(e);
    
            hideLoading();
        });
    });
    //reader.readAsArrayBuffer(e[0]);
    reader.readAsDataURL(e[0]);
}


function loadSystemSetting(async,callback){
    var settings = {
        "url": _api_sysSetting,
        "type": "GET",
        "timeout": 5000,
        "async":async
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Load system setting req error: "+response.msg);
            alert(_language.system.load_err+response.msg);
            if(typeof(callback)==="function")
                callback(null);
        }
        else{
            if(typeof(callback)==="function")
                callback(response.data);
        }

    }).error(function(e){
        //alert("Load system setting req error." + e.statusText);
        alert(_language.system.load_req_err + e.statusText);
        if(typeof(callback)==="function")
            callback(null);
    });
}

function loadInputBox(data){
    //console.log(data);
    _apOldPw = data.ap.passwd;
    $("#apName").val(data.ap.name);

    if(data.work.enable=="1")
        $("input[name='enableSample'][value='enable']").attr('checked',true);
    else
        $("input[name='enableSample'][value='disable']").attr('checked',true);

    $("#ftpUsername").val(data.ftp.name);
    $("#ftpUserpwView").val(data.ftp.pwd);
    $("#ftpUserpw").val(data.ftp.pwd);
    $(".uploadFTPType").val(data.ftp.type);

    $("#statusIp").val(data.status.ip);
    $("#statusProxy").val(data.status.proxy);
    
    
    $("#webIp").val(data.server.ip);
    $("#webProxy").val(data.server.proxy);
    $("#ntpIp").val(data.ntp.ip);
    $("#ftpIp").val(data.ftp.ip);
    $("#ntpProxy").val(data.ntp.proxy);
    $("#ftpProxy").val(data.ftp.proxy);
    
    
    $("#sgIp").val(data.mqtt.ip);
    $("#sgPort").val(data.mqtt.port);
    $("#sgTopic").val(data.mqtt.topic);
    $("#sgUser").val(data.mqtt.name);
    $("#sgUserpw").val(data.mqtt.passwd);
    $("#sgUserpwView").val(data.mqtt.passwd);
    
    $("select[name='changeLanguage']").val(data.language.value);
    
    //console.log(data);
    loadInterIP(data.lan,"lan");
    loadInterIP(data.lan2,"lan2");
    loadInterIP(data.wifi,"wifi");
    /*
    if((data.lan.ip != "..." && data.lan.ip!="") ||
        (data.lan.mask != "..." && data.lan.mask!="") ||
        (data.lan.getway != "..." && data.lan.getway!="")){
        $("input[name='lanSetting'][value='manual']").attr('checked',true);
        loadIP(data.lan.ip,"lanIp");
        loadIP(data.lan.mask,"lanMk");
        loadIP(data.lan.getway,"lanGw");
        $('.lanInput').attr('disabled', false);
        $('.lanInput').css('opacity', "1");
    }
    else{
        $("input[name='lanSetting'][value='auto']").attr('checked',true);
        loadIP("...","lanIp");
        loadIP("...","lanMk");
        loadIP("...","lanGw");
        $('.lanInput').attr('disabled', true);
        $('.lanInput').css('opacity', "0.5");
    }
    */
    if(data.server.type=="1")
        $("input[name='uploadData2Server'][value='enable']").attr('checked',true);
    else
        $("input[name='uploadData2Server'][value='disable']").attr('checked',true);
}

function loadInterIP(data,name){
    if((data.ip != "..." && data.ip!="") ||
        (data.mask != "..." && data.mask!="") ||
        (data.getway != "..." && data.getway!="")){
        $("input[name='"+name+"Setting'][value='manual']").attr('checked',true);
        loadIP(data.ip,name+"Ip");
        loadIP(data.mask,name+"Mk");
        loadIP(data.getway,name+"Gw");
        $('.'+name+'Input').attr('disabled', false);
        $('.'+name+'Input').css('opacity', "1");
    }
    else{
        $("input[name='"+name+"Setting'][value='auto']").attr('checked',true);
        loadIP("...",name+"Ip");
        loadIP("...",name+"Mk");
        loadIP("...",name+"Gw");
        $('.'+name+'Input').attr('disabled', true);
        $('.'+name+'Input').css('opacity', "0.5");
    }
    
}

function loadIP(data,name){
    var ip_arr = data.split(".");
    if(ip_arr.length==4)
        for(var i =0;i<ip_arr.length;i++)
            $("#"+name+(i+1)).val(ip_arr[i]);
}


function getIP(name){
    var ret="";
    for(var i =0;i<4;i++){
        if(i>0)
            ret +=".";
        ret+= $("#"+name+(i+1)).val();
    }
    return ret;
}


function isIP(ip){
    var exp=/^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
    return exp.test(ip); 
}
function isHostname(ip){
    var exp=/^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$/;
    return exp.test(ip); 
}


function getForm(){
    var ret = {};
    ret.ntp={};
    ret.lan={};
    ret.lan2={};
    ret.wifi={};
    ret.server={};
    ret.ftp={};
    ret.status={};
    ret.mqtt={};
    ret.ntp.ip = $("#ntpIp").val();
    ret.ntp.proxy = $("#ntpProxy").val();
    ret.server.ip = $("#webIp").val();
    ret.server.proxy = $("#webProxy").val();
    ret.server.type = "0";
    ret.mqtt.ip = $("#sgIp").val();
    ret.mqtt.port = $("#sgPort").val();
    ret.mqtt.topic = $("#sgTopic").val();
    ret.mqtt.name = $("#sgUser").val();
    ret.mqtt.passwd = $("#sgUserpw").val();
    ret.status.ip = $("#statusIp").val();
    ret.status.proxy = $("#statusProxy").val();
    if($("input[name='uploadData2Server']:checked").val()=="enable")
        ret.server.type = "1";
    ret.ftp.ip = $("#ftpIp").val();
    ret.ftp.name = $("#ftpUsername").val();
    ret.ftp.pwd = $("#ftpUserpw").val();
    ret.ftp.type = $(".uploadFTPType").val();
    ret.ftp.proxy = $("#ftpProxy").val();
    getIPsetting(ret.lan,"lan");
    getIPsetting(ret.lan2,"lan2");
    getIPsetting(ret.wifi,"wifi");
    
    return ret;
    /*
    {
        "ntp": {
            "ip": "192.168.0.2"
        },
        "ap": {
            "passwd": "00000000"
        },
        "wifi": {
            "ssid": "",
            "passwd": ""
        },
        "lan": {
            "ip": "192.168.0.0",
            "mask": "255.255.255.0",
            "getway": "255.255.255.0"
        },
        "server": {
            "ip": "192.168.0.1"
        },
        "ftp": {
            "ip": "192.168.0.0",
            "name": "account",
            "pwd": "password"
        },
        "work": {
            "enable": "0"
        },
        "sensor_test": {
            "enable": "1",
            "mexsec": "120"
        },
        "seg_test": {
            "enable": "0"
        }
    }
    */
}

function getIPsetting(obj,name){
    if($("input[name='"+name+"Setting']:checked").val() == "manual"){
        obj.ip = getIP(name+"Ip");
        obj.mask = getIP(name+"Mk");
        obj.getway = getIP(name+"Gw");
    }
    else{
        obj.ip = "...";
        obj.mask = "...";
        obj.getway = "...";
    }
}

function compareObject(x, y){
    if(x === y)
        return true;
    else if ((typeof x == "object" && x != null) && (typeof y == "object" && y != null)) {
        if (Object.keys(x).length != Object.keys(y).length)
        return false;
    
        for (var prop in x) {
            if (y.hasOwnProperty(prop))
            {  
                if(typeof(x[prop])=="object" && typeof(y[prop])=="object" ){
                    if(! compareObject(x[prop], y[prop]))
                        return false;
                }
                else if(x[prop] != y[prop])
                    return false;
            }
            else
                return false;
        }
        return true;
    }
    else 
        return false;
}
