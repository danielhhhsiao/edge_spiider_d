_language = {} //use on all object

_api_sysSetting = "/api/system/config";

_page_lang_change_map = {}
_page_lang_change_map["/"] = _lang_home_page
_page_lang_change_map["/home"] = _lang_home_page
_page_lang_change_map["/fromFile"] = _lang_fromFile_page
_page_lang_change_map["/sample"] = _lang_sample_page
_page_lang_change_map["/system"] = _lang_system_page
_page_lang_change_map["/login"] = _lang_login_page
_page_lang_change_map["/status"] = _lang_status_page
_page_lang_change_map["/network"] = _lang_network_page
_page_lang_change_map["/wifi"] = _lang_wifi_page

_lang_map = {}
_lang_map["english"] = _language_english
_lang_map["chinese"] = _language_chinese
_lang_map["traditional_chinese"] = _language_t_chinese

$(function(){
	initLanguage();
	setTimeout(checkLanguage,1);
});

function initLanguage(){
	var language = cookieFind("language");
	if(language in _lang_map)
		_language=_lang_map[language]();
	else
		_language=_language_english();
	
	if(location.pathname in _page_lang_change_map)
		_page_lang_change_map[location.pathname]();
	else
		_lang_404_page();
}

function checkLanguage(){
    var settings = {
        "url": _api_sysSetting,
        "type": "GET",
        "timeout": 0
    };
      
    $.ajax(settings).success(function (response) {
        var done = false;
        if(response.state==200){
			var language = cookieFind("language");
			if(language != response.data.language.value){
				cookieAdd("language",response.data.language.value,999999999);
				window.location.reload(); 
			}
        }
    }).error(function(e){
		// pass
	});
}

function putHtml(name,value){
	var obj = $(name);
	obj.html(value);
	
	//for test
	if(obj.length==0)
		console.log("!!obj undefind",name);
}

function putValue(name,value){
	var obj = $(name);
	obj.val(value);
	
	//for test
	if($(obj).length==0)
		console.log("!!obj undefind",name);
}

function _lang_home_page(){
	var isPCCheck = cookieFind("isPC");
	if(isPCCheck=="true"){
		_lang_sample_page();
		return;
	}
	console.log("_lang_home_page");
	document.title = _language.html.home.title
	putHtml("#lang_home_sample",_language.html.home.sample );
	putHtml("#lang_home_system",_language.html.home.system );
	putHtml("#lang_home_wifi",_language.html.home.wifi );
	putHtml("#lang_home_network",_language.html.home.network );
	putHtml("#lang_home_device",_language.html.home.device );
	putHtml("#lang_home_export",_language.html.home.exprot );
}
function _lang_fromFile_page(){
	console.log("_lang_fromFile_page");
	document.title = _language.html.fromFile.title
	putHtml("#lang_fromFile_sample",_language.html.fromFile.sample);
	putHtml("#lang_fromFile_system",_language.html.fromFile.system);
	putHtml(".lang_fromFile_import",_language.html.fromFile.import);
	putHtml(".lang_fromFile_export",_language.html.fromFile.export);
}
function _lang_sample_page(){
	console.log("_lang_sample_page");
	document.title = _language.html.sample.title
	putHtml("#lang_sample_tab_sensor",_language.html.sample.tab_sensor);
	putHtml("#lang_sample_tab_seg",_language.html.sample.tab_seg);
	putHtml("#lang_sample_tab_test",_language.html.sample.tab_test);
	putHtml("#lang_sample_sensor_source",_language.html.sample.source);
	putHtml("option[value='voltageInput']",_language.html.sample.source_vol);
	putHtml("option[value='currentInput']",_language.html.sample.source_cur);
	putHtml("option[value='digitalInput']",_language.html.sample.source_Di);
	putHtml("option[value='vibration']",_language.html.sample.source_vib);
	putHtml("option[value='prognosis']",_language.html.sample.source_vpa308);
	putHtml("option[value='audio']",_language.html.sample.source_audio);
	putHtml("option[value='modbus']",_language.html.sample.source_modbus);
	putHtml("option[value='distance']",_language.html.sample.source_distance);
	putHtml("#lang_sample_seg_rule",_language.html.sample.rule);
	putHtml("option[value='0']",_language.html.sample.rule_normal);
	putHtml("option[value='1']",_language.html.sample.rule_strangth);
	putHtml("option[value='2']",_language.html.sample.rule_freq);
	putHtml("option[value='3']",_language.html.sample.rule_sg);
	putHtml("#lang_sample_seg_TDMA",_language.html.sample.rule_tdma);
	putHtml("#lang_sample_seg_TDMA_remind",_language.html.sample.rule_tdma_remind);
	putHtml(".lang_radio_no",_language.html.sample.rule_tdma_n);
	putHtml(".lang_radio_yes",_language.html.sample.rule_tdma_y);
	putHtml("#lang_sample_sensor_result",_language.html.sample.sensor_result);
	putHtml("#lang_sample_sensor_result_n",_language.html.sample.sensor_result_n);
	putHtml("#lang_sample_sensor_result_link",_language.html.sample.sensor_result_link);
	putHtml("#lang_sample_seg_result",_language.html.sample.seg_result);
	putHtml("#lang_sample_seg_result_n",_language.html.sample.seg_result_n);
	putHtml("#lang_sample_seg_result_link",_language.html.sample.seg_result_link);
	putValue("#oldSensorTest",_language.html.sample.old_test);
	putValue("#sensorTest",_language.html.sample.new_test);
	putHtml(".showAdvanced",_language.html.universal.advanced);
	putValue("#sensorAdd",_language.html.universal.add);
	putValue("#segAdd",_language.html.universal.add);
	putValue("#sensorSubmit",_language.html.universal.submit );
	putValue("#segSubmit",_language.html.universal.submit );
}
function _lang_system_page(){
	console.log("_lang_system_page");
	document.title = _language.html.system.title;
	putHtml("option[value='english']",_language.html.system.lang_english);
	putHtml("option[value='chinese']",_language.html.system.lang_chinese);
	putHtml("option[value='traditional_chinese']",_language.html.system.lang_t_chinese);
	
	putHtml("#lang_system_status",_language.html.system.status);
	putHtml("#lang_system_model_server",_language.html.system.model_server);
	putHtml("#lang_system_status_server",_language.html.system.status_server);
	putHtml("#lang_system_smart_grid",_language.html.system.smart_grid);
	putHtml("#lang_system_FTP",_language.html.system.FTP);
	putHtml("#lang_system_NTP",_language.html.system.NTP);
	putHtml("#lang_system_time",_language.html.system.time);
	putHtml("#lang_system_pin",_language.html.system.pin);
	putHtml("#lang_system_reboot",_language.html.system.reboot);
	putValue("#enableSubmit",_language.html.universal.submit);
	putValue("#webSubmit",_language.html.universal.submit);
	putValue("#statusSubmit",_language.html.universal.submit);
	putValue("#sgSubmit",_language.html.universal.submit);
	putValue("#ftpSubmit",_language.html.universal.submit);
	putValue("#ntpSubmit",_language.html.universal.submit);
	putValue("#timeSubmit",_language.html.universal.submit);
	putValue("#pinSubmit",_language.html.universal.submit);
	putValue("#langSubmit",_language.html.universal.submit);
	putValue("#rebootSubmit",_language.html.system.submit_btn);
	putValue(".btnShow",_language.html.universal.show);
	putHtml(".lang_system_work",_language.html.system.status_work);
	putHtml(".lang_system_idle",_language.html.system.status_idle);
	putHtml(".lang_universal_enable",_language.html.universal.enable);
	putHtml(".lang_universal_disable",_language.html.universal.disable);
	putHtml(".lang_system_hostname",_language.html.system.hostname);
	putHtml(".lang_system_proxy",_language.html.system.proxy);
	putHtml(".lang_system_port",_language.html.system.port);
	putHtml("#lang_system_upload_api",_language.html.system.upload_api);
	putHtml("#lang_system_mqtt_topic",_language.html.system.mqtt_topic);
	putHtml("#lang_system_mqtt_name",_language.html.system.mqtt_name);
	putHtml("#lang_system_mqtt_passwd",_language.html.system.mqtt_passwd);
	putHtml("#lang_system_ftp_user",_language.html.system.ftp_user);
	putHtml("#lang_system_ftp_passwd",_language.html.system.ftp_passwd);
	putHtml("#lang_system_ftp_file",_language.html.system.ftp_file_type);
	putHtml("option[value='0']",_language.html.system.ftp_file_disable);
	putHtml("option[value='1']",_language.html.system.ftp_file_csv);
	putHtml("option[value='2']",_language.html.system.ftp_file_binary);
	putHtml("option[value='3']",_language.html.system.ftp_file_both);
	putHtml("#lang_system_pin_remind",_language.html.system.pin_remind);
	putHtml("#lang_system_pin_valida",_language.html.system.pin_valida);
	putHtml("#lang_system_change_language",_language.html.system.lang_title);
}
function _lang_login_page(){
	console.log("_lang_login_page");
	document.title = _language.html.login.title
	putHtml("#lang_login_main_box",_language.html.login.main_box );
	putHtml("#lang_login_remind",_language.html.login.remind );
	putValue("#pinSubmit",_language.html.universal.submit );
	putValue(".btnShow",_language.html.universal.show );
}
function _lang_status_page(){
	console.log("_lang_status_page");
	document.title = _language.html.status.title
	putHtml("#lang_status_system",_language.html.status.system);
	putHtml("#lang_status_network",_language.html.status.network);
	putHtml("#lang_status_update_time",_language.html.status.update_time);
	putHtml("#lang_status_edge_data",_language.html.status.edge_data); 
	putHtml("#lang_status_error",_language.html.status.error); 
	putHtml("#OTASubmit",_language.html.status.OTA);
	putValue("#clearSubmit",_language.html.status.clear_file);
	putValue("#clearMemorySubmit",_language.html.status.clear_queue);
}
function _lang_network_page(){
	console.log("_lang_network_page");
	document.title = _language.html.network.title
	putHtml("#lang_network_wifi_title",_language.html.network.wifi_title);
	putHtml("#lang_network_wifi_link",_language.html.network.wifi_link);
	putHtml("#lang_network_wifi_ip",_language.html.network.wifi_ip);
	putHtml(".lang_network_ip_address",_language.html.network.ip_address);
	putHtml(".lang_network_ip_mask",_language.html.network.ip_mask);
	putHtml(".lang_network_ip_gw",_language.html.network.ip_gw);
	putHtml("#lang_network_lan1_ip",_language.html.network.lan1_title);
	putHtml("#lang_network_lan2_ip",_language.html.network.lan2_title);
	putHtml("#lang_network_ap_title",_language.html.network.ap_title);
	putHtml("#lang_network_ap_ssid",_language.html.network.ap_ssid);
	putHtml("#lang_network_ap_old_pw",_language.html.network.ap_old_pw);
	putHtml("#lang_network_ap_new_pw",_language.html.network.ap_new_pw);
	putHtml("#lang_network_ap_confirm",_language.html.network.ap_comfirm);
	putValue("#wifiSubmit",_language.html.universal.submit);
	putValue("#lanSubmit",_language.html.universal.submit);
	putValue("#lan2Submit",_language.html.universal.submit);
	putValue("#apSubmit",_language.html.universal.submit);
	putValue(".btnShow",_language.html.universal.show);
	putHtml(".lang_network_auto",_language.html.network.ip_auto);
	putHtml(".lang_network_manual",_language.html.network.ip_manual);
}
function _lang_wifi_page(){
	console.log("_lang_wifi_page");
	document.title = _language.html.wifi.title
}
function _lang_404_page(){
	console.log("_lang_404_page");
	document.title = _language.html.page404.title;
}




function _language_english(){
	console.log("use english");
	var language = {}
	language.check_left_page = 					"There are forms that have not been saved. Are you sure to leave the page?";
	language.check_over_setting = 				"This operation will overwrite the original setting. Are you sure to execute？";
	
	language.topBar = {}
	language.topBar.change_network = 			"Your device already change network and SPIIDER.";
	language.topBar.spiider_time =	 			"SPIIDER-D time is ";
	language.topBar.device_time = 				". Your device is ";
	language.topBar.update_time = 				". Please update the time.";
	language.topBar.FW_not_finish = 			"Upload FW not finish. Please wait!";
	language.topBar.FW_upload_OK = 				"Upload successfully.";
	language.topBar.FW_upload_error = 			"Upload fail. msg : ";
	language.topBar.status_idel_connected = 	"SPIIDER-D idle, and status server is connected";
	language.topBar.status_work_connected = 	"SPIIDER-D work, and status server is connected";
	language.topBar.status_idel_disconnected = 	"SPIIDER-D idle, and status server is disconnected";
	language.topBar.status_work_disconnected = 	"SPIIDER-D work, and status server is disconnected";
	language.topBar.status_DAQ_disconnected = 	"SPIIDER-D is disconnected";
	language.topBar.load = 						"Load";
	
	language.system = {}
	language.system.status_server_host_err = 	"Status server hostname format error.";
	language.system.status_server_proxy_err = 	"Server proxy format error.";
	language.system.status_server_set_OK = 		"Setting successfully.";
	language.system.status_server_set_err = 	"Server setting error: ";
	language.system.status_server_req_err = 	"Server setting error (from server).";
	language.system.clear_file_OK = 			"Clear local file successfully.";
	language.system.clear_file_err = 			"Clear local file error: ";
	language.system.clear_file_req_err = 		"Clear local file error. (from server)";
	language.system.clear_queue_OK = 			"Clear queue successfully.";
	language.system.clear_queue_err = 			"Clear queue error: ";
	language.system.clear_queue_req_err = 		"Clear queue error. (from server)";
	language.system.smart_grid = 				"Smart Grid (MQTT) Server ";
	language.system.smart_grid_empty = 			" can't empty.";
	language.system.smart_grid_format = 		" format error.";
	language.system.smart_grid_OK = 			"Smart Grid (MQTT) Setting successfully."
	language.system.smart_grid_err = 			"Smart Grid (MQTT) setting error: ";
	language.system.smart_grid_req_err = 		"Smart Grid (MQTT) setting error. (from server)";
	language.system.NTP_format = 				"NTP IP address format error.";
	language.system.NTP_proxy = 				"NTP proxy format error.";
	language.system.NTP_err = 					"NTP setting error: ";
	language.system.NTP_OK = 					"Setting successfully.";
	language.system.NTP_req_err = 				"NTP setting error. (from server)";
	language.system.FTP_format = 				"FTP IP address format error.";
	language.system.FTP_proxy = 				"FTP proxy format error.";
	language.system.FTP_err = 					"FTP setting error: ";
	language.system.FTP_OK = 					"FTP Setting successfully.";
	language.system.FTP_req_err = 				"FTP setting error. (from server)";
	language.system.pin_format_valida = 		"New password and check password are difference.";
	language.system.pin_format_num = 			"The password only accepts numbers.";
	language.system.pin_format_min_len = 		"The password length cannot be less than 4.";
	language.system.pin_format_max_len = 		"The password length cannot be more than 20.";
	language.system.pin_err = 					"PIN setting req error: ";
	language.system.pin_OK = 					"Setting successfully.";
	language.system.pin_req_err = 				"PIN setting error. (from server)";
	language.system.lang_set_err = 				"Language setting req error: ";
	language.system.lang_set_OK = 				"Language setting successfully.";
	language.system.lang_req_err = 				"Language setting error. (from server)";
	language.system.reboot_check = 				"The operation will force reboot device. Do you want to continue?";
	language.system.reboot_err = 				"Reboot req error: ";
	language.system.reboot_OK = 				"Reboot req successfully. Please wait.";
	language.system.reboot_check = 				"Reboot error. (from server)";
	language.system.AP_SSID_empty = 			"The ap name cannot be empty.";
	language.system.AP_SSID_format = 			"The ap name only accepts symbol, English and numbers.";
	language.system.AP_passwd_err = 			"Old password input error.";
	language.system.AP_passwd_valida = 			"New password and check password are difference.";
	language.system.AP_passwd_format = 			"The password only accepts English and numbers.";
	language.system.AP_passwd_len = 			"The password length cannot be less then 8.";
	language.system.AP_err = 					"AP setting req error: ";
	language.system.AP_OK = 					"Setting successfully. Please wait moment to take effect.";
	language.system.AP_req_err = 				"AP setting error.";
	language.system.IP_format = 				"IP address format error.";
	language.system.IP_mask_format = 			"Subnet mask IP address format error.";
	language.system.IP_gw_format = 				"Default getway IP address format error.";
	language.system.IP_err = 					"IP setting error: ";
	language.system.IP_OK = 					"Setting successfully.";
	language.system.IP_req_err = 				"IP setting error. (from server)";
	language.system.time_format = 				"Date format error. Follow: yyyy-MM-dd hh:mm:ss";
	language.system.time_empty = 				"Please select time.";
	language.system.time_err = 					"Time setting error: ";
	language.system.time_OK = 					"Setting successfully.";
	language.system.time_req_err = 				"Time setting error. (from server)";
	language.system.work_err = 					"work state change error: ";
	language.system.work_OK = 					"Request sent successfully. Waiting for device processing";
	language.system.work_req_err = 				"work state change error. (from server)";
	language.system.work_wait_err = 			"wait work state change req error: ";
	language.system.work_wait_OK = 				"Process successfully.";
	language.system.work_wait_req_err = 		"wait work state change error.";
	language.system.import_err = 				"import file req error: ";
	language.system.import_OK = 				"Request sent successfully.";
	language.system.OTA_err = 					"Update req error: ";
	language.system.OTA_req_OK = 				"Request sent successfully. Please wait upload FW.";
	language.system.load_err = 					"Load system setting req error: ";
	language.system.load_req_err = 				"Load system setting req error. (from server)";
	
	language.wifi = {};
	language.wifi.connect = 					"Are you sure that?\nConnect ";
	language.wifi.input_passwd = 				"Please input the password.";
	language.wifi.disconnect = 					"Are you sure that?\nDisconnect ";
	language.wifi.req_OK = 						"Request sent successfully. Please wait a moment.";
	
	language.login = {};
	language.login.passwd_err = 				"Password error";
	language.login.req_err = 					"PIN req error: ";
	language.login.device_change = 				"PIN request error. Please check connection with SPIIDER-D.";
	
	language.form = {};
	language.form.version = 					"Version: ";
	language.form.wifiMac = 					"Wi-Fi mac: ";
	language.form.wifiIP = 						"Wi-Fi IP: ";
	language.form.eth0Mac = 					"LAN1 mac: ";
	language.form.eth0IP = 						"LAN1 IP: ";
	language.form.eth1Mac = 					"LAN2 mac: ";
	language.form.eth1IP = 						"LAN2 IP: ";
	language.form.systemTime = 					"Local Time: ";
	language.form.uploadTimeAPI = 				"(API) ";
	language.form.uploadTimeFTP = 				"(FTP) ";
	language.form.uploadTimeMQTT = 				"(MQTT) ";
	language.form.uploadTimeStatus = 			"(Status) ";
	language.form.st1ErrMsg = 					"(ST1) ";
	language.form.st2ErrMsg = 					"(ST2) ";
	language.form.localCount = 					"Local file count : ";
	language.form.memoryCount = 				"Memory queue count : ";
	
	language.sample = {};
	language.sample.FE_json_check = 			"Please upload feature extraction format json file.";
	language.sample.FE_json_file_err =			"Feature extraction format file content error.";
	language.sample.keep_test_alert = 			"Testing is continue. Please wait processing.";
	language.sample.sensor_name_validat = 		"The name is duplicated or format error, please rename";
	language.sample.remove_check = 				"The operation cannot recovery. Do you want to continue?";
	language.sample.over_len_for_bus = 			"Bus is full, please remove device on bus.";
	language.sample.over_len_for_distanse = 	"The distance sensor already up to limit.";
	language.sample.over_len_for_prognosis = 	"The prognosis vibration sensor already up to limit.";
	language.sample.over_len_for_DI = 			"The digital input sensor already up to limit.";
	language.sample.over_len_for_audio = 		"The audio input already up to limit.";
	language.sample.over_len_for_modbus = 		"The Modbus input already up to limit.";
	language.sample.not_save_setting = 			"Your setting doesn't save. Please submit and tun again.";
	language.sample.enable_err = 				"Work state change req error: ";
	language.sample.enable_OK = 				"Request sent successfully. Waiting for device processing";
	language.sample.enable_req_err = 			"Work state change error. (from server)" ;
	language.sample.test_setting_not_save = 	"Your setting doesn't save. Please submit and tun again.";
	language.sample.test_old_data_check = 		"The device will use old sampling data to run the segmentation setting. Do you want to continue?";
	language.sample.test_err = 					"Run test error: ";
	language.sample.test_OK = 					"Request sent successfully. Waiting for device processing";
	language.sample.test_req_err = 				"Run test error. (from server)";
	language.sample.test_delay_change_err = 	"wait test state change req error: ";
	language.sample.test_delay_err = 			"Wait test error: ";
	language.sample.test_delay_req_err = 		"Wait test error. (from server)";
	language.sample.test_time = 				"Please input maximun testing time";
	language.sample.test_time_unit = 			"sec";
	language.sample.test_time_format = 			"Please input integer number.";
	language.sample.test_time_format_limit = 	"Please input number from 1 to ";
	language.sample.test_status_1_0 = 			" Initial parameter...";
	language.sample.test_status_2_0 = 			" Sampling is done ";
	language.sample.test_status_2_1 = 			"%";
	language.sample.test_status_3_0 = 			" Stop sample processing...";
	language.sample.test_status_4_0 = 			" Analysis segmentation data...";
	language.sample.test_status_5_0 = 			" Wait to upload done for ";
	language.sample.test_status_5_1 = 			" data.";
	language.sample.test_status_6_0 = 			" Plot the sensor chart ";
	language.sample.test_status_7_0 = 			" Plot the segmentation chart ";
	language.sample.test_status_8_0 = 			" Testing done!";
	language.sample.sensor_submit_err = 		"Update sensor setting error: ";
	language.sample.sensor_submit_OK = 			"Update sensor setting successfully.";
	language.sample.sensor_submit_req_err =		"Update sensor setting error. (from server)";
	language.sample.seg_submit_err = 			"Update segmentation setting req error: ";
	language.sample.seg_submit_OK = 			"Update segmentation setting successfully.";
	language.sample.seg_submit_req_err = 		"Update segmentation setting error.";
	language.sample.source = 					"Sample source";
	language.sample.source_voltate = 			"Voltage input";
	language.sample.source_current = 			"Current input";
	language.sample.source_vibration = 			"Vibration";
	language.sample.source_distance = 			"Distance";
	language.sample.source_DI = 				"Digital input";
	language.sample.source_vibration_P = 		"Vibration(Prognosis)";
	language.sample.source_audio = 				"Audio";
	language.sample.source_modbus = 			"Modbus(RTU)";
	language.sample.select_bus = 				"Select bus (auto):";
	language.sample.select_bus1 = 				"Bus 1";
	language.sample.select_bus2 = 				"Bus 2";
	language.sample.select_bus3 = 				"Bus 3";
	language.sample.select_bus4 = 				"Bus 4";
	language.sample.Sample_rate = 				"Sampling rate: ";
	language.sample.Sample_rate_alert = 		"Can't setting even channel when sampling rate is 8000 Hz.";
	language.sample.Signal_source = 			"Signal source: ";
	language.sample.Sample_range = 				"Signal range:";
	language.sample.Signal_type = 				"Signal type: ";
	language.sample.sensor_differential =		"Differential";
	language.sample.sensor_single_ended =		"Single-ended";
	language.sample.sensor_engineering_up =		"Engineering upper limit : ";
	language.sample.sensor_engineering_low =	"Engineering lower limit : ";
	language.sample.sensor_engineering_offset =	"Engineering value offset : ";
	language.sample.sensor_engineering_unit =	"Engineering unit : ";
	language.sample.channel_setting = 			"Channel setting:";
	language.sample.jump_descript = 			"Please follow signal range background color to set the jumper:";
	language.sample.jump_descript_remain = 		"(Need to switch jumper on board)";
	language.sample.DI_scal_descript = 			"Please follow DC24V / DC12V type to set jumper:";
	language.sample.modbus_baud = 				"Baud: ";
	language.sample.modbus_date_length = 		"Data length(bit): ";
	language.sample.modbus_parity = 			"Parity: ";
	language.sample.modbus_stop_bit = 			"Stop bit: ";
	language.sample.modbus_period = 			"Sample period(ms): ";
	language.sample.modbus_data = 				"Data: ";
	language.sample.modbus_device = 			"Device address(hex): ";
	language.sample.modbus_register = 			"Register(hex): ";
	language.sample.modbus_response = 			"Response time(ms): ";
	language.sample.modbus_check = 				"Error check type: ";
	language.sample.modbus_type = 				"Data type: ";
	language.sample.modbus_name = 				"Name";
	language.sample.modbus_name_end = 			": ";
	language.sample.modbus_order = 				"Order: ";
	language.sample.modbus_ratio = 				"Ratio: ";
	language.sample.modbus_err_device_format = 	"Devive address format error!";
	language.sample.modbus_err_reg_format = 	"Slave register format error!";
	language.sample.modbus_err_device_empty = 	"Devive address can't empty!";
	language.sample.modbus_err_device_range = 	"Devive over the range 0x0~0xFF";
	language.sample.modbus_err_reg_empty = 		"Slave register can't empty!";
	language.sample.modbus_err_reg_range= 		"Slave over the range 0x0~0xFFFF";
	language.sample.modbus_err_name_empty = 	"Name can't be all empty.";
	language.sample.modbus_err_name_format = 	"Name format error.";
	language.sample.modbus_err_name_repeat = 	"Naming repeat.";
	language.sample.modbus_err_retio_format = 	"Retio format error.";
	language.sample.modbus_err_retio_empty = 	"Retio can't be empty.";
	language.sample.modbus_err_period_empty = 	"Modbus period can't be empty.";
	language.sample.modbus_err_period_format = 	"Modbus period format error.";
	language.sample.modbus_err_period_vlaue = 	"Modbus period have to be heigher than 100.";
	language.sample.sensor_enable = 			"Enable";
	language.sample.sensor_name = 				"Name: ";
	language.sample.sensor_remove = 			"Remove this sensor:";
	language.sample.sensor_remove_btn = 		"Remove";
	language.sample.rule_normal = 				"Rule: Normal";
	language.sample.rule_strength = 			"Rule: By Strength";
	language.sample.rule_frequency = 			"Rule: By Frequency.";
	language.sample.rule_smart_grid = 			"Rule: Smar grid.";
	language.sample.rule_name = 				"Rule Name:";
	language.sample.rule_name_unit = 			"Unit Name: (allow empty)";
	language.sample.rule_name_subunit = 		"Subunit Name: (allow empty)";
	language.sample.input_item = 				"Input item:";
	language.sample.output_item = 				"Output item:";
	language.sample.output_item_enable = 		"(Click item to enable 'blue')";
	language.sample.trigger_enable = 			"Enable trigger method:";
	language.sample.trigger_no = 				"No. Process without trigger.";
	language.sample.trigger_yes = 				"Yes";
	language.sample.trigger_item = 				"Trigger item";
	language.sample.trigger_edge = 				"start edge:";
	language.sample.trigger_rising = 			"Rising";
	language.sample.trigger_falling = 			"Falling";
	language.sample.trigger_thrshold = 			"Trigger Threshold";
	language.sample.trigger_shift = 			"start point shift";
	language.sample.time_unit = 				"sec.";
	language.sample.seg_window_size = 			"Window size.";
	language.sample.seg_capture_length =		"Capture length";
	language.sample.seg_ignore_length =			"Ignore length";
	language.sample.seg_threshold =				"Segmentation Threshold:";
	language.sample.seg_shift =					"Start point shift";
	language.sample.seg_sub_cap_use_windows =	"Use window size.";
	language.sample.seg_sub_cap_use_manual =	"Manual setting";
	language.sample.seg_sub_cap_length =		"Length";
	language.sample.seg_freq_main =				"Target frequency";
	language.sample.seg_freq_auto =				"Auto settings";
	language.sample.seg_freq_manual =			"Manual settings";
	language.sample.seg_freq_sub_auto =			"Use auto size.";
	language.sample.seg_freq_sub_manual =		"Manual setting.";
	language.sample.seg_freq_range = 			"1~Fs/2 Hz";
	language.sample.seg_filter_select =			"Signal filter ";
	language.sample.seg_filter_enable =			"Enable";
	language.sample.seg_filter_disable =		"Disable";
	language.sample.seg_filter_remain =			"Condition";
	language.sample.seg_filter_exception =		"Use exception data between 5% to 95% of filter size";
	language.sample.seg_upload =				"Upload segmentation result";
	language.sample.seg_upload_interval =		"Upload interval";
	language.sample.seg_upload_remain =			"(When Feature extraction enable)";
	language.sample.seg_FE_project =			"Feature extraction project";
	language.sample.seg_FE_upload =				"Upload feature extraction result:";
	language.sample.seg_FE_upload_file =		"Setting upload";
	language.sample.seg_FE_upload_file_btn =	"Select file";
	language.sample.seg_remove =				"Remove this setting:";
	language.sample.seg_remove_btn =			"Remove";
	language.sample.seg_edit =					"edit. . . ";
	language.sample.import_setting_err =		"import file req error: ";
	language.sample.import_setting_OK =			"Request sent successfully.";
	language.sample.seg_FE_json_parse = 		"Json parse error.";
	language.sample.seg_FE_json_format = 		"Data format error.";
	language.sample.seg_FE_json_OK = 			"Upload OK!";
	language.sample.load_err = 					"Load setting req error: ";
	language.sample.load_req_err = 				"Load setting req error (from server): ";
	language.sample.check_bus_repeat = 			"The bus setting is repeat.";
	language.sample.check_bus_1 = 				"The bus ";
	language.sample.check_bus_2 = 				" isn't ";
	language.sample.check_bus_3 = 				". Do you want to continue?";
	// "The bus "+(busIndex+1)+" isn't "+ sensorType +". Do you want to continue?"
	language.sample.check_vib_1 = 				"The vibration (bus ";
	language.sample.check_vib_2 = 				") channel (";
	language.sample.check_vib_3 = 				") is empty on device. Do you want to continue?";
	//"The vibration (bus "+(busIndex+1)+") channel ("+channelList+") is empty on device. Do you want to continue?"
	language.sample.check_distanse = 			"The distance sensor isnot installed. Do you want to continue?";
	language.sample.check_audio_1 = 			"USB port ";
	language.sample.check_audio_2 = 			" conflict. Please check setting.";
	//"USB port "+(j+1)+" conflict. Please check setting."
	language.sample.check_empty_name = 			"The name of the channel is empty.";
    language.sample.check_empty_max_value = 	"The max value of the channel is empty.";
    language.sample.check_empty_min_value = 	"The min value of the channel is empty.";
    language.sample.check_empty_bias = 			"The bias value of the channel is empty.";
    language.sample.check_empty_unit = 			"The unit of the channel is empty.";
    language.sample.check_format_name = 		"The name of the channel is format error.";
    language.sample.check_format_max_value = 	"The max value of the channel is format error.";
    language.sample.check_format_min_value = 	"The min value of the channel is format error.";
    language.sample.check_format_bias = 		"The bias value of the channel is format error.";
    language.sample.check_format_unit = 		"The unit of the channel is format error.";
    language.sample.check_max_min = 			"The max value can't be less min value.";
    language.sample.check_rule_name_empty = 	"The rule name is empty.";
    language.sample.check_rule_name_format = 	"The rule name format is error.";
    language.sample.check_unit_name_empty = 	"The unit name format is error.";
    language.sample.check_unit_name_format = 	"The subunit name format is error.";
	language.sample.check_rule_name_repeat = 	"The rule name is repeat.";
	language.sample.check_rule_not_item_1 = 	"The rule '";
	language.sample.check_rule_not_item_2 = 	"' not select output item.";
	//"The rule '"+name+"' not select output item."
	language.sample.check_input_empty =			"The input cannot empty.";
	language.sample.check_input_num =			"Please input number.";
	language.sample.check_input_range_L =		"The input value less than range.";
	language.sample.check_input_range_H =		"The input value heigher than range.";
	
	language.test={}
	language.test.alert_done = 					"Testing done.";
	language.test.alert_title = 				"Upload result (success/total) ";
	language.test.alert_seg_csv_FTP = 			"Seg. csv file was sent by FTP : ";
	language.test.alert_seg_binary_FTP = 		"Seg. binary file was sent by FTP : ";
	language.test.alert_seg_json_API = 			"Seg. result was sent by API : ";
	language.test.alert_FE_csv_FTP = 			"FE csv file was sent by FTP : ";
	language.test.alert_FE_binary_FTP = 		"FE binary file was sent by FTP : ";
	language.test.alert_FE_json_API = 			"FE result was sent by API : ";
	language.test.alert_smart_grid_MQTT = 		"Smart grid was sent by MQTT : ";
	language.test.html_title = 					"Message(success/total)";
	language.test.html_seg_title = 				"Segmentation:";
	language.test.html_seg_csv_FTP = 			". . . FTP(csv) = ";
	language.test.html_seg_binary_FTP = 		". . . FTP(binary) = ";
	language.test.html_seg_json_API = 			". . . Web API = ";
	language.test.html_FE_title = 				"Feature Extraction:";
	language.test.html_FE_csv_FTP = 			". . . FTP(csv) = ";
	language.test.html_FE_binary_FTP = 			". . . FTP(binary) = ";
	language.test.html_FE_json_API = 			". . . Web API = ";
	language.test.html_smart_grid_title = 		"Smart grid:";
	language.test.html_smart_grid_MQTT = 		". . . MQTT = ";
	
	language.html = {}
	language.html.universal = {}
	language.html.universal.hidden = 			"Hidden";
	language.html.universal.show = 				"Show";
	language.html.universal.submit = 			"Submit";
	language.html.universal.ok = 				"OK";
	language.html.universal.remove = 			"Remove";
	language.html.universal.cancel = 			"Cancel";
	language.html.universal.advanced = 			"Show advanced";
	language.html.universal.add = 				"Add";
	language.html.universal.enable = 			"Enable";
	language.html.universal.disable = 			"Disable";
	
	language.html.home = {}
	language.html.home.title = 					"Home";
	language.html.home.sample = 				"Sample</br>parameter";
	language.html.home.system = 				"System</br>setting";
	language.html.home.wifi = 					"Wi-Fi</br>selection";
	language.html.home.network = 				"Network</br>setting";
	language.html.home.device = 				"Device</br>status";
	language.html.home.exprot = 				"Export/Import</br>setting";
	
	language.html.page404 = {}
	language.html.page404.title = 				"404 page";
	language.html.page404.remain = 				"404 not found. Jump after";
	language.html.page404.time_unit = 			"sec.";
	//"404 not found. Jump after "+sec+" sec."
	
	language.html.fromFile = {}
	language.html.fromFile.title = 				"Import/Export";
	language.html.fromFile.topBar = 			"Import/Export";
	language.html.fromFile.sample = 			"Sample setting";
	language.html.fromFile.system = 			"System setting";
	language.html.fromFile.import = 			"Import";
	language.html.fromFile.export = 			"Export";
	
	language.html.login = {}
	language.html.login.title = 				"Device login";
	language.html.login.main_box = 				"Device login";
	language.html.login.remind = 				"PIN 4-20 numbers";
	//"404 not found. Jump after "+sec+" sec."
	
	language.html.wifi = {}
	language.html.wifi.title = 					"Wi-Fi Select";
	language.html.wifi.topBar = 				"Wi-Fi Select";
	
	language.html.network = {}
	language.html.network.title = 				"Network setting";
	language.html.network.topBar = 				"Network Setting";
	language.html.network.wifi_title = 			"Wi-Fi setting";
	language.html.network.wifi_link = 			"Wi-Fi select page";
	language.html.network.wifi_ip = 			"Wi-Fi IP setting";
	language.html.network.ip_address = 			"IP address:";
	language.html.network.ip_mask = 			"Subnet mask:";
	language.html.network.ip_gw = 				"Default gateway:";
	language.html.network.ip_auto = 			"Auto settings";
	language.html.network.ip_manual = 			"Use manual settings";
	language.html.network.lan1_title = 			"LAN1 IP setting";
	language.html.network.lan2_title = 			"LAN2 IP setting";
	language.html.network.ap_title = 			"AP setting";
	language.html.network.ap_ssid = 			"AP SSID:";
	language.html.network.ap_old_pw = 			"AP old password:";
	language.html.network.ap_new_pw = 			"AP new password:";
	language.html.network.ap_comfirm = 			"AP password comfirm:";
	
	language.html.sample = {}
	language.html.sample.title = 				"Sample parameter";
	language.html.sample.topBar = 				"Sample parameter";
	language.html.sample.tab_sensor = 			"Sensor";
	language.html.sample.tab_seg = 				"Segmentation";
	language.html.sample.tab_test = 			"Testing";
	language.html.sample.source = 				"Sample source:";
	language.html.sample.source_vol = 			"Voltage input";
	language.html.sample.source_cur = 			"Current input";
	language.html.sample.source_Di = 			"Digital input";
	language.html.sample.source_vib = 			"Vibration(AUO)";
	language.html.sample.source_vpa308 = 		"Vibration(Prognosis)";
	language.html.sample.source_audio = 		"Audio";
	language.html.sample.source_modbus = 		"Modbus(RTU)";
	language.html.sample.source_distance = 		"Distance";
	language.html.sample.rule = 				"Rule:";
	language.html.sample.rule_normal = 			"Normal";
	language.html.sample.rule_strangth = 		"By strength";
	language.html.sample.rule_freq = 			"By frequency";
	language.html.sample.rule_sg = 				"Smart Grid";
	language.html.sample.rule_tdma = 			"Run only one rule at a time:";
	language.html.sample.rule_tdma_remind =		"Work time for a rule ( 60~N Sec.):";
	language.html.sample.rule_tdma_n = 			"No";
	language.html.sample.rule_tdma_y = 			"Yes";
	language.html.sample.sensor_result = 		"Sample result:";
	language.html.sample.sensor_result_n = 		"No result";
	language.html.sample.sensor_result_link = 	"Look clear result at new page";
	language.html.sample.seg_result = 			"Segmentation result:";
	language.html.sample.seg_result_n = 		"No result";
	language.html.sample.seg_result_link = 		"Look clear result at new page"
	language.html.sample.old_test = 			"Run by old data";
	language.html.sample.new_test = 			"Run new setting";
	
	language.html.status = {}
	language.html.status.title = 				"Device status";
	language.html.status.topBar = 				"Device status";
	language.html.status.system = 				"System";
	language.html.status.network = 				"Network";
	language.html.status.update_time = 			"Last upload time";
	language.html.status.edge_data = 			"Edge data";
	language.html.status.error = 				"Error msg";
	language.html.status.OTA = 					"Update FW";
	language.html.status.clear_file = 			"Clear file";
	language.html.status.clear_queue = 			"Clear queue";
	
	language.html.system = {}
	language.html.system.title = 				"System setting";
	language.html.system.topBar = 				"System setting";
	language.html.system.status = 				"SPIIDER-D Status";
	language.html.system.model_server = 		"Model server";
	language.html.system.status_server = 		"Status server";
	language.html.system.smart_grid = 			"Smart Grid (MQTT)server";
	language.html.system.FTP = 					"FTP server";
	language.html.system.NTP = 					"NTP server";
	language.html.system.time = 				"System time setting";
	language.html.system.pin = 					"PIN setting";
	language.html.system.reboot = 				"Boot control";
	language.html.system.submit_btn = 			"Reboot";
	language.html.system.status_work = 			"Work";
	language.html.system.status_idle = 			"Idle";
	language.html.system.hostname = 			"Hostname";
	language.html.system.proxy = 				"Proxy";
	language.html.system.port = 				"Port";
	language.html.system.upload_api = 			"Upload data";
	language.html.system.mqtt_topic = 			"Publish Topic:";
	language.html.system.mqtt_name = 			"User Name:";
	language.html.system.mqtt_passwd = 			"User Password:";
	language.html.system.ftp_user = 			"Username:";
	language.html.system.ftp_passwd = 			"Password:";
	language.html.system.ftp_file_type = 		"FTP file type:";
	language.html.system.ftp_file_disable = 	"Disable upload";
	language.html.system.ftp_file_csv = 		"csv";
	language.html.system.ftp_file_binary = 		"binary";
	language.html.system.ftp_file_both = 		"csv & binary";
	language.html.system.pin_remind = 			"New password: 4~20 Numbers";
	language.html.system.pin_valida = 			"Check password:";
	language.html.system.lang_title = 			"Language";
	language.html.system.lang_english = 		"English";
	language.html.system.lang_chinese = 		"Chinese";
	language.html.system.lang_t_chinese = 		"Traditional Chinese";
	
	return language;
}


function _language_chinese(){
	console.log("use chinese");
	var language = {}
	language.check_left_page = 					"尚有设定为储存，是否确定离开网页？";
	language.check_over_setting = 				"该操作将覆盖原有设定，是否确定要执行？";
	
	language.topBar = {}
	language.topBar.change_network = 			"装置已变更网路，请确认当前连线之SPIIDER对象。";
	language.topBar.spiider_time =	 			"SPIIDER-D 时间为 ";
	language.topBar.device_time = 				"你的装置时间为 ";
	language.topBar.update_time = 				"，请确认后手动更新时间。";
	language.topBar.FW_not_finish = 			"韧体更新未完成，请稍候片刻。";
	language.topBar.FW_upload_OK = 				"韧体更新成功！";
	language.topBar.FW_upload_error = 			"韧体更新失败，错误资讯 ： ";
	language.topBar.status_idel_connected = 	"SPIIDER-D 为闲置状态，且与状态伺服器保持连线。";
	language.topBar.status_work_connected = 	"SPIIDER-D 为运行状态，且与状态伺服器保持连线。";
	language.topBar.status_idel_disconnected = 	"SPIIDER-D 为闲置状态，且与状态伺服器断线。";
	language.topBar.status_work_disconnected = 	"SPIIDER-D 为运行状态，且与状态伺服器断线。";
	language.topBar.status_DAQ_disconnected = 	"与SPIIDER-D断线！";
	language.topBar.load = 						"载入中";
	
	language.system = {}
	language.system.status_server_host_err = 	"状态伺服器主机名称格式错误";
	language.system.status_server_proxy_err = 	"状态伺服器的代理伺服器格式错误";
	language.system.status_server_set_OK = 		"成功设定状态伺服器";
	language.system.status_server_set_err = 	"状态伺服器设定失败，错误码：";
	language.system.status_server_req_err = 	"状态伺服器设定失败，错误码：(from server)";
	language.system.clear_file_OK = 			"清除装置本地暂存成功！";
	language.system.clear_file_err = 			"清除装置本地暂存失败，错误码：";
	language.system.clear_file_req_err = 		"清除装置本地暂存失败，错误码：(from server)";
	language.system.clear_queue_OK = 			"清除装置快取伫列成功！";
	language.system.clear_queue_err = 			"清除装置快取伫列失败，错误码：";
	language.system.clear_queue_req_err = 		"清除装置快取伫列失败，错误码：(from server)";
	language.system.smart_grid = 				"Smart grid伺服器(MQTT)";
	language.system.smart_grid_empty = 			"不可为空值！";
	language.system.smart_grid_format = 		"栏位格式错误！";
	language.system.smart_grid_OK = 			"Smart grid设定成功"
	language.system.smart_grid_err = 			"Smart grid设定失败，错误码：";
	language.system.smart_grid_req_err = 		"Smart grid设定失败，错误码：(from server)";
	language.system.NTP_format = 				"网路时间(NTP) IP 位址格式错误。";
	language.system.NTP_proxy = 				"网路时间(NTP) 代理伺服器格式错误。";
	language.system.NTP_err = 					"网路时间(NTP) 设定失败，错误码：";
	language.system.NTP_OK = 					"网路时间(NTP) 设定成功";
	language.system.NTP_req_err = 				"网路时间(NTP) 设定失败，错误码：(from server)";
	language.system.FTP_format = 				"档案传输(FTP)  IP address 格式错误。";
	language.system.FTP_proxy = 				"档案传输(FTP) 代理伺服器格式错误。";
	language.system.FTP_err = 					"档案传输(FTP) 失败，错误码：";
	language.system.FTP_OK = 					"档案传输(FTP) 设定成功";
	language.system.FTP_req_err = 				"档案传输(FTP) 失败，错误码：(from server)";
	language.system.pin_format_valida = 		"新PIN码与新PIN码确认不相符。";
	language.system.pin_format_num = 			"PIN码仅支援数字。";
	language.system.pin_format_min_len = 		"PIN码长度须大于4 (包含)";
	language.system.pin_format_max_len = 		"PIN码长度须小于20 (包含)";
	language.system.pin_err = 					"PIN码设定失败，错误码：";
	language.system.pin_OK = 					"PIN码设定成功";
	language.system.pin_req_err = 				"PIN码设定失败，错误码：(from server)";
	language.system.lang_set_err = 				"语言设定失败，错误码：";
	language.system.lang_set_OK = 				"语言设定成功";
	language.system.lang_req_err = 				"语言设定失败，错误码：(from server)";
	language.system.reboot_check = 				"该操作将重新启动装置，可能遗失部分工作，请问是否继续执行？";
	language.system.reboot_err = 				"重新启动装置请求失败，错误码：";
	language.system.reboot_OK = 				"重新启动装置请求发送成功，请稍候片刻。";
	language.system.reboot_check = 				"重新启动装置请求失败，错误码：(from server)";
	language.system.AP_SSID_empty = 			"无线存取点(AP) 命名不得为空白。";
	language.system.AP_SSID_format = 			"无线存取点(AP) 命名仅支援英文与数字";
	language.system.AP_passwd_err = 			"无线存取点(AP) 旧密码输入错误";
	language.system.AP_passwd_valida = 			"无线存取点(AP) 新密码与密码确认不相符。";
	language.system.AP_passwd_format = 			"无线存取点(AP) 密码仅支援英文与数字";
	language.system.AP_passwd_len = 			"无线存取点(AP) 密码长度须大于 8(包含)";
	language.system.AP_err = 					"无线存取点(AP) 设定失败，错误码：";
	language.system.AP_OK = 					"无线存取点(AP) 设定成功，请稍待片刻使之生效．";
	language.system.AP_req_err = 				"无线存取点(AP) 设定失败。";
	language.system.IP_format = 				"IP位址格式错误。";
	language.system.IP_mask_format = 			"网路子遮罩格式错误。";
	language.system.IP_gw_format = 				"预设闸道器位址格式错误。";
	language.system.IP_err = 					"设定失败，错误码：";
	language.system.IP_OK = 					"设定成功！";
	language.system.IP_req_err = 				"设定失败，错误码：(from server)";
	language.system.time_format = 				"时间格式错误。 请使用 yyyy-MM-dd hh:mm:ss";
	language.system.time_empty = 				"请选择时间。";
	language.system.time_err = 					"时间设定请求失败，错误码：";
	language.system.time_OK = 					"时间设定成功．";
	language.system.time_req_err = 				"时间设定请求失败，错误码：(from server)";
	language.system.work_err = 					"装置状态修改失败，错误码：";
	language.system.work_OK = 					"装置状态修改成功，请稍候片刻使之生效。";
	language.system.work_req_err = 				"装置状态修改失败，错误码：(from server)";
	language.system.work_wait_err = 			"装置状态确认失败，错误码：";
	language.system.work_wait_OK = 				"装置状态修改请求生效！";
	language.system.work_wait_req_err = 		"装置状态确认错误，错误码：";
	language.system.import_err = 				"汇入设定档失败，错误码：";
	language.system.import_OK = 				"汇入设定档成功！";
	language.system.OTA_err = 					"韧体更新请求失败，错误码：";
    language.system.OTA_req_OK = 				"韧体更新请求成功送出，请稍候片刻等待生效。 ";
	language.system.load_err = 					"载入系统设定失败，错误码：";
	language.system.load_req_err = 				"载入系统设定失败，错误码：(from server)";
	
	language.wifi = {};
	language.wifi.connect = 					"请问是否连线至 ";
	language.wifi.input_passwd = 				"请输入无线网路密码";
	language.wifi.disconnect = 					"请问是否断线当前网路 ";
	language.wifi.req_OK = 						"请求发送成功，请稍候片刻等待生效";
	
	language.login = {};
	language.login.passwd_err = 				"PIN码错误。";
	language.login.req_err = 					"PIN码请求失败，错误码：";
	language.login.device_change = 				"PIN码请求失败，请确认与SPIIDER-D保持连线状态。";
	
	language.form = {};
	language.form.version = 					"装置版本";
	language.form.wifiMac = 					"无线网路(Wi-Fi) mac：";
	language.form.wifiIP = 						"无线网路(Wi-Fi) IP：";
	language.form.eth0Mac = 					"乙太网路(LAN1) mac：";
	language.form.eth0IP = 						"乙太网路(LAN1) IP：";
	language.form.eth1Mac = 					"乙太网路(LAN2) mac：";
	language.form.eth1IP = 						"乙太网路(LAN2) IP：";
	language.form.systemTime = 					"装置时间：";
	language.form.uploadTimeAPI = 				"(API) ";
	language.form.uploadTimeFTP = 				"(FTP) ";
	language.form.uploadTimeMQTT = 				"(MQTT) ";
	language.form.uploadTimeStatus = 			"(Status) ";
	language.form.st1ErrMsg = 					"(ST1) ";
	language.form.st2ErrMsg = 					"(ST2) ";
	language.form.localCount = 					"装置本地暂存数量：";
	language.form.memoryCount = 				"装置快取伫列数量：";
	
	language.sample = {};
	language.sample.FE_json_check = 			"请上传特征萃取的设定档(.json)";
	language.sample.FE_json_file_err =			"特征萃取的设定档格式错误。";
	language.sample.keep_test_alert = 			"测试中，请等待程序完成。";
	language.sample.sensor_name_validat = 		"感测器命名异常，请重新命名。";
	language.sample.remove_check = 				"删除的动作不可复原，请问是否继续执行？";
	language.sample.over_len_for_bus = 			"支援子板的资料总线(Bus)已满。ｓ";
	language.sample.over_len_for_distanse = 	"距离感测器数量已达最高上限。";
	language.sample.over_len_for_prognosis = 	"普格诺斯震动感测器已达最大上限。";
	language.sample.over_len_for_DI = 			"数位输入已新增至最大数量。";
	language.sample.over_len_for_audio = 		"声音输入已新增至最大支援数量。";
	language.sample.over_len_for_modbus = 		"Modbus已新增至最大支援数量。";
	language.sample.not_save_setting = 			"你的设定尚为保存，请保存后再次尝试。";
	language.sample.enable_err = 				"装置状态修改请求失败，错误码：";
	language.sample.enable_OK = 				"装置状态修改请求成功，请稍待片可使之生效。";
	language.sample.enable_req_err = 			"装置状态修改请求设定失败，错误码：(from server)" ;
	language.sample.test_setting_not_save = 	"你的设定尚为保存，请保存后再次尝试。";
	language.sample.test_old_data_check = 		"仅使用上次的取样子料测试切割参数，请问是否继续执行？";
	language.sample.test_err = 					"测试请求失败，错误码：";
	language.sample.test_OK = 					"测试请求成功，请等待测试程序完成";
	language.sample.test_req_err = 				"测试请求失败，错误码：(from server)";
	language.sample.test_delay_change_err = 	"测试状态更换确认失败，错误码：";
	language.sample.test_delay_err = 			"测试状态确认失败，错误码：";
	language.sample.test_delay_req_err = 		"测试状态确认失败，错误码：(from server)";
	language.sample.test_time = 				"请输入欲测试之时间：";
	language.sample.test_time_unit = 			"秒";
	language.sample.test_time_format = 			"输入之时间须为整数";
	language.sample.test_time_format_limit = 	"输入时间范围为 1 至 ";
	language.sample.test_status_1_0 = 			" 初始化设定...";
	language.sample.test_status_2_0 = 			" 已完成取样 ";
	language.sample.test_status_2_1 = 			"%";
	language.sample.test_status_3_0 = 			" 停止取样程序中...";
	language.sample.test_status_4_0 = 			" 分析切割资料中...";
	language.sample.test_status_5_0 = 			" 等待完成上传，剩余 ";
	language.sample.test_status_5_1 = 			" 笔";
	language.sample.test_status_6_0 = 			" 绘制感测器信号 ";
	language.sample.test_status_7_0 = 			" 绘制切割结果 ";
	language.sample.test_status_8_0 = 			" 测试完成！";
	language.sample.sensor_submit_err = 		"更新感测器设定失败，错误码：";
	language.sample.sensor_submit_OK = 			"更新感测器设定成功";
	language.sample.sensor_submit_req_err =		"更新感测器设定失败，错误码：(from server)";
	language.sample.seg_submit_err = 			"更新切割参数失败，错误码：";
	language.sample.seg_submit_OK = 			"更新切割参数成功";
	language.sample.seg_submit_req_err = 		"更新切割参数之败，错误码：(from server)";
	language.sample.source = 					"信号来源";
	language.sample.source_voltate = 			"类比电压输入";
	language.sample.source_current = 			"类比电流输入";
	language.sample.source_vibration = 			"震动";
	language.sample.source_distance = 			"距离";
	language.sample.source_DI = 				"数位输入";
	language.sample.source_vibration_P = 		"普格诺斯震动感测器";
	language.sample.source_audio = 				"音源输入";
	language.sample.source_modbus = 			"Modbus(RTU)";
	language.sample.select_bus = 				"选择资料线(自动)：";
	language.sample.select_bus1 = 				"Bus 1";
	language.sample.select_bus2 = 				"Bus 2";
	language.sample.select_bus3 = 				"Bus 3";
	language.sample.select_bus4 = 				"Bus 4";
	language.sample.Sample_rate = 				"取样率：";
	language.sample.Signal_source = 			"信号源：";
	language.sample.Sample_range = 				"信号范围：";
	language.sample.Signal_type = 				"信号类型：";
	language.sample.sensor_differential =		"差分模式(Differential)";
	language.sample.sensor_single_ended =		"单端模式(Single-ended)";
	language.sample.sensor_engineering_up =		"工程单位上限：";
	language.sample.sensor_engineering_low =	"工程单位下限：";
	language.sample.sensor_engineering_offset =	"工程单位偏差值：";
	language.sample.sensor_engineering_unit =	"工程单位：";
	language.sample.channel_setting = 			"通道设定：";
	language.sample.jump_descript = 			"请根据信号范围的底色，调整电流子板上的跳线帽(Jumper)位置。";
	language.sample.jump_descript_remain = 		"需要于子板上调整跳线帽(Jumper)";
	language.sample.DI_scal_descript = 			"请根据数位输入为直流24伏 或 直流12伏调整板子的跳线帽(Jumper)位置。";
	language.sample.modbus_baud = 				"鲍率: ";
	language.sample.modbus_date_length = 		"资料长度(bit): ";
	language.sample.modbus_parity = 			"同位元检查: ";
	language.sample.modbus_stop_bit = 			"停止位元数: ";
	language.sample.modbus_period = 			"取值周期(毫秒): ";
	language.sample.modbus_data = 				"资料设定: ";
	language.sample.modbus_device = 			"装置地址(hex): ";
	language.sample.modbus_register = 			"暂存器(hex): ";
	language.sample.modbus_response = 			"响应时间(毫秒): ";
	language.sample.modbus_check = 				"校验方式: ";
	language.sample.modbus_type = 				"资料型态: ";
	language.sample.modbus_name = 				"名称";
	language.sample.modbus_name_end = 			": ";
	language.sample.modbus_order = 				"有效位元顺序: ";
	language.sample.modbus_ratio = 				"倍数: ";
	language.sample.modbus_err_device_format = 	"装置地址格式错误!";
	language.sample.modbus_err_reg_format = 	"暂存器格式错误!";
	language.sample.modbus_err_device_empty = 	"装置位址不可为空白!";
	language.sample.modbus_err_device_range = 	"装置位址须为 0x0~0xFF";
	language.sample.modbus_err_reg_empty = 		"暂存器不可为空白!";
	language.sample.modbus_err_reg_range= 		"暂存器范围须为 0x0~0xFFFF";
	language.sample.modbus_err_name_empty = 	"名称不可为空白。";
	language.sample.modbus_err_name_format = 	"名称格式错误。";
	language.sample.modbus_err_name_repeat = 	"名称重复。";
	language.sample.modbus_err_retio_format = 	"倍率设定格式错误。";
	language.sample.modbus_err_retio_empty = 	"倍率不得为空白";
	language.sample.modbus_err_period_empty = 	"取值周期不得为空白。";
	language.sample.modbus_err_period_format = 	"取值周期格是错误。";
	language.sample.modbus_err_period_vlaue = 	"取值周期需大于100毫秒。";
	language.sample.sensor_enable = 			"启用";
	language.sample.sensor_name = 				"命名：";
	language.sample.sensor_remove = 			"删除该设定：";
	language.sample.sensor_remove_btn = 		"删除";
	language.sample.rule_normal = 				"规则：一般模式";
	language.sample.rule_strength = 			"规则：信号时域强度模式";
	language.sample.rule_frequency = 			"规则：信号时频域模式";
	language.sample.rule_smart_grid = 			"规则：Smart grid";
	language.sample.rule_name = 				"规则名称：";
	language.sample.rule_name_unit = 			"规则单元名称(允许留空)：";
	language.sample.rule_name_subunit= 		    "规则子单元名称(允许留空)：";
	language.sample.input_item = 				"参考信号源：";
	language.sample.output_item = 				"输出之信号：";
	language.sample.output_item_enable = 		"(选项切换为'蓝色'样式，表示使用)";
	language.sample.trigger_enable = 			"使用触发功能：";
	language.sample.trigger_no = 				"不使用，直接使用信号往后运算。";
	language.sample.trigger_yes = 				"使用。";
	language.sample.trigger_item = 				"触发信号源";
	language.sample.trigger_edge = 				"边缘类型：";
	language.sample.trigger_rising = 			"上缘触发";
	language.sample.trigger_falling = 			"下缘触发";
	language.sample.trigger_thrshold = 			"触发阀值";
	language.sample.trigger_shift = 			"起始点偏移";
	language.sample.time_unit = 				"秒";
	language.sample.seg_window_size = 			"移动窗格大小";
	language.sample.seg_capture_length =		"切割长度";
	language.sample.seg_ignore_length =			"忽略长度";
	language.sample.seg_threshold =				"强度阀值";
	language.sample.seg_shift =					"切割起始点位移";
	language.sample.seg_sub_cap_use_windows =	"使用移动窗格大小";
	language.sample.seg_sub_cap_use_manual =	"手动设定";
	language.sample.seg_sub_cap_length =		"长度：";
	language.sample.seg_freq_main =				"目标频率";
	language.sample.seg_freq_auto =				"自动设定";
	language.sample.seg_freq_manual =			"手动设定";
	language.sample.seg_freq_sub_auto =			"使用移动窗格大小";
	language.sample.seg_freq_sub_manual =		"手动设定";
	language.sample.seg_freq_range = 			"1~Fs/2 Hz";
	language.sample.seg_filter_select =			"信号过滤";
	language.sample.seg_filter_enable =			"启用";
	language.sample.seg_filter_disable =		"禁用";
	language.sample.seg_filter_remain =			"条件";
	language.sample.seg_filter_exception =		"例外范围保存(5% 至 95%)";
	language.sample.seg_upload =				"上传切割结果";
	language.sample.seg_upload_interval =		"间隔上传数量";
	language.sample.seg_upload_remain =			"(具备特征萃取设定时生效)";
	language.sample.seg_FE_project =			"特征萃取设定";
	language.sample.seg_FE_upload =				"上传特征萃取结果";
	language.sample.seg_FE_upload_file =		"上传特征设定档";
	language.sample.seg_FE_upload_file_btn =	"选择档案";
	language.sample.seg_remove =				"删除该切割规则：";
	language.sample.seg_remove_btn =			"删除";
	language.sample.seg_edit =					"正在编辑. . . ";
	language.sample.import_setting_err =		"汇入设定档请求失败，错误码：";
	language.sample.import_setting_OK =			"汇入设定档成功。";
	language.sample.seg_FE_json_parse = 		"特征设定档解析错误";
	language.sample.seg_FE_json_format = 		"特征设定档格式错误。";
	language.sample.seg_FE_json_OK = 			"特征设定选择成功";
	language.sample.load_err = 					"载入设定失败，错误码：";
	language.sample.load_req_err = 				"载入设定失败，错误码： (from server)：";
	language.sample.check_bus_repeat = 			"资料总线(Bus)重複";
	language.sample.check_bus_1 = 				"此资料总线(Bus)";
	language.sample.check_bus_2 = 				"不是";
	language.sample.check_bus_3 = 				"，是否继续执行操作？";
	// "The bus "+(busIndex+1)+" isn't "+ sensorType +". Do you want to continue?"
	language.sample.check_vib_1 = 				"震动感测器资料总线(Bus ";
	language.sample.check_vib_2 = 				") 通道 (";
	language.sample.check_vib_3 = 				") 无辨识任何感测器。 是否继续执行操作？";
	//"The vibration (bus "+(busIndex+1)+") channel ("+channelList+") is empty on device. Do you want to continue?"
	language.sample.check_distanse = 			"无辨识到距离感测器的安装，是否继续执行操作？";
	language.sample.check_audio_1 = 			"USB 通道 ";
	language.sample.check_audio_2 = 			" 设定冲突，请确认该设定。";
	//"USB port "+(j+1)+" conflict. Please check setting."
	language.sample.check_empty_name = 			"命名不得为空白。";
    language.sample.check_empty_max_value = 	"工程单位上限不得为空白。";
    language.sample.check_empty_min_value = 	"工程单位下限不得为空白。";
    language.sample.check_empty_bias = 			"工程单位偏移值不得为空白。";
    language.sample.check_empty_unit = 			"工程单位不得为空白。";
    language.sample.check_format_name = 		"命名格式错误。";
    language.sample.check_format_max_value = 	"工程单位上限格式错误。";
    language.sample.check_format_min_value = 	"工程单位下限格式错误。";
    language.sample.check_format_bias = 		"工程单位偏移值格式错误。";
    language.sample.check_format_unit = 		"工程单位格式错误。";
    language.sample.check_max_min = 			"工程单位上限不得低于工程单位下限。";
    language.sample.check_rule_name_empty = 	"切割规则命名为空白。";
    language.sample.check_rule_name_format = 	"切割规则命名格式错误。";
    language.sample.check_unit_name_empty = 	"切割规则单元命名格式错误。";
    language.sample.check_unit_name_format = 	"切割规则子单元命名格式错误。";
	language.sample.check_rule_name_repeat = 	"切割规则命名重复";
	language.sample.check_rule_not_item_1 = 	"切割规则'";
	language.sample.check_rule_not_item_2 = 	"' 无选择输出输出信号。";
	//"The rule '"+name+"' not select output item."
	language.sample.check_input_empty =			"输入不得为空。";
	language.sample.check_input_num =			"请输入数字。";
	language.sample.check_input_range_L =		"输入的数值低于允许范围。";
	language.sample.check_input_range_H =		"输入的数值大于允许范围。";
	
	language.test={}
	language.test.alert_done = 					"测试完成";
	language.test.alert_title = 				"上传状态 (成功数 / 总数) ";
	language.test.alert_seg_csv_FTP = 			"由FTP上传切割结果的 .csv 档案：";
	language.test.alert_seg_binary_FTP = 		"由FTP上传切割结果的 .pkl 档案：";
	language.test.alert_seg_json_API = 			"由API上传切割结果的数据：";
	language.test.alert_FE_csv_FTP = 			"由FTP上传特征萃取结果的 .csv 档案：";
	language.test.alert_FE_binary_FTP = 		"由FTP上传特征萃取结果的 .pkl 档案：";
	language.test.alert_FE_json_API = 			"由API上传特征萃取结果的数据：";
	language.test.alert_smart_grid_MQTT = 		"由MQTT上传至Smart grid的数据：";
	language.test.html_title = 					"上传状态 (成功数 / 总数) ";
	language.test.html_seg_title = 				"切割结果：";
    language.test.html_seg_csv_FTP = 			". . . FTP(csv) = ";
	language.test.html_seg_binary_FTP = 		". . . FTP(binary) = ";
	language.test.html_seg_json_API = 			". . . Web API = ";
	language.test.html_FE_title = 				"特征萃取：";
	language.test.html_FE_csv_FTP = 			". . . FTP(csv) = ";
	language.test.html_FE_binary_FTP = 			". . . FTP(binary) = ";
	language.test.html_FE_json_API = 			". . . Web API = ";
	language.test.html_smart_grid_title = 		"Smart grid：";
	language.test.html_smart_grid_MQTT = 		". . . MQTT = ";
	
	language.html = {}
	language.html.universal = {}
	language.html.universal.hidden = 			"隐藏";
	language.html.universal.show = 				"显示";
	language.html.universal.submit = 			"提交";
	language.html.universal.ok = 				"确认";
	language.html.universal.remove = 			"删除";
	language.html.universal.cancel = 			"取消";
	language.html.universal.advanced = 			"显示进阶设定";
	language.html.universal.add = 				"加入";
	language.html.universal.enable = 			"启用";
	language.html.universal.disable = 			"禁用";
	
	language.html.home = {}
	language.html.home.title = 					"主页";
	language.html.home.sample = 				"取样参数设定";
	language.html.home.system = 				"系统设定";
	language.html.home.wifi = 					"无线网路(Wi-Fi)";
	language.html.home.network = 				"网路设定";
	language.html.home.device = 				"装置状态";
	language.html.home.exprot = 				"设定档汇入/汇出";
	
	language.html.page404 = {}
	language.html.page404.title = 				"404 错误页面";
	language.html.page404.remain = 				"404 错误，找不到对应的网页，于 ";
	language.html.page404.time_unit = 			" 秒后跳转．";
	//"404 not found. Jump after "+sec+" sec."
	
	language.html.fromFile = {}
	language.html.fromFile.title = 				"汇入/汇出";
	language.html.fromFile.topBar = 			"汇入/汇出";
	language.html.fromFile.sample = 			"取样设定档";
	language.html.fromFile.system = 			"系统设定档";
	language.html.fromFile.import = 			"汇入";
	language.html.fromFile.export = 			"汇出";
	
	language.html.login = {}
	language.html.login.title = 				"登入装置";
	language.html.login.main_box = 				"登入装置";
	language.html.login.remind = 				"PIN码 (长度为 4-20 的数字)";
	//"404 not found. Jump after "+sec+" sec."
	
	language.html.wifi = {}
	language.html.wifi.title = 					"无线网路(Wi-Fi) 选择";
	language.html.wifi.topBar = 				"无线网路(Wi-Fi) 选择";
	
	language.html.network = {}
	language.html.network.title = 				"网路设定";
	language.html.network.topBar = 				"网路设定";
	language.html.network.wifi_title = 			"无线网路(Wi-Fi) 设定";
	language.html.network.wifi_link = 			"前往设定";
	language.html.network.wifi_ip = 			"无线网路(Wi-Fi) IP 位址设定";
	language.html.network.ip_address = 			"IP 位址：";
	language.html.network.ip_mask = 			"网路遮罩：";
	language.html.network.ip_gw = 				"预设闸道器：";
	language.html.network.ip_auto = 			"自动配置";
	language.html.network.ip_manual = 			"手动设定";
	language.html.network.lan1_title = 			"乙太网路 (LAN1) IP 位址设定";
	language.html.network.lan2_title = 			"乙太网路 (LAN2) IP 位址设定";
	language.html.network.ap_title = 			"无线存取点(AP) 设定";
	language.html.network.ap_ssid = 			"名称 (SSID)：";
	language.html.network.ap_old_pw = 			"旧密码：";
	language.html.network.ap_new_pw = 			"新密码：";
	language.html.network.ap_comfirm = 			"新密码确认：";
	
	language.html.sample = {}
	language.html.sample.title = 				"取样参数设定";
	language.html.sample.topBar = 				"取样参数设定";
	language.html.sample.tab_sensor = 			"感测器";
	language.html.sample.tab_seg = 				"切割规则";
	language.html.sample.tab_test = 			"参数测试";
	language.html.sample.source = 				"信号来源：";
	language.html.sample.source_vol = 			"类比电压输入";
	language.html.sample.source_cur = 			"类比电流输入";
	language.html.sample.source_Di = 			"数位输入";
	language.html.sample.source_vib = 			"震动感测器 (AUO)";
	language.html.sample.source_vpa308 = 		"震动感测器 (普格诺斯)";
	language.html.sample.source_audio = 		"音源输入";
	language.html.sample.source_modbus = 		"Modbus(RTU)";
	language.html.sample.source_distance = 		"距离感测";
	language.html.sample.rule = 				"规则：";
	language.html.sample.rule_normal = 			"一般模式";
	language.html.sample.rule_strangth = 		"信号时域强度模式";
	language.html.sample.rule_freq = 			"信号时频域模式";
	language.html.sample.rule_sg = 				"Smart grid";
	language.html.sample.rule_tdma = 			"分时轮流执行切割规则";
	language.html.sample.rule_tdma_remind =		"规则持续运行时间( 60~N 秒)：";
	language.html.sample.rule_tdma_n = 			"不使用";
	language.html.sample.rule_tdma_y = 			"使用";
	language.html.sample.sensor_result = 		"取样结果：";
	language.html.sample.sensor_result_n = 		"无任何数据";
	language.html.sample.sensor_result_link = 	"于新分页开启高清图片";
	language.html.sample.seg_result = 			"切割结果：";
	language.html.sample.seg_result_n = 		"无任何数据";
	language.html.sample.seg_result_link = 		"于新分页开启高清图片"
	language.html.sample.old_test = 			"使用旧数据运行";
	language.html.sample.new_test = 			"重新运行取样";
	
	language.html.status = {}
	language.html.status.title = 				"装置状态";
	language.html.status.topBar = 				"装置状态";
	language.html.status.system = 				"系统";
	language.html.status.network = 				"网路";
	language.html.status.update_time = 			"上次上传时间";
	language.html.status.edge_data = 			"装置本地数据";
	language.html.status.error = 				"错误讯息";
	language.html.status.OTA = 					"更新韧体";
	language.html.status.clear_file = 			"清除暂存";
	language.html.status.clear_queue = 			"清除队列";
	
	language.html.system = {}
	language.html.system.title = 				"系统设定";
	language.html.system.topBar =               "系统设定";
	language.html.system.status = 				"SPIIDER-D 状态";
	language.html.system.model_server = 		"预测平台伺服器";
	language.html.system.status_server = 		"状态伺服器";
	language.html.system.smart_grid = 			"Smart grid(MQTT) 伺服器";
	language.html.system.FTP = 					"档案传输(FTP) 伺服器";
	language.html.system.NTP = 					"网路时间(NTP)  伺服器";
	language.html.system.time = 				"装置系统时间设定";
	language.html.system.pin = 					"PIN码 设定";
	language.html.system.reboot = 				"开机控制";
	language.html.system.submit_btn = 			"重新启动";
	language.html.system.status_work = 			"工作";
	language.html.system.status_idle = 			"闲置";
	language.html.system.hostname = 			"主机名称／位址";
	language.html.system.proxy = 				"代理伺服器";
	language.html.system.port = 				"连接埠";
	language.html.system.upload_api = 			"上传数据";
	language.html.system.mqtt_topic = 			"订阅主题：";
	language.html.system.mqtt_name = 			"使用者名称：";
	language.html.system.mqtt_passwd = 			"密码：";
	language.html.system.ftp_user = 			"使用者名称：";
	language.html.system.ftp_passwd = 			"密码：";
	language.html.system.ftp_file_type = 		"档案传输(FTP) 档案格式：";
	language.html.system.ftp_file_disable = 	"禁用上传";
	language.html.system.ftp_file_csv = 		"逗点分隔档(.csv)";
	language.html.system.ftp_file_binary = 		"二进制档";
	language.html.system.ftp_file_both = 		"逗点分隔档(.csv) 与 二进制档";
	language.html.system.pin_remind = 			"新密码：4~20 个数字";
	language.html.system.pin_valida = 			"新密码确认：";
	language.html.system.lang_title = 			"语言";
	language.html.system.lang_english = 		"英文";
	language.html.system.lang_chinese = 		"简体中文";
	language.html.system.lang_t_chinese = 		"繁体中文";
	
	
	return language;
}

function _language_t_chinese(){
	console.log("use chinese");
	var language = {}
	language.check_left_page = 					"尚有設定為儲存，是否確定離開網頁？";
	language.check_over_setting = 				"該操作將覆蓋原有設定，是否確定要執行？";
	
	language.topBar = {}
	language.topBar.change_network = 			"裝置已變更網路，請確認當前連線之SPIIDER對象。";
	language.topBar.spiider_time =	 			"SPIIDER-D 時間為 ";
	language.topBar.device_time = 				"你的裝置時間為 ";
	language.topBar.update_time = 				"，請確認後手動更新時間。";
	language.topBar.FW_not_finish = 			"韌體更新未完成，請稍候片刻。";
	language.topBar.FW_upload_OK = 				"韌體更新成功！";
	language.topBar.FW_upload_error = 			"韌體更新失敗，錯誤資訊 ： ";
	language.topBar.status_idel_connected = 	"SPIIDER-D 為閒置狀態，且與狀態伺服器保持連線。";
	language.topBar.status_work_connected = 	"SPIIDER-D 為運行狀態，且與狀態伺服器保持連線。";
	language.topBar.status_idel_disconnected = 	"SPIIDER-D 為閒置狀態，且與狀態伺服器斷線。";
	language.topBar.status_work_disconnected = 	"SPIIDER-D 為運行狀態，且與狀態伺服器斷線。";
	language.topBar.status_DAQ_disconnected = 	"與SPIIDER-D斷線！";
	language.topBar.load = 						"載入中";
	
	language.system = {}
	language.system.status_server_host_err = 	"狀態伺服器主機名稱格式錯誤";
	language.system.status_server_proxy_err = 	"狀態伺服器的代理伺服器格式錯誤";
	language.system.status_server_set_OK = 		"成功設定狀態伺服器";
	language.system.status_server_set_err = 	"狀態伺服器設定失敗，錯誤碼：";
	language.system.status_server_req_err = 	"狀態伺服器設定失敗，錯誤碼：(from server)";
	language.system.clear_file_OK = 			"清除裝置本地暫存成功！";
	language.system.clear_file_err = 			"清除裝置本地暫存失敗，錯誤碼：";
	language.system.clear_file_req_err = 		"清除裝置本地暫存失敗，錯誤碼：(from server)";
	language.system.clear_queue_OK = 			"清除裝置快取佇列成功！";
	language.system.clear_queue_err = 			"清除裝置快取佇列失敗，錯誤碼：";
	language.system.clear_queue_req_err = 		"清除裝置快取佇列失敗，錯誤碼：(from server)";
	language.system.smart_grid = 				"Smart grid伺服器(MQTT)";
	language.system.smart_grid_empty = 			"不可為空值！";
	language.system.smart_grid_format = 		"欄位格式錯誤！";
	language.system.smart_grid_OK = 			"Smart grid設定成功"
	language.system.smart_grid_err = 			"Smart grid設定失敗，錯誤碼：";
	language.system.smart_grid_req_err = 		"Smart grid設定失敗，錯誤碼：(from server)";
	language.system.NTP_format = 				"網路時間(NTP) IP 位址格式錯誤。";
	language.system.NTP_proxy = 				"網路時間(NTP) 代理伺服器格式錯誤。";
	language.system.NTP_err = 					"網路時間(NTP) 設定失敗，錯誤碼：";
	language.system.NTP_OK = 					"網路時間(NTP) 設定成功";
	language.system.NTP_req_err = 				"網路時間(NTP) 設定失敗，錯誤碼：(from server)";
	language.system.FTP_format = 				"檔案傳輸(FTP)  IP address 格式錯誤。";
	language.system.FTP_proxy = 				"檔案傳輸(FTP) 代理伺服器格式錯誤。";
	language.system.FTP_err = 					"檔案傳輸(FTP) 失敗，錯誤碼：";
	language.system.FTP_OK = 					"檔案傳輸(FTP) 設定成功";
	language.system.FTP_req_err = 				"檔案傳輸(FTP) 失敗，錯誤碼：(from server)";
	language.system.pin_format_valida = 		"新PIN碼與新PIN碼確認不相符。";
	language.system.pin_format_num = 			"PIN碼僅支援數字。";
	language.system.pin_format_min_len = 		"PIN碼長度須大於4 (包含)";
	language.system.pin_format_max_len = 		"PIN碼長度須小於20 (包含)";
	language.system.pin_err = 					"PIN碼設定失敗，錯誤碼：";
	language.system.pin_OK = 					"PIN碼設定成功";
	language.system.pin_req_err = 				"PIN碼設定失敗，錯誤碼：(from server)";
	language.system.lang_set_err = 				"語言設定失敗，錯誤碼：";
	language.system.lang_set_OK = 				"語言設定成功";
	language.system.lang_req_err = 				"語言設定失敗，錯誤碼：(from server)";
	language.system.reboot_check = 				"該操作將重新啟動裝置，可能遺失部分工作，請問是否繼續執行？";
	language.system.reboot_err = 				"重新啟動裝置請求失敗，錯誤碼：";
	language.system.reboot_OK = 				"重新啟動裝置請求發送成功，請稍候片刻。";
	language.system.reboot_check = 				"重新啟動裝置請求失敗，錯誤碼：(from server)";
	language.system.AP_SSID_empty = 			"無線存取點(AP) 命名不得為空白。";
	language.system.AP_SSID_format = 			"無線存取點(AP) 命名僅支援英文與數字";
	language.system.AP_passwd_err = 			"無線存取點(AP) 舊密碼輸入錯誤";
	language.system.AP_passwd_valida = 			"無線存取點(AP) 新密碼與密碼確認不相符。";
	language.system.AP_passwd_format = 			"無線存取點(AP) 密碼僅支援英文與數字";
	language.system.AP_passwd_len = 			"無線存取點(AP) 密碼長度須大於 8(包含)";
	language.system.AP_err = 					"無線存取點(AP) 設定失敗，錯誤碼：";
	language.system.AP_OK = 					"無線存取點(AP) 設定成功，請稍待片刻使之生效．";
	language.system.AP_req_err = 				"無線存取點(AP) 設定失敗。";
	language.system.IP_format = 				"IP位址格式錯誤。";
	language.system.IP_mask_format = 			"網路子遮罩格式錯誤。";
	language.system.IP_gw_format = 				"預設閘道器位址格式錯誤。";
	language.system.IP_err = 					"設定失敗，錯誤碼：";
	language.system.IP_OK = 					"設定成功！";
	language.system.IP_req_err = 				"設定失敗，錯誤碼：(from server)";
	language.system.time_format = 				"時間格式錯誤。 請使用 yyyy-MM-dd hh:mm:ss";
	language.system.time_empty = 				"請選擇時間。";
	language.system.time_err = 					"時間設定請求失敗，錯誤碼：";
	language.system.time_OK = 					"時間設定成功．";
	language.system.time_req_err = 				"時間設定請求失敗，錯誤碼：(from server)";
	language.system.work_err = 					"裝置狀態修改失敗，錯誤碼：";
	language.system.work_OK = 					"裝置狀態修改成功，請稍候片刻使之生效。";
	language.system.work_req_err = 				"裝置狀態修改失敗，錯誤碼：(from server)";
	language.system.work_wait_err = 			"裝置狀態確認失敗，錯誤碼：";
	language.system.work_wait_OK = 				"裝置狀態修改請求生效！";
	language.system.work_wait_req_err = 		"裝置狀態確認錯誤，錯誤碼：";
	language.system.import_err = 				"匯入設定檔失敗，錯誤碼：";
	language.system.import_OK = 				"匯入設定檔成功！";
	language.system.OTA_err = 					"韌體更新請求失敗，錯誤碼：";
	language.system.OTA_req_OK = 				"韌體更新請求成功送出，請稍候片刻等待生效。";
	language.system.load_err = 					"載入系統設定失敗，錯誤碼：";
	language.system.load_req_err = 				"載入系統設定失敗，錯誤碼：(from server)";
	
	language.wifi = {};
	language.wifi.connect = 					"請問是否連線至 ";
	language.wifi.input_passwd = 				"請輸入無線網路密碼";
	language.wifi.disconnect = 					"請問是否斷線當前網路 ";
	language.wifi.req_OK = 						"請求發送成功，請稍候片刻等待生效";
	
	language.login = {};
	language.login.passwd_err = 				"PIN碼錯誤。";
	language.login.req_err = 					"PIN碼請求失敗，錯誤碼：";
	language.login.device_change = 				"PIN碼請求失敗，請確認與SPIIDER-D保持連線狀態。";
	
	language.form = {};
	language.form.version = 					"裝置版本";
	language.form.wifiMac = 					"無線網路(Wi-Fi) mac：";
	language.form.wifiIP = 						"無線網路(Wi-Fi) IP：";
	language.form.eth0Mac = 					"乙太網路(LAN1) mac：";
	language.form.eth0IP = 						"乙太網路(LAN1) IP：";
	language.form.eth1Mac = 					"乙太網路(LAN2) mac：";
	language.form.eth1IP = 						"乙太網路(LAN2) IP：";
	language.form.systemTime = 					"裝置時間：";
	language.form.uploadTimeAPI = 				"(API) ";
	language.form.uploadTimeFTP = 				"(FTP) ";
	language.form.uploadTimeMQTT = 				"(MQTT) ";
	language.form.uploadTimeStatus = 			"(Status) ";
	language.form.st1ErrMsg = 					"(ST1) ";
	language.form.st2ErrMsg = 					"(ST2) ";
	language.form.localCount = 					"裝置本地暫存數量：";
	language.form.memoryCount = 				"裝置快取佇列數量：";
	
	language.sample = {};
	language.sample.FE_json_check = 			"請上傳特徵萃取的設定檔(.json)";
	language.sample.FE_json_file_err =			"特徵萃取的設定檔格式錯誤。";
	language.sample.keep_test_alert = 			"測試中，請等待程序完成。";
	language.sample.sensor_name_validat = 		"感測器命名異常，請重新命名。";
	language.sample.remove_check = 				"刪除的動作不可復原，請問是否繼續執行？";
	language.sample.over_len_for_bus = 			"支援子板的資料總線(Bus)已滿。ｓ";
	language.sample.over_len_for_distanse = 	"距離感測器數量已達最高上限。";
	language.sample.over_len_for_prognosis = 	"普格諾斯震動感測器已達最大上限。";
	language.sample.over_len_for_DI = 			"數位輸入已新增至最大數量。";
	language.sample.over_len_for_audio = 		"聲音輸入已新增至最大支援數量。";
	language.sample.over_len_for_modbus = 		"Modbus已新增至最大支援數量。";
	language.sample.not_save_setting = 			"你的設定尚為保存，請保存後再次嘗試。";
	language.sample.enable_err = 				"裝置狀態修改請求失敗，錯誤碼：";
	language.sample.enable_OK = 				"裝置狀態修改請求成功，請稍待片可使之生效。";
	language.sample.enable_req_err = 			"裝置狀態修改請求設定失敗，錯誤碼：(from server)" ;
	language.sample.test_setting_not_save = 	"你的設定尚為保存，請保存後再次嘗試。";
	language.sample.test_old_data_check = 		"僅使用上次的取樣子料測試切割參數，請問是否繼續執行？";
	language.sample.test_err = 					"測試請求失敗，錯誤碼：";
	language.sample.test_OK = 					"測試請求成功，請等待測試程序完成";
	language.sample.test_req_err = 				"測試請求失敗，錯誤碼：(from server)";
	language.sample.test_delay_change_err = 	"測試狀態更換確認失敗，錯誤碼：";
	language.sample.test_delay_err = 			"測試狀態確認失敗，錯誤碼：";
	language.sample.test_delay_req_err = 		"測試狀態確認失敗，錯誤碼：(from server)";
	language.sample.test_time = 				"請輸入欲測試之時間：";
	language.sample.test_time_unit = 			"秒";
	language.sample.test_time_format = 			"輸入之時間須為整數";
	language.sample.test_time_format_limit = 	"輸入時間範圍為 1 至 ";
	language.sample.test_status_1_0 = 			" 初始化設定...";
	language.sample.test_status_2_0 = 			" 已完成取樣 ";
	language.sample.test_status_2_1 = 			"%";
	language.sample.test_status_3_0 = 			" 停止取樣程序中...";
	language.sample.test_status_4_0 = 			" 分析切割資料中...";
	language.sample.test_status_5_0 = 			" 等待完成上傳，剩餘 ";
	language.sample.test_status_5_1 = 			" 筆";
	language.sample.test_status_6_0 = 			" 繪製感測器信號 ";
	language.sample.test_status_7_0 = 			" 繪製切割結果 ";
	language.sample.test_status_8_0 = 			" 測試完成！";
	language.sample.sensor_submit_err = 		"更新感測器設定失敗，錯誤碼：";
	language.sample.sensor_submit_OK = 			"更新感測器設定成功";
	language.sample.sensor_submit_req_err =		"更新感測器設定失敗，錯誤碼：(from server)";
	language.sample.seg_submit_err = 			"更新切割參數失敗，錯誤碼：";
	language.sample.seg_submit_OK = 			"更新切割參數成功";
	language.sample.seg_submit_req_err = 		"更新切割參數之敗，錯誤碼：(from server)";
	language.sample.source = 					"信號來源";
	language.sample.source_voltate = 			"類比電壓輸入";
	language.sample.source_current = 			"類比電流輸入";
	language.sample.source_vibration = 			"震動";
	language.sample.source_distance = 			"距離";
	language.sample.source_DI = 				"數位輸入";
	language.sample.source_vibration_P = 		"普格諾斯震動感測器";
	language.sample.source_audio = 				"音源輸入";
	language.sample.source_modbus = 			"Modbus(RTU)";
	language.sample.select_bus = 				"選擇資料線(自動)：";
	language.sample.select_bus1 = 				"Bus 1";
	language.sample.select_bus2 = 				"Bus 2";
	language.sample.select_bus3 = 				"Bus 3";
	language.sample.select_bus4 = 				"Bus 4";
	language.sample.Sample_rate = 				"取樣率：";
	language.sample.Signal_source = 			"信號源：";
	language.sample.Sample_range = 				"信號範圍：";
	language.sample.Signal_type = 				"信號類型：";
	language.sample.sensor_differential =		"差分模式(Differential)";
	language.sample.sensor_single_ended =		"單端模式(Single-ended)";
	language.sample.sensor_engineering_up =		"工程單位上限：";
	language.sample.sensor_engineering_low =	"工程單位下限：";
	language.sample.sensor_engineering_offset =	"工程單位偏差值：";
	language.sample.sensor_engineering_unit =	"工程單位：";
	language.sample.channel_setting = 			"通道設定：";
	language.sample.jump_descript = 			"請根據信號範圍的底色，調整電流子板上的跳線帽(Jumper)位置。";
	language.sample.jump_descript_remain = 		"需要於子板上調整跳線帽(Jumper)";
	language.sample.DI_scal_descript = 			"請根據數位輸入為直流24伏 或 直流12伏調整板子的跳線帽(Jumper)位置。";
	language.sample.modbus_baud = 				"鮑率: ";
	language.sample.modbus_date_length = 		"資料長度(bit): ";
	language.sample.modbus_parity = 			"同位元檢查: ";
	language.sample.modbus_stop_bit = 			"停止位元數: ";
	language.sample.modbus_period = 			"取值週期(毫秒): ";
	language.sample.modbus_data = 				"資料設定: ";
	language.sample.modbus_device = 			"裝置地址(hex): ";
	language.sample.modbus_register = 			"暫存器(hex): ";
	language.sample.modbus_response = 			"響應時間(毫秒): ";
	language.sample.modbus_check = 				"校驗方式: ";
	language.sample.modbus_type = 				"資料型態: ";
	language.sample.modbus_name = 				"名稱";
	language.sample.modbus_name_end = 			": ";
	language.sample.modbus_order = 				"有效位元順序: ";
	language.sample.modbus_ratio = 				"倍數: ";
	language.sample.modbus_err_device_format = 	"裝置地址格式錯誤!";
	language.sample.modbus_err_reg_format = 	"暫存器格式錯誤!";
	language.sample.modbus_err_device_empty = 	"裝置位址不可為空白!";
	language.sample.modbus_err_device_range = 	"裝置位址須為 0x0~0xFF";
	language.sample.modbus_err_reg_empty = 		"暫存器不可為空白!";
	language.sample.modbus_err_reg_range= 		"暫存器範圍須為 0x0~0xFFFF";
	language.sample.modbus_err_name_empty = 	"名稱不可為空白。";
	language.sample.modbus_err_name_format = 	"名稱格式錯誤。";
	language.sample.modbus_err_name_repeat = 	"名稱重複。";
	language.sample.modbus_err_retio_format = 	"倍率設定格式錯誤。";
	language.sample.modbus_err_retio_empty = 	"倍率不得為空白";
	language.sample.modbus_err_period_empty = 	"取值週期不得為空白。";
	language.sample.modbus_err_period_format = 	"取值週期格是錯誤。";
	language.sample.modbus_err_period_vlaue = 	"取值周期需大於100毫秒。";
	language.sample.sensor_enable = 			"啟用";
	language.sample.sensor_name = 				"命名：";
	language.sample.sensor_remove = 			"刪除該設定：";
	language.sample.sensor_remove_btn = 		"刪除";
	language.sample.rule_normal = 				"規則：一般模式";
	language.sample.rule_strength = 			"規則：信號時域強度模式";
	language.sample.rule_frequency = 			"規則：信號時頻域模式";
	language.sample.rule_smart_grid = 			"規則：Smart grid";
	language.sample.rule_name = 				"規則名稱：";
	language.sample.rule_name_unit = 			"規則單元名稱(允許留空)：";
	language.sample.rule_name_subunit = 		"規則子單元名稱(允許留空)：";
	language.sample.input_item = 				"參考信號源：";
	language.sample.output_item = 				"輸出之信號：";
	language.sample.output_item_enable = 		"(選項切換為'藍色'樣式，表示使用)";
	language.sample.trigger_enable = 			"使用觸發功能：";
	language.sample.trigger_no = 				"不使用，直接使用信號往後運算。";
	language.sample.trigger_yes = 				"使用。";
	language.sample.trigger_item = 				"觸發信號源";
	language.sample.trigger_edge = 				"邊緣類型：";
	language.sample.trigger_rising = 			"上緣觸發";
	language.sample.trigger_falling = 			"下緣觸發";
	language.sample.trigger_thrshold = 			"觸發閥值";
	language.sample.trigger_shift = 			"起始點偏移";
	language.sample.time_unit = 				"秒";
	language.sample.seg_window_size = 			"移動窗格大小";
	language.sample.seg_capture_length =		"切割長度";
	language.sample.seg_ignore_length =			"忽略長度";
	language.sample.seg_threshold =				"強度閥值";
	language.sample.seg_shift =					"切割起始點位移";
	language.sample.seg_sub_cap_use_windows =	"使用移動窗格大小";
	language.sample.seg_sub_cap_use_manual =	"手動設定";
	language.sample.seg_sub_cap_length =		"長度：";
	language.sample.seg_freq_main =				"目標頻率";
	language.sample.seg_freq_auto =				"自動設定";
	language.sample.seg_freq_manual =			"手動設定";
	language.sample.seg_freq_sub_auto =			"使用移動窗格大小";
	language.sample.seg_freq_sub_manual =		"手動設定";
	language.sample.seg_freq_range = 			"1~Fs/2 Hz";
	language.sample.seg_filter_select =			"信號過濾";
	language.sample.seg_filter_enable =			"啟用";
	language.sample.seg_filter_disable =		"禁用";
	language.sample.seg_filter_remain =			"條件";
	language.sample.seg_filter_exception =		"例外範圍保存(5% 至 95%)";
	language.sample.seg_upload =				"上傳切割結果";
	language.sample.seg_upload_interval =		"間隔上傳數量";
	language.sample.seg_upload_remain =			"(具備特徵萃取設定時生效)";
	language.sample.seg_FE_project =			"特徵萃取設定";
	language.sample.seg_FE_upload =				"上傳特徵萃取結果";
	language.sample.seg_FE_upload_file =		"上傳特徵設定檔";
	language.sample.seg_FE_upload_file_btn =	"選擇檔案";
	language.sample.seg_remove =				"刪除該切割規則：";
	language.sample.seg_remove_btn =			"刪除";
	language.sample.seg_edit =					"正在編輯. . . ";
	language.sample.import_setting_err =		"匯入設定檔請求失敗，錯誤碼：";
	language.sample.import_setting_OK =			"匯入設定檔成功。";
	language.sample.seg_FE_json_parse = 		"特徵設定檔解析錯誤";
	language.sample.seg_FE_json_format = 		"特徵設定檔格式錯誤。";
	language.sample.seg_FE_json_OK = 			"特徵設定選擇成功";
	language.sample.load_err = 					"載入設定失敗，錯誤碼：";
	language.sample.load_req_err = 				"載入設定失敗，錯誤碼： (from server)：";
	language.sample.check_bus_repeat = 			"資料總線(Bus)重複";
	language.sample.check_bus_1 = 				"此資料總線(Bus)";
	language.sample.check_bus_2 = 				"不是";
	language.sample.check_bus_3 = 				"，是否繼續執行操作？";
	// "The bus "+(busIndex+1)+" isn't "+ sensorType +". Do you want to continue?"
	language.sample.check_vib_1 = 				"震動感測器資料總線(Bus ";
	language.sample.check_vib_2 = 				") 通道 (";
	language.sample.check_vib_3 = 				") 無辨識任何感測器。 是否繼續執行操作？";
	//"The vibration (bus "+(busIndex+1)+") channel ("+channelList+") is empty on device. Do you want to continue?"
	language.sample.check_distanse = 			"無辨識到距離感測器的安裝，是否繼續執行操作？";
	language.sample.check_audio_1 = 			"USB 通道 ";
	language.sample.check_audio_2 = 			" 設定衝突，請確認該設定。";
	//"USB port "+(j+1)+" conflict. Please check setting."
	language.sample.check_empty_name = 			"命名不得為空白。";
    language.sample.check_empty_max_value = 	"工程單位上限不得為空白。";
    language.sample.check_empty_min_value = 	"工程單位下限不得為空白。";
    language.sample.check_empty_bias = 			"工程單位偏移值不得為空白。";
    language.sample.check_empty_unit = 			"工程單位不得為空白。";
    language.sample.check_format_name = 		"命名格式錯誤。";
    language.sample.check_format_max_value = 	"工程單位上限格式錯誤。";
    language.sample.check_format_min_value = 	"工程單位下限格式錯誤。";
    language.sample.check_format_bias = 		"工程單位偏移值格式錯誤。";
    language.sample.check_format_unit = 		"工程單位格式錯誤。";
    language.sample.check_max_min = 			"工程單位上限不得低於工程單位下限。";
    language.sample.check_rule_name_empty = 	"切割規則命名為空白。";
    language.sample.check_rule_name_format = 	"切割規則命名格式錯誤。";
    language.sample.check_unit_name_empty = 	"切割規則單元命名格式錯誤。";
    language.sample.check_unit_name_format = 	"切割規則子單元命名格式錯誤。";
	language.sample.check_rule_name_repeat = 	"切割規則命名重複";
	language.sample.check_rule_not_item_1 = 	"切割規則'";
	language.sample.check_rule_not_item_2 = 	"' 無選擇輸出輸出信號。";
	//"The rule '"+name+"' not select output item."
	language.sample.check_input_empty =			"輸入不得為空。";
	language.sample.check_input_num =			"請輸入數字。";
	language.sample.check_input_range_L =		"輸入的數值低於允許範圍。";
	language.sample.check_input_range_H =		"輸入的數值大於允許範圍。";
	
	language.test={}
	language.test.alert_done = 					"測試完成";
	language.test.alert_title = 				"上傳狀態 (成功數 / 總數) ";
	language.test.alert_seg_csv_FTP = 			"由FTP上傳切割結果的 .csv 檔案：";
	language.test.alert_seg_binary_FTP = 		"由FTP上傳切割結果的 .pkl 檔案：";
	language.test.alert_seg_json_API = 			"由API上傳切割結果：";
	language.test.alert_FE_csv_FTP = 			"由FTP上傳特徵萃取的 .csv 檔案：";
	language.test.alert_FE_binary_FTP = 		"由FTP上傳特徵萃取的 .pkl 檔案：";
	language.test.alert_FE_json_API = 			"由API上傳特徵萃取：";
	language.test.alert_smart_grid_MQTT = 		"由MQTT上傳至Smart grid：";
	language.test.html_title = 					"上傳狀態 (成功數 / 總數) ";
	language.test.html_seg_title = 				"切割結果：";
	language.test.html_seg_csv_FTP = 			". . . FTP(csv) = ";
	language.test.html_seg_binary_FTP = 		". . . FTP(binary) = ";
	language.test.html_seg_json_API = 			". . . Web API = ";
	language.test.html_FE_title = 				"特徵萃取：";
	language.test.html_FE_csv_FTP = 			". . . FTP(csv) = ";
	language.test.html_FE_binary_FTP = 			". . . FTP(binary) = ";
	language.test.html_FE_json_API = 			". . . Web API = ";
	language.test.html_smart_grid_title = 		"Smart grid：";
	language.test.html_smart_grid_MQTT = 		". . . MQTT = ";
	
	language.html = {}
	language.html.universal = {}
	language.html.universal.hidden = 			"隱藏";
	language.html.universal.show = 				"顯示";
	language.html.universal.submit = 			"提交";
	language.html.universal.ok = 				"確認";
	language.html.universal.remove = 			"刪除";
	language.html.universal.cancel = 			"取消";
	language.html.universal.advanced = 			"顯示進階設定";
	language.html.universal.add = 				"加入";
	language.html.universal.enable = 			"啟用";
	language.html.universal.disable = 			"禁用";
	
	language.html.home = {}
	language.html.home.title = 					"主頁";
	language.html.home.sample = 				"取樣參數設定";
	language.html.home.system = 				"系統設定";
	language.html.home.wifi = 					"無線網路(Wi-Fi)";
	language.html.home.network = 				"網路設定";
	language.html.home.device = 				"裝置狀態";
	language.html.home.exprot = 				"設定檔匯入/匯出";
	
	language.html.page404 = {}
	language.html.page404.title = 				"404 錯誤頁面";
	language.html.page404.remain = 				"404 錯誤，找不到對應的網頁，於 ";
	language.html.page404.time_unit = 			" 秒後跳轉．";
	//"404 not found. Jump after "+sec+" sec."
	
	language.html.fromFile = {}
	language.html.fromFile.title = 				"匯入/匯出";
	language.html.fromFile.topBar = 			"匯入/匯出";
	language.html.fromFile.sample = 			"取樣設定檔";
	language.html.fromFile.system = 			"系統設定檔";
	language.html.fromFile.import = 			"匯入";
	language.html.fromFile.export = 			"匯出";
	
	language.html.login = {}
	language.html.login.title = 				"登入裝置";
	language.html.login.main_box = 				"登入裝置";
	language.html.login.remind = 				"PIN碼 (長度為 4-20 的數字)";
	//"404 not found. Jump after "+sec+" sec."
	
	language.html.wifi = {}
	language.html.wifi.title = 					"無線網路(Wi-Fi) 選擇";
	language.html.wifi.topBar = 				"無線網路(Wi-Fi) 選擇";
	
	language.html.network = {}
	language.html.network.title = 				"網路設定";
	language.html.network.topBar = 				"網路設定";
	language.html.network.wifi_title = 			"無線網路(Wi-Fi) 設定";
	language.html.network.wifi_link = 			"前往設定";
	language.html.network.wifi_ip = 			"無線網路(Wi-Fi) IP 位址設定";
	language.html.network.ip_address = 			"IP 位址：";
	language.html.network.ip_mask = 			"網路遮罩：";
	language.html.network.ip_gw = 				"預設閘道器：";
	language.html.network.ip_auto = 			"自動配置";
	language.html.network.ip_manual = 			"手動設定";
	language.html.network.lan1_title = 			"乙太網路 (LAN1) IP 位址設定";
	language.html.network.lan2_title = 			"乙太網路 (LAN2) IP 位址設定";
	language.html.network.ap_title = 			"無線存取點(AP) 設定";
	language.html.network.ap_ssid = 			"名稱 (SSID)：";
	language.html.network.ap_old_pw = 			"舊密碼：";
	language.html.network.ap_new_pw = 			"新密碼：";
	language.html.network.ap_comfirm = 			"新密碼確認：";
	
	language.html.sample = {}
	language.html.sample.title = 				"取樣參數設定";
	language.html.sample.topBar = 				"取樣參數設定";
	language.html.sample.tab_sensor = 			"感測器";
	language.html.sample.tab_seg = 				"切割規則";
	language.html.sample.tab_test = 			"參數測試";
	language.html.sample.source = 				"信號來源：";
	language.html.sample.source_vol = 			"類比電壓輸入";
	language.html.sample.source_cur = 			"類比電流輸入";
	language.html.sample.source_Di = 			"數位輸入";
	language.html.sample.source_vib = 			"震動感測器 (AUO)";
	language.html.sample.source_vpa308 = 		"震動感測器 (普格諾斯)";
	language.html.sample.source_audio = 		"音源輸入";
	language.html.sample.source_modbus = 		"Modbus(RTU)";
	language.html.sample.source_distance = 		"距離感測";
	language.html.sample.rule = 				"規則：";
	language.html.sample.rule_normal = 			"一般模式";
	language.html.sample.rule_strangth = 		"信號時域強度模式";
	language.html.sample.rule_freq = 			"信號時頻域模式";
	language.html.sample.rule_sg = 				"Smart grid";
	language.html.sample.rule_tdma = 			"分時輪流執行切割規則";
	language.html.sample.rule_tdma_remind =		"規則持續運行時間( 60~N 秒)：";
	language.html.sample.rule_tdma_n = 			"不使用";
	language.html.sample.rule_tdma_y = 			"使用";
	language.html.sample.sensor_result = 		"取樣結果：";
	language.html.sample.sensor_result_n = 		"無任何數據";
	language.html.sample.sensor_result_link = 	"於新分頁開啟高清圖片";
	language.html.sample.seg_result = 			"切割結果：";
	language.html.sample.seg_result_n = 		"無任何數據";
	language.html.sample.seg_result_link = 		"於新分頁開啟高清圖片"
	language.html.sample.old_test = 			"使用舊數據運行";
	language.html.sample.new_test = 			"重新運行取樣";
	
	language.html.status = {}
	language.html.status.title = 				"裝置狀態";
	language.html.status.topBar = 				"裝置狀態";
	language.html.status.system = 				"系統";
	language.html.status.network = 				"網路";
	language.html.status.update_time = 			"上次上傳時間";
	language.html.status.edge_data = 			"裝置本地數據";
	language.html.status.error = 				"錯誤訊息";
	language.html.status.OTA = 					"更新韌體";
	language.html.status.clear_file = 			"清除暫存";
	language.html.status.clear_queue = 			"清除列";
	
	language.html.system = {}
	language.html.system.title = 				"系統設定";
	language.html.system.topBar = 				"系統設定";
	language.html.system.status = 				"SPIIDER-D 狀態";
	language.html.system.model_server = 		"預測平台伺服器";
	language.html.system.status_server = 		"狀態伺服器";
	language.html.system.smart_grid = 			"Smart grid(MQTT) 伺服器";
	language.html.system.FTP = 					"檔案傳輸(FTP) 伺服器";
	language.html.system.NTP = 					"網路時間(NTP)  伺服器";
	language.html.system.time = 				"裝置系統時間設定";
	language.html.system.pin = 					"PIN碼 設定";
	language.html.system.reboot = 				"開機控制";
	language.html.system.submit_btn = 			"重新啟動";
	language.html.system.status_work = 			"工作";
	language.html.system.status_idle = 			"閒置";
	language.html.system.hostname = 			"主機名稱／位址";
	language.html.system.proxy = 				"代理伺服器";
	language.html.system.port = 				"連接埠";
	language.html.system.upload_api = 			"上傳數據";
	language.html.system.mqtt_topic = 			"訂閱主題：";
	language.html.system.mqtt_name = 			"使用者名稱：";
	language.html.system.mqtt_passwd = 			"密碼：";
	language.html.system.ftp_user = 			"使用者名稱：";
	language.html.system.ftp_passwd = 			"密碼：";
	language.html.system.ftp_file_type = 		"檔案傳輸(FTP) 檔案格式：";
	language.html.system.ftp_file_disable = 	"禁用上傳";
	language.html.system.ftp_file_csv = 		"逗點分隔檔(.csv)";
	language.html.system.ftp_file_binary = 		"二進制檔";
	language.html.system.ftp_file_both = 		"逗點分隔檔(.csv) 與 二進制檔";
	language.html.system.pin_remind = 			"新密碼：4~20 個數字";
	language.html.system.pin_valida = 			"新密碼確認：";
	language.html.system.lang_title = 			"語言";
	language.html.system.lang_english = 		"英文";
	language.html.system.lang_chinese = 		"簡體中文";
	language.html.system.lang_t_chinese = 		"繁體中文";
	
	
	return language;
}






















