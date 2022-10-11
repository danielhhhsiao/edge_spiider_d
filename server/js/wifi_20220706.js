var _api_wifi = "/api/wifi";
var _refreshPerial = 10000;
var _wifiRefreshTimer=null;

$(function(){
    refreshWifi();
});
function refreshWifi(){
    console.log("wifi refresh.")
    var settings = {
        "url": _api_wifi,
        "type": "GET",
        "timeout": 0,
      };
      
    $.ajax(settings).success(function (response) {
        if(response.state==200){
            var view=document.getElementById( 'view' );
            view.innerHTML="";

            var wifi = response.data.wifi;
            for(var i=0 ; i<wifi.length;i++)
                if(wifi[i].connected==1)
                    create(wifi[i]);
            for(var i=0 ; i<wifi.length;i++)
                if(wifi[i].connected!=1)
                    create(wifi[i]);
        }
        else{
            console.log("wifi list req error:");
            console.log(response);
        }

        clearTimeout(_wifiRefreshTimer);
        _wifiRefreshTimer=setTimeout(refreshWifi,_refreshPerial);
    }).error(function(e){
        
        document.getElementById( 'view' ).innerHTML="";
        console.log("get wifi list error.");
        console.log(e);
        
        clearTimeout(_wifiRefreshTimer);
        _wifiRefreshTimer=setTimeout(refreshWifi,_refreshPerial);
    });
}
function create(data){
    var view=document.getElementById( 'view' );
    //console.log(data);
    var level=Math.floor((data.level-1)/25);
    level=(level<0)?0:level;
    var LOCK=0;
    var color="secColor";
    if(data.type!=0)
        LOCK=1;
    if(data.connected==1){
        LOCK=2;
        color="niceColor";
    }
    var box = document.createElement( 'div' );
    var pre = document.createElement( 'div' );
    var SSID = document.createElement( 'div' );
    var next = document.createElement( 'div' );
    SSID.innerHTML=data.ssid;
    box.setAttribute("id", "box");
    box.setAttribute("ssid", data.ssid);
    box.setAttribute("lock", LOCK);
    box.className = 'wifiSelect box '+color;
    pre.className = 'pre lock'+LOCK;
    SSID.className = 'SSID';
    next.className = 'next wifi'+level;
    box.appendChild(pre);
    box.appendChild(SSID);
    box.appendChild(next);
    view.appendChild(box);
}

$(document).on("click",".wifiSelect",function(){
    var ssid = $(this).attr("ssid");
    var lock = $(this).attr("lock");
    if(lock=="0"){
        //if(confirm("Are you sure that?\nConnect \""+ssid+"\".")){
        if(confirm(_language.wifi.connect+"\""+ssid+"\".")){
            connectWifi(ssid,"");
        }
    }
    else if(lock=="1"){
        //if(pass = prompt("Please input the password.","")){
        if(pass = prompt(_language.wifi.input_passwd,"")){
            connectWifi(ssid,pass);
        }

    }
    else if(lock=="2"){
        //if(confirm("Are you sure that?\nDisconnect \""+ssid+"\".")){
        if(confirm(_language.wifi.disconnect+"\""+ssid+"\".")){
            disconnectWifi();
        }
    }
});

function connectWifi(ssid,passwd){
    showLoading();
    document.getElementById( 'view' ).innerHTML="";
    var settings = {
        "url": _api_wifi,
        "type": "PUT",
        "timeout": 0,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "wifi": {
                "ssid": ssid,
                "passwd": passwd
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            console.log("connect wifi req error:");
            console.log(response);
        }
        else{
            //alert("Request sent successfully. Please wait a moment.");
            alert(_language.wifi.req_OK);
        }
        
        clearTimeout(_wifiRefreshTimer);
        _wifiRefreshTimer=setTimeout(refreshWifi,3000);
        hideLoading();
    }).error(function(e){
        console.log("connect wifi error.");
        console.log(e);

        clearTimeout(_wifiRefreshTimer);
        _wifiRefreshTimer=setTimeout(refreshWifi,3000);
        hideLoading();
    });
}


function disconnectWifi(){
    showLoading();
    document.getElementById( 'view' ).innerHTML="";
    var settings = {
        "url": _api_wifi,
        "type": "DELETE",
        "timeout": 0,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        }
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            console.log("disconnect wifi req error:");
            console.log(response);
        }
        else{
            //alert("Request sent successfully. Please wait a moment.");
            alert(_language.wifi.req_OK);
        }

        clearTimeout(_wifiRefreshTimer);
        _wifiRefreshTimer=setTimeout(refreshWifi,3000);
        hideLoading();
    }).error(function(e){
        console.log("disconnect wifi error.");
        console.log(e);

        clearTimeout(_wifiRefreshTimer);
        _wifiRefreshTimer=setTimeout(refreshWifi,3000);
        hideLoading();
    });
}
