
Date.prototype.Format = function (fmt) { //author: meizz 
    var o = {
        "M+": this.getMonth() + 1, //月份 
        "d+": this.getDate(), //日 
        "h+": this.getHours(), //小时 
        "m+": this.getMinutes(), //分 
        "s+": this.getSeconds(), //秒 
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度 
        "S": this.getMilliseconds() //毫秒 
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
    if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}
function cookieFind(name){
	var arr = document.cookie.split(';');
	var i;
	var ckTitle;
	for(i=0;i<arr.length;i++){
		ckTitle = arr[i].split('=')[0].replace(' ','');
		if(ckTitle === name)
			return unescape(arr[i].split('=')[1]);
	}
	return null;
}
function cookieAdd(name,value,time){
	var time=0||time;
	var input;
	value=escape(value);
	if(time){
		var expires = new Date();
		expires.setTime(expires.getTime() + time);
		input=name+'='+value+';expires=' + expires.toGMTString();
	}
	else input=name+'='+value;
	document.cookie=input;
}
