var _api_loadFEPlist = "/api/server/featureExtraction";
var _api_refreshSensorList = "/api/sensor/list";
var _api_sensorConfig = "/api/sensor/config";
var _api_testStates = "/api/sensor/test";
var _api_segConfig = "/api/segmentation/config";
var _api_importSensorFile = "/api/work/file";
var _api_workStates = "/api/work/state";
var _api_sysSetting = "/api/system/config";

var _oldForm=null;

var _maxTestSec=601;
var _maxSegRule=16;
var _maxSensorDaughter=4;
var _maxSensorDistange=1;
var _maxPrognosisSerial=1;
var _maxMicrophon=1;
var _maxModbus=1;
var _maxSensorSerial=4;
var _maxSensorDI=1;
var _maxAnalogChannelNum=8;
var _maxVibChannelNum=6;
var _maxDIChannelNum=4;
var _maxUSBNum=2;
var _maxSerialNum=4;
var _loadFEPlist=[];
var _currenFEObj=null;

// name will be vibration / voltageInput / currentInput / none / ""
// "" meaning is not data load
var _sensorListDef = {
    "bus":[
        {
            "name":""
        },{
            "name":""
        },{
            "name":""
        },{
            "name":""
        }
    ]
};

var _sensorList = _sensorListDef;
var _voltage_range = ["1.5","3.3","5","6","10","12"];
var _voltage_level = ["6","5","4","3","2","1"];
var _current_list_value = [
    ["200m","100m","25m","2m","1m","0.25m"],
    ["4m ~ 20mA"],
    ["15","1.5","0.75","0.2"],
    ["80","5.6","2.8","0.7"],
    ["120","75","5.6","2.8","0.7"],
    ["120","50","3.8","1.9","0.5"],
    ["200","75","5.6","2.8","0.7"],
    ["300","200","50","3.8","1.9","0.5"],
    ["360","300","75","5.6","2.8","0.7"],
    ["400","200","50","3.8","1.9","0.5"]
];
var _current_list_level = [
    ["4","5","6","1","2","3"],
    ["6"],
    ["4","1","2","3"],
    ["6","1","2","3"],
    ["4","6","1","2","3"],
    ["4","6","1","2","3"],
    ["4","6","1","2","3"],
    ["4","5","6","1","2","3"],
    ["4","5","6","1","2","3"],
    ["4","5","6","1","2","3"]
];
/*
var _current_list_value = [
    ["0.25m","1m","2m","25m","100m","200m"],
    ["4m ~ 20mA"],
    ["0.2","0.75","1.5","15"],
    ["0.7","2.8","5.6","75","80"],
    ["0.7","2.8","5.6","75","120"],
    ["0.5","1.9","3.8","50","120"],
    ["0.7","2.8","5.6","75","200"],
    ["0.5","1.9","3.8","50","200","300"],
    ["0.7","2.8","5.6","75","300","360"],
    ["0.5","1.9","3.8","50","200","400"]
];
var _current_list_level = [
    ["3","2","1","6","5","4"],
    ["6"],
    ["3","2","1","4"],
    ["3","2","1","6","4"],
    ["3","2","1","6","4"],
    ["3","2","1","6","4"],
    ["3","2","1","6","4"],
    ["3","2","1","6","5","4"],
    ["3","2","1","6","5","4"],
    ["3","2","1","6","5","4"]
];
* */
var _current_list = [
    "Current",
    "Communication protocol",
    "CTL-6-S32-8F-CL",
    "CTL-10-CLS",
    "CTL-16-CLS",
    "CTU-22-CLF",
    "CTL-24-CLSF",
    "CTL-24-CLS",
    "CTU-24-CLF",
    "CTL-36-CLS"
];
var _DE_list = [
    "Differential",
    "Single-ended"
];
var _DE_list_value = [
    "d",
    "s"
];
var _vib_range = [
    "-2 ~ 2 G",
    "-4 ~ 4 G",
    "-8 ~ 8 G",
    "-16 ~ 16 G"
];

var _porgnosis_vib_sour = ["VPA308R","VPA30816"];
var _porgnosis_vib_sour_defualt = "VPA308R";
var _porgnosis_vib_range = {
    "VPA308R":[
        "-2 ~ 2 G",
        "-4 ~ 4 G",
        "-8 ~ 8 G"
    ],
    "VPA30816":[
        "-2 ~ 2 G",
        "-4 ~ 4 G",
        "-8 ~ 8 G",
        "-16 ~ 16 G"
]};
var _porgnosis_vib_range_val = {
    "VPA308R":[
        "2",
        "4",
        "8"
    ],
    "VPA30816":[
        "2",
        "4",
        "8",
        "16"
]};
var _porgnosis_vib_range_val_defualt = {
    "VPA308R":"4",
    "VPA30816":"4"
};
var _porgnosis_vib_fs={
    "VPA308R":[
        "125",
        "250",
        "500",
        "1000",
        "2000",
        "4000"
    ],
    "VPA30816":[
        "833",
        "1667",
        "3333",
        "6667",
        "13333"//,"26667"
]};
var _porgnosis_vib_fs_defualt = {
    "VPA308R":"4000",
    "VPA30816":"13333" //"26667"
};
var _porgnosis_usb_location = ["1-1.6","1-1.2"];


var _modbus_baud = ["1200","2400","4800","9600","19200","38400","57600","115200"];
var _modbus_baud_default = "9600"; 
var _modbus_length = ["7","8"];
var _modbus_length_default = "8"; 
var _modbus_parity = ["None","Odd","Even","Mark","Space"];
var _modbus_parity_default = "None"; 
var _modbus_stop_bit = ["1","2"];
var _modbus_stop_bit_default = "1"; 
var _modbus_check = ["CRC"];
var _modbus_check_default = "CRC"; 
var _modbus_type = ["float32","int8","int16","int32","uint8","uint16","uint32","BCD","bit8","bit16"];
var _modbus_type_default = "int16"; 
var _modbus_order = ["LSB","MSB"];
var _modbus_order_default = "LSB"; 
var _modbus_usb_location = ["1-1.6","1-1.2","1-1.3:1.0","1-1.3:1.2"];

        
var _inputCheckList=[{
        "preObj":"",
        "isTrue":"",
        "default":"",
        "class":".segOperationLen",
        "min":0.1,
        "max":600
    },
    {
        "preObj":"",
        "isTrue":"",
        "default":"",
        "class":".segIgnoreLen",
        "min":0,
        "max":-1
    },
    {
        "preObj":"",
        "isTrue":"",
        "default":"",
        "class":".segThreshold",
        "min":-1,
        "max":-1
    },
    {
        "preObj":".centerFrequencySelect",
        "isTrue":"Yes",
        "default":"-1",
        "class":".centerFrequency",
        "min":1,
        "max":-1
    },
    {
        "preObj":"",
        "isTrue":"",
        "default":"",
        "class":".signalPadding",
        "min":0,
        "max":-1
    },
    {
        "preObj":"",
        "isTrue":"",
        "default":"",
        "class":".segShift",
        "min":-10,
        "max":10
    },
    {
        "preObj":".subOperation",
        "isTrue":"Yes",
        "default":0,
        "class":".subOperationSec",
        "min":0.01,
        "max":900
    },
    {
        "preObj":".signalFilter",
        "isTrue":"Yes",
        "default":0,
        "class":".signalFilterSec",
        "min":0.01,
        "max":-1
    },
    {
        "preObj":".uploadResultSeg",
        "isTrue":"Yes",
        "default":0,
        "class":".uploadResultSegInterval",
        "min":0,
        "max":-1
    },
    {
        "preObj":".loopModeForRule",
        "isTrue":"Yes",
        "default":0,
        "class":"#loopTimeForRule",
        "min":60,
        "max":-1
    },
    {
        "preObj":".uploadResultFE",
        "isTrue":"Yes",
        "default":-1,
        "class":".featureSelectBtn",
        "min":1,
        "max":-1,
        "callback":function(Obj){
                Obj=$(Obj);
                var fedata = Obj.attr("fedata");
                var flag = 0;
                if(typeof(fedata)=="undefined")
                    flag=1;
                else if(fedata=="")
                    flag=1;
                else{
                        try{
                            JSON.parse(fedata);
                        }
                        catch(e){
                            flag=2;
                        }
                }
                    
                if(flag==1){
                    //alert("Please upload feature extraction format json file.");
                    alert(_language.sample.FE_json_check);
                    Obj.focus();
                    return false;
                }
                if(flag==2){
                    //alert("Feature extraction format file content error.");
                    alert(_language.sample.FE_json_file_err);
                    Obj.focus();
                    return false;
                }
                return true;
            }
    },
    {
        "preObj":".triggerEnable",
        "isTrue":"Yes",
        "default":0,
        "class":".triggerShift",
        "min":-10,
        "max":10
    },
    {
        "preObj":".triggerEnable",
        "isTrue":"Yes",
        "default":0,
        "class":".triggerThreshold",
        "min":-1,
        "max":-1
    }
];

// program start point
function topBarCallback(){
    
    showLoading();
    _DE_list = [
        _language.sample.sensor_differential,
        _language.sample.sensor_single_ended
    ];
        
    //loadFEPlist();
    refreshSensor();

    var config = {}
    loadSetting(false,"Sensor",_api_sensorConfig,function(data){
		config.sensor = data;
    });
    loadSetting(false,"Segmentation",_api_segConfig,function(data){
        config.seg = data;
    });
    loadSetting(false,"System",_api_sysSetting,function(data){
        config.system = data;
    });
    console.log(config);
    loadForm(config);
    

    $(document).scrollTop(0);
    _oldForm = getForm();
    //console.log(_oldForm);
	
	if(_isSPIIDER){
		$("#offlineTest").hide();
	}
	else{
		$("#oldSensorTest").hide();
		$("#sensorTest").hide();
	}
    
    if(config.system.sensor_test.enable!="0" && config.system.work.enable=="0"){
        //alert("Testing is continue. Please wait processing.");
        alert(_language.sample.keep_test_alert);
        
        delayToWaitTest(1000);
    }
    else
        hideLoading();
        
    //showRegisterBox("","");
}

window.onbeforeunload=function(e){
    var nowData = getForm();
    if(! compareObject(nowData,_oldForm)){
        console.log(nowData);
        console.log(_oldForm);
        var e=window.event||e;
        //e.returnValue=("There are forms that have not been saved. Are you sure to leave the page?");
        e.returnValue=(_language.check_left_page);
    }
}

var _oldPageHeight=0;
document.addEventListener('scroll',function(e){
    var bH = document.body.clientHeight;
    if(bH!=_oldPageHeight){
        _oldPageHeight = bH;
        refreshRuleHeight();
    }
    else{
        refreshBottomInfo();
    }
});

var _ruleHeight=[];
function refreshRuleHeight(){
    _ruleHeight=[];
    var segRule = $(".segRule");
    var offset = $("#segContainer")[0].getBoundingClientRect().top;
    for(var i=0;i<segRule.length;i++){
        var obj = segRule.eq(i);
        var neme = obj.find(".segRuleName").val();
        neme += "@"+obj.find(".segRuleUnit").val();
        neme += obj.find(".segRuleSubunit").val();
        _ruleHeight.push({
            "name":neme,
            "top":obj[0].getBoundingClientRect().top-offset
            });
    }
    _ruleHeight.push({
        "name":"",
        "top":$("#segAddBox")[0].getBoundingClientRect().top-offset
        });
    
    //console.log(_ruleHeight);
    refreshBottomInfo();
}
function refreshBottomInfo(){
    var offset = $("#segContainer")[0].getBoundingClientRect().top;
    var windowH = 0;
    if(offset==0)
        $(".bottomInfo").hide();
    else{
        $(".bottomInfo").show();
        var scroll = window.scrollY;
        var screenHalfH = screen.height/2;
        //console.log("scroll",scroll);
        for(var i=0;i<_ruleHeight.length;i++){
            if(scroll>=_ruleHeight[i].top-screenHalfH){
                $(".bottomInfo").html(_language.sample.seg_edit+_ruleHeight[i].name);
            }
        }
    }
        
}
$(document).on("change",".segRuleName",function(){
    refreshRuleHeight();
});
$(document).on("change",".segRuleUnit",function(){
    refreshRuleHeight();
});
$(document).on("change",".segRuleSubunit",function(){
    refreshRuleHeight();
});

$(document).on("change","select[name='sensorFs']",function(){
    var sensortype = $(this).parent().find(".sensorSelect").eq(0).find(".heddened").find(".sensorChName").attr("sensortype");
    if(sensortype=="vibration"){
        var sensorFs = parseInt($(this).val());
        if(sensorFs==8000){ //disable even channel setting when fs=8kHz
            var enableChannel = $(this).parent().find(".sensorSelect").find(".showHeddened").find(".enableChannel");
            for(var i=0;i<enableChannel.length;i++){
                if(enableChannel.eq(i).attr("checked")=="checked" && i%2==1){
                    var target = enableChannel.eq(i).parent().parent().prevAll(".popBtn").eq(0);
                    enableChannel.eq(i).attr("checked",false);
                    target.css("background-color","");
                    target.css("color","");
               }
            }
            
        }
    }
});

$(document).on("click",".topTab",function(){
    $(".topTab").attr("class","topTab");
    $(this).attr("class","topTab topTabFocus");
    var className = $(this).attr("data-show");
    $(".topTabHide").hide();
    $("."+className).show();
    window.document.body.scrollTop=0;
    window.document.documentElement.scrollTop=0;
    refreshRuleHeight();
});

$(document).on("click",".popBtn",function(){
    var sensortype = $(this).nextAll(".sensorSelect").eq(0).find(".heddened").find(".sensorChName").attr("sensortype");
    var show=true;
    if(sensortype=="vibration"){
        var sensorFs = parseInt($(this).parent().find("select[name='sensorFs']").val());
        var sensorNum = parseInt($(this).val().split(" ")[1]);
        if(sensorFs==8000 && sensorNum%2==0){ //avoid open even channel setting when fs=8kHz
            alert(_language.sample.Sample_rate_alert);
            show=false;
        }
    }
    
    if(show){
        $(this).nextAll(".sensorSelect").eq(0).attr("class","nestBox sensorSelect popWindow");
        $("#popWindowMask").show();
    }
});

$(document).on("click",".popFeatureBtn",function(){
    showManualFeatureBox();
});
$(document).on("click",".popFeatureOKBtn",function(){
    hideManualFeatureBox();
});

$(document).on("click",".targetFeature",function(){
    var enable = $(this).attr("enable");
    if(enable=="1"){
        $(this).attr("enable","0");
        $(this).css("background-color","");
        $(this).css("color","");
    }
    else{
        $(this).attr("enable","1");
        $(this).css("background-color","rgb(98, 152, 234)");
        $(this).css("color","#FFF");
    }
});

$(document).on("click",".manualFeatureDefaultBtn",function(){
    $('#targetFeatureMean').attr("enable","0");
    $('#targetFeatureMean').css("background-color","");
    $('#targetFeatureMean').css("color","");
    $('#targetFeatureMax').attr("enable","0");
    $('#targetFeatureMax').css("background-color","");
    $('#targetFeatureMax').css("color","");
    $('#targetFeatureMin').attr("enable","0");
    $('#targetFeatureMin').css("background-color","");
    $('#targetFeatureMin').css("color","");
    $('#targetFeatureP2P').attr("enable","0");
    $('#targetFeatureP2P').css("background-color","");
    $('#targetFeatureP2P').css("color","");
    $('#targetFeatureStd').attr("enable","0");
    $('#targetFeatureStd').css("background-color","");
    $('#targetFeatureStd').css("color","");
    
    $('#targetFeatureRms').attr("enable","1");
    $('#targetFeatureRms').css("background-color","rgb(98, 152, 234)");
    $('#targetFeatureRms').css("color","#FFF");
    $('#targetFeatureVelRms').attr("enable","1");
    $('#targetFeatureVelRms').css("background-color","rgb(98, 152, 234)");
    $('#targetFeatureVelRms').css("color","#FFF");
    $('#targetFeatureLowPsdRms').attr("enable","1");
    $('#targetFeatureLowPsdRms').css("background-color","rgb(98, 152, 234)");
    $('#targetFeatureLowPsdRms').css("color","#FFF");
    $('#targetFeatureMidPsdRms').attr("enable","1");
    $('#targetFeatureMidPsdRms').css("background-color","rgb(98, 152, 234)");
    $('#targetFeatureMidPsdRms').css("color","#FFF");
    $('#targetFeatureHighPsdRms').attr("enable","1");
    $('#targetFeatureHighPsdRms').css("background-color","rgb(98, 152, 234)");
    $('#targetFeatureHighPsdRms').css("color","#FFF");
});

$(document).on("click",".targetFeatureVelRms",function(){
	
	/*let check_enable_list = [];
	
	check_enable_list.push($("#targetFeatureVelRms").attr("enable"));
	check_enable_list.push($("#targetFeatureLowPsdRms").attr("enable"));
	check_enable_list.push($("#targetFeatureMidPsdRms").attr("enable"));
	check_enable_list.push($("#targetFeatureHighPsdRms").attr("enable"));
	console.log(check_enable_list);
    console.log(check_enable_list[0]);
    console.log(check_enable_list[1]);
    console.log(check_enable_list[2]);
    console.log(check_enable_list[3]);
    var temp = 0;
    for(var i=0;i<check_enable_list.length;i++){
		temp = temp + check_enable_list[i];
	}
	if(temp == 0){
		console.log('Please enter the pump revolution speed (RPM):');
		basefreq = prompt('Please enter the pump revolution speed (RPM):');   //this is for temparary test
		
	}*/
    
    var enable = $(this).attr("enable");
    if(enable=="1"){
        $(this).attr("enable","0");
        $(this).css("background-color","");
        $(this).css("color","");
        console.log('disable');
    }
    else{
        $(this).attr("enable","1");
        $(this).css("background-color","rgb(98, 152, 234)");
        $(this).css("color","#FFF");
        console.log('enable');
    }
});

$(document).on("click",".popOK",function(){
    var target = $(this).parent().parent().prevAll(".popBtn").eq(0);
    var enable = $(this).parent().prevAll(".showHeddened").eq(0).find(".enableChannel:checked");
    var defaultVal = target.attr("data-default");
    if(enable.length==0){
        //target.val(defaultVal);
        target.css("background-color","");
        target.css("color","");
    }
    else{
        if(!formCheck("channel")){
            return;
        }
        
        //var name = $(this).parent().parent().find(".sensorName").val();
        //target.val(defaultVal+"("+name+")");
        target.css("background-color","rgb(98, 152, 234)");
        target.css("color","#FFF");
    }
    $(this).parent().parent().attr("class","nestBox sensorSelect");
    updateChannelName();
    $("#popWindowMask").hide();
});

$(document).on("click",".switchOut",function(){
    var enable=$(this).attr("data-enable");
    var defaultClass=$(this).attr("data-defaultClass");
    var lable_1 = $(this).parent().nextAll(".leftLabel")[0];
    var lable_2 = $(this).parent().nextAll(".leftLabel")[1];
    if(enable=="1"){
        $(this).attr("data-enable","0");
        $(this).attr("class","switchOut");
        lable_1.click();
    }
    else{
        $(this).attr("data-enable","1");
        $(this).attr("class","switchOut switchFocus");
        lable_2.click();
    }
});

$(document).on("click","#ImportSubmit",function(){
    //if(confirm("This operation will overwrite the original setting. Are you sure to execute？")){
    if(confirm(_language.check_over_setting)){
        $("#ImportSubmitSelect").val(null);
        $("#ImportSubmitSelect").click();
    }
});


$(document).on("click",".featureSelectBtn",function(){
    _currenFEObj=this;
    $("#FEjsonFileBtn").val(null);
    $("#FEjsonFileBtn").click();
    
});

$(document).on("click",".defaultFeatureBtn",function(){
    if(rpm = prompt("Please enter the pump revolution speed (RPM):")){
        if (!isInt(rpm)) { 
            //alert("Please input integer number."); 
            alert(_language.sample.test_time_format); 
            return;
        }
        if (rpm<=0){
            alert(_language.sample.basefreq_format);
            return;
        }
        if (rpm%60 != 0){
            alert(_language.sample.basefreq_format);
            return;
        }
        basefreq=parseInt(rpm/60);
        var obj={};
        obj.default_flag=1;
        obj.base_freq=basefreq;
        
        console.log(obj);
        $(this).prevAll(".featureSelectBtn").attr("fedata",JSON.stringify(obj));
    }
});

$(document).on("click",".manualFeatureSubmitBtn",function(){
    console.log("Submit the manual feature");
    let check_enable_list = [];
	check_enable_list.push($("#targetFeatureVelRms").attr("enable"));
	check_enable_list.push($("#targetFeatureLowPsdRms").attr("enable"));
	check_enable_list.push($("#targetFeatureMidPsdRms").attr("enable"));
	check_enable_list.push($("#targetFeatureHighPsdRms").attr("enable"));
	console.log(check_enable_list);
	//judge whether the PSD Vel feature is enabled
	var Use_PSD = 0
	for (var i=0;i<4;i++){
		if (check_enable_list[i]=='1'){
			console.log(check_enable_list[i]);
			Use_PSD=1;
		}
	}
	var obj={};
	if (Use_PSD===1){
		console.log("!!!!!");
		if(rpm = prompt(_language.sample.seg_default_FE_baseFreq)){
			if (!isInt(rpm)) { 
				//alert("Please input integer number."); 
				alert(_language.sample.test_time_format); 
				return;
			}
			else if (rpm<=0){
				alert(_language.sample.basefreq_format);
				return;
			}
			else if (rpm%60 != 0){
				alert(_language.sample.basefreq_format);
				return;
			}
			else if (rpm== null || ''){
				alert(_language.sample.basefreq_format);
				return;
			}
			basefreq=parseInt(rpm/60);
			obj.base_freq=basefreq;
			
			hideManualFeatureBox();
			obj.manual_flag=1;
			obj.mean=($("#targetFeatureMean").attr("enable"));
			obj.max=($("#targetFeatureMax").attr("enable"));
			obj.min=($("#targetFeatureMin").attr("enable"));
			obj.p2p=($("#targetFeatureP2P").attr("enable"));
			obj.rms=($("#targetFeatureRms").attr("enable"));
			obj.std=($("#targetFeatureStd").attr("enable"));
			obj.velrms=($("#targetFeatureVelRms").attr("enable"));
			obj.lowPsdRms=($("#targetFeatureLowPsdRms").attr("enable"));
			obj.midPsdRms=($("#targetFeatureMidPsdRms").attr("enable"));
			obj.highPsdRms=($("#targetFeatureHighPsdRms").attr("enable"));
			
			let a = $('.featureSelectBtn').attr("fedata",JSON.stringify(obj));
			console.log(a);
		}
	}else{
    hideManualFeatureBox();
	obj.manual_flag=1;
	obj.mean=($("#targetFeatureMean").attr("enable"));
	obj.max=($("#targetFeatureMax").attr("enable"));
	obj.min=($("#targetFeatureMin").attr("enable"));
	obj.p2p=($("#targetFeatureP2P").attr("enable"));
	obj.rms=($("#targetFeatureRms").attr("enable"));
	obj.std=($("#targetFeatureStd").attr("enable"));
	obj.velrms=($("#targetFeatureVelRms").attr("enable"));
	obj.lowPsdRms=($("#targetFeatureLowPsdRms").attr("enable"));
	obj.midPsdRms=($("#targetFeatureMidPsdRms").attr("enable"));
	obj.highPsdRms=($("#targetFeatureHighPsdRms").attr("enable"));
	if (obj.mean==="0" && obj.max==="0" && obj.min==="0" && obj.p2p==="0" && obj.rms==="0" && obj.rms==="0"){
		return;
	}
	let a = $('.featureSelectBtn').attr("fedata",JSON.stringify(obj));
	console.log(a);
	}
});

$(document).on("click",".enableChannel",function(){
    updateChannelName();
});


$(document).on("keyup",".sensorChName",function(){
    updateChannelName();
});


$(document).on("change",".sensorChName",function(){
    var finish = updateChannelName();
    if(finish==false){
        //alert("The name is duplicated or format error, please rename");
        alert(_language.sample.sensor_name_validat);
        var data=$(this).val();
        do{
            data=data.slice(0,data.length-1);
        }
        while(!isＷord(data) && data!="");
        $(this).val(data);
        $(this).focus();
    }
});


$(document).on("change",".sensorSelectList",function(){
    var val = $(this).val();
    var url="";
    if(val == "voltageInput")
        url="/example/voltageInput.png";
    else if(val == "currentInput")
        url="/example/currentInput.png";
    else if(val == "digitalInput")
        url="/example/digital.png";
    else if(val == "vibration")
        url="/example/vibration.png";
    else if(val == "distance")
        url="/example/distance.png";
    else if(val == "prognosis")
        url="/example/prognosis.png";
    else if(val == "modbus")
        url="/example/modbus.png";
    else if(val == "audio")
        url="/example/microphone.png";
    $("#sensorAddRemine").attr("src",url);
});

//20230130
/*
$(document).on("change",".featureSourceSelectList",function(){
    var val = $(this).val();
    if(val == "-Select Feature source-")
		console.log("Select Feature source");
    else if(val == "Select file")
		console.log("Select file");
        //insertBtn(subMainDiv,"btn featureSelectBtn",_language.sample.seg_FE_upload_file_btn);
    else if(val == "Default feature")
		console.log("Default feature");
		//Default feature
		//insertBtn(subMainDiv,"btn defaultFeatureBtn",_language.sample.seg_default_FE_btn);
    else if(val == "Manual setting feature")
        console.log("Manual setting feature");
});
*/
$(document).on("change",".segTypeList",function(){
    var val = parseInt($(this).val());
    var url=["/example/segNormal.png",
        "/example/segStrength.png",
        "/example/segFreq.png",
        "/example/segNormal.png"];
    $("#segAddRemine").attr("src",url[val]);
});


$(document).on("click",".removeBtn",function(){
    //if(!confirm("The operation cannot recovery. Do you want to continue?"))
    if(!confirm(_language.sample.remove_check))
        return;
    var father = $(this).parent().parent();
    father.remove();

    if($(".sensorDaughter").length<_maxSensorDaughter || 
        $(".sensorDistange").length<_maxSensorDistange||
        $(".sensorDI").length<_maxSensorDI||
        $(".sensorPrognosis").length<_maxPrognosisSerial||
        $(".sensorAudio").length<_maxMicrophon||
        $(".sensorModbus").length<_maxModbus)
        $("#sensorAddBox").show();
    
    if($(".segRule").length<_maxSegRule)
    $("#segAddBox").show();
    
    updateChannelName();
    refreshRuleHeight();
});


$(document).on("click",".segTarget",function(){
    var enable = $(this).attr("enable");
    if(enable=="1"){
        $(this).attr("enable","0");
        $(this).css("background-color","");
        $(this).css("color","");
    }
    else{
        $(this).attr("enable","1");
        $(this).css("background-color","rgb(98, 152, 234)");
        $(this).css("color","#FFF");
    }
    /*
    var s="";
    for(var i=0;i<$(".segTarget[enable='1']").length;i++){
        if(s.length>0)
            s+=",";
        s+=$(".segTarget[enable='1']")[i].value;
    }
    console.log(s);
    */
});


$(document).on("change",".analogSource",function(){
    if($(this).parent().children(".sensorChName").attr("sensorType")=="prognosis"){ //is vib
        var source = $(this).val();
        var select = $(this).parent().children(".analogRange");
        var namelist = _porgnosis_vib_range[source];
        var valueList = _porgnosis_vib_range_val[source];
        select.empty();
        for(var i=0;i<namelist.length;i++){
            var option = document.createElement("option");
            option.text = namelist[i];
            option.value = valueList[i];
            select.append(option);
        }
        select.val(_porgnosis_vib_range_val_defualt[source]);
        select.attr("data-value",select.val());
        
        select = $(this).parent().children(".subSamplingRate");
        namelist = _porgnosis_vib_fs[source];
        valueList = _porgnosis_vib_fs[source];
        select.empty();
        for(var i=0;i<namelist.length;i++){
            var option = document.createElement("option");
            option.text = namelist[i];
            option.value = valueList[i];
            select.append(option);
        }
        select.val(_porgnosis_vib_fs_defualt[source]);
        select.attr("data-value",select.val());
        
    }
    else{
        var type = $(this).parent().children(".typeHeddened").children(".analogType").val();
        var source = parseInt($(this).val());
        var sensorClass = $(this).parent().parent().parent().attr("type");
        var select = $(this).parent().children(".analogRange");
        select.empty();
        if(sensorClass=="voltageInput"){
            var namelist = getAnalogRange(_voltage_range,"V",type);
            var valueList = _voltage_level;
        }
        else{
            var val = _current_list_value[source];
            var namelist = getAnalogRange(val,"A",type);
            var valueList = _current_list_level[source];
            //for 4-20mA default value
            if(source=="1"){
                namelist=val;
            }
        }
        for(var i=0;i<namelist.length;i++){
            var option = document.createElement("option");
            option.text = namelist[i];
            option.value = valueList[i];
            select.append(option);
        }
        select.attr("data-value",select.val());
        //console.log(select);
        //console.log(select.val());
        var obj = $(this).parent().parent().children(".analogRange");
        refreshMaxMin(select);
    }
});

$(document).on("change",".analogType",function(){
    var source = parseInt($(this).parent().parent().children(".analogSource").val());
    var type = $(this).val();
    var sensorClass = $(this).parent().parent().parent().parent().attr("type");
    var select = $(this).parent().parent().children(".analogRange");
    var selectVal = select.val();
    select.empty();
    if(sensorClass=="voltageInput"){
        var namelist = getAnalogRange(_voltage_range,"V",type);
        var valueList = _voltage_level;
    }
    else{
        var val = _current_list_value[source];
        var namelist = getAnalogRange(val,"A",type);
        var valueList = _current_list_level[source];
    }
    for(var i=0;i<namelist.length;i++){
        var option = document.createElement("option");
        option.text = namelist[i];
        option.value = valueList[i];
        select.append(option);
    }
    select.val(selectVal);
    
    
    var obj = $(this).parent().parent().children(".analogRange");
    refreshMaxMin(obj);
});


$(document).on("click","#sensorAdd",function(){
    var type=$(".sensorSelectList").val();
    if($(".sensorDaughter").length>=_maxSensorDaughter && type=="voltageInput"){
        //alert("Bus is full, please remove device on bus.");
        alert(_language.sample.over_len_for_bus);
        return;
    }
    if($(".sensorDaughter").length>=_maxSensorDaughter && type=="currentInput"){
        //alert("Bus is full, please remove device on bus.");
        alert(_language.sample.over_len_for_bus);
        return;
    }
    if($(".sensorDaughter").length>=_maxSensorDaughter && type=="vibration"){
        //alert("Bus is full, please remove device on bus.");
        alert(_language.sample.over_len_for_bus);
        return;
    }
    if($(".sensorDistange").length>=_maxSensorDistange && type=="distance"){
        //alert("The distance sensor already up to limit.");
        alert(_language.sample.over_len_for_distanse);
        return;
    }
    if($(".sensorPrognosis").length>=_maxPrognosisSerial && type=="prognosis"){
        //alert("The prognosis vibration sensor already up to limit.");
        alert(_language.sample.over_len_for_prognosis);
        return;
    }
    if($(".sensorDI").length>=_maxSensorDI && type=="digitalInput"){
        //alert("The digital input sensor already up to limit.");
        alert(_language.sample.over_len_for_DI);
        return;
    }
    if($(".sensorAudio").length>=_maxMicrophon && type=="audio"){
        //alert("The audio input already up to limit.");
        alert(_language.sample.over_len_for_audio);
        return;
    }
    if($(".sensorModbus").length>=_maxModbus && type=="modbus"){
        //alert("The audio input already up to limit.");
        alert(_language.sample.over_len_for_modbus);
        return;
    }
    
    if(type=="voltageInput" || type=="currentInput" || type=="vibration"){
        refreshSensor();

        var busIndex=1;
        var emptyBus=[1,2,3,4];
        var bus = $("select[name='sensorBus']");
        
        //find the empty bus
        for(var i=0;i<bus.length;i++,busIndex++){
            let index = parseInt(bus.eq(i).val());
            let findIndex = emptyBus.indexOf(index);
            if(findIndex!=-1)
                emptyBus.splice(findIndex, 1);
        }
        busIndex=emptyBus[0]; //default 

        //default use empty
        for(var i=0;i<emptyBus.length;i++)
            if(_sensorList.bus[emptyBus[i]-1].name == "" || _sensorList.bus[emptyBus[i]-1].name == "none"){
                busIndex=emptyBus[i];
                break;
            }
        
        //check HW mapping
        for(var i=0;i<emptyBus.length;i++)
            if(_sensorList.bus[emptyBus[i]-1].name == type){
                busIndex=emptyBus[i];
                break;
            }
        
        
        creatSensorSetting(type,undefined,busIndex+"");
    }
    else{
        creatSensorSetting(type);
    }
    sensorBoxCheck();
    updateChannelName();
});


$(document).on("click",".addRegister",function(){
    var target=$(this).parent().find(".sensorModbusRegister");
    showRegisterBox(target,-1);
});


$(document).on("click","#segAdd",function(){
    var type=$(".segTypeList").val();
    var name=$(".segRuleName");
    var finalName = "RuleName";
    var formList = [];
    for(var i=0;i<name.length;i++)
        formList.push(name.eq(i).val());
    for(var i=0;i<_maxSegRule;i++){
        if(formList.indexOf("Rule_"+(i+1))==-1){
            finalName = "Rule_"+(i+1);
            break;
        }
    }

    creatSegSetting(finalName,"","",type);
    segBoxCheck();
    refreshRuleHeight();
});



$(document).on("click","#enableSubmit",function(){
    var select=$("input[name='enableSample']:checked").val();
    var val = "0";
    if(select=="enable"){
        var newForm = getForm();
        
        if(!compareObject(newForm,_oldForm)){
            //alert("Your setting doesn't save. Please submit and tun again.");
            alert(_language.sample.not_save_setting);
            return;
        }
        val="1";
    }
    
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
            //alert("Work state change req error: "+response.msg);
            alert(_language.sample.enable_err+response.msg);
            hideLoading();
        }
        else{
            //alert("Request sent successfully. Waiting for device processing");
            alert(_language.sample.enable_OK);
            setTimeout(waitWorkStates,1000,val,function(){
                hideLoading();
            });
        }

    }).error(function(e){
        //alert("Work state change error." + e.statusText);
        alert(_language.sample.enable_req_err+ e.statusText);
        hideLoading();
    });
});


$(document).on("click","#oldSensorTest",function(){
    var newForm = getForm();
    
    if(!compareObject(newForm,_oldForm)){
        //alert("Your setting doesn't save. Please submit and tun again.");
        alert(_language.sample.test_setting_not_save);
        return;
    }
    //if(confirm("The device will use old sampling data to run the segmentation setting. Do you want to continue?")){
    if(confirm(_language.sample.test_old_data_check)){
        showLoading();
        var settings = {
            "url": _api_testStates,
            "type": "PUT",
            "timeout": 30000,
            "cache":false,
            "headers": {
                "Content-Type": "application/json"
            },
            "data": JSON.stringify({
                "sensor_test":{
                    "enable":"2",
                    "maxsec":"1"
                }
            }),
        };
        $.ajax(settings).success(function (response) {
            if(response.state!=200){
                //alert("Run test req error: "+response.msg);
                alert(_language.sample.test_err+response.msg);
                hideLoading();
            }
            else{
                delayToWaitTest(3000);
                //alert("Request sent successfully. Waiting for device processing");
                alert(_language.sample.test_OK);
            }

        }).error(function(e){
            //alert("Run test error." + e.statusText);
            alert(_language.sample.test_req_err + e.statusText);
            //console.log("Run test error." + e.statusText);
            hideLoading();
        });
    }
});

$(document).on("click","#offlineTest",function(){
    var newForm = getForm();
    
    if(!compareObject(newForm,_oldForm)){
        //alert("Your setting doesn't save. Please submit and tun again.");
        alert(_language.sample.test_setting_not_save);
        return;
    }
	showLoading();
	var settings = {
		"url": _api_testStates,
		"type": "PUT",
		"timeout": 30000,
		"cache":false,
		"headers": {
			"Content-Type": "application/json"
		},
		"data": JSON.stringify({
			"sensor_test":{
				"enable":"1"
			}
		}),
	};
	$.ajax(settings).success(function (response) {
		if(response.state!=200){
			//alert("Run test req error: "+response.msg);
			alert(_language.sample.test_err+response.msg);
			hideLoading();
		}
		else{
			//setTimeout(waitTestStates,1000);
            delayToWaitTest(3000);
			//alert("Request sent successfully. Waiting for device processing");
			alert(_language.sample.test_OK);
		}

	}).error(function(e){
		//alert("Run test error." + e.statusText);
		alert(_language.sample.test_req_err + e.statusText);
		//console.log("Run test error." + e.statusText);
		hideLoading();
	});
});

//Change_mark 20230202
$(document).on("click","#sensorTest",function(){
    var newForm = getForm();
    if(!compareObject(newForm,_oldForm)){
        //alert("Your setting doesn't save. Please submit and tun again.");
        alert(_language.sample.test_setting_not_save);
        return;
    }
    var maxSec="1";
    //if(maxSec = prompt("Please input maximun testing time (1~"+_maxTestSec+"sec.)","")){
    if(maxSec = prompt(_language.sample.test_time+" (1~"+_maxTestSec+" "+_language.sample.test_time_unit+")","")){
        if (!isInt(maxSec)) { 
            //alert("Please input integer number."); 
            alert(_language.sample.test_time_format); 
            return;
        }
        //alert('Test time will be add 0.01');
        maxSec=parseInt(maxSec)+0.01;
        if(!inRange(maxSec,1,_maxTestSec)){
            //alert("Please input number from 1 to "+_maxTestSec+" sec."); 
            alert(_language.sample.test_time_format_limit+_maxTestSec+" "+_language.sample.test_time_unit+"."); 
            return;
        }
        
        
        showLoading();
        var settings = {
            "url": _api_testStates,
            "type": "PUT",
            "timeout": 30000,
            "cache":false,
            "headers": {
                "Content-Type": "application/json"
            },
            "data": JSON.stringify({
                "sensor_test":{
                    "enable":"1",
                    "maxsec":maxSec
                }
            }),
        };
        $.ajax(settings).success(function (response) {
            if(response.state!=200){
                //alert("Run test req error: "+response.msg);
                alert("Run test req error: "+response.msg);
                hideLoading();
            }
            else{
                delayToWaitTest(maxSec/2);
                //alert("Request sent successfully. Waiting for device processing");
                alert(_language.sample.test_OK);
            }

        }).error(function(e){
            //alert("Run test error." + e.statusText);
            alert(_language.sample.test_req_err + e.statusText);
            //console.log("Run test error." + e.statusText);
            hideLoading();
        });
    }
});


$(document).on("click","#sensorSubmit",function(){

    if(formCheck("sensor")){
        var newForm = getForm();
        var sensor = {};
        sensor.setting=newForm.setting;
        sensor.analog=newForm.analog;
        sensor.vibration=newForm.vibration;
        sensor.distance=newForm.distance;
        sensor.prognosis=newForm.prognosis;
        sensor.gpio=newForm.gpio;
        sensor.audio=newForm.audio;
        sensor.modbus=newForm.modbus;

        var settings = {
            "url": _api_sensorConfig,
            "type": "PUT",
            "timeout": 5000,
            "cache":false,
            "headers": {
                "Content-Type": "application/json"
            },
            "data": JSON.stringify(sensor),
        };
        showLoading();
        $.ajax(settings).success(function (response) {
            if(response.state!=200){
                //alert("Update sensor setting req error: "+response.msg);
                alert(_language.sample.sensor_submit_err+response.msg);
            }
            else{
                //alert("Update sensor setting successfully.");
                alert(_language.sample.sensor_submit_OK);
                //_oldForm.setting=JSON.parse(JSON.stringify(newForm.setting));
                _oldForm.analog=JSON.parse(JSON.stringify(newForm.analog));
                _oldForm.vibration=JSON.parse(JSON.stringify(newForm.vibration));
                _oldForm.distance=JSON.parse(JSON.stringify(newForm.distance));
                _oldForm.gpio=JSON.parse(JSON.stringify(newForm.gpio));
                _oldForm.prognosis=JSON.parse(JSON.stringify(newForm.prognosis));
                _oldForm.audio=JSON.parse(JSON.stringify(newForm.audio));
                _oldForm.modbus=JSON.parse(JSON.stringify(newForm.modbus));
            }
            hideLoading();
        }).error(function(e){
            //alert("Update sensor setting error." + e.statusText);
            alert(_language.sample._sensor_submit_req_err + e.statusText);
            hideLoading();
        });
    }
});


$(document).on("click","#segSubmit",function(){
    if(formCheck("seg")){
        var newForm = getForm();
        var seg = {};
        for(var i=0;i<_maxSegRule;i++)
            seg['segmentation_'+(i+1)]=newForm['segmentation_'+(i+1)];
        seg['tdma']=newForm['tdma'];
        //console.log(seg);
        var settings = {
            "url": _api_segConfig,
            "type": "PUT",
            "timeout": 5000,
            "cache":false,
            "headers": {
                "Content-Type": "application/json"
            },
            "data": JSON.stringify(seg),
        };
        //console.log(settings);
        showLoading();
        $.ajax(settings).success(function (response) {
            if(response.state!=200){
                //alert("Update segmentation setting req error: "+response.msg);
                alert(_language.sample.seg_submit_err+response.msg);
            }
            else{
                //alert("Update segmentation setting successfully.");
                alert(_language.sample.seg_submit_OK);
                for(var i=0;i<_maxSegRule;i++)
                    _oldForm['segmentation_'+(i+1)]=JSON.parse(JSON.stringify(newForm['segmentation_'+(i+1)]));
                _oldForm['tdma']=JSON.parse(JSON.stringify(newForm['tdma']));
            }
            hideLoading();
        }).error(function(e){
            //alert("Update segmentation setting error." + e.statusText);
            alert(_language.sample.seg_submit_req_err + e.statusText);
            hideLoading();
        });
    }
});




//displaySelect displayBox event 
var _displaySelectClass=[".triggerEnable",".subOperation",".signalFilter",".uploadResultSeg",".uploadResultFE",".centerFrequencySelect",".loopModeForRule"];
var _displaySelectTarget=["Yes","Yes","Yes","Yes","Yes","Yes","Yes"]; 
for(let i =0;i<_displaySelectClass.length;i++){
    let className = _displaySelectClass[i];
    let value = _displaySelectTarget[i];
    //console.log(className,value);
    $(document).on("change",className,function(){
        var val = this.value;
        //console.log(className,val,value,val==value,$(this).parent().nextAll(".displayBox").eq(0));
        if(val==value)
            $(this).parent().nextAll(".displayBox").eq(0).show();
        else
            $(this).parent().nextAll(".displayBox").eq(0).hide();
    });
}
      

//displaySelect displayBox event 
var _displayListClass=[".analogSource"];
var _displayListTarget=[[["1"],["2","3","4","5","6","7","8","9"]]];
var _displayListClassEnable=[[".typeHeddenedCT",""]];
var _displayListClassDisable=[[".typeHeddened",".typeHeddenedCT"]];
for(let i =0;i<_displayListClass.length;i++){
    let className = _displayListClass[i];
    let value = _displayListTarget[i];
    let endble = _displayListClassEnable[i];
    let disable = _displayListClassDisable[i];
    $(document).on("change",className,function(){
        var val = this.value;
        //console.log(val,_displayListClassDisable[i],$(this).parent().find(_displayListClassDisable[i]));
        for(var j=0;j<value.length;j++){
            if(_displayListClassEnable[i][j]!="")
                $(this).parent().find(endble[j]).show();
            //console.log(i,j,value[j],value[j].indexOf(val)>=0);
            if(value[j].indexOf(val)>=0)
                $(this).parent().find(disable[j]).hide();
        }
    });
}
      
                
$(document).on("change",".sgSelect",function(){
    var val = this.value;
    if(val=="1")
        $(this).parent().parent().find(".segSourceList").eq(0).attr("onlyAnalog","1");
    else
        $(this).parent().parent().find(".segSourceList").eq(0).attr("onlyAnalog","0");
        
    updateChannelName();
});
      
                
$(document).on("change",".analogRange",function(){
    $(this).attr("data-value",this.value);
    refreshMaxMin($(this));
});

function refreshMaxMin(obj){
    var maxObj = obj.parent().find(".sensorChMaxValue");
    var minObj = obj.parent().find(".sensorChMinValue");
    
    var newStr = obj.find("option:selected").text();
    var min = parseFloat(newStr.split("~")[0]);
    var max = parseFloat(newStr.split("~")[1]);
    
    if(newStr.split("~")[0].indexOf("m")!=-1)
        min*=0.001;
    if(newStr.split("~")[1].indexOf("m")!=-1)
        max*=0.001;
    maxObj.val(max);
    minObj.val(min);
}

function getAnalogRange(val,unit,type){
    var ret=[];
    for(var i=0;i<val.length;i++){
        var name =  " ~ " +val[i]+" "+unit;
        if(type=="d")
            name="-"+val[i]+name;
        else
            name="0"+name;
        ret.push(name);
    }
    return ret;
}


function updateChannelName(){
    var obj = getSensorName();
    var name = obj.name;
    for(var i=0;i<name.length-1;i++)
        for(var j=i+1;j<name.length;j++)
            if(name[i]==name[j])
                return false; 
                
    for(var i=0;i<name.length;i++){
        if(!isＷord(name[i]) && name[i]!="")
            return false;
            
        //if(name[i].replaceAll(" ","")=="" && name[i]!="")
        if(name[i].replace(/\s/g,"")=="" && name[i]!="")
            return false;
    }

    //console.log(obj);
    updateSegSourceList(obj);
    return true;
}


function getSensorName(){
    var checkbox = $(".enableChannel:checked").parent().next().children(".sensorChName");
    var modbusBox = $(".enableChannel:checked").parent().next().children(".sensorModbusRegister");
    var ret={"name":[],"type":[]};
    for(var i=0;i<modbusBox.length;i++){
        var param = modbusBox.eq(i).attr("registerJSON");
        param = JSON.parse(param);
        for(var j=0;j<param.length;j++){
            if(!param[j].name)
                break;
            for(var k=0;k<param[j].name.length;k++){
                if(param[j].name[k]!=""){
                    ret.name.push(param[j].name[k]);
                    ret.type.push("modbus");
                }
            }
        }
    }
    for(var i=0;i<checkbox.length;i++){
        //if(checkbox.eq(i).val().replaceAll(" ","") == "")
        if(checkbox.eq(i).val().replace(/\s/g,"") == "")
            continue;
        //console.log(checkbox.eq(i));
        if(checkbox.eq(i).attr("sensorType")){
            if(checkbox.eq(i).attr("sensorType")=="vibration" || checkbox.eq(i).attr("sensorType")=="prognosis"){
                var n=checkbox.eq(i).val();
                ret.name.push("aX_"+n);
                ret.name.push("aY_"+n);
                ret.name.push("aZ_"+n);
                ret.type.push(checkbox.eq(i).attr("sensorType"));
                ret.type.push(checkbox.eq(i).attr("sensorType"));
                ret.type.push(checkbox.eq(i).attr("sensorType"));
            }
            else{
                ret.name.push(checkbox.eq(i).val());
                ret.type.push(checkbox.eq(i).attr("sensorType"));
            }
        }
        else{
            ret.name.push(checkbox.eq(i).val());
            ret.type.push(checkbox.eq(i).attr("sensorType"));
        }
    }
    return ret;
}


function updateSegSourceList(btnObj){
    var name=btnObj.name;
    var type=btnObj.type;
    var segSourceList=$(".segSourceList");
    for(var i=0;i<segSourceList.length;i++){
        var c = segSourceList.eq(i).children();
        var btn=[];
        for(var j=0;j<c.length;j++){
            var n = c.eq(j).val();
            if(name.indexOf(n)<0)
                c.eq(j).remove();
            else if(type[name.indexOf(n)]!="voltageInput" 
                && type[name.indexOf(n)]!="currentInput" 
                && segSourceList.eq(i).attr("onlyAnalog")=="1")
                c.eq(j).remove();
            else 
                btn.push(n);
            
        }
        for(var j=0;j<name.length;j++){
            if(type[j]!="voltageInput" 
                && type[j]!="currentInput" 
                && segSourceList.eq(i).attr("onlyAnalog")=="1")
                continue
            if(btn.indexOf(name[j])==-1){
                var obj = document.createElement("input");
                obj.value=name[j];
                obj.type="button";
                obj.className="btn nestBtn segTarget";
                obj.setAttribute('enable', '0');
                segSourceList.eq(i).append(obj);
            }
        }
    }

    var segSelectList = $(".segSelectList");
    for(var i=0;i<segSelectList.length;i++){
        var oldValue=segSelectList.eq(i).val();
        segSelectList.eq(i).empty();
        for(var j=0;j<name.length;j++){
            if(type[j]!="voltageInput" 
                && type[j]!="currentInput" 
                && segSelectList.eq(i).attr("onlyAnalog")=="1")
                continue
            var option = document.createElement("option");
            option.text = name[j];
            option.value = name[j];
            segSelectList.eq(i).append(option);
        }
        if(name.indexOf(oldValue)>=0)
            segSelectList.eq(i).val(oldValue);
    }
}


function creatSensorSetting(type,name,bus,rate,range,source,sensorType,maxValue,minValue,biasValue,unit,fsUseVal,modbus_connect,modbus_setting){
    var mainDiv=document.createElement("div");
    var mainDivClass="nestBox sensorSetting ";
    var vibration8kHz=false;
    if(type=="voltageInput" || type=="currentInput" || type=="vibration")
        mainDivClass+="sensorDaughter";
    if(type=="distance")
        mainDivClass+="sensorDistange";
    if(type=="digitalInput")
        mainDivClass+="sensorDI";
    if(type=="prognosis")
        mainDivClass+="sensorPrognosis";
    if(type=="audio")
        mainDivClass+="sensorAudio";
    if(type=="modbus")
        mainDivClass+="sensorModbus";
    mainDiv.setAttribute("type",type);
    mainDiv.className=mainDivClass;

    var titleDivHtml=_language.sample.source+" : ";
    if(type=="voltageInput")
        titleDivHtml+=_language.sample.source_voltate;
    if(type=="currentInput")
        titleDivHtml+=_language.sample.source_current;
    if(type=="vibration")
        titleDivHtml+=_language.sample.source_vibration;
    if(type=="distance")
        titleDivHtml+=_language.sample.source_distance;
    if(type=="digitalInput")
        titleDivHtml+=_language.sample.source_DI;
    if(type=="prognosis")
        titleDivHtml+=_language.sample.source_vibration_P;
    if(type=="audio")
        titleDivHtml+=_language.sample.source_audio;
    if(type=="modbus")
        titleDivHtml+=_language.sample.source_modbus;
    insertSubTitle(mainDiv,titleDivHtml,true);

    var advancedBox = document.createDocumentFragment();
    if(type == "voltageInput"){
        insertImg(mainDiv,"/example/voltageInput.png");
        insertDashed(advancedBox);
        insertImg(advancedBox,"/example/analogInputBus.png");
    }
    else if(type == "currentInput"){
        insertImg(mainDiv,"/example/currentInput.png");
        insertDashed(advancedBox);
        insertImg(advancedBox,"/example/analogInputBus.png");
    }
    else if(type == "digitalInput"){
        insertImg(mainDiv,"/example/digital.png");
        insertDashed(mainDiv);
        insertImg(mainDiv,"/example/digitalInput.png");
    }
    else if(type == "vibration"){
        insertImg(mainDiv,"/example/vibration.png");
        insertDashed(advancedBox);
        insertImg(advancedBox,"/example/vibrationBus.png");
    }
    else if(type == "distance"){
        insertImg(mainDiv,"/example/distance.png");
        insertDashed(mainDiv);
        insertImg(mainDiv,"/example/distanceInput.png");
    }
    else if(type == "prognosis"){
        insertImg(mainDiv,"/example/prognosis.png");
        insertDashed(mainDiv);
        insertImg(mainDiv,"/example/serialInput.png");
    }
    else if(type == "audio"){
        insertImg(mainDiv,"/example/microphone.png");
        insertDashed(mainDiv);
        insertImg(mainDiv,"/example/serialInput.png");
    }

    else if(type == "modbus"){
        insertImg(mainDiv,"/example/modbus.png");
        insertDashed(mainDiv);
        insertImg(mainDiv,"/example/serialInputAll.png");
    }

       
    if(type=="voltageInput" || type=="currentInput" || type=="vibration"){
        insertAdvanced(mainDiv,advancedBox);
        let _rate="1000";
        if(rate)
            _rate=rate;
        insertSubTitle(mainDiv,_language.sample.select_bus,false);
        insertSelectList(mainDiv,
            "sensorBus",
            [
                _language.sample.select_bus1
                ,_language.sample.select_bus2
                ,_language.sample.select_bus3
                ,_language.sample.select_bus4
            ],
            ["1","2","3","4"],
            true,bus);
        insertBr(mainDiv);
        if(type=="voltageInput" || type=="currentInput"){
            insertSubTitle(mainDiv,_language.sample.Sample_rate,false);
            insertSelectList(mainDiv,
                "sensorFs",
                ["500","1000","2000","4000","8000"],
                ["500","1000","2000","4000","8000"],
                true,_rate);
        }
        if(type=="vibration"){
            insertSubTitle(mainDiv,_language.sample.Sample_rate,false);
            insertSelectList(mainDiv,
                "sensorFs",
                ["1000","4000","8000"],
                ["1000","4000","8000"],
                true,_rate);
            if(parseInt(_rate)==8000)
                vibration8kHz=true;
        }
        insertDashed(mainDiv);
        if(type=="voltageInput" || type=="currentInput")
            insertImg(mainDiv,"/example/analogInputChannel.png");
        if(type=="vibration")
            insertImg(mainDiv,"/example/vibrationChannel.png");
    }
    insertSubTitle(mainDiv,_language.sample.channel_setting,true);

    if(type == "voltageInput"){
        let _range = ["0","0","0","0","0","0","0","0"];
        if(range)
            _range=range;
            
        _defaultMax = parseFloat(_voltage_range[0]);
        _defaultMin = parseFloat(_voltage_range[0])*-1
        let _sensorType = ["d","d","d","d","d","d","d","d"];
        if(sensorType)
            _sensorType=sensorType;
            
        let _maxValue = [_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax];
        if(maxValue)
            _maxValue=maxValue
            
        let _minValue = [_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin];
        if(minValue)
            _minValue=minValue;
            
        let _biasValue = ["0","0","0","0","0","0","0","0"];
        if(biasValue)
            _biasValue=biasValue;
            
        let _unit = ["V","V","V","V","V","V","V","V"];
        if(unit)
            _unit=unit
            
        for(var i=0;i<_maxAnalogChannelNum;i++){
            //let _name = "Vol_"+bus+"_"+(i+1);
            let _name = "";
            if(name)
                _name=name[i];
            let rangelist = getAnalogRange(_voltage_range,"V",_sensorType[i]);
            insertSensorSelectBox(mainDiv,
                "c"+(i+1),
                _name,
                rangelist,
                _voltage_level,
                _range[i],
                undefined,
                undefined,
                undefined,
                _DE_list,
                _DE_list_value,
                _sensorType[i],
                false,
                type,
                _maxValue[i],
                _minValue[i],
                _biasValue[i],
                _unit[i]
                );
        }

    }
    else if(type == "currentInput"){
        let _range =  ["6","6","6","6","6","6","6","6"];
        if(range)
            _range=range;
            
        _sceintGain = 1;
        if(_current_list_value[0][0].indexOf("m")!=-1)
            _sceintGain=0.001;
        _defaultMax = parseFloat(_current_list_value[0][0])*_sceintGain;
        _defaultMin = parseFloat(_current_list_value[0][0])*_sceintGain*-1;
        
        let _source = ["0","0","0","0","0","0","0","0"];
        let _sensorType = ["d","d","d","d","d","d","d","d"];
        let _maxValue = [_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax,_defaultMax];
        let _minValue = [_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin,_defaultMin];
        let _biasValue = ["0","0","0","0","0","0","0","0"];
        let _unit = ["A","A","A","A","A","A","A","A"];
        
        if(source)
            _source=source;
        if(sensorType)
            _sensorType=sensorType;
        if(maxValue)
            _maxValue=maxValue;
        if(minValue)
            _minValue=minValue;
        if(biasValue)
            _biasValue=biasValue;
        if(unit)
            _unit=unit
            
            
        for(var i=0;i<_maxAnalogChannelNum;i++){
            //let _name = "Current_"+bus+"_"+(i+1);
            let _name = "";
            if(name)
                _name=name[i];
                
            let rangelist =[];
            if(_source[i]=="1")
                rangelist = _current_list_value[parseInt(_source[i])];
            else
                rangelist = getAnalogRange(_current_list_value[parseInt(_source[i])],"A",_sensorType[i]);
            let sourceVal=[];
            for(var j=0;j<_current_list.length;j++)
                sourceVal.push(j+"");
            insertSensorSelectBox(mainDiv,
                "c"+(i+1),
                _name,
                rangelist,
                _current_list_level[parseInt(_source[i])],
                _range[i],
                _current_list,
                sourceVal,
                _source[i],
                _DE_list,
                _DE_list_value,
                _sensorType[i],
                false,
                type,
                _maxValue[i],
                _minValue[i],
                _biasValue[i],
                _unit[i]
                );
        }

        insertDashed(mainDiv);
        insertSubTitle(mainDiv,_language.sample.jump_descript,true);
        insertImg(mainDiv,"/example/jumperSetting.png");
    }
    else if(type == "digitalInput"){
        for(var i=0;i<_maxDIChannelNum;i++){
            let _name = "DI_"+(i+1);
            if(name)
                _name=name[i];
            insertSensorSelectBox(mainDiv,
                "DI "+(i+1),
                _name,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                type
                );
        }
        insertDashed(mainDiv);
        insertSubTitle(mainDiv,_language.sample.DI_scal_descript,true);
        insertImg(mainDiv,"/example/digitalInputJumperSetting.png");

    }
    else if(type == "vibration"){
        let _range = ["4","4","4","4","4","4"];
        if(range)
            _range=range;
        let rangeVal=["2","4","8","16"];
        for(var i=0;i<_maxVibChannelNum;i++){
            //let _name = "Vib_"+bus+"_"+(i+1);
            let _name = "";
            if(name)
                _name=name[i];
            if(vibration8kHz && i%2==1) //disable even channel
                _name="";
            insertSensorSelectBox(mainDiv,
                "CH "+(i+1),
                _name,
                _vib_range,
                rangeVal,
                _range[i],
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                type
                );
        }
    }
    else if(type == "distance"){
        let _name = "Distance";
        if(name)
            _name=name;
        insertSensorSelectBox(mainDiv,
            "Channel 1",
            _name,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            type
            );

    }
    else if(type == "prognosis"){
        let _source = [];
        for(var i=0;i<_maxUSBNum;i++)
            _source.push(_porgnosis_vib_sour_defualt);
        if(source){
            _source=source;
            for(var i=0;i<_source.length;i++)
                if(_source[i]=="")
                    _source[i]=_porgnosis_vib_sour_defualt;
        }
            
        let _range = [];
        for(var i=0;i<_maxUSBNum;i++)
            _range.push(_porgnosis_vib_range_val_defualt[_source[i]]);
        if(range){
            _range=range;
            for(var i=0;i<_range.length;i++)
                if(_range[i]=="")
                    _range[i]=_porgnosis_vib_range_val_defualt[_source[i]];
        }
            
        let _fsUseVal = [];
        for(var i=0;i<_maxUSBNum;i++)
            _fsUseVal.push(_porgnosis_vib_fs_defualt[_source[i]]);
        if(fsUseVal){
            _fsUseVal=fsUseVal;
            for(var i=0;i<_fsUseVal.length;i++)
                if(_fsUseVal[i]=="")
                    _fsUseVal[i]=_porgnosis_vib_fs_defualt[_source[i]];
        }
            
        for(var i=0;i<_maxUSBNum;i++){
            let _name = "";
            if(name)
                _name=name[i];
            insertSensorSelectBox(mainDiv,
                "Ch"+(i+1),
                _name,
                _porgnosis_vib_range[_source[i]],
                _porgnosis_vib_range_val[_source[i]],
                _range[i],
                _porgnosis_vib_sour,
                _porgnosis_vib_sour,
                _source[i],
                undefined,
                undefined,
                undefined,
                undefined,
                type,
                undefined,
                undefined,
                undefined,
                undefined,
                _porgnosis_vib_fs[_source[i]],
                _fsUseVal[i]
                );
        }
    }
    else if(type == "audio"){
        for(var i=0;i<_maxUSBNum;i++){
            let _name = "";
            if(name)
                _name=name[i];
            insertSensorSelectBox(mainDiv,
                "Ch"+(i+1),
                _name,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                type,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined
                );
        }
    }
    else if(type == "modbus"){
        if(modbus_connect && modbus_connect)
            for(var i=0;i<_maxSerialNum;i++){
                var j=0;
                for(j=0;j<modbus_connect.length;j++)//find usb_num to match obj
                    if(modbus_connect[j].usb_num==i)
                        break
                if(j<modbus_connect.length)//is break
                    insertModbusBox(mainDiv,"Ch"+(i+1),modbus_connect[j],modbus_setting[j]);
                else
                    insertModbusBox(mainDiv,"Ch"+(i+1),{},[]);
                    
            }
        else
            for(var i=0;i<_maxSerialNum;i++){
                insertModbusBox(mainDiv,"Ch"+(i+1),{},[]);
            }
    }
    insertDashed(mainDiv);
    insertSubTitle(mainDiv,_language.sample.sensor_remove,true);
    insertCenterBtn(mainDiv,"btn sensorRemove removeBtn",_language.sample.sensor_remove_btn);
    
    sensorBoxCheck();
    var inputObj = document.getElementById("sensorContainer");
    inputObj.appendChild(mainDiv);
}


function creatSegSetting(name,
        unit,
        sub_unit,
        rule,
        upload_seg,
        basis_column,
        target_column,
        ignore_time,
        operation_reverse,
        operation_count,
        operation_filter,
        sub_operation_count,
        operation_threshold,
        operation_shift,
        padding,
        certain_freq,
        upload_extraction,
        extraction_project,
        operation_rising_falling,
        upload_interval,
        FE_json,
        operation_trigger_threshold,
        trigger_column,
        trigger_shift,
        smart_grid,
        useFilterException){
        

    var mainDiv=document.createElement("div");
    mainDiv.className="nestBox segRule";
    mainDiv.setAttribute("rule",rule);
    var subMainDiv = null;
    var SGclass = "";
    var SGflag = true;
    
    if(rule == "0" ){
        insertSubTitle(mainDiv,_language.sample.rule_normal);
        insertImg(mainDiv,"/example/segNormal.png");
    }
    else if(rule == "1"){
        insertSubTitle(mainDiv,_language.sample.rule_strength);
        insertImg(mainDiv,"/example/segStrength.png");
    }
    else if(rule == "2"){
        insertSubTitle(mainDiv,_language.sample.rule_frequency);
        insertImg(mainDiv,"/example/segFreq.png");
    }
    else if(rule == "3"){
        insertSubTitle(mainDiv,_language.sample.rule_smart_grid);
        insertImg(mainDiv,"/example/segNormal.png");
        SGclass = "SGdiable";
        SGflag=false;
    }
    
    insertSubTitle(mainDiv,_language.sample.rule_name,true);
    insertInputBox(mainDiv,"input_1_1 segRuleName",name);
    insertSubTitle(mainDiv,_language.sample.rule_name_unit,true,SGclass);
    insertInputBox(mainDiv,"input_1_1 segRuleUnit "+SGclass,unit);
    insertSubTitle(mainDiv,_language.sample.rule_name_subunit,true,SGclass);
    insertInputBox(mainDiv,"input_1_1 segRuleSubunit "+SGclass,sub_unit);
    if(rule != "0" && rule != "3")
        insertSubTitle(mainDiv,_language.sample.input_item,true);
        
    insertSelectList(mainDiv,"SegSource "+SGclass,[],[],false,"","SegSource segSelectList",true);
    if(rule == "0" || rule == "3")
        $(mainDiv).children(".segSelectList").hide();

    insertSubTitle(mainDiv,_language.sample.output_item,true);
    insertSubTitle(mainDiv,_language.sample.output_item_enable,true);
        
    var output=document.createElement("div");
    output.className="nestBox segSourceList";
    output.setAttribute("onlyAnalog","0");
    mainDiv.appendChild(output);
    
    /*
    if(rule == "0"){ //normal type
        insertSubTitle(mainDiv,"Is it for Smart Grid?",true);
        insertRadio(mainDiv,"leftLabel","sgSelect",
            ["0","1"],
            ["No","Yes"]);
            //["0","1","2"],
            //["No","Yes. Use RMS","Yes. Use mean"]);
    }
    */
    if(rule == "3"){ //Smart Grid type => disable view and selet 1
        insertRadio(mainDiv,"leftLabel "+SGclass,"sgSelect SGclass",
            ["1","0"],
            ["Yes","No"],SGflag);
        output.setAttribute("onlyAnalog","1");
    }
    
    insertDashed(mainDiv,SGclass);
    insertImg(mainDiv,"/example/triggerPoint.png",SGclass);
    insertSubTitle(mainDiv,_language.sample.trigger_enable,true,SGclass);
    insertRadio(mainDiv,"leftLabel "+SGclass,"triggerEnable",
        ["No","Yes"],
        [_language.sample.trigger_no,_language.sample.trigger_yes],SGflag);
        
    var subMainDiv= insertDisplayBox(mainDiv,SGclass);
    insertImg(subMainDiv,"/example/segRisingFalling.png");
    insertSubTitle(subMainDiv,_language.sample.trigger_item+":",true);
    insertSelectList(subMainDiv,"TriggerSource",[],[],false,"","TriggerSource segSelectList");
    insertSubTitle(subMainDiv,_language.sample.trigger_edge,true);
    insertRadio(subMainDiv,"leftLabel","startEdge",
        ["1","2"],
        [_language.sample.trigger_rising,_language.sample.trigger_falling]);
    insertSubTitle(subMainDiv,_language.sample.trigger_thrshold+":",true);
    insertInputBox(subMainDiv,"input_1_1 triggerThreshold","0");
    insertSubTitle(subMainDiv,_language.sample.trigger_shift+"(-10~10 "+_language.sample.time_unit+"):",true);
    insertInputBox(subMainDiv,"input_1_1 triggerShift","0");

    insertDashed(mainDiv,SGclass);
    
    if(rule != "0" && rule != "3" ){
        insertImg(mainDiv,"/example/signalOperation.png");
         insertSubTitle(mainDiv,_language.sample.seg_window_size+"(0.1~600 "+_language.sample.time_unit+"):",true);
    }
    else{
        insertSubTitle(mainDiv,_language.sample.seg_capture_length+"(0.1~600 "+_language.sample.time_unit+"):",true);
    }
    if(rule == "3")
        insertInputBox(mainDiv,"input_1_1 segOperationLen","10");
    else
        insertInputBox(mainDiv,"input_1_1 segOperationLen","1");
        
    insertSubTitle(mainDiv,_language.sample.seg_ignore_length+"(0~N "+_language.sample.time_unit+"):",true);
    insertInputBox(mainDiv,"input_1_1 segIgnoreLen","0");

    if(rule != "0" && rule != "3"){
        
        insertDashed(mainDiv);
        if(rule == "1"){ //segTime.
            insertImg(mainDiv,"/example/segSubOperationAndShiftAndThreshold.png");
        }
        else{
            insertImg(mainDiv,"/example/segSubOperationAndShiftAndThresholdForFreq.png");
        }
        insertSubTitle(mainDiv,_language.sample.seg_threshold,true);
        insertInputBox(mainDiv,"input_1_1 segThreshold","0");
        insertSubTitle(mainDiv,_language.sample.seg_shift+"(-10~10 "+_language.sample.time_unit+"):",true);
        insertInputBox(mainDiv,"input_1_1 segShift","0");
        
        if(rule == "1"){ //segTime.
            insertSubTitle(mainDiv,_language.sample.seg_capture_length+":",true);
            insertRadio(mainDiv,"leftLabel","subOperation",
                ["No","Yes"],
                [_language.sample.seg_sub_cap_use_windows,_language.sample.seg_sub_cap_use_manual],true);
                
            subMainDiv= insertDisplayBox(mainDiv);
            insertSubTitle(subMainDiv,_language.sample.seg_sub_cap_length+"(0.01~900 "+_language.sample.time_unit+"):",true);
            insertInputBox(subMainDiv,"input_1_1 subOperationSec","0");
        }
        
    
        if(rule == "2"){ //segFreq.
            insertDashed(mainDiv);
            insertImg(mainDiv,"/example/segByFrequencyEx.png");
            insertSubTitle(mainDiv,_language.sample.seg_freq_main+":",true);
            insertRadio(mainDiv,"leftLabel","centerFrequencySelect",
                ["No","Yes"],
                [_language.sample.seg_freq_auto,_language.sample.seg_freq_manual+" ("+_language.sample.seg_freq_range+")"],true);
            subMainDiv= insertDisplayBox(mainDiv);
            insertInputBox(subMainDiv,"input_1_1 centerFrequency","1");
            //insertSubTitle(mainDiv,"Padding(0~N sec):",true);
            //insertInputBox(mainDiv,"input_1_1 signalPadding","1");
            
            insertSubTitle(mainDiv,_language.sample.seg_capture_length+":",true);
            insertRadio(mainDiv,"leftLabel","subOperation",
                ["No","Yes"],
                [_language.sample.seg_freq_sub_auto,_language.sample.seg_freq_sub_manual],true);
                
            subMainDiv= insertDisplayBox(mainDiv);
            insertSubTitle(subMainDiv,_language.sample.seg_sub_cap_length+"(0.01~900 "+_language.sample.time_unit+"):",true);
            insertInputBox(subMainDiv,"input_1_1 subOperationSec","0");
        }
        
        
        insertDashed(mainDiv);
        insertImg(mainDiv,"/example/signalFilter.png");
        //insertSubTitle(mainDiv,"Signal filter (95~105%):",true);
        var signalFilterSwitch = insertRadio(mainDiv,"leftLabel","signalFilter",
            ["No","Yes"],
            [_language.sample.seg_filter_disable,_language.sample.seg_filter_enable],true,true,_language.sample.seg_filter_select+" (95~105%):");
        //console.log(signalFilterSwitch);
        subMainDiv= insertDisplayBox(mainDiv);
        insertSubTitle(subMainDiv,_language.sample.seg_filter_remain+"(0.01~N "+_language.sample.time_unit+"):",true);
        insertInputBox(subMainDiv,"input_1_1 signalFilterSec","0");
        if(rule == "1"){
            //insertSubTitle(subMainDiv,"Use exception data between 5% to 95% of filter size:",true);
            var useFilterExceptionSwitch = insertRadio(subMainDiv,"leftLabel","useFilterException",
                ["No","Yes"],
                ["No","Yes"],true,true,_language.sample.seg_filter_exception+":");
        }

        /*
        insertDashed(mainDiv);
        insertImg(mainDiv,"/example/signalReverse.png");
        insertSubTitle(mainDiv,"Signal reverse:",true);
        insertRadio(mainDiv,"leftLabel","signalReverse",
            ["No","Yes"],
            ["No","Yes"]);
        */
        
        /*
        insertDashed(mainDiv);
        insertSubTitle(mainDiv,"Seg parameter test:",true);
        insertCenterBtn(mainDiv,"btn segTest","Test");
        var segmentationResult=document.createElement("div");
        segmentationResult.className="nestBox segmentationResult";
        mainDiv.appendChild(segmentationResult);
        insertSubTitle(segmentationResult,"Result:",true);
        var resultImg=document.createElement("img");
        resultImg.className="resultImg";
        resultImg.setAttribute("src","/example/segResult.png");
        segmentationResult.appendChild(resultImg);
        var resultImgLink=document.createElement("a");
        resultImgLink.href="/example/segResult.png";
        resultImgLink.setAttribute("target","_blank");
        segmentationResult.appendChild(resultImgLink);
        var resultImgLinkText=document.createElement("div");
        resultImgLinkText.className="centerOutside link";
        resultImgLinkText.innerHTML="Look result at new page";
        resultImgLink.appendChild(resultImgLinkText);
        */

    }
    insertDashed(mainDiv,SGclass);
    //insertSubTitle(mainDiv,"Upload segmentation result:",true,SGclass);
    var uploadResultSegSwitch = insertRadio(mainDiv,"leftLabel "+SGclass,"uploadResultSeg",
        ["No","Yes"],
        ["No","Yes"],SGflag,true,_language.sample.seg_upload+":");
    subMainDiv= insertDisplayBox(mainDiv,SGclass);
    insertSubTitle(subMainDiv,_language.sample.seg_upload_interval+":(0~N)",true,SGclass);
    insertSubTitle(subMainDiv,_language.sample.seg_upload_remain,true,SGclass);
    insertInputBox(subMainDiv,"input_1_1 uploadResultSegInterval "+SGclass,"0");


    insertDashed(mainDiv,SGclass);
    insertSubTitle(mainDiv,_language.sample.seg_FE_project+":",true,SGclass);
    /*
    var projectName = ["Don't use"];
    var projectId=["-1"];
    for(var i=0;i<_loadFEPlist.length;i++){
        projectName.push("["+_loadFEPlist[i].id+"] "+_loadFEPlist[i].name);
        projectId.push(_loadFEPlist[i].id+"");
    }
    insertSelectList(mainDiv,"FeProject",projectName,projectId,false,"","featureSelectList");
    */
    
    //insertSubTitle(mainDiv,"Upload feature extraction result:",true,SGclass);
    var uploadResultFESwitch = insertRadio(mainDiv,"leftLabel "+SGclass,"uploadResultFE",
        ["No","Yes"],
        ["No","Yes"],SGflag,true,_language.sample.seg_FE_upload);
        
    subMainDiv= insertDisplayBox(mainDiv);


    //var br = document.createElement("br");
    //mainDiv.appendChild(br);
    //insertSubTitle(mainDiv,"Project ID (1~N) : ",false);
    //insertInputBox(mainDiv,"input_1_5 featureSelectList","");
    if(rule != "3"){
        var br = document.createElement("br");
        mainDiv.appendChild(br);
    }
    insertSubTitle(subMainDiv,_language.sample.seg_FE_upload_file+":",false);
    insertBr(subMainDiv);
    //20230130 Try to improve FE function
    
    insertBtn(subMainDiv,"btn featureSelectBtn",_language.sample.seg_FE_upload_file_btn);
    //Default feature
    //insertBtn(subMainDiv,"btn defaultFeatureBtn",_language.sample.seg_default_FE_btn);
    insertBtn(subMainDiv,"btn popFeatureBtn manualFeatureBtn",_language.sample.seg_manual_FE_btn);
    
    insertDashed(mainDiv);
    insertSubTitle(mainDiv,_language.sample.seg_remove,true);
    insertCenterBtn(mainDiv,"btn segRemove removeBtn",_language.sample.seg_remove_btn);
    

    var inputObj = document.getElementById("segContainer");
    inputObj.appendChild(mainDiv);


    updateChannelName();
    mainDiv = $(mainDiv);
    if(basis_column){
        mainDiv.children(".SegSource").val(basis_column);
    }
    if(target_column){
        target_column = target_column.split(",");
        var segTarget = mainDiv.children(".segSourceList").children(".segTarget");
        var segTargetInner = [];
        for(var i =0;i<segTarget.length;i++){
            segTargetInner.push(segTarget.eq(i).val());
        }
        for(var i =0;i<target_column.length;i++){
            let index = segTargetInner.indexOf(target_column[i]);
            if(index>=0){
                segTarget.eq(index).attr("enable","1");
                segTarget.eq(index).css("background-color","rgb(98, 152, 234)");
                segTarget.eq(index).css("color","#FFF");
            }
        }
    }
    if(operation_count){
        mainDiv.find(".segOperationLen").val(operation_count);
    }
    if(ignore_time){
        mainDiv.find(".segIgnoreLen").val(ignore_time);
    }
    if(operation_threshold && mainDiv.find(".segThreshold").length>0){
        mainDiv.find(".segThreshold").val(operation_threshold);
    }
    if(certain_freq && mainDiv.find(".centerFrequency").length>0){
        if(parseFloat(certain_freq)>=1){
            mainDiv.find(".centerFrequency").val(certain_freq);
            mainDiv.find(".leftLabel").children(".centerFrequencySelect[value='Yes']").prop('checked',true);
            mainDiv.find(".leftLabel").children(".centerFrequencySelect").parent().nextAll(".displayBox").eq(0).show();
        }
    } 
    if(padding && mainDiv.find(".signalPadding").length>0){
        mainDiv.find(".signalPadding").val(padding);
    }
    if(operation_shift){
        mainDiv.find(".segShift").val(operation_shift);
    }
    if(sub_operation_count){
        if(parseFloat(sub_operation_count)>0){
            mainDiv.find(".leftLabel").children(".subOperation[value='Yes']").prop('checked',true);
            mainDiv.find(".leftLabel").children(".subOperation").parent().nextAll(".displayBox").eq(0).show();
            mainDiv.find(".subOperationSec").val(sub_operation_count);
            
        }
    }
    if(operation_filter){
        if(parseFloat(operation_filter)>0){
            mainDiv.find(".leftLabel").children(".signalFilter[value='Yes']").prop('checked',true);
            mainDiv.find(".leftLabel").children(".signalFilter").parent().nextAll(".displayBox").eq(0).show();
            mainDiv.find(".signalFilterSec").val(operation_filter);
            $(signalFilterSwitch).find(".switchOut").attr("data-enable","1");
            $(signalFilterSwitch).find(".switchOut").attr("class","switchOut switchFocus");
        }
    }
    if(useFilterException && useFilterException)
        if(useFilterException=="1"){
            mainDiv.find(".leftLabel").children(".useFilterException[value='Yes']").prop('checked',true);
            $(useFilterExceptionSwitch).find(".switchOut").attr("data-enable","1");
            $(useFilterExceptionSwitch).find(".switchOut").attr("class","switchOut switchFocus");
        }
    /*    
    if(operation_reverse){
        if(operation_reverse=="1")
            mainDiv.find(".leftLabel").children(".signalReverse[value='Yes']").prop('checked',true);
    }
    */
    if(upload_seg){
        if(upload_seg=="1"){
            mainDiv.find(".leftLabel").children(".uploadResultSeg[value='Yes']").prop('checked',true);
            mainDiv.find(".leftLabel").children(".uploadResultSeg").parent().nextAll(".displayBox").eq(0).show();
            $(uploadResultSegSwitch).find(".switchOut").attr("data-enable","1");
            $(uploadResultSegSwitch).find(".switchOut").attr("class","switchOut switchFocus");
            
        }
    }
    if(upload_extraction){
        if(upload_extraction=="1"){
            mainDiv.find(".leftLabel").children(".uploadResultFE[value='Yes']").prop('checked',true);
            mainDiv.find(".leftLabel").children(".uploadResultFE").parent().nextAll(".displayBox").eq(0).show();
            $(uploadResultFESwitch).find(".switchOut").attr("data-enable","1");
            $(uploadResultFESwitch).find(".switchOut").attr("class","switchOut switchFocus");
        }
    }
    /*
    if(smart_grid && mainDiv.find(".sgSelect").length>0){
            mainDiv.find(".leftLabel").children(".sgSelect[value='"+smart_grid+"']").prop('checked',true);
            if(smart_grid!=0){
                output.setAttribute("onlyAnalog","1");
                updateChannelName();
            }
    }
    */
    /*
    if(extraction_project){
        mainDiv.children(".featureSelectList").val(extraction_project);
        if(extraction_project=="-1")
            mainDiv.children(".featureSelectList").val("");
    }
    */
    if(upload_interval){
        if(upload_interval!="")
            mainDiv.find(".uploadResultSegInterval").val(upload_interval);
    }
    if(FE_json){
        mainDiv.find(".featureSelectBtn").attr("fedata",FE_json);
    }
    else{
        mainDiv.find(".featureSelectBtn").attr("fedata","");
    }
    /*
    if(operation_rising_falling && mainDiv.children(".leftLabel").children(".startEdge").length>0){
        if(operation_rising_falling=="1")
            mainDiv.children(".leftLabel").children(".startEdge[value='1']").prop('checked',true);
    }
    */
    if(operation_rising_falling){
        if(operation_rising_falling=="0"){
            mainDiv.find(".leftLabel").children(".triggerEnable[value='No']").prop('checked',true);
            mainDiv.find(".leftLabel").children(".startEdge[value='1']").prop('checked',true);
        }
        else{
            if(operation_rising_falling=="1"){
                mainDiv.find(".leftLabel").children(".startEdge[value='1']").prop('checked',true);
            }
            else if(operation_rising_falling=="2"){
                mainDiv.find(".leftLabel").children(".startEdge[value='2']").prop('checked',true);
            }
            mainDiv.find(".leftLabel").children(".triggerEnable[value='Yes']").prop('checked',true);
            mainDiv.find(".leftLabel").children(".triggerEnable").parent().nextAll(".displayBox").eq(0).show();
            if(operation_trigger_threshold){
                mainDiv.find(".triggerThreshold").val(operation_trigger_threshold);
            }

            if(trigger_column){
                mainDiv.find(".TriggerSource").val(trigger_column);
            }

            if(trigger_shift){
                mainDiv.find(".triggerShift").val(trigger_shift);
            }
             
        }
    }
}


function insertSensorSelectBox(main,
    enableName,
    name,
    range,
    rangeVal,
    rangeUseVal,
    source,
    sourceVal,
    sourceUseVal,
    type,
    typeVal,
    typeUseVal,
    d_s_remain,
    sensorType,
    maxValue,
    minValue,
    biasValue,
    unit,
    fsVal,
    fsUseVal){
    var enableBtn = document.createElement("input");
    enableBtn.value=enableName;
    enableBtn.type="button";
    enableBtn.className="btn nestBtn popBtn";
    enableBtn.setAttribute("data-default",enableName);
    main.appendChild(enableBtn);
        
    var nestBox=document.createElement("div");
    nestBox.className="nestBox sensorSelect";
    main.appendChild(nestBox);
    
    var label=document.createElement("label");
    label.className="showHeddened";
    nestBox.appendChild(label);

    var checkBox=document.createElement("input");
    checkBox.className="enableChannel";
    checkBox.type="checkbox";
    if(name!=""){
        checkBox.setAttribute("checked",true);
        enableBtn.style.background="rgb(98, 152, 234)";
        enableBtn.style.color="#FFF";
        //enableBtn.value=enableName+"("+name+")";
    }
    label.appendChild(checkBox);
    label.innerHTML+=_language.sample.sensor_enable+" "+enableName;
    

    var heddened=document.createElement("div");
    heddened.className="heddened";
    nestBox.appendChild(heddened);
    if(name!=""){
        heddened.setAttribute("style","display:block");
    }

    insertSubTitle(heddened,_language.sample.sensor_name,false);
    var nameInput=document.createElement("input");
    nameInput.className="input_1_2 sensorChName";
    nameInput.value=name;
    nameInput.type="text";
    nameInput.setAttribute("sensorType",sensorType);
    heddened.appendChild(nameInput);
    insertBr(heddened);
    insertCenterBtn(nestBox,"btn popOK",_language.html.universal.ok);
    
    if(source){
        insertSubTitle(heddened,_language.sample.Signal_source,false);
        insertSelectList(heddened,"",source,sourceVal,true,sourceUseVal,"analogSource");
        insertBr(heddened);
    }
    if(fsVal){
        insertSubTitle(heddened,_language.sample.Sample_rate,false);
        insertSelectList(heddened,"",fsVal,fsVal,true,fsUseVal,"subSamplingRate");
        insertBr(heddened);
    }
    if(range){
        insertSubTitle(heddened,_language.sample.Sample_range,false);
        if(sensorType=="currentInput")
            insertSelectList(heddened,"",range,rangeVal,true,rangeUseVal,"analogRange currentRange");
        else
            insertSelectList(heddened,"",range,rangeVal,true,rangeUseVal,"analogRange");
        insertBr(heddened);
    }
    if(type){
        var typeHeddened=document.createElement("div");
        typeHeddened.className="typeHeddened typeHeddenedCT";
        insertSubTitle(typeHeddened,_language.sample.Signal_type,false);
        insertSelectList(typeHeddened,"",type,typeVal,true,typeUseVal,"analogType");
        insertBr(typeHeddened);
        heddened.appendChild(typeHeddened);
        
        //4-20mA and CT sensor diable type
        if(source && sourceUseVal!="0"){
            $(typeHeddened).hide();
        }
    }
    if(maxValue){
        var typeHeddened=document.createElement("div");
        typeHeddened.className="typeHeddenedCT";
        insertSubTitle(typeHeddened,_language.sample.sensor_engineering_up,false);
        let maxInput=document.createElement("input");
        maxInput.className="input_1_5 sensorChMaxValue";
        maxInput.value=maxValue;
        maxInput.type="text";
        maxInput.setAttribute("data-default",maxValue);
        typeHeddened.appendChild(maxInput);
        insertBr(typeHeddened);
        heddened.appendChild(typeHeddened);
        //CT sensor diable type
        if(source && sourceUseVal!="0" && sourceUseVal!="1"){
            $(typeHeddened).hide();
        }
    }
    if(minValue){
        var typeHeddened=document.createElement("div");
        typeHeddened.className="typeHeddenedCT";
        insertSubTitle(typeHeddened,_language.sample.sensor_engineering_low,false);
        let minInput=document.createElement("input");
        minInput.className="input_1_5 sensorChMinValue";
        minInput.value=minValue;
        minInput.type="text";
        minInput.setAttribute("data-default",minValue);
        typeHeddened.appendChild(minInput);
        insertBr(typeHeddened);
        heddened.appendChild(typeHeddened);
        //CT sensor diable type
        if(source && sourceUseVal!="0" && sourceUseVal!="1"){
            $(typeHeddened).hide();
        }
    }
    if(biasValue){
        var typeHeddened=document.createElement("div");
        typeHeddened.className="typeHeddenedCT";
        insertSubTitle(typeHeddened,_language.sample.sensor_engineering_offset,false);
        let biasInput=document.createElement("input");
        biasInput.className="input_1_5 sensorChBiasValue";
        biasInput.value=biasValue;
        biasInput.type="text";
        biasInput.setAttribute("data-default",biasValue);
        typeHeddened.appendChild(biasInput);
        insertBr(typeHeddened);
        heddened.appendChild(typeHeddened);
        //CT sensor diable type
        if(source && sourceUseVal!="0" && sourceUseVal!="1"){
            $(typeHeddened).hide();
        }
    }
    if(unit){
        var typeHeddened=document.createElement("div");
        typeHeddened.className="typeHeddenedCT";
        insertSubTitle(typeHeddened,_language.sample.sensor_engineering_unit,false);
        let unitInput=document.createElement("input");
        unitInput.className="input_1_5 sensorChUnit";
        unitInput.value=unit;
        unitInput.type="text";
        unitInput.setAttribute("data-default",unit);
        typeHeddened.appendChild(unitInput);
        insertBr(typeHeddened);
        heddened.appendChild(typeHeddened);
        //CT sensor diable type
        if(source && sourceUseVal!="0" && sourceUseVal!="1"){
            $(typeHeddened).hide();
        }
    }
    
    if(d_s_remain){
        insertSubTitle(heddened,_language.sample.jump_descript_remain,true);
    }


}

function insertModbusBox(main,
    enableName,
    connection,
    setting){
        
    var enableBtn = document.createElement("input");
    enableBtn.value=enableName;
    enableBtn.type="button";
    enableBtn.className="btn nestBtn popBtn";
    enableBtn.setAttribute("data-default",enableName);
    main.appendChild(enableBtn);
        
    var nestBox=document.createElement("div");
    nestBox.className="nestBox sensorSelect";
    main.appendChild(nestBox);

    var label=document.createElement("label");
    label.className="showHeddened";
    nestBox.appendChild(label);

    var checkBox=document.createElement("input");
    checkBox.className="enableChannel";
    checkBox.type="checkbox";
    if(connection.length>0 && setting.length>0){
        checkBox.setAttribute("checked",true);
        enableBtn.style.background="rgb(98, 152, 234)";
        enableBtn.style.color="#FFF";
        //enableBtn.value=enableName+"("+name+")";
    }
    label.appendChild(checkBox);
    label.innerHTML+=_language.sample.sensor_enable+" "+enableName;
    

    var heddened=document.createElement("div");
    heddened.className="heddened";
    nestBox.appendChild(heddened);
    if(connection.length>0 && setting.length>0){
        heddened.setAttribute("style","display:block");
    }
    
        

    
    insertSubTitle(heddened,_language.sample.modbus_baud,false);
    var subSamplingModbusBaud = insertSelectList(heddened,"",_modbus_baud,_modbus_baud,true,_modbus_baud_default,"subSamplingModbusBaud");
    insertBr(heddened);
    
    insertSubTitle(heddened,_language.sample.modbus_date_length,false);
    var subSamplingModbusLength = insertSelectList(heddened,"",_modbus_length,_modbus_length,true,_modbus_length_default,"subSamplingModbusLength");
    insertBr(heddened);
    
    insertSubTitle(heddened,_language.sample.modbus_parity,false);
    var subSamplingModbusParity = insertSelectList(heddened,"",_modbus_parity,_modbus_parity,true,_modbus_parity_default,"subSamplingModbusParity");
    insertBr(heddened);
    
    insertSubTitle(heddened,_language.sample.modbus_stop_bit,false);
    var subSamplingModbusStopBit = insertSelectList(heddened,"",_modbus_stop_bit,_modbus_stop_bit,true,_modbus_stop_bit_default,"subSamplingModbusStopBit");
    insertBr(heddened);
    
    insertSubTitle(heddened,_language.sample.modbus_period,false);
    var sensorModbusPeriod = insertInputBox(heddened,"input_1_5 sensorModbusPeriod","1000");
    insertBr(heddened);
    
    if(connection.buad && connection.length && connection.parity && connection.stopbit && connection.period ){
        subSamplingModbusBaud.value = connection.buad;
        subSamplingModbusLength.value = connection.length;
        subSamplingModbusParity.value = connection.parity;
        subSamplingModbusStopBit.value = connection.stopbit;
        sensorModbusPeriod.value = connection.period;
    }
    
    
    insertSubTitle(heddened,_language.sample.modbus_data,false);
    insertBtn(heddened,"btn addRegister",_language.html.universal.add);
    //insertBtn(heddened,"btn addRegisterFromFile","From File");
    
    var registerBox=document.createElement("div");
    registerBox.className="nestBox sensorModbusRegister";
    registerBox.setAttribute("registerJSON",JSON.stringify(setting));
    heddened.appendChild(registerBox);
    refleshModbusBoxItem($(registerBox));
    
    insertCenterBtn(nestBox,"btn popOK",_language.html.universal.ok);
}

function insertAdvanced(main,obj){
    var btn=document.createElement("div");
    btn.className="showAdvanced";
    btn.innerHTML=_language.html.universal.advanced;
    main.appendChild(btn);

    var box=document.createElement("div");
    box.className="showDetail";
    
    box.appendChild(obj);
    main.appendChild(box);
}

function insertImg(main,url,exClass){
    var _class = "";
    if(exClass)
        _class=exClass;
    var btn=document.createElement("input");
    btn.className="btn showImg sensorName "+exClass;
    btn.value="Show descriptive picture";
    btn.type="button";
    main.appendChild(btn);

    var img=document.createElement("img");
    img.className="img "+exClass;
    img.setAttribute("src",url);
    main.appendChild(img);
}


function insertCenterBtn(main,className,value){
    var centerOutside=document.createElement("div");
    centerOutside.className="centerOutside";
    main.appendChild(centerOutside);
    var segRemove=document.createElement("input");
    segRemove.className=className;
    segRemove.type="button";
    segRemove.value=value;
    centerOutside.appendChild(segRemove);
}
function insertBtn(main,className,value){
    var segRemove=document.createElement("input");
    segRemove.className=className;
    segRemove.type="button";
    segRemove.value=value;
    main.appendChild(segRemove);
}
//SHOW
function showManualFeatureBox(){
    var MainDiv = document.getElementById("popManuelFeatureBox")
    
    $("#popWindowMask").show();
    $("#popManuelFeatureBox").show();
}
//UNSHOW
function hideManualFeatureBox(){
    $("#popWindowMask").hide();
    $("#popManuelFeatureBox").hide();
}


function insertSubTitle(main,title,newline,exClass){
    var _class = "";
    if(exClass)
        _class=exClass;
    var div=document.createElement("div");
    if(newline)
        div.className="subTitle "+_class;
    else 
        div.className="subTitle noNewLine "+_class;
    div.innerHTML=title;
    
    main.appendChild(div);
    return div;
}


function insertSelectList(main,name,list,value,is1_3,useValue,otherClassName,onlyAnalog){
    var select=document.createElement("select");
    select.setAttribute("data-value",useValue);
	if(onlyAnalog)
		select.setAttribute("onlyAnalog","1");
    select.name=name;
    select.className="selectList";
    if(is1_3)
        select.className+="_1_3";
    if(otherClassName)
        select.className+=" "+otherClassName;


    for(var i=0;i<list.length;i++){
        var option = document.createElement("option");
        option.text = list[i];
        option.value = value[i];
        select.options.add(option);
    }
    if(useValue){
        $(select).val(useValue);
        $(select).attr("data-default",useValue);
    }
    main.appendChild(select);
    return select;
}

function insertDisplayBox(mainDiv,exClass){
    var _class = "";
    if(exClass)
        _class=exClass;
    var obj = document.createElement("div");
    obj.className="displayBox "+_class;
    mainDiv.appendChild(obj);
    return obj;
}

function insertDashed(main,exClass){
    var _class = "";
    if(exClass)
        _class=exClass;
    var div=document.createElement("div");
    div.className="dashed "+_class;
    main.appendChild(div);
}


function insertBr(main,exClass){
    var _class = "";
    if(exClass)
        _class=exClass;
    var br=document.createElement("br");
    if(_class!="")
        br.className=_class;
    main.appendChild(br);
}


function insertInputBox(main,className,value){
    var box=document.createElement("input");
    box.type="text";
    box.className=className;
    box.value=value;
    main.appendChild(box);
    return box;
}


function insertRadio(main,labelClass,name,value,text,newLine,newStyle,siwtchTitle){
    var _newLine=true;
    var _newStyle=false;
    if(typeof(newLine)!="undefine")
        _newLine=newLine;
    if(typeof(_newStyle)!="undefine" && value.length==2)
        _newStyle=newStyle;
    var serial = Math.floor(Math.random() * 100000);
    var switchBox = null;
    if(newStyle){
        switchBox=document.createElement("div");
        switchBox.className="switchBox "+labelClass;
        main.appendChild(switchBox);
        var title = insertSubTitle(switchBox,siwtchTitle,true);
        title.style.paddingRight="2.5rem";
        var outBorder=document.createElement("div");
        outBorder.className="switchOut";
        outBorder.setAttribute("data-enable","0");
        "data-defaultClass"
        switchBox.appendChild(outBorder);
        var inBorder=document.createElement("div");
        inBorder.className="switchIn";
        outBorder.appendChild(inBorder);
    }
    for(var i=0;i<value.length;i++){
        var label=document.createElement("label");
        label.className=labelClass;
        if(_newStyle)
            label.style.display="none";
        main.appendChild(label);

        var input=document.createElement("input");
        input.type="radio";
        input.className=name;
        input.name=name+"_"+serial;
        input.value=value[i];
        if(i==0)
            input.setAttribute("checked", true)
        label.appendChild(input);
        label.innerHTML+=text[i];
        if(i!=value.length-1 && _newLine && !newStyle)
            insertBr(main);
    }
    
    return switchBox;
    //console.log($(main).children("."+labelClass).children("."+name+"[value='"+value[0]+"']"));
    //$(main).children("."+labelClass).children("."+name+"[value='"+value[0]+"']").prop('checked',true);
}

_registerBoxTarget = null;
_registerBoxIndex = null;
function hideRegisterBox(){
    $("#popWindowMask").css("z-index","979");
    $("#popRegisterBox").hide();
}
function showRegisterBox(target,index){
    _registerBoxTarget = target;
    _registerBoxIndex = index;
    var main = document.getElementById("popRegisterBox");
    if(main.innerHTML==""){// first time init
        
        insertSubTitle(main,_language.sample.modbus_device,false);
        insertInputBox(main,"input_1_5 modbus_box_device","");
        insertBr(main);
        
        insertSubTitle(main,_language.sample.modbus_register,false);
        insertInputBox(main,"input_1_5 modbus_box_register","");
        insertBr(main);
        
        insertSubTitle(main,_language.sample.modbus_response,false);
        insertInputBox(main,"input_1_5 modbus_box_response","20");
        insertBr(main);
        
        insertSubTitle(main,_language.sample.modbus_type,false);
        insertSelectList(main,"",_modbus_type,_modbus_type,true,_modbus_type_default,"modbus_box_type");
        insertBr(main);
        
        var i;
        for(i=0;i<17;i++){ //0~16. 1~16 is use on bit.
            if(i)
                insertSubTitle(main,_language.sample.modbus_name+" bit"+i+_language.sample.modbus_name_end,false,"modbus_box_name_title");
            else
                insertSubTitle(main,_language.sample.modbus_name+_language.sample.modbus_name_end,false,"modbus_box_name_title");
            insertInputBox(main,"input_1_2 modbus_box_name","");
            insertBr(main,"modbus_box_name_br");
        }
        
        
        insertSubTitle(main,_language.sample.modbus_ratio,false);
        insertInputBox(main,"input_1_5 modbus_box_ratio","1");
        insertBr(main);
        
        insertSubTitle(main,_language.sample.modbus_order,false);
        insertSelectList(main,"",_modbus_order,_modbus_order,true,_modbus_order_default,"modbus_box_order");
        insertBr(main);
        
        insertSubTitle(main,_language.sample.modbus_check,false);
        insertSelectList(main,"",_modbus_check,_modbus_check,true,_modbus_check_default,"modbus_box_check");
        insertBr(main);
        
        var centerOutside=document.createElement("div");
        centerOutside.className="centerOutside";
        main.appendChild(centerOutside);
        var remove=document.createElement("input");
        remove.className="btn modbus_box_remove";
        remove.type="button";
        remove.value=_language.html.universal.remove;
        var OK=document.createElement("input");
        OK.className="btn modbus_box_submit";
        OK.type="button";
        OK.value=_language.html.universal.ok;
        centerOutside.appendChild(remove);
        centerOutside.appendChild(OK);
    }
    
    var param = target.attr("registerJSON");
    param = JSON.parse(param);
    if(index==-1){ //empty input
        $("#popRegisterBox").find(".modbus_box_remove").val(_language.html.universal.cancel);
        $("#popRegisterBox").find(".modbus_box_device").val("");
        $("#popRegisterBox").find(".modbus_box_register").val("");
        $("#popRegisterBox").find(".modbus_box_response").val("20");
        $("#popRegisterBox").find(".modbus_box_ratio").val("1");
        $("#popRegisterBox").find(".modbus_box_type").val(_modbus_type_default);
        $("#popRegisterBox").find(".modbus_box_order").val(_modbus_order_default);
        $("#popRegisterBox").find(".modbus_box_check").val(_modbus_check_default);
        $("#popRegisterBox").find(".modbus_box_name").val("");
    }
    else if(param.length>index){//load input
        $("#popRegisterBox").find(".modbus_box_remove").val(_language.html.universal.remove);
        $("#popRegisterBox").find(".modbus_box_device").val(param[index].address.toString(16));
        $("#popRegisterBox").find(".modbus_box_register").val(param[index].register.toString(16));
        $("#popRegisterBox").find(".modbus_box_response").val(param[index].delay);
        $("#popRegisterBox").find(".modbus_box_ratio").val(param[index].ratio);
        $("#popRegisterBox").find(".modbus_box_type").val(param[index].type);
        $("#popRegisterBox").find(".modbus_box_order").val(param[index].order);
        $("#popRegisterBox").find(".modbus_box_check").val(param[index].check);
        var i=0;
        var shift=0;
        if(param[index].type.indexOf("bit")==0)
            shift=1;
        for(i=0;i<param[index].name.length;i++)
            $("#popRegisterBox").find(".modbus_box_name").eq(i+shift).val(param[index].name[i]);
    }
    
    
    refleshModbusDataTypeOfName();
    $("#popWindowMask").css("z-index","985");
    $("#popRegisterBox").show();
}

function refleshModbusDataTypeOfName(){
    var select = $("#popRegisterBox").find(".modbus_box_type");
    if(select){
        $(".modbus_box_name_title").hide();
        $(".modbus_box_name_br").hide();
        $(".modbus_box_name").hide();
        var val = select.val();
        var i=0;
        if(val=="bit8"){
            for(i=0;i<8;i++){
                $(".modbus_box_name_title").eq(1+i).show();
                $(".modbus_box_name_br").eq(1+i).show();
                $(".modbus_box_name").eq(1+i).show();
            }
        }
        else if(val=="bit16"){
            for(i=0;i<16;i++){
                $(".modbus_box_name_title").eq(1+i).show();
                $(".modbus_box_name_br").eq(1+i).show();
                $(".modbus_box_name").eq(1+i).show();
            }
        }
        else{
            $(".modbus_box_name_title").eq(0).show();
            $(".modbus_box_name_br").eq(0).show();
            $(".modbus_box_name").eq(0).show();
        }
    }
}

function refleshModbusBoxItem(target){
    var param = target.attr("registerJSON");
    param = JSON.parse(param);
    target.html(""); //clear children
    var i;
    var j;
    for(i=0;i<param.length;i++){
        for(j=0;j<param[i].name.length;j++){
            if(param[i].name[j]!=""){
                var obj = document.createElement("input");
                obj.value=param[i].name[j];
                obj.className="btn modbosRegisterBtn";
                obj.type="button";
                obj.setAttribute("index",i);
                target[0].append(obj);
            }
        }
    }
}

$(document).on("click",".modbosRegisterBtn",function(){
    var parent = $(this).parent();
    var index = parseInt($(this).attr("index"));
    showRegisterBox(parent,index);
});

$(document).on("change",".modbus_box_type",function(){
    refleshModbusDataTypeOfName();
});

$(document).on("click",".modbus_box_remove",function(){
    var param = _registerBoxTarget.attr("registerJSON");
    param = JSON.parse(param);
    if(param.length>_registerBoxIndex && _registerBoxIndex!=-1){
        param.splice(_registerBoxIndex,1);
        _registerBoxTarget.attr("registerJSON",JSON.stringify(param));
    }
    refleshModbusBoxItem(_registerBoxTarget);
    hideRegisterBox();
});

$(document).on("click",".modbus_box_submit",function(){
    var modbus_box_device = $(".modbus_box_device").val();
    var modbus_box_register = $(".modbus_box_register").val();
    var modbus_box_response = $(".modbus_box_response").val();
    var modbus_box_type = $(".modbus_box_type").val();
    var modbus_box_ratio = $(".modbus_box_ratio").val();
    var modbus_box_order = $(".modbus_box_order").val();
    var modbus_box_check = $(".modbus_box_check").val();
    var modbus_box_name = $(".modbus_box_name");
    var name_list = Array();
    
    if(modbus_box_device==""){
        alert(_language.sample.modbus_err_device_empty);
        $(".modbus_box_device").focus();
        return;
    }
    if(modbus_box_register==""){
        alert(_language.sample.modbus_err_reg_empty);
        $(".modbus_box_register").focus();
        return;
    }
    
    
    if(modbus_box_device.indexOf("0x")==0)
        modbus_box_device = modbus_box_device.slice(2);
    if(modbus_box_register.indexOf("0x")==0)
        modbus_box_register = modbus_box_register.slice(2);
        
    try{
        modbus_box_device_decimal = parseInt(modbus_box_device,16);
        if(modbus_box_device_decimal.toString(16).toUpperCase()!=modbus_box_device.toUpperCase()){
            alert(_language.sample.modbus_err_device_format);
            $(".modbus_box_device").focus();
            return;
        }
        if(modbus_box_device_decimal<0 || modbus_box_device_decimal>255){
            alert(_language.sample.modbus_err_device_range);
            $(".modbus_box_device").focus();
            return;
        }
    }
    catch(e){
        alert(_language.sample.modbus_err_device_format);
        $(".modbus_box_device").focus();
        return;
    }
      
    try{
        modbus_box_register_decimal = parseInt(modbus_box_register,16);
        if(modbus_box_register_decimal.toString(16).toUpperCase()!=modbus_box_register.toUpperCase()){
            alert(_language.sample.modbus_err_reg_format);
            $(".modbus_box_register").focus();
            return;
        }
        if(modbus_box_register_decimal<0 || modbus_box_register_decimal>65535){
            alert(_language.sample.modbus_err_reg_range);
            $(".modbus_box_register").focus();
            return;
        }
    }
    catch(e){
        alert(_language.sample.modbus_err_reg_format);
        $(".modbus_box_register").focus();
        return;
    }
    
    var empty = true;
    var name="";
    if(modbus_box_type=="bit8"){
        for(i=0;i<8;i++){
            name = $(".modbus_box_name").eq(1+i).val();
            name_list.push(name);
            if(name!=""){
                empty=false;
                if(!isＷord(name)){
                    alert(_language.sample.modbus_err_name_format);
                    $(".modbus_box_name").eq(1+i).focus();
                    return;
                }
            }
        }
    }
    else if(modbus_box_type=="bit16"){
        for(i=0;i<16;i++){
            name = $(".modbus_box_name").eq(1+i).val();
            name_list.push(name);
            if(name!=""){
                empty=false;
                if(!isＷord(name)){
                    alert(_language.sample.modbus_err_name_format);
                    $(".modbus_box_name").eq(1+i).focus();
                    return;
                }
            }
        }
    }
    else{
        name = $(".modbus_box_name").eq(0).val();
        name_list.push(name);
        if(name!=""){
            empty=false;
            if(!isＷord(name)){
                alert(_language.sample.modbus_err_name_format);
                $(".modbus_box_name").eq(0).focus();
                return;
            }
        }
    }
    
    if(empty){
        alert(_language.sample.modbus_err_name_empty);
        return;
    }
    
    if(!isFloat(modbus_box_ratio)){
        alert(_language.sample.modbus_err_retio_format);
        $(".modbus_box_ratio").focus();
        return;
    }
    if(modbus_box_ratio==""){
        alert(_language.sample.modbus_err_retio_empty);
        $(".modbus_box_ratio").focus();
        return;
    }
    
    var newObj = {};
    newObj.address = modbus_box_device_decimal;
    newObj.register = modbus_box_register_decimal;
    newObj.delay = parseFloat(modbus_box_response);
    newObj.function = 3;
    newObj.check = modbus_box_check;
    newObj.type = modbus_box_type;
    newObj.name = name_list;
    newObj.order = modbus_box_order;
    newObj.ratio = parseFloat(modbus_box_ratio);
    
    var param = _registerBoxTarget.attr("registerJSON");
    var oldParam = JSON.parse(param);
    param = JSON.parse(param);
    if(_registerBoxIndex==-1){
        if(modbusNameCheck(param,newObj)){
            param.push(newObj);
        }
        else{
            alert(_language.sample.modbus_err_name_repeat);
            return;
        }
    }
    else if(param.length>_registerBoxIndex){
        var cerrentData = JSON.parse(JSON.stringify(param));
        cerrentData.splice(_registerBoxIndex,1);
        if(modbusNameCheck(cerrentData,newObj)){
            param[_registerBoxIndex]=newObj;
        }
        else{
            alert(_language.sample.modbus_err_name_repeat);
            return;
        }
    }
    
    _registerBoxTarget.attr("registerJSON",JSON.stringify(param));
    var finish = updateChannelName();
    if(finish==false){
        alert(_language.sample.modbus_err_name_repeat);
        _registerBoxTarget.attr("registerJSON",JSON.stringify(oldParam));
        return;
    }
    
    refleshModbusBoxItem(_registerBoxTarget);
    hideRegisterBox();
});

function modbusNameCheck(obj,newObj){
    var i,j;
    var nameList = modbusNameList(obj);
    for(i=0;i<newObj.name.length;i++){
        if(nameList.indexOf(newObj.name[i])!=-1)
            return false;
    }
    
    //self check
    if(newObj.name.length>1){
        for(i=0;i<newObj.name.length;i++){
            for(j=i+1;j<newObj.name.length;j++){
                if(newObj.name[i]==newObj.name[j] && newObj.name[i]!="" )
                    return false;
            }
        }
        
    }
    
    return true;
}
function modbusNameList(obj){
    var ret = Array();
    var i;
    var j;
    for(i=0;i<obj.length;i++){
        for(j=0;j<obj[i].name.length;j++){
            if(obj[i].name[j]!="")
                ret.push(obj[i].name[j])
        }
    }
    return ret;
}

function importFiles(e){
    if(e.length==0)
        return;
    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        showLoading();
        var data=event.target.result.split("base64,")[1];
        //console.log(data);
        //console.log(atob(data));
        var settings = {
            "url": _api_importSensorFile,
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
                alert(_language.sample.import_setting_err+response.msg);
            }
            else{
                //alert("Request sent successfully.");
                alert(_language.sample.import_setting_OK);
                window.location.reload(); 
            }
    
            hideLoading();
        }).error(function(e){
            console.log("import file error.");
            console.log(e);
    
            hideLoading();
        });
    });
    reader.readAsDataURL(e[0]);
}



function importFEFiles(e){
    if(e.length==0)
        return;
    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        var data=event.target.result.split("base64,")[1];
        try{
            jData = JSON.parse(atob(data));
        }
        catch(e){
            alert(_language.sample.seg_FE_json_parse);
            //alert("Json parse error.");
            return;
        }
        if(jData.project_id){
            if(!isInt(jData.project_id)){
                alert(_language.sample.seg_FE_json_format);
                //alert("Data format error.");
                return;
            }
        }
        else{
                alert(_language.sample.seg_FE_json_format);
            //alert("Data format error.");
            return;
        }
        
        alert(_language.sample.seg_FE_json_OK);
        //alert("Upload OK!");
        _currenFEObj.setAttribute("FEdata",atob(data));
        console.log(atob(data));
        hideLoading();
    });
    reader.readAsDataURL(e[0]);
}
// load feature extraction project id list
// disable function
function loadFEPlist(){
    var settings = {
        "url": _api_loadFEPlist,
        "type": "GET",
        "timeout": 0,
        "async":false 
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            console.log("load project id req error:");
            console.log(response);
            _loadFEPlist=[];
        }
        else{
            _loadFEPlist = response.data.project;
            console.log(_loadFEPlist);
        }
    }).error(function(e){
        console.log("load project error.");
        console.log(e);
        _loadFEPlist=[];
    });
}


function refreshSensor(){
	if(!_isSPIIDER)
		return;
    var settings = {
        "url": _api_refreshSensorList,
        "type": "GET",
        "timeout": 3,
        "async":false 
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            console.log("load sensor list req error:");
            console.log(response);
            _sensorList = _sensorListDef;
        }
        else{
            _sensorList = response.data;
            for(var i =0;i<_sensorList.bus.length;i++){
                if(_sensorList.bus[i].name=="vib")
                    _sensorList.bus[i].name="vibration";
                if(_sensorList.bus[i].name=="voltage")
                    _sensorList.bus[i].name="voltageInput";
                if(_sensorList.bus[i].name=="current")
                    _sensorList.bus[i].name="currentInput";
            }
        }
    }).error(function(e){
        console.log("load sensor list error:");
        console.log(e);
        _sensorList = _sensorListDef;
    });
    //console.log(_sensorList);
}


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

function delayToWaitTest(maxSec){
    setTimeout(waitTestStates,maxSec,function(){
        var settings = {
            "url": _api_testStates,
            "type": "PUT",
            "timeout": 30000,
            "cache":false,
            "headers": {
                "Content-Type": "application/json"
            },
            "data": JSON.stringify({
                "sensor_test":{
                    "enable":"0",
                    "maxsec":"0"
                }
            }),
        };
        $.ajax(settings).success(function (response) {
            if(response.state!=200)
                alert(_language.sample.test_delay_err+response.msg);
                //alert("Run test req error: "+response.msg);
            hideLoading();
        }).error(function(e){
            alert(_language.sample.test_delay_req_err + e.statusText);
            //alert("Run test error." + e.statusText);
            hideLoading();
        });
    });
}


function waitTestStates(callback){
    var settings = {
        "url": _api_testStates,
        "type": "GET",
        "timeout": 30000
    };
    $.ajax(settings).success(function (response) {
        //console.log(response);
		if(response.state!=200){
            alert(_language.sample.test_delay_change_err+response.msg);
            if(typeof(callback)==="function")
                callback();
        }
        else{
            if( (_isSPIIDER && response.data.environment.sensor_test_state=="1") || (!_isSPIIDER && response.data.environment.sensor_test_state=="0")){
                showLoading("(8/8)"+_language.sample.test_status_8_0);
				if(!_isSPIIDER){
					setTimeout(function(){
						alert(_language.test.alert_done);
						if(typeof(callback)==="function")
							callback();
					},500);
					return;
				}
				
                var timestamp = new Date().getTime();
                var count = parseInt(response.data.environment.sensor_test_output);
                if(count>=1){
                    $("#sensorResult").children("img").attr("src","");
                    $("#sensorResult").children("img").hide();
                    setTimeout(function(){
                        $("#sensorResult").children("img").attr("src","/example/sampleResult.png?t=" + timestamp);
                        $("#sensorResult").children("img").show();
                    },500);
                    $("#sensorResult").children("a").attr("href","/example/sampleResult_hight.png?t=" + timestamp);
                    $("#sensorResult").children("img").show();
                    $("#sensorResult").children("a").show();
                    $("#sensorResult").children(".centerOutside").hide();
                }
                else{
                    $("#sensorResult").children("img").hide();
                    $("#sensorResult").children("a").hide();
                    $("#sensorResult").children(".centerOutside").show();
                }
                
                if(count>=2){
                    $("#segResult").children("img").attr("src","");
                    $("#segResult").children("img").hide();
                    setTimeout(function(){
                        $("#segResult").children("img").attr("src","/example/segResult_hight.png?t=" + timestamp);
                        $("#segResult").children("img").show();
                    },500);
                    $("#segResult").children("a").attr("href","/example/segResult_hight.png?t=" + timestamp);
                    $("#segResult").children("img").show();
                    $("#segResult").children("a").show();
                    $("#segResult").children(".centerOutside").hide();
                }
                else{
                    $("#segResult").children("img").hide();
                    $("#segResult").children("a").hide();
                    $("#segResult").children(".centerOutside").show();
                }
                $("#sensorResult").show();
                $("#segResult").show();
                
                var enter="\n";
                var alertWord = _language.test.alert_title+enter;
                alertWord += _language.test.alert_seg_csv_FTP+response.data.environment.upload_ftp_seg_csv+enter;
                alertWord += _language.test.alert_seg_binary_FTP+response.data.environment.upload_ftp_seg_pkl+enter;
                alertWord += _language.test.alert_seg_json_API+response.data.environment.upload_api_seg+enter;
                alertWord += _language.test.alert_FE_csv_FTP+response.data.environment.upload_ftp_fe_csv+enter;
                alertWord += _language.test.alert_FE_binary_FTP+response.data.environment.upload_ftp_fe_pkl+enter;
                alertWord += _language.test.alert_FE_json_API+response.data.environment.upload_api_fe+enter;
                alertWord += _language.test.alert_smart_grid_MQTT+response.data.environment.upload_mqtt;
                
                enter="</br>";
                var textResult = _language.test.html_title+enter
                textResult += enter
                textResult += _language.test.html_seg_title+enter
                textResult += _language.test.html_seg_csv_FTP+response.data.environment.upload_ftp_seg_csv+enter;
                textResult += _language.test.html_seg_binary_FTP+response.data.environment.upload_ftp_seg_pkl+enter;
                textResult += _language.test.html_seg_json_API+response.data.environment.upload_api_seg+enter;
                textResult += enter
                textResult += _language.test.html_FE_title+enter
                textResult += _language.test.html_FE_csv_FTP+response.data.environment.upload_ftp_fe_csv+enter;
                textResult += _language.test.html_FE_binary_FTP+response.data.environment.upload_ftp_fe_pkl+enter;
                textResult += _language.test.html_FE_json_API+response.data.environment.upload_api_fe+enter;
                textResult += enter
                textResult += _language.test.html_smart_grid_title+enter
                textResult += _language.test.html_smart_grid_MQTT+response.data.environment.upload_mqtt;
                
                $("#msgResultText").html(textResult);
                $("#msgResult").show();
                
                setTimeout(function(){
                    alert(alertWord);
                    if(typeof(callback)==="function")
                        callback();
                },500);
            }
            else{
                //console.log(response.data);
                var num = response.data.var.num+"";
                var schedule = "("+num+"/8)";
                var mapping = {};
                mapping["1"] = _language.sample.test_status_1_0;
                mapping["2"] = _language.sample.test_status_2_0 + response.data.var.n + _language.sample.test_status_2_1;
                mapping["3"] = _language.sample.test_status_3_0;
                mapping["4"] = _language.sample.test_status_4_0;
                mapping["5"] = _language.sample.test_status_5_0 + response.data.var.n + _language.sample.test_status_5_1;
                mapping["6"] = _language.sample.test_status_6_0 + response.data.var.n + "/" + response.data.var.m;
                mapping["7"] = _language.sample.test_status_7_0 + response.data.var.n + "/" + response.data.var.m;
                
                showLoading(schedule+mapping[num]);
                setTimeout(waitTestStates,3000,callback);
            }
        }

    }).error(function(e){
        console.log("wait test state change error." + e.statusText);
        setTimeout(waitTestStates,3000,callback);
        //alert("wait test state change error." + e.statusText);
        //if(typeof(callback)==="function")
        //    callback();
    });
}


function loadSetting(async,name,path,callback){
    var settings = {
        "url": path,
        "type": "GET",
        "timeout": 5000,
        "async":async,
        "cache":false
    };
    $.ajax(settings).success(function (response) {
        if(response.state!=200){
            //alert("Load setting req error: "+"("+name+")"+response.msg);
            alert(_language.sample.load_err+"("+name+")"+response.msg);
            if(typeof(callback)==="function")
                callback(null);
        }
        else{
            if(typeof(callback)==="function")
                callback(response.data);
        }

    }).error(function(e){
        //alert("Load setting req error: "+"("+name+")"+e.statusText);
        alert(_language.sample.load_req_err+"("+name+")"+e.statusText);
        if(typeof(callback)==="function")
            callback(null);
    });
}

function loadForm(data){
    var analogRate = data.sensor.analog.sample_rate.split(",");
    var vibRate = data.sensor.vibration.sample_rate.split(",");
    /*
    var deviceName = data.sensor.setting.device_name;
    var uploadRaw = data.sensor.setting.upload_raw;

    $("#deviceName").val(deviceName);
    if(uploadRaw=="1")
        $("input[name='uploadResultSampling'][value='Yes']").attr("checked",true);
    else
        $("input[name='uploadResultSampling'][value='No']").attr("checked",true);
    */
	
    if(data.system.work.enable=="1")
        $("input[name='enableSample'][value='enable']").attr('checked',true);
    else
        $("input[name='enableSample'][value='disable']").attr('checked',true);
        
    loadAnalogHub(1,analogRate[0],
        data.sensor.analog.hub1_name,
        data.sensor.analog.hub1_type,
        data.sensor.analog.hub1_mode,
        data.sensor.analog.hub1_level,
        data.sensor.analog.hub1_max,
        data.sensor.analog.hub1_min,
        data.sensor.analog.hub1_bias,
        data.sensor.analog.hub1_unit);
    loadAnalogHub(2,analogRate[1],
        data.sensor.analog.hub2_name,
        data.sensor.analog.hub2_type,
        data.sensor.analog.hub2_mode,
        data.sensor.analog.hub2_level,
        data.sensor.analog.hub2_max,
        data.sensor.analog.hub2_min,
        data.sensor.analog.hub2_bias,
        data.sensor.analog.hub2_unit);
    loadAnalogHub(3,analogRate[2],
        data.sensor.analog.hub3_name,
        data.sensor.analog.hub3_type,
        data.sensor.analog.hub3_mode,
        data.sensor.analog.hub3_level,
        data.sensor.analog.hub3_max,
        data.sensor.analog.hub3_min,
        data.sensor.analog.hub3_bias,
        data.sensor.analog.hub3_unit);
    loadAnalogHub(4,analogRate[3],
        data.sensor.analog.hub4_name,
        data.sensor.analog.hub4_type,
        data.sensor.analog.hub4_mode,
        data.sensor.analog.hub4_level,
        data.sensor.analog.hub4_max,
        data.sensor.analog.hub4_min,
        data.sensor.analog.hub4_bias,
        data.sensor.analog.hub4_unit);

    loadVibHub(1,vibRate[0],
        data.sensor.vibration.hub1_name,
        data.sensor.vibration.hub1_level);
    loadVibHub(2,vibRate[1],
        data.sensor.vibration.hub2_name,
        data.sensor.vibration.hub2_level);
    loadVibHub(3,vibRate[2],
        data.sensor.vibration.hub3_name,
        data.sensor.vibration.hub3_level);
    loadVibHub(4,vibRate[3],
        data.sensor.vibration.hub4_name,
        data.sensor.vibration.hub4_level);


    var prognosisName = data.sensor.prognosis.name;
    var prognosisFs = data.sensor.prognosis.sample_rate;
    var prognosisLevel = data.sensor.prognosis.level;
    var prognosisSource = data.sensor.prognosis.mode;
    if(prognosisName!=",")
        creatSensorSetting(
            "prognosis",
            prognosisName.split(","),
            undefined,
            undefined,
            prognosisLevel.split(","),
            prognosisSource.split(","),
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            prognosisFs.split(","));
            
    var audioName = data.sensor.audio.name;
    if(audioName!=",")
        creatSensorSetting(
            "audio",
            audioName.split(","));
            
    
    var gpioName = data.sensor.gpio.ch1_name+","+
        data.sensor.gpio.ch2_name+","+
        data.sensor.gpio.ch3_name+","+
        data.sensor.gpio.ch4_name;
    if(gpioName!=",,,")
        creatSensorSetting(
            "digitalInput",
            gpioName.split(","));

    if(data.sensor.distance.ch1_name!="")
        creatSensorSetting(
            "distance",
            data.sensor.distance.ch1_name);
            
    if(data.sensor.modbus){
        var modbus_connect = JSON.parse(data.sensor.modbus.connection);
        var modbus_setting = JSON.parse(data.sensor.modbus.setting);
        var i=0;
        if(modbus_connect.length>0){
            creatSensorSetting(
                "modbus",
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                undefined,
                modbus_connect,
                modbus_setting);
        }
    }
    
    for(var i=0;i<_maxSegRule;i++)
        loadSeg(data.seg['segmentation_'+(i+1)]);
    
    
    if(parseInt(data.seg['tdma']["period"])>=60){
        $(".loopModeForRuleBtn").hide();
        $(".loopModeForRuleBox").show();
        console.log("$(.loopModeForRuleBox).show();");
		$(".loopModeForRule[value='Yes']").prop('checked',true); 
		$(".loopModeForRuleBox").find(".displayBox").eq(0).show();
		console.log(".loopModeForRuleBox).find(.displayBox).eq(0).show();");
        $("#loopTimeForRule").val(data.seg['tdma']["period"]);
    }
    
    sensorBoxCheck();
    segBoxCheck();
}



function loadAnalogHub(bus,rate,name,type,mode,select,maxValue,minValue,biasValue,unit){
    if(name==",,,,,,,")
        return;

    name = name.split(",");
    type = type.split(",");
    mode = mode.split(",");
    select = select.split(",");
    maxValue = maxValue.split(",");
    minValue = minValue.split(",");
    biasValue = biasValue.split(",");
    unit = unit.split(",");

    var hub = "voltageInput";
    for(var i=0;i<mode.length;i++){
        if(mode[i]!="0"){
            hub="currentInput";
            break;
        }
    }
    if(hub=="voltageInput")
        mode=undefined;
    if(hub=="currentInput")
        for(var i;i<mode.length;i++){
            mode[i]=(parseInt(mode[i])-1)+"";
        }
        
    for(var i;i<maxValue.length;i++){
        maxValue[i]=parseFloat(maxValue[i]);
        minValue[i]=parseFloat(minValue[i]);
        biasValue[i]=parseFloat(biasValue[i]);
    }
    creatSensorSetting(
        hub,
        name,
        bus+"",
        rate,
        select,
        mode,
        type,
        maxValue,
        minValue,
        biasValue,
        unit);
}

function loadVibHub(bus,rate,name,level){
    if(name==",,,,,")
        return;

    name = name.split(",");
    level = level.split(",");

    creatSensorSetting(
        "vibration",
        name,
        bus+"",
        rate,
        level);
}

function loadSeg(obj){
    var type = (parseInt(obj.type)-1)+"";
    if(type=="-1")
        return;
    creatSegSetting(obj.name,
        obj.unit,
        obj.sub_unit,
        type,
        obj.upload_seg,
        obj.basis_column,
        obj.target_column,
        obj.ignore_time,
        obj.operation_reverse,
        obj.operation_count,
        obj.operation_filter,
        obj.sub_operation_count,
        obj.operation_threshold,
        obj.operation_shift,
        obj.padding,
        obj.certain_freq,
        obj.upload_extraction,
        obj.extraction_project,
        obj.operation_rising_falling,
        obj.upload_interval,
        obj.fe_json,
        obj.operation_trigger_threshold,
        obj.trigger_column,
        obj.trigger_shift,
        obj.smart_grid,
        obj.use_filter_exception);
}

function getForm(){
    var ret = {};
    for(var i=0;i<_maxSegRule;i++)
        ret['segmentation_'+(i+1)]={};

    //setting defualt or load
    //sensorSettingLoad(ret,undefined,"setting",false);
    sensorSettingLoad(ret,undefined,"voltageInput",true);
    sensorSettingLoad(ret,undefined,"digitalInput",true);
    sensorSettingLoad(ret,undefined,"vibration",true);
    sensorSettingLoad(ret,undefined,"distance",true);
    sensorSettingLoad(ret,undefined,"prognosis",true);
    sensorSettingLoad(ret,undefined,"modbus",true);
    sensorSettingLoad(ret,undefined,"audio",true);

    //console.log(ret);
    var sensorSetting = $(".sensorSetting");
    //console.log(sensorSetting.length);
    for(var i=0;i<sensorSetting.length;i++){
        let obj = sensorSetting.eq(i);
        let sensorType = obj.attr("type");
        sensorSettingLoad(ret,obj,sensorType,false);

    }
    
    //setting defualt
    //console.log(ret);
    for(var i=0;i<_maxSegRule;i++)
        segRuleLoad(ret['segmentation_'+(i+1)],undefined,ret,true,i+1);
    var segRule = $(".segRule");
    for(var i=0;i<_maxSegRule;i++)
        if(segRule.length>i)
            segRuleLoad(ret['segmentation_'+(i+1)],segRule.eq(i),ret,false,i+1);

    ret.tdma={}
    ret.tdma.period=0
    if($(".loopModeForRule:checked").val()=="Yes")
        ret.tdma.period = Math.ceil($("#loopTimeForRule").val());
        console.log(ret.tdma.period);
    
    //console.log(ret);
    return ret;
}

function sensorSettingLoad(obj,form,type,useDefault){
    if(useDefault){
        if(type=="voltageInput" || type=="currentInput"){
            obj.analog={};
            obj.analog.sample_rate="1000,1000,1000,1000";
            obj.analog.hub1_name=",,,,,,,";
            obj.analog.hub2_name=",,,,,,,";
            obj.analog.hub3_name=",,,,,,,";
            obj.analog.hub4_name=",,,,,,,";
            obj.analog.hub1_type="d,d,d,d,d,d,d,d";
            obj.analog.hub2_type="d,d,d,d,d,d,d,d";
            obj.analog.hub3_type="d,d,d,d,d,d,d,d";
            obj.analog.hub4_type="d,d,d,d,d,d,d,d";
            obj.analog.hub1_mode="0,0,0,0,0,0,0,0";
            obj.analog.hub2_mode="0,0,0,0,0,0,0,0";
            obj.analog.hub3_mode="0,0,0,0,0,0,0,0";
            obj.analog.hub4_mode="0,0,0,0,0,0,0,0";
            obj.analog.hub1_select="0,0,0,0,0,0,0,0";
            obj.analog.hub2_select="0,0,0,0,0,0,0,0";
            obj.analog.hub3_select="0,0,0,0,0,0,0,0";
            obj.analog.hub4_select="0,0,0,0,0,0,0,0";
            obj.analog.hub1_level="1,1,1,1,1,1,1,1";
            obj.analog.hub2_level="1,1,1,1,1,1,1,1";
            obj.analog.hub3_level="1,1,1,1,1,1,1,1";
            obj.analog.hub4_level="1,1,1,1,1,1,1,1";
            obj.analog.hub1_max = "0,0,0,0,0,0,0,0";
            obj.analog.hub2_max = "0,0,0,0,0,0,0,0";
            obj.analog.hub3_max = "0,0,0,0,0,0,0,0";
            obj.analog.hub4_max = "0,0,0,0,0,0,0,0";
            obj.analog.hub1_min = "0,0,0,0,0,0,0,0";
            obj.analog.hub2_min = "0,0,0,0,0,0,0,0";
            obj.analog.hub3_min = "0,0,0,0,0,0,0,0";
            obj.analog.hub4_min = "0,0,0,0,0,0,0,0";
            obj.analog.hub1_bias = "0,0,0,0,0,0,0,0";
            obj.analog.hub2_bias = "0,0,0,0,0,0,0,0";
            obj.analog.hub3_bias = "0,0,0,0,0,0,0,0";
            obj.analog.hub4_bias = "0,0,0,0,0,0,0,0";
            obj.analog.hub1_unit = "V,V,V,V,V,V,V,V";
            obj.analog.hub2_unit = "V,V,V,V,V,V,V,V";
            obj.analog.hub3_unit = "V,V,V,V,V,V,V,V";
            obj.analog.hub4_unit = "V,V,V,V,V,V,V,V";
        }
        else if(type=="digitalInput"){
            obj.gpio={};
            obj.gpio.ch1_name="";
            obj.gpio.ch2_name="";
            obj.gpio.ch3_name="";
            obj.gpio.ch4_name="";
        }
        else if(type=="vibration"){
            obj.vibration={};
            obj.vibration.sample_rate="1000,1000,1000,1000";
            obj.vibration.hub1_name=",,,,,";
            obj.vibration.hub2_name=",,,,,";
            obj.vibration.hub3_name=",,,,,";
            obj.vibration.hub4_name=",,,,,";
            obj.vibration.hub1_level="4,4,4,4,4,4";
            obj.vibration.hub2_level="4,4,4,4,4,4";
            obj.vibration.hub3_level="4,4,4,4,4,4";
            obj.vibration.hub4_level="4,4,4,4,4,4";
        }
        else if(type=="distance"){
            obj.distance={};
            obj.distance.ch1_name="";
        }
        else if(type=="prognosis"){
            obj.prognosis={};
            obj.prognosis.sample_rate="1000,1000";
            obj.prognosis.name=",";
            obj.prognosis.level="4,4";
            obj.prognosis.mode="VPA308R,VPA308R";
            obj.prognosis.location=_porgnosis_usb_location.join(",");
            //console.log(obj);
        }
        else if(type=="audio"){
            obj.audio={};
            obj.audio.name=",";
        }
        else if(type=="setting"){
            obj.setting={};
            obj.setting.device_name="DAQ_device";
            obj.setting.upload_raw="0";
        }
        else if(type=="modbus"){
            obj.modbus={};
            obj.modbus.connection="[]";
            obj.modbus.setting="[]";
        }
        return;
    }
    /*
    if(type=="setting"){
        if(!obj.setting)
            obj.setting={};
        obj.setting.device_name=$("#deviceName").val();
        
        if($("input[name='uploadResultSampling']:checked").val()=="Yes")
            obj.setting.upload_raw="1";
        else
            obj.setting.upload_raw="0";
    }
    else */
    if(type=="distance"){
        var enableChannel=form.children(".sensorSelect").children(".showHeddened").children(".enableChannel");
        if(enableChannel.eq(0).attr("checked")){
            var sensorChName=form.children(".sensorSelect").children(".heddened").children(".sensorChName");
            obj.distance.ch1_name=sensorChName.val();
        }
        else{
            obj.distance.ch1_name="";
        }
    }
    else if(type=="modbus"){
        var enableChannel=form.children(".sensorSelect").children(".showHeddened").children(".enableChannel");
        var modbus_connect = [];
        var modbus_setting = [];
        for(var i=0;i<enableChannel.length;i++){
            if(enableChannel.eq(i).attr("checked")){
                var subSamplingModbusBaud=form.children(".sensorSelect").children(".heddened").children(".subSamplingModbusBaud").eq(i).val();
                var subSamplingModbusLength=form.children(".sensorSelect").children(".heddened").children(".subSamplingModbusLength").eq(i).val();
                var subSamplingModbusParity=form.children(".sensorSelect").children(".heddened").children(".subSamplingModbusParity").eq(i).val();
                var subSamplingModbusStopBit=form.children(".sensorSelect").children(".heddened").children(".subSamplingModbusStopBit").eq(i).val();
                var sensorModbusPeriod=form.children(".sensorSelect").children(".heddened").children(".sensorModbusPeriod").eq(i).val();
                var sensorModbusRegister=form.children(".sensorSelect").children(".heddened").children(".sensorModbusRegister").eq(i).attr("registerJSON");
                var connection = {};
                connection.usb_num=i;
                connection.location=_modbus_usb_location[i];
                connection.buad=parseFloat(subSamplingModbusBaud);;
                connection.length=parseFloat(subSamplingModbusLength);;
                connection.parity=subSamplingModbusParity;
                connection.stopbit=subSamplingModbusStopBit;
                connection.period=parseFloat(sensorModbusPeriod);
                var setting = JSON.parse(sensorModbusRegister);
                modbus_connect.push(connection);
                modbus_setting.push(setting);
            }
        }
        obj.modbus.connection=JSON.stringify(modbus_connect);
        obj.modbus.setting=JSON.stringify(modbus_setting);
    }
    else{
        var enableChannel=form.children(".sensorSelect").children(".showHeddened").children(".enableChannel");
        var sensorChName=form.children(".sensorSelect").children(".heddened").children(".sensorChName");
        var sensorChMaxValue=form.children(".sensorSelect").children(".heddened").find(".sensorChMaxValue");
        var sensorChMinValue=form.children(".sensorSelect").children(".heddened").find(".sensorChMinValue");
        var sensorChBiasValue=form.children(".sensorSelect").children(".heddened").find(".sensorChBiasValue");
        var sensorChUnit=form.children(".sensorSelect").children(".heddened").find(".sensorChUnit");
        var analogSource=form.children(".sensorSelect").children(".heddened").children(".analogSource");
        var analogRange=form.children(".sensorSelect").children(".heddened").children(".analogRange");
        var analogType=form.children(".sensorSelect").children(".heddened").find(".analogType");
        var subSamplingRate=form.children(".sensorSelect").children(".heddened").children(".subSamplingRate");
        var nameData = [];
        var typeData = [];
        var modeData = [];
        var levelData = [];
        var fsData = [];
        var maxValData = [];
        var minValData = [];
        var biasValData = [];
        var unitData = [];
        for(var i=0;i<enableChannel.length;i++){
            if(enableChannel.eq(i).attr("checked")){
                nameData.push(sensorChName.eq(i).val());
                if(analogType.length>0)
                    typeData.push(analogType.eq(i).val());
                if(analogRange.length>0){
                    levelData.push(analogRange.eq(i).val());
                    //console.log(analogRange.eq(i));
                    //console.log(analogRange.eq(i).val());
                }
                    
                if(sensorChMaxValue.length>0)
                    maxValData.push(sensorChMaxValue.eq(i).val());
                if(sensorChMinValue.length>0)
                    minValData.push(sensorChMinValue.eq(i).val());
                if(sensorChBiasValue.length>0)
                    biasValData.push(sensorChBiasValue.eq(i).val());
                if(sensorChUnit.length>0)
                    unitData.push(sensorChUnit.eq(i).val());
                if(subSamplingRate.length>0)
                    fsData.push(subSamplingRate.eq(i).val());
                    
                if(type=="voltageInput"){
                    modeData.push("0");
                }
                if(type=="currentInput"){
                    modeData.push((parseInt(analogSource.eq(i).val())+1)+"");
                }
                if(type=="prognosis"){
                    modeData.push(analogSource.eq(i).val());
                }
            }
            else{
                //push default value
                nameData.push("");
                if(analogType.length>0)
                    typeData.push(analogType.eq(i).val());
                    //typeData.push("d");
                if(type=="voltageInput"){
                    modeData.push("0");
                }
                if(type=="currentInput"){
                    //modeData.push("1");
                    modeData.push((parseInt(analogSource.eq(i).val())+1)+"");
                }
                if(type=="prognosis"){
                    modeData.push(_porgnosis_vib_sour_defualt);
                }
                if(analogRange.length>0){
                    if(type=="vibration")
                        levelData.push("4");
                    else if(type=="prognosis")
                        levelData.push(_porgnosis_vib_range_val_defualt[_porgnosis_vib_sour_defualt]);
                    else
                        levelData.push(analogRange.eq(i).attr("data-default"));
                }
                if(subSamplingRate.length>0){
                    if(type=="prognosis")
                        fsData.push(_porgnosis_vib_fs_defualt[_porgnosis_vib_sour_defualt]);
                    else
                        fsData.push(subSamplingRate.eq(i).attr("data-default"));
                }
                if(sensorChMaxValue.length>0)
                    maxValData.push(sensorChMaxValue.eq(i).attr("data-default"));
                if(sensorChMinValue.length>0)
                    minValData.push(sensorChMinValue.eq(i).attr("data-default"));
                if(sensorChBiasValue.length>0)
                    biasValData.push(sensorChBiasValue.eq(i).attr("data-default"));
                if(sensorChUnit.length>0)
                    unitData.push(sensorChUnit.eq(i).attr("data-default"));
                
                /*
                if(sensorChMaxValue.length>0)
                    maxValData.push("0");
                if(sensorChMinValue.length>0)
                    minValData.push("0");
                if(sensorChBiasValue.length>0)
                    biasValData.push("0");
                if(sensorChUnit.length>0){
                    if(type=="voltageInput"){
                        unitData.push("V");
                    }
                    if(type=="currentInput"){
                        unitData.push("A");
                    }
                }
                */
            }
        }
        if(type=="voltageInput" || type=="currentInput"){
            var bus=form.children("select[name='sensorBus']").val();
            var sampleRate = form.children("select[name='sensorFs']").val();
            var sampleRateArr = obj.analog.sample_rate.split(",");
            sampleRateArr[parseInt(bus)-1]=sampleRate;
            obj.analog.sample_rate=sampleRateArr.join(",");
            if(bus=="1"){
                obj.analog.hub1_name=nameData.join(",");
                obj.analog.hub1_type=typeData.join(",");
                obj.analog.hub1_mode=modeData.join(",");
                obj.analog.hub1_level=levelData.join(",");
                obj.analog.hub1_max=maxValData.join(",");
                obj.analog.hub1_min=minValData.join(",");
                obj.analog.hub1_bias=biasValData.join(",");
                obj.analog.hub1_unit=unitData.join(",");
            }
            else if(bus=="2"){
                obj.analog.hub2_name=nameData.join(",");
                obj.analog.hub2_type=typeData.join(",");
                obj.analog.hub2_mode=modeData.join(",");
                obj.analog.hub2_level=levelData.join(",");
                obj.analog.hub2_max=maxValData.join(",");
                obj.analog.hub2_min=minValData.join(",");
                obj.analog.hub2_bias=biasValData.join(",");
                obj.analog.hub2_unit=unitData.join(",");
            }
            else if(bus=="3"){
                obj.analog.hub3_name=nameData.join(",");
                obj.analog.hub3_type=typeData.join(",");
                obj.analog.hub3_mode=modeData.join(",");
                obj.analog.hub3_level=levelData.join(",");
                obj.analog.hub3_max=maxValData.join(",");
                obj.analog.hub3_min=minValData.join(",");
                obj.analog.hub3_bias=biasValData.join(",");
                obj.analog.hub3_unit=unitData.join(",");
            }
            else if(bus=="4"){
                obj.analog.hub4_name=nameData.join(",");
                obj.analog.hub4_type=typeData.join(",");
                obj.analog.hub4_mode=modeData.join(",");
                obj.analog.hub4_level=levelData.join(",");
                obj.analog.hub4_max=maxValData.join(",");
                obj.analog.hub4_min=minValData.join(",");
                obj.analog.hub4_bias=biasValData.join(",");
                obj.analog.hub4_unit=unitData.join(",");
            }
        }
        else if(type=="vibration"){
            var bus=form.children("select[name='sensorBus']").val();
    
            var sampleRate = form.children("select[name='sensorFs']").val();
            var sampleRateArr = obj.vibration.sample_rate.split(",");
            sampleRateArr[parseInt(bus)-1]=sampleRate;
            obj.vibration.sample_rate=sampleRateArr.join(",");
            
            if(bus=="1"){
                obj.vibration.hub1_name=nameData.join(",");
                obj.vibration.hub1_level=levelData.join(",");
            }
            else if(bus=="2"){
                obj.vibration.hub2_name=nameData.join(",");
                obj.vibration.hub2_level=levelData.join(",");
            }
            else if(bus=="3"){
                obj.vibration.hub3_name=nameData.join(",");
                obj.vibration.hub3_level=levelData.join(",");
            }
            else if(bus=="4"){
                obj.vibration.hub4_name=nameData.join(",");
                obj.vibration.hub4_level=levelData.join(",");
            }
        }
        else if(type=="prognosis"){
            obj.prognosis.sample_rate=fsData.join(",");
            obj.prognosis.name=nameData.join(",");
            obj.prognosis.level=levelData.join(",");
            obj.prognosis.mode=modeData.join(",");
        }
        else if(type=="audio"){
            obj.audio.name=nameData.join(",");
        }
        else if(type=="digitalInput"){
            obj.gpio.ch1_name=nameData[0];
            obj.gpio.ch2_name=nameData[1];
            obj.gpio.ch3_name=nameData[2];
            obj.gpio.ch4_name=nameData[3];
        }

    }

}

function segRuleLoad(obj,form,sensor_form,useDefault,segCnt){
    //console.log(segCnt);
    obj.name="";
    obj.unit="";
    obj.sub_unit="";
    obj.type="0";
    obj.upload_seg="0";
    obj.basis_column="";
    obj.target_column="";
    obj.ignore_time="0";
    obj.operation_reverse="0";
    obj.operation_count="0";
    obj.operation_filter="0";
    obj.sub_operation_count="0";
    obj.operation_threshold="0";
    obj.operation_shift="0";
    obj.padding="0";
    obj.certain_freq="0";
    obj.upload_extraction="0";
    obj.extraction_project="";
    obj.operation_rising_falling="0";
    obj.operation_trigger_threshold="0";
    obj.trigger_column="";
    obj.trigger_shift="0";
    obj.upload_interval="0";
    obj.fe_json="";
    obj.smart_grid="0";
    obj.use_filter_exception="0";
    obj.default_flag="0";
    obj.manuel_flag="0";
    if(useDefault==true)
        return;
    console.log(sensor_form);
    obj.name=form.find(".segRuleName").val();
    obj.unit=form.find(".segRuleUnit").val();
    obj.sub_unit=form.find(".segRuleSubunit").val();
    var redio = form.find(".leftLabel");
    var segSourceList = form.find(".segSourceList").children();
    for(var i=0;i<segSourceList.length;i++){
        if(segSourceList.eq(i).attr("enable")=="1"){
            if(obj.target_column!="")
                obj.target_column+=",";
            //console.log(segSourceList.eq(i));
            obj.target_column+=segSourceList.eq(i).val();
        }
    }
    obj.type=(parseInt(form.attr("rule"))+1)+"";
    obj.basis_column = form.find(".SegSource").val();
    if(obj.type=="1")
        obj.basis_column = "";
    obj.operation_count = form.find(".segOperationLen").val();
    obj.ignore_time = form.find(".segIgnoreLen").val();
    if(form.find(".segThreshold").length>0)
        obj.operation_threshold = form.find(".segThreshold").val();
    
    if(form.find(".centerFrequency").length>0)
        if(redio.children(".centerFrequencySelect:checked").val()=="Yes")
            obj.certain_freq = form.find(".centerFrequency").val();
        
    if(form.find(".signalPadding").length>0)
        obj.padding = form.find(".signalPadding").val();
    
    if(redio.children(".sgSelect").length>0)
        obj.smart_grid = redio.children(".sgSelect:checked").val();
    if(form.find(".segShift").length>0)
        obj.operation_shift = form.find(".segShift").val();
    if(redio.children(".subOperation:checked").val()=="Yes")
        obj.sub_operation_count = form.find(".subOperationSec").val();
    if(redio.children(".signalFilter:checked").val()=="Yes")
        obj.operation_filter = form.find(".signalFilterSec").val();
    if(redio.children(".useFilterException:checked").val()=="Yes")
        obj.use_filter_exception = "1";
    if(redio.children(".signalReverse:checked").val()=="Yes")
        obj.operation_reverse = "1";
    if(redio.children(".uploadResultSeg:checked").val()=="Yes")
        obj.upload_seg = "1";
    if(redio.children(".uploadResultSeg:checked").val()=="Yes")
        obj.upload_interval = form.find(".uploadResultSegInterval").val();
    console.log(redio.children(".uploadResultFE:checked"));
    if(redio.children(".uploadResultFE:checked").val()=="Yes"){
        obj.fe_json = form.find(".featureSelectBtn").attr("fedata");
        //console.log(obj.fe_json)
        if(obj.fe_json!="" & !obj.fe_json.includes('"default_flag":1') & !obj.fe_json.includes('"manual_flag":1')){
            try{
                jData = JSON.parse(obj.fe_json);
                obj.upload_extraction = "1";
                obj.extraction_project = jData.project_id;
            }
            catch(e){
                obj.upload_extraction = "";
                obj.extraction_project = "";
                obj.fe_json="";
            }
        }
        else if (obj.fe_json.includes('"default_flag":1')){
            try{
                jData = JSON.parse(obj.fe_json);
                obj.upload_extraction = "1";
                obj.extraction_project = 2147483646-segCnt;
                console.log(jData.base_freq);
                
                var temp_project_id = 2147483646-segCnt;
                var temp_parameter_list = [];
                var temp_feature_config = '';
                for(var i=0;i<segSourceList.length;i++){
                    if(segSourceList.eq(i).attr("enable")=="1"){
                        //append to temp_parameter_list
                        if(temp_parameter_list!="")
                            temp_parameter_list+=",";
                        temp_parameter_list+=('"'+segSourceList.eq(i).val()+'"');
                        //append to temp_feature_config
                        
                        temp_sampleRate=chFindSamplerate(segSourceList.eq(i).val(),sensor_form);
                        console.log(segSourceList.eq(i).val());
                        console.log(temp_sampleRate);
                        var single_feature_config='{"parameter": "'+segSourceList.eq(i).val()+'", "spectrum": [{"item": "Time_Domain", "spectrum_param": {"samplerate": '+temp_sampleRate+', "level":7}, "bin": 1, "statistical": ["Rms"]}, '+'{"item": "VibVelocity", "spectrum_param": {"samplerate": '+temp_sampleRate+', "base_freq": '+jData.base_freq+'}, "bin": 10, "statistical": ["VelRms","LowPsdRms","MidPsdRms","HighPsdRms"]}]}';
                        console.log(single_feature_config);
                        if(temp_feature_config!="")
                            temp_feature_config+=",";
                        temp_feature_config+=single_feature_config;
                        //console.log(temp_feature_config);
                    }
                }
                
                obj.fe_json = '{"project_id": '+temp_project_id+', "parameter_list": ['+temp_parameter_list+'], "feature_config": ['+temp_feature_config+']}';
                console.log(obj);
            }
            catch(e){
                obj.upload_extraction = "";
                obj.extraction_project = "";
                obj.fe_json=""; 
            }
        }
        else if(obj.fe_json.includes('"manual_flag":1')){
			try{
				jData = JSON.parse(obj.fe_json);
                obj.upload_extraction = "1";
                obj.extraction_project = 2147483646-segCnt;
                console.log(jData.base_freq);
                console.log("Manual Feature Flag = 1")
                var temp_project_id = 2147483646-segCnt;
                var temp_parameter_list = [];
                var temp_feature_config = '';
                for(var i=0;i<segSourceList.length;i++){
                    if(segSourceList.eq(i).attr("enable")=="1"){
                        //append to temp_parameter_list
                        if(temp_parameter_list!="")
                            temp_parameter_list+=",";
                        temp_parameter_list+=('"'+segSourceList.eq(i).val()+'"');
                        //append to temp_feature_config
                        
                        temp_sampleRate=chFindSamplerate(segSourceList.eq(i).val(),sensor_form);
                        console.log(segSourceList.eq(i).val());
                        console.log(temp_sampleRate);
                        var single_feature_config='{"parameter": "'+segSourceList.eq(i).val()+'", "spectrum": [';
                        
                        if (jData.mean==='1' || jData.max==='1' || jData.min==='1' || jData.p2p==='1' || jData.rms==='1' || jData.std==='1'){
							single_feature_config+='{"item": "Time_Domain", "spectrum_param": {"samplerate": '+temp_sampleRate+', "level":7}, "bin": 1, "statistical": [';
							if (jData.mean==='1'){single_feature_config+='"Mean",'}
							if (jData.max==='1'){single_feature_config+='"Max",'}
							if (jData.min==='1'){single_feature_config+='"Min",'}
							if (jData.p2p==='1'){single_feature_config+='"Max_Min",'}
							if (jData.rms==='1'){single_feature_config+='"Rms",'}
							if (jData.std==='1'){single_feature_config+='"Std",'}
							single_feature_config=single_feature_config.substr(0,single_feature_config.length - 1);
							single_feature_config+=']}';
						}
						if ((jData.mean==='1' || jData.max==='1' || jData.min==='1' || jData.p2p==='1' || jData.rms==='1' || jData.std==='1') && (jData.Velrms==='1' || jData.lowPsdRms==='1' || jData.midPsdRms==='1' || jData.highPsdRms==='1')){
							single_feature_config+=',';
						}
                        if (jData.Velrms==='1' || jData.lowPsdRms==='1' || jData.midPsdRms==='1' || jData.highPsdRms==='1'){
							single_feature_config+='{"item": "VibVelocity", "spectrum_param": {"samplerate": '+temp_sampleRate+', "base_freq": '+jData.base_freq+'}, "bin": 10, "statistical": ['
							if (jData.velrms==='1'){single_feature_config+='"VelRms",'}
							if (jData.lowPsdRms==='1'){single_feature_config+='"LowPsdRms",'}
							if (jData.midPsdRms==='1'){single_feature_config+='"MidPsdRms",'}
							if (jData.highPsdRms==='1'){single_feature_config+='"HighPsdRms",'}
							single_feature_config=single_feature_config.substr(0,single_feature_config.length - 1);
							single_feature_config+=']}]}';
						}
						else{
							single_feature_config+=']}';
						}
                        
                        //var single_feature_config='{"parameter": "'+segSourceList.eq(i).val()+'", "spectrum": [{"item": "Time_Domain", "spectrum_param": {"samplerate": '+temp_sampleRate+', "level":7}, "bin": 1, "statistical": ["Rms"]}, '+'{"item": "VibVelocity", "spectrum_param": {"samplerate": '+temp_sampleRate+', "base_freq": '+jData.base_freq+'}, "bin": 10, "statistical": ["VelRms","LowPsdRms","MidPsdRms","HighPsdRms"]}]}';
                        console.log(single_feature_config);
                        if(temp_feature_config!="")
                            temp_feature_config+=",";
                        temp_feature_config+=single_feature_config;
                        //console.log(temp_feature_config);
                    }
                }
                
                obj.fe_json = '{"project_id": '+temp_project_id+', "parameter_list": ['+temp_parameter_list+'], "feature_config": ['+temp_feature_config+']}';
                console.log(obj);
			}
			catch(e){
				obj.upload_extraction = "";
                obj.extraction_project = "";
                obj.fe_json="";
			}
		}
    }
    
    /*
    if(redio.children(".uploadResultFE:checked").val()=="Yes" && form.find(".featureSelectList").val()!="-1"){
        obj.upload_extraction = "1";
        obj.extraction_project = form.find(".featureSelectList").val();
    }
    */
    if(redio.children(".triggerEnable:checked").val()=="Yes"){
        obj.operation_rising_falling=redio.children(".startEdge:checked").val();
        obj.operation_trigger_threshold = form.find(".triggerThreshold").val();
        obj.trigger_column = form.find(".TriggerSource").val();
        obj.trigger_shift = form.find(".triggerShift").val();
    }
        
}

function formCheck(type){
    if(type=="sensor"){
        var USB=[false,false,false,false];
        /*
        var deviceName = $("#deviceName").val();
        if(deviceName.length==0){
            $("#deviceName").focus();
            alert("The device name cannot empty.");
            return false;
        }
        if(!isＷord(deviceName)){
            $("#deviceName").focus();
            alert("The device name only accepts symbol, English and numbers.");
            return false;
        }
        */
        var bus = $("select[name='sensorBus']");
        var busSelect = [];
        for(var i=0;i<bus.length;i++){
            let obj = bus.eq(i)
            let busIndex=obj.val();
            if(busSelect.indexOf(busIndex)<0){
                busSelect.push(busIndex);
            }
            else{
                obj.focus();
                //alert("The bus setting is repeat.");
                alert(_language.sample.check_bus_repeat);
                return false;
            }
        }


        var sensorSetting = $(".sensorSetting");
        refreshSensor();
        for(var i=0;i<sensorSetting.length;i++){
            let obj = sensorSetting.eq(i);
            let sensorType = obj.attr("type");
            let busIndex=parseInt(obj.children("select[name='sensorBus']").val())-1;
            //console.log(busIndex,_sensorList);
            //console.log(sensorType);
            if(!isNaN(busIndex) && _sensorList.bus[busIndex].name!=sensorType && _isSPIIDER){
                //if(!confirm("The bus "+(busIndex+1)+" isn't "+ sensorType +". Do you want to continue?")){
                if(!confirm(_language.sample.check_bus_1+(busIndex+1)+_language.sample.check_bus_2+ sensorType +_language.sample.check_bus_3)){
                    obj.children("select[name='sensorBus']").focus();
                    return;
                }
            }
            else if(sensorType=="vibration" && _isSPIIDER){
                var channelList = "";
                //console.log(_sensorList.bus[busIndex].channel);
                for(var j=0;j<_sensorList.bus[busIndex].channel.length;j++){
                    let states = obj.children(".sensorSelect").children("label").children(".enableChannel").eq(j).attr("checked");
                    if(states && _sensorList.bus[busIndex].channel[j]!=1){
                        if(channelList!="")
                            channelList+=", ";
                        channelList+=(j+1)+"";
                    }
                }
                if(channelList!=""){
                    //if(!confirm("The vibration (bus "+(busIndex+1)+") channel ("+channelList+") is empty on device. Do you want to continue?")){
                    if(!confirm(_language.sample.check_vib_1+(busIndex+1)+_language.sample.check_vib_2+channelList+_language.sample.check_vib_3)){
                        obj.children("select[name='sensorBus']").focus();
                        return;
                    }
                }
            }
            else if(sensorType=="distance" && _sensorList.distance==false && _isSPIIDER){
                //if(!confirm("The distance sensor isnot installed. Do you want to continue?")){
                if(!confirm(_language.sample.check_distanse)){
                    return;
                }
            }
            else if(sensorType=="audio" || sensorType=="prognosis" || sensorType=="modbus"){
                let enableChannel = obj.find(".enableChannel");
                //console.log(enableChannel);
                for(var j=0;j<enableChannel.length;j++){
                    if(enableChannel.eq(j).attr("checked")=="checked"){
                        if(USB[j]){
                            //alert("USB port "+(j+1)+" conflict. Please check setting.");
                            alert(_language.sample.check_audio_1+(j+1)+_language.sample.check_audio_2);
                            return false;
                        }
                        else{
                            USB[j]=true;
                        }
                    }
                }
            }
        }
    }
    if(type=="sensor" || type=="channel"){
        var checkbox = $(".enableChannel:checked");
        for(var i=0;i<checkbox.length;i++){
            let checkList = [
                ".sensorChName",
                ".sensorChMaxValue",
                ".sensorChMinValue",
                ".sensorChBiasValue",
                ".sensorChUnit",
                ".sensorModbusPeriod"];
            let emptyAlermList = [
                _language.sample.check_empty_name,
                _language.sample.check_empty_max_value,
                _language.sample.check_empty_min_value,
                _language.sample.check_empty_bias,
                _language.sample.check_empty_unit,
                _language.sample.modbus_err_period_empty];
            let detectAlermList = [
                _language.sample.check_format_name,
                _language.sample.check_format_max_value,
                _language.sample.check_format_min_value,
                _language.sample.check_format_bias,
                _language.sample.check_format_unit,
                _language.sample.modbus_err_period_format];
            let detectFuncList = [
                isＷord,
                isFloat,
                isFloat,
                isFloat,
                isＷord,
                isFloat];
            let valueList = [
                -1,
                -1,
                -1,
                -1,
                -1,
                100];
            let parseAlermList = [
                -1,
                -1,
                -1,
                -1,
                -1,
                parseFloat];
            let valueAlermList = [
                -1,
                -1,
                -1,
                -1,
                -1,
                _language.sample.modbus_err_period_vlaue];
            
            for(var j=0;j<checkList.length;j++){
                let obj = checkbox.eq(i).parent().next().find(checkList[j]);
                if(obj.length == 0)
                    continue
                let value = obj.val();
                //console.log(checkList[j]);
                //console.log(obj);
                //console.log(value);
                if(value.length==0){
                    obj.focus();
                    alert(emptyAlermList[j]);
                    return false;
                }
                else if(! detectFuncList[j](value)){
                    obj.focus();
                    alert(detectAlermList[j]);
                    return false;
                }
                else if(valueList[j]!=-1){
                    if(parseAlermList[j](value)<valueList[j]){
                        obj.focus();
                        alert(valueAlermList[j]);
                        return false;
                    }
                }
            }
            let max = checkbox.eq(i).parent().next().find(".sensorChMaxValue").val();
            let min = checkbox.eq(i).parent().next().find(".sensorChMinValue").val();
            if(max<=min){
                checkbox.eq(i).parent().next().find(".sensorChMaxValue").focus();
                //alert("The max value can't be less min value.");
                alert(_language.sample.check_max_min);
                
                return false;
            }
        }
    }
    else{
        
        var ruleName = $(".segRuleName");
        for(var i=0;i<ruleName.length;i++){
            let val = ruleName.eq(i).val();
            if(val==""){
                ruleName.eq(i).focus();
                //alert("The rule name is empty.");
                alert(_language.sample.check_rule_name_empty);
                return false;
            }
            else if(!isＷord(val)){
                ruleName.eq(i).focus();
                //alert("The rule name format is error.");
                alert(_language.sample.check_rule_name_format);
                return false;
            }
        }
        var ruleUnit = $(".segRuleUnit");
        for(var i=0;i<ruleUnit.length;i++){
            let val = ruleUnit.eq(i).val();
            if(!isＷord(val) && val!=""){
                ruleUnit.eq(i).focus();
                //alert("The unit name format is error.");
                alert(_language.sample.check_unit_name_empty);
                return false;
            }
        }
        var ruleSubunit = $(".segRuleSubunit");
        for(var i=0;i<ruleSubunit.length;i++){
            let val = ruleSubunit.eq(i).val();
            if(!isＷord(val) && val!=""){
                ruleSubunit.eq(i).focus();
                //alert("The subunit name format is error.");
                alert(_language.sample.check_unit_name_format);
                return false;
            }
        }
        
        var ruleNameList = [];
        for(var i=0;i<ruleName.length;i++){
            let val = ruleName.eq(i).val()+"_"+ruleUnit.eq(i).val()+"_"+ruleSubunit.eq(i).val();
            if(ruleNameList.indexOf(val)!=-1){
                ruleName.eq(i).focus();
                //alert("The rule name is repeat.");
                alert(_language.sample.check_rule_name_repeat);
                return false;
            }
            else
                ruleNameList.push(val);
        }
    
        var segRule = $(".segRule");
        for(var i=0;i<segRule.length;i++){
            var segSourceList = segRule.eq(i).children(".segSourceList").children();
            var flag=false;
            for(var j=0;j<segSourceList.length;j++){
                if(segSourceList.eq(j).attr("enable")=="1")
                    flag=true;
            }
            if(flag!=true){
                let name = segRule.eq(i).children(".segRuleName").val();
                //alert("The rule '"+name+"' not select output item.");
                alert(_language.sample.check_rule_not_item_1+name+_language.sample.check_rule_not_item_2);
                return false;
            }
        }
        
        var segRule = $(".segRule");
        for(var i=0;i<segRule.length;i++){
            var segSelectList = segRule.eq(i).children(".segSelectList");
                //console.log(segSelectList.css("display"));
            if(segSelectList.css("display")!="none"){
                if(segSelectList.val()==null){
                    let name = segRule.eq(i).children(".segRuleName").val();
                    segSelectList.focus();
                    alert(_language.sample.check_rule_not_input_1+name+_language.sample.check_rule_not_input_2);
                    return false;
                }
            }
        }
        
        for(var i=0;i<_inputCheckList.length;i++){
            let obj=_inputCheckList[i];
            for(var j=0;j<$(obj.class).length;j++){
                let subObj = $(obj.class).eq(j);
                if(obj.preObj!=""){
                    let preObj = subObj.parent().find(".leftLabel").children(obj.preObj+":checked");
                    if(preObj.length==0)
                        preObj = subObj.parent().parent().find(".leftLabel").children(obj.preObj+":checked");
                        
                    if(preObj.val() != obj.isTrue)
                        continue;
                }
                if(typeof(obj.callback)=="function"){
                    return obj.callback(subObj);
                }
                
                let objVal=subObj.val();
                if (objVal=="") { 
                    subObj.focus();
                    //alert("The input cannoot empty."); 
                    alert(_language.sample.check_input_empty); 
                    return false;
                }
                
                if (!isFloat(objVal)) { 
                    subObj.focus();
                    //alert("Please input number."); 
                    alert(_language.sample.check_input_num); 
                    return false;
                }
                let objFloat=parseFloat(objVal);
                if(obj.min!=-1 && objFloat < obj.min){
                    subObj.focus();
                    //alert("The input value less than range."); 
                    alert(_language.sample.check_input_range_L); 
                    return false;
                }
                if(obj.max!=-1 && objFloat > obj.max){
                    subObj.focus();
                    //alert("The input value heigher than range."); 
                    alert(_language.sample.check_input_range_H); 
                    return false;
                }
    
            }
        }

    }
    return true;
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


function sensorBoxCheck(){
    if($(".sensorDaughter").length>=_maxSensorDaughter && 
        $(".sensorDistange").length>=_maxSensorDistange &&
        $(".sensorDI").length>=_maxSensorDI &&
        $(".sensorPrognosis").length>=_maxPrognosisSerial &&
        $(".sensorAudio").length>=_maxMicrophon &&
        $(".sensorModbus").length>=_maxModbus)
        $("#sensorAddBox").hide();
}


function segBoxCheck(){
    if($(".segRule").length>=_maxSegRule)
        $("#segAddBox").hide();
}

function chFindSamplerate(chName,sensorform){
    //Analog
    //console.log("TEST for: "+chName);
    if(chName.includes('aX')||chName.includes('aY')||chName.includes('aZ')){
        chName = chName.split('_')[1];
    }
    if(sensorform.analog.hub1_name.includes(chName)){
        temp_fs=sensorform.analog.sample_rate.split(",")[0];
    }
    else if(sensorform.analog.hub2_name.includes(chName)){
        temp_fs=sensorform.analog.sample_rate.split(",")[1];
    }
    else if(sensorform.analog.hub3_name.includes(chName)){
        temp_fs=sensorform.analog.sample_rate.split(",")[2];
    }
    else if(sensorform.analog.hub4_name.includes(chName)){
        temp_fs=sensorform.analog.sample_rate.split(",")[3];
    }
    //Vibration
    else if(sensorform.vibration.hub1_name.includes(chName)){
        temp_fs=sensorform.vibration.sample_rate.split(",")[0];
    }
    else if(sensorform.vibration.hub2_name.includes(chName)){
        temp_fs=sensorform.vibration.sample_rate.split(",")[1];
    }
    else if(sensorform.vibration.hub3_name.includes(chName)){
        temp_fs=sensorform.vibration.sample_rate.split(",")[2];
    }
    else if(sensorform.vibration.hub4_name.includes(chName)){
        temp_fs=sensorform.vibration.sample_rate.split(",")[3];
    }
    //prognosis
    else if(sensorform.prognosis.name.split(",")[0]==chName){
        temp_fs=sensorform.prognosis.sample_rate.split(",")[0];
    }
    else if(sensorform.prognosis.name.split(",")[1]==chName){
        temp_fs=sensorform.prognosis.sample_rate.split(",")[1];
    }
    //Audio
    else if(sensorform.audio.name.includes(chName)){
        temp_fs=44100;
    }
    return temp_fs;
}
