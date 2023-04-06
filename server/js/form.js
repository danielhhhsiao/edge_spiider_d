$(document).on("click",".title",function(){
    var div=$(this).children("div")
    var s=div.html();
    if(s=="-"){
        div.html("+");
        $(this).next().hide();
    }
    else{
        div.html("-");
        $(this).next().show();
    }
});
$(document).on("click",".autoClean",function(){
    $(this).val("");
});
$(document).on("keydown",".autoClean",function(e){
    let _code =  e.keyCode;
    if ( (_code < 48 || _code > 57) && _code != 190 && _code != 8){
        e.preventDefault();
    }
});
$(document).on("input",".autoClean",function(e){
    var s = $(this).val();
    $(this).val(s.replace(/[^0-9.]/g,""));
});
$(document).on("keyup",".autoNext",function(){
    var s=$(this).val();
    if(s.length>=3){
        $(this).val(s.slice(0,3));
        $(this).next().next().focus();
    }
});

$(document).on("keydown",".protect3",function(e){
    var s=$(this).val();
    if(s.length>=3)
        e.preventDefault();
});

$(document).on("keyup",".protect3",function(){
    var s=$(this).val();
    if(s.length>=3)
        $(this).val(s.slice(0,3));
});

$(document).on("keyup",".passwordP",function(){
    var s=$(this).val();
    $(this).next().val(s);
});
$(document).on("keyup",".passwordN",function(){
    var s=$(this).val();
    $(this).prev().val(s);
});
$(document).on("click",".btnShow",function(){
    var s=$(this).val();
    if(s=="Show"){
        $(this).val("Hidden");
        $(this).prev().show();
        $(this).prev().prev().hide();
    }
    else{
        $(this).val("Show");
        $(this).prev().hide();
        $(this).prev().prev().show();
    }
});

$(document).on("change","input[name='showPicture']",function(){
    var status = $("input[name='showPicture']:checked").val();
    if(status=="Yes"){
        $('.img').css('display', "block");
        $('.showImg').css('display', "none");

    }
    else{
        $('.img').css('display', "none");
        $('.showImg').css('display', "block");
    }
});

$(document).on("click",".showImg",function(){
    $(this).next('.img').css('display', "block");
    $(this).css('display', "none");
    $("input[name='showPicture']").prop('checked', false);
});

$(document).on("click",".showHeddened",function(){
    var check = $(this).children('input').is(":checked");
    if(check)
        $(this).next('.heddened').css('display', "block");
    else
        $(this).next('.heddened').css('display', "none");
});

$(document).on("click",".showAdvanced",function(){
    $(this).css('display', "none");
    $(this).next('.showDetail').css('display', "block");
});

function isFloat(string){
    var re = /^[+-]?\d+(\.\d+)?$/; 
    return re.test(string);
}
function isInt(string){
    var re = /^\d+$/; 
    return re.test(string);
}
function isURL(string){
    var re = new RegExp('^(?:[a-z]+:)?//','i'); 
    return re.test(string);
}

function inRange(num,min,max){
    if(num<min || num>max)
        return false;
    return true;
}



function isNumEnglish(word) {
    var regExp = /^[\d|a-zA-Z]+$/;
    return regExp.test(word);
}


function isＷord(word) {
    var regExp = /^[\w-]+$/;
    return regExp.test(word);
}
