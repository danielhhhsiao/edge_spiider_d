var _api_pin = "/api/pin";
var _home= "/home";

$(document).on("keyup",'#pinPw', function(e) {
    if (e.keyCode == 13) {
        loginValidat();
    }
});

$(document).on("keyup",'#pinPwHide', function(e) {
    if (e.keyCode == 13) {
        loginValidat();
    }
});

$(document).on("click","#pinSubmit",loginValidat);
var runValidat=false;
function loginValidat(){
    if(runValidat)
        return;
    runValidat = true;
    var pinPw = $("#pinPw").val();
    if(pinPw.length<4){
        alert("The password length cannot be less than 4.");
        runValidat = false;
        return;
    }
    if(pinPw.length>8){
        alert("The password length cannot be more than 8.");
        runValidat = false;
        return;
    }

    var settings = {
        "url": _api_pin,
        "type": "POST",
        "timeout": 10000,
        "cache":false,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "pin":{
                "pwd":pinPw
            }
        }),
    };
    $.ajax(settings).success(function (response) {
        if(response.state==501){
            alert("Password error");
        }
        else if(response.state!=200){
            alert("PIN req error: "+response.msg);
        }
        else{
            //console.log(cookieFind("login"));
            cookieAdd("login","true",0);
            cookieAdd("hostname",response.hostname,0);
            window.location=_home;
        }
        runValidat = false;
    }).error(function(e){
        alert("PIN request error. Please check connection with SPIIDER-D.");
        runValidat = false;
    });

}
