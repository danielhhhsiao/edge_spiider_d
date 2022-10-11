var _api_heartbeat = "/api/device/heartbeat";
var _api_uploadOTAFile = "/api/system/ota";
var _OTAcheckPerial = 10000;
var _heartbeatPerial = 10000;
var _serverState = 0;
var _login = "/login";
function goToLogin(){
    var loginCheck = cookieFind("login");
    //console.log(loginCheck);
    if(loginCheck!="true"){
        window.location=_login;
    }
}

function initTopBar(name){

    var name = (typeof name !== 'undefined') ?  name : "AUO DAQ";
    if($("#topBar").length>0)
        $("#topBarName").html(name)
    else{
        var mainBox = document.createElement( 'div' );
        var nameBox = document.createElement( 'div' );
        var serverBox = document.createElement( 'div' );
        var serverDotBox = document.createElement( 'div' );
        var iconBox = document.createElement( 'div' );
        var iconBoxLink = document.createElement( 'a' );
        nameBox.innerHTML=name;
        mainBox.className="mainColor";
        serverDotBox.className="alertColor";
        if(cookieFind("serverState")!=""){
            var _serverState = parseInt(cookieFind("serverState"));
            if(_serverState==1){
                serverDotBox.className="niceColor";
            }
            else if(_serverState==2){
                serverDotBox.className="niceColor flicker";
            }
            else if(_serverState==3){
                serverDotBox.className="warnColor";
            }
            else if(_serverState==4){
                serverDotBox.className="warnColor flicker";
            }
        }
        
        
        mainBox.setAttribute("id", "topBar");
        serverBox.setAttribute("id", "topBarServer");
        serverDotBox.setAttribute("id", "topBarServerDot");
        iconBox.setAttribute("id", "topBarIcon");
        iconBoxLink.setAttribute("href", "/");
        nameBox.setAttribute("id", "topBarName");
        serverBox.addEventListener("click", serverCheck);
        mainBox.appendChild(nameBox);
        mainBox.appendChild(serverBox);
        serverBox.appendChild(serverDotBox);
        mainBox.appendChild(iconBoxLink);
        iconBoxLink.appendChild(iconBox);
        document.body.appendChild(mainBox);

        var load_box = document.createElement( 'div' );
        var load_box_BG = document.createElement( 'div' );
        var load_box_contein = document.createElement( 'div' );
        var load_box_contein_in = document.createElement( 'div' );
        var load_box_text = document.createElement( 'div' );
        var load_box_remind = document.createElement( 'div' );
        load_box.setAttribute("id","load_box");
        load_box_BG.setAttribute("id","load_box_BG");
        load_box_contein.setAttribute("id","load_box_contein");
        load_box_text.setAttribute("id","load_box_text");
        load_box_remind.setAttribute("id","load_box_remind");
        //load_box_text.innerHTML="Load";
        load_box_text.innerHTML=_language.topBar.load;
        load_box.appendChild(load_box_BG);
        load_box.appendChild(load_box_contein);
        load_box_contein.appendChild(load_box_contein_in);
        load_box_contein_in.appendChild(load_box_text);
        load_box_contein_in.appendChild(load_box_remind);
        document.body.appendChild(load_box);

        setTimeout(loadAnimate,10,0);
        setTimeout(heartbeat,10,function(){
			OTAcheck(true,function(){
				setTimeout(function(){
					hideLoading();
					if(typeof(topBarCallback)==="function")
						topBarCallback();
				},200);
			});
			},function(){
				setTimeout(function(){
					hideLoading();
					if(typeof(topBarCallback)==="function")
						topBarCallback();
				},200);
			});
    }
}
function serverCheck(){
    if(_serverState==1)
        alert(_language.topBar.status_idel_connected);
        //alert("SPIIDER-D idle, and status server is connected");
    else if(_serverState==2)
        alert(_language.topBar.status_work_connected);
        //alert("SPIIDER-D work, and status server is connected");
    else if(_serverState==3)
        alert(_language.topBar.status_idel_disconnected);
        //alert("SPIIDER-D idle, but status server is disconnected");
    else if(_serverState==4)
        alert(_language.topBar.status_work_disconnected);
        //alert("SPIIDER-D work, but status server is disconnected");
    else 
        alert(_language.topBar.status_DAQ_disconnected);
        //alert("SPIIDER-D is disconnected");
}
function loadAnimate(sw){
        sw=sw%6;
        if(sw%2==0)
            $(".flicker").hide();
        else
            $(".flicker").show();
            
        var list=["",".","..","...","..","."];
        //$("#load_box_text").html(list[sw]);
        $("#load_box_text").html(_language.topBar.load + list[sw]);
        setTimeout(loadAnimate,500,sw+1);
}
function showLoading(remind){
    var _remind="";
    if(remind)
        _remind = remind;
    $("#load_box_remind").html(_remind);
    $("#load_box").show();
}
function hideLoading(){
    $("#load_box").hide();
    $("#load_box_remind").html("");
}

_isSPIIDER = true;
function heartbeat(callback,elseCallback){
    console.log("heartbeat refresh.");
    if($(".wifiMac").length>0){
        var settings = {
            "url": _api_heartbeat+"?all=all",
            "type": "GET",
            "timeout": 0
        };
    }
    else{
        var settings = {
            "url": _api_heartbeat,
            "type": "GET",
            "timeout": 0
        };
    }
      
    $.ajax(settings).success(function (response) {
        if(response.state==200){
			
            //console.log(hostname,response.data.environment.hostname);
            _isSPIIDER = response.data.environment.spiider;
            var hostname = cookieFind("hostname");
			if(_isSPIIDER){
				if(typeof(callback)=="function"){
					callback();
				}
				
				goToLogin();
				if(hostname!=response.data.environment.hostname){
					cookieAdd("login","false",0);
					cookieAdd("timecheck","false",0);
					//alert("Your device already change network and SPIIDER.");
					alert(_language.topBar.change_network);
					window.location=_login;
				}
			}
			else{
				var isPCCheck = cookieFind("isPC");
				if(isPCCheck!="true"){
					cookieAdd("isPC","true",0);
					window.location.reload(); 
				}
				if(typeof(elseCallback)=="function"){
					elseCallback();
				}
			}
            
            var timecheck = cookieFind("timecheck");
            var timestamp = Math.floor(response.data.environment.timestamp*1000);
            var timeStr = new Date(timestamp).Format("yyyy-MM-dd hh:mm:ss");
            var timestampNow = Date.now();
            var timeNow = new Date(timestampNow).Format("yyyy-MM-dd hh:mm:ss");
            if(timecheck!="true"){
                cookieAdd("timecheck","true",0);
                if(Math.abs(timestamp-timestampNow)>600000) //10min
                    //alert("SPIIDER-D time is "+timeStr+". Your device is "+timeNow+". Please update the time.");
                    alert(
                    _language.topBar.spiider_time
                    +timeStr
                    +_language.topBar.device_time
                    +timeNow
                    +_language.topBar.update_time
                    );
            }
            
            var newserverState=parseInt(response.data.environment.server_connect);
            if(newserverState!=_serverState){
                _serverState=newserverState;
                cookieAdd("serverState",response.data.environment.server_connect,0);
                if(_serverState==1){
                    $("#topBarServerDot").attr("class","niceColor");
                }
                else if(_serverState==2){
                    $("#topBarServerDot").attr("class","niceColor flicker");
                }
                else if(_serverState==3){
                    $("#topBarServerDot").attr("class","warnColor");
                }
                else if(_serverState==4){
                    $("#topBarServerDot").attr("class","warnColor flicker");
                }
                $("#topBarServerDot").show();
            }
            //console.log(response);
                
            if($(".version").length>0)
                $(".version").html(_language.form.version + response.data.environment.version)
            if($(".memoryCount").length>0){
                if(parseInt(response.data.environment.upload_queue)==0)
                    $(".memoryCount").html(_language.form.memoryCount + 0);
                else
                    $(".memoryCount").html(_language.form.memoryCount + response.data.environment.upload_queue);
            }
            if($(".localCount").length>0)
                $(".localCount").html(_language.form.localCount + response.data.environment.localCount)
            if($(".wifiMac").length>0)
                $(".wifiMac").html(_language.form.wifiMac + response.data.environment.wlanMac)
            if($(".wifiIP").length>0)
                $(".wifiIP").html(_language.form.wifiIP + response.data.environment.wlanIp)
            if($(".eth0Mac").length>0)
                $(".eth0Mac").html(_language.form.eth0Mac + response.data.environment.eth0Mac)
            if($(".eth0IP").length>0)
                $(".eth0IP").html(_language.form.eth0IP + response.data.environment.eth0Ip)
            if($(".eth1Mac").length>0)
                $(".eth1Mac").html(_language.form.eth1Mac + response.data.environment.eth1Mac)
            if($(".eth1IP").length>0)
                $(".eth1IP").html(_language.form.eth1IP + response.data.environment.eth1Ip)
            if($(".st1ErrMsg").length>0)
                $(".st1ErrMsg").html(_language.form.st1ErrMsg + response.data.environment.st1_err_msg)
            if($(".st2ErrMsg").length>0)
                $(".st2ErrMsg").html(_language.form.st2ErrMsg + response.data.environment.st2_err_msg)
            if($(".systemTime").length>0){
                $(".systemTime").html(_language.form.systemTime + timeStr);
            }
            if($(".uploadTimeAPI").length>0){
                if(response.data.environment.time_api!="--"){
                    var timestamp = Math.floor(parseFloat(response.data.environment.time_api)*1000);
                    var timeStr = new Date(timestamp).Format("yyyy-MM-dd hh:mm:ss");
                    $(".uploadTimeAPI").html(_language.form.uploadTimeAPI + timeStr);
                }
                else
                    $(".uploadTimeAPI").html(_language.form.uploadTimeAPI + response.data.environment.time_api)
            }
            if($(".uploadTimeFTP").length>0){
                if(response.data.environment.time_ftp!="--"){
                    var timestamp = Math.floor(parseFloat(response.data.environment.time_ftp)*1000);
                    var timeStr = new Date(timestamp).Format("yyyy-MM-dd hh:mm:ss");
                    $(".uploadTimeFTP").html(_language.form.uploadTimeFTP + timeStr);
                }
                else
                    $(".uploadTimeFTP").html(_language.form.uploadTimeFTP + response.data.environment.time_ftp)
            }
            if($(".uploadTimeMQTT").length>0){
                if(response.data.environment.time_mqtt!="--"){
                    var timestamp = Math.floor(parseFloat(response.data.environment.time_mqtt)*1000);
                    var timeStr = new Date(timestamp).Format("yyyy-MM-dd hh:mm:ss");
                    $(".uploadTimeMQTT").html(_language.form.uploadTimeMQTT + timeStr);
                }
                else
                    $(".uploadTimeMQTT").html(_language.form.uploadTimeMQTT + response.data.environment.time_mqtt)
            }
            if($(".uploadTimeStatus").length>0){
                if(response.data.environment.time_status!="--"){
                    var timestamp = Math.floor(parseFloat(response.data.environment.time_status)*1000);
                    var timeStr = new Date(timestamp).Format("yyyy-MM-dd hh:mm:ss");
                    $(".uploadTimeStatus").html(_language.form.uploadTimeStatus + timeStr);
                }
                else
                    $(".uploadTimeStatus").html(_language.form.uploadTimeStatus + response.data.environment.time_status)
            }
            
        }
        else{
            console.log("heartbeat req error:");
            console.log(response);
        }

        _refreshTimer=setTimeout(heartbeat,_heartbeatPerial);
    }).error(function(e){
        _serverState=0;
        cookieAdd("serverState","0",0);
        $("#topBarServerDot").attr("class","alertColor");
        $("#topBarServerDot").show();
        console.log("get heartbeat error.");
        console.log(e);
        _refreshTimer=setTimeout(heartbeat,_heartbeatPerial);
    });
}

function OTAcheck(first,callback){
    console.log("OTAcheck.");
    var settings = {
        "url": _api_uploadOTAFile,
        "type": "GET",
        "timeout": 0
    };
      
    $.ajax(settings).success(function (response) {
        var done = false;
        if(response.state==200){
            if(response.data.code=="1" || response.data.code=="2"){ //keep wait
                if(first){
                    //alert("Upload FW not finish. Please wait!");
                    alert(_language.topBar.FW_not_finish);
                }
                _refreshTimer=setTimeout(OTAcheck,_OTAcheckPerial,false,callback);
            }
            else if(response.data.code=="3"){
                //alert("Upload successfully.");
                alert(_language.topBar.FW_upload_OK);
                done=true;
            }
            else if(response.data.code=="4"){
                //alert("Upload fail. msg : "+response.data.msg);
                alert(_language.topBar.FW_upload_error+response.data.msg);
                done=true;
            }
            else if(response.data.code=="0"){
                if(typeof(callback)==="function")
                    callback();
            }
        }
        else{
            console.log("OTAcheck req not 200:");
            console.log(response);
            _refreshTimer=setTimeout(OTAcheck,_OTAcheckPerial,false,callback);
        }
        
        if(done){
            var settings = {
                "url": _api_uploadOTAFile,
                "type": "PUT",
                "timeout": 10000,
                "cache":false,
                "headers": {
                    "Content-Type": "application/json"
                }
            };
            $.ajax(settings).success(function (response) {
                if(typeof(callback)==="function")
                    callback();
                
                window.location.reload(); 
            }).error(function(e){
                console.log(e.statusText);
                _refreshTimer=setTimeout(OTAcheck,_OTAcheckPerial,false,callback);
            });    
        }
    }).error(function(e){
        console.log("OTA error."+e);
        _refreshTimer=setTimeout(OTAcheck,_OTAcheckPerial,false,callback);
    });
}


