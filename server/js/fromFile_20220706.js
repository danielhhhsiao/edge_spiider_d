var _api_importSystemFile = "/api/system/file";
var _api_importSensorFile = "/api/work/file";

function topBarCallback(){
    
}

$(document).on("click","#ImportSubmitWork",function(){
    //if(confirm("This operation will overwrite the original setting. Are you sure to execute？")){
    if(confirm(_language.check_over_setting)){
        $("#ImportSubmitSelectWork").val(null);
        $("#ImportSubmitSelectWork").click();
    }
});

$(document).on("click","#ImportSubmitSys",function(){
    //if(confirm("This operation will overwrite the original setting. Are you sure to execute？")){
    if(confirm(_language.check_over_setting)){
        $("#ImportSubmitSelectSys").val(null);
        $("#ImportSubmitSelectSys").click();
    }
});

function importFilesWork(e){
    importFiles(e,_api_importSensorFile)
}

function importFilesSys(e){
    importFiles(e,_api_importSystemFile)
}

function importFiles(e,path){
    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        showLoading();
        var data=event.target.result.split("base64,")[1];
        //console.log(data);
        //console.log(atob(data));
        var settings = {
            "url": path,
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
                //window.location.reload(); 
            }
    
            hideLoading();
        }).error(function(e){
            //console.log("import file error.");
            console.log("import file error.");
            console.log(e);
    
            hideLoading();
        });
    });
    reader.readAsDataURL(e[0]);
}
