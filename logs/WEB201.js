/**
 * WEB_201 �ㅼ�伊� 議고쉶
 */
var condNum = 0;

var plc_params={};
plc_params.I_AS_COUNTRY_CD = "";
plc_params.I_AS_PLC_CAT_CD = "";
plc_params.I_AS_PLC_NM = "";
plc_params.I_PROGRESS_GUID = "Web251";
plc_params.I_REQUEST_USER_ID = "USER";
plc_params.I_REQUEST_IP_ADDRESS = "0.0.0.0";
plc_params.I_REQUEST_PROGRAM_ID = "PMG";

var colModel = [
	{name:'VSL_VOY',index:'VSL_VOY' , align:"center", width:200 },
	{name:'CLOSED',index:'CLOSED',align:"center",width:100},
	{name:'POL',index:'POL' , align:"center", width:250,formatter:function(cellValue){
		return cellValue.replace(" / ", "<br/>");
	}},
	{name:'POL_ETA',index:'POL_ETA', align:"center", width:100,formatter:function(cellValue){
		return getDateFormat(cellValue,"YYYY-MM-DD HH");
	}},
	{name:'POL_ETD',index:'POL_ETD', align:"center", width:100,formatter:function(cellValue){
		return getDateFormat(cellValue,"YYYY-MM-DD HH");
	}},
	{name:'TS',index:'TS',align:"center", width:100,formatter:function(cellValue){
		return cellValue.replace(" / ", "<br/>");
	}},
	{name:'POD',index:'POD', align:"center", width:250,formatter:function(cellValue){
		return cellValue.replace(" / ", "<br/>");
	}},
	{name:'POD_ETA',index:'POD_ETA', align:"center", width:100,formatter:function(cellValue){
		return getDateFormat(cellValue,"YYYY-MM-DD HH");
	}},
	{name:'TT',index:'TT', align:"center", width:50},
	{name:'DOC_CLS_DTM',index:'DOC_CLS_DTM',align:"center", width:100,formatter:function(cellValue){
		return getDateFormat(cellValue,"YYYY-MM-DD HH");
	}},
	{name:'CGO_CLS_DTM',index:'CGO_CLS_DTM', align:"center", width:100,formatter:function(cellValue){
		return getDateFormat(cellValue,"YYYY-MM-DD HH");
	}}
	];
var colNames = [
				'VSL_VOY','BOOKING', 'POL', 'POL_ETA', 'POL_ETD', 'T/S', 'POD', 'POD_ETA', 'TT', 'DOC_CLS_DTM', 'CGO_CLS_DTM'
				];
var colNamesItemCd = [
	'VSL_VOY','CLOSED', 'POL', 'POL_ETA', 'POL_ETD', 'TS', 'POD', 'POD_ETA', 'TT','DOC_CLS_DTM','CGO_CLS_DTM'
];
var isSearch = false;
var bkg_closed_msg = '';
var bkg_check_msg = '';
var bkg_open_msg = '';

$(document).ready(function(){

	$("#addCond").hide();
	$("#delCond").hide();
	$("#calendar").hide();

	comLib.getScreenIetm("WEB_201", null, setItemCallbackFs);
	comLib.getScreenIetm("WEB_201_D",null, gridHeaderNameCallbackFs);

	$("#addCond").click(function(){

		//alert($.find("div[id*=cond]").length);
		if ($.find("div[id*=cond]").length>2) {
			alert("理쒕� 3嫄닿퉴吏� �숈떆�� 議고쉶�섏떎 �� �덉뒿�덈떎.");
			return;
		}

		var curId = "cond"+(++condNum);
		//alert(condClone.find("#cond0"));
		var condClone = $("#cond0").clone();
		condClone.attr("id", curId);
		//condClone.attr("id", "cond"+curNum);
		condClone.find("#delCond").show();
		//condClone.find("button #delCond").show();
		condClone.find("#delCond").click(function(){
			$("#"+curId).remove();
		});
		condClone.find("#addCond").hide();
		$("#searchForm").append(condClone);
	});

	$("#WEB_201_INQ").click(function(){
		if (validate()){
		//if (!pcCalendar.isInit){
			$("#calendar").fadeIn("slow", getSchedule());
			isSearch = true;
		}

	});

	$("#pol_country_plc_nm")
	.on('focus', function(e){
		$(this).val('');
		if($("#div_pol_search").is(":visible")){
			$("#btn_pol_port").trigger("click");
		}
	}).on('keyup', function(e){
		if ((e.keyCode<48)||(e.keyCode>57&&e.keyCode<65)||e.keyCode>90) return false;
		var cp_nm = $(this).val();
		if (cp_nm.length>2){
			getPLCNoCountry($(this));
		}
	}).on('blur', function(e){
		//$(this).parent().find(".port-block").hide();
	}).on('keydown', function(e){
		if (e.keyCode==40){
			var selected = $(this).parent().find("#auto_plc_nm li a.on").eq(0);
			if (selected.length==0) $(this).parent().find("#auto_plc_nm:eq(0) li:eq(0) a").addClass("on");
			else{
				console.log(selected.parent().next().children("a"));
				selected.parent().next().children("a").addClass("on");
				selected.parent().next().siblings().children("a").removeClass("on");
			}
		}else if (e.keyCode==38){
			var selected = $(this).parent().find("#auto_plc_nm li a.on").eq(0);
			if (selected.length==0) return;
			else{
				selected.parent().prev().children("a").addClass("on");
				selected.parent().prev().siblings().children("a").removeClass("on");
			}
		}else if (e.keyCode==13){
			$(this).parent().find("#auto_plc_nm li a.on").eq(0).trigger("click");

		}else if (e.keyCode==27){
			$(this).parent().find(".port-block").hide();
		}
	});

	$("#pod_country_plc_nm")
	.on('focus', function(e){
		$(this).val('');
		if($("#div_pod_search").is(":visible")){
			$("#btn_pod_port").trigger("click");
		}
	}).on('keyup', function(e){
		if (e.keyCode<48||(e.keyCode>57&&e.keyCode<65)||e.keyCode>90) return false;
		var cp_nm = $(this).val();
		if (cp_nm.length>2){
			getPLCNoCountry($(this));
		}
	}).on('blur', function(e){
		//$(this).parent().find(".port-block").hide();
	}).on('keydown', function(e){
		if (e.keyCode==40){
			var selected = $(this).parent().find("#auto_plc_nm li a.on").eq(0);
			console.log(selected);
			if (selected.length==0) $(this).parent().find("#auto_plc_nm:eq(0) li:eq(0) a").addClass("on");
			else{
				console.log(selected.parent().next().children("a"));
				selected.parent().next().children("a").addClass("on");
				selected.parent().next().siblings().children("a").removeClass("on");
			}
		}else if (e.keyCode==38){
			var selected = $(this).parent().find("#auto_plc_nm li a.on").eq(0);
			console.log(selected);
			if (selected.length==0) return;
			else{
				selected.parent().prev().children("a").addClass("on");
				selected.parent().prev().siblings().children("a").removeClass("on");
			}
		}else if (e.keyCode==13){
			$(this).parent().find("#auto_plc_nm li a.on").eq(0).trigger("click");

		}else if (e.keyCode==27){
			$(this).parent().find(".port-block").hide();
		}
	});

	/**異뷀썑 �뺤옣 �� each �꾩슂*/
	$("#btn_pol_port").click(function(){
		if ($("#div_pol_search").is(":hidden")){
			$("#div_pol_search").show();
			//$(this).find("img").attr("src", $(this).find("img").attr("src").replace(".png", "_over.png"));
		}else if ($("#div_pol_search").is(":visible")){
			$("#div_pol_search").hide();
			//$(this).find("img").attr("src", $(this).find("img").attr("src").replace("_over.png", ".png"));
		}
	});

	$("#btn_pod_port").click(function(){
		if ($("#div_pod_search").is(":hidden")){
			$("#div_pod_search").show();
			//$(this).find("img").attr("src", $(this).find("img").attr("src").replace(".png", "_over.png"));
		}else if ($("#div_pod_search").is(":visible")){
			$("#div_pod_search").hide();
			//$(this).find("img").attr("src", $(this).find("img").attr("src").replace("_over.png", ".png"));
		}
	});
	/**each �꾩슂 end*/

	$("#WEB_201_MY_SCH").click(function(){
		getDataWeb226CR();
	});

	$("#WEB_201_TMPLT_SAVE").click(function(){
		if (validate()) setDataWeb226AC();
	});


	$("#WEB_201_LIST").click(function(){
		if (!isSearch){
			//alert("癒쇱� 議고쉶瑜� �댁＜�몄슂.");
			comLib.messageOut('0','Schedule');
			return;
		}
		$("#div_calendar").fadeOut("slow");
		$("#div_list").fadeIn("slow");
		$("#btn_cal").show();
		$("#WEB_201_LIST").hide();
	});

	$("#btn_cal").click(function(){
		$("#div_list").fadeOut("slow");
		$("#div_calendar").fadeIn("slow");
		$("#btn_cal").hide();
		$("#WEB_201_LIST").show();
	});

	$("#WEB_201_TO_DAY").click(function(){
		pcCalendar.setToday();
	});

	$("#WEB_201_DWN").click(function(){
		$("#gridList").table2excel({
			name:$("#WEB_201_SCH").text()+'_'+$("#schYM").text(),
			filename:$("#WEB_201_SCH").text()+'_'+$("#schYM").text(),
			fileext:'.xls',
			sheetName:$("#WEB_201_SCH").text()
			/*header:'Vessel Schedule'*/
		});
	});

	$("#div_list").hide();
	$("#btn_cal").hide();
	$("#myschedule").hide();

	$("#calendar").fadeIn("slow", getSchedule());

	getDataWeb252();
});

function getDataWeb252(){
	var params={};
	params.I_AS_COUNTRY_CD = "";
	params.I_PROGRESS_GUID = "Web252";
	params.I_REQUEST_USER_ID = "USER";
	params.I_REQUEST_IP_ADDRESS = "0.0.0.0";
	params.I_REQUEST_PROGRAM_ID = "PMG";

	$.ajax({
        type : 'post',
        contentType : 'application/json',
        url : 'common/selectWeb252.pcl',
        data : JSON.stringify(params),
        dataType : 'text',
        async : true,
        error: function(xhr, status, error){
            alert("error : "+error);
        },
        success : function(data){
        	getDataWeb252CallBack(data);
        },
    });
}

function getDataWeb252CallBack(data){
	var list = JSON.parse(data).list;
	var cnt = $("#pol_country_cd option").length;
	$("#pol_country_cd option").each(function(index){
		if (index!=0) $(this).remove();
	});
	$("#pod_country_cd option").each(function(index){
		if (index!=0) $(this).remove();
	});
	for (var i=0;i<list.length;i++){
		var opt = "<option value='"+list[i].COUNTRY_CD+"'>"+list[i].COUNTRY_ENM+"</option>";
		$("#pol_country_cd").append(opt);
		$("#pod_country_cd").append(opt);
	}

	if ($("#P_POL_COUNTRY_CD").val()!='' && $("#P_POD_COUNTRY_CD").val()!=''){
		$("#cond0 #pol_country_cd").val($("#P_POL_COUNTRY_CD").val());
		$("#cond0 #pod_country_cd").val($("#P_POD_COUNTRY_CD").val());
		$("#cond0 #pol_country_cd").trigger("change");
		$("#P_POL_COUNTRY_CD").val("");
	}
}

function getPLC(arg, divId){
	plc_params.I_AS_COUNTRY_CD = arg.value;
	plc_params.I_AS_PLC_NM = '';
	$.ajax({
        type : 'post',
        contentType : 'application/json',
        url : 'common/plc_cd.pcl',
        data : JSON.stringify(plc_params),
        dataType : 'text',
        async : true,
        error: function(xhr, status, error){
            alert("error : "+error);
        },
        success : function(data){
        	getPLCCallBack(data, arg, divId);
        },
    });
}

function getPLCCallBack(data, arg, divId){
	var plcList = JSON.parse(data).list;
	var cName = arg.name.replace("country_cd", "");
	var cnt = $("#"+divId+" #"+cName+"port_cd option").length;
	$("#"+divId+" #"+cName+"port_cd option").each(function(index){
		if (index!=0) $(this).remove();
	});
	for (var i=0;i<plcList.length;i++){
		var opt = "<option value='"+plcList[i].PLC_CD+"' enm='"+plcList[i].PLC_ENM+"' portnm='"+plcList[i].PORT_NM+"'>"+($("#hidLang").val()=="KR"?plcList[i].PLC_NM:plcList[i].PLC_ENM)+"</option>";
		$("#"+divId).find("#"+cName+"port_cd").append(opt);
	}

	$("#"+divId).find("#I_AS_"+cName.toUpperCase()+"CTR").val(arg.value);

	if ($("#P_"+cName.toUpperCase()+"PORT_CD").val()!=''){
		$("#"+divId).find("#"+cName+"port_cd").val($("#P_"+cName.toUpperCase()+"PORT_CD").val());
		$("#"+divId).find("#"+cName+"port_cd").trigger("change");
		$("#P_"+cName.toUpperCase()+"PORT_CD").val("");
		if (cName.toUpperCase()=="POD_"){
			$("#WEB_201_INQ").trigger("click");
		}else{
			if ($("#P_POD_COUNTRY_CD").val()!=''){
				$("#cond0 #pod_country_cd").trigger("change");
				$("#P_POD_COUNTRY_CD").val("");
			}
		}


	}
}

function setPLC(arg, divId){
	var cName = arg.name.replace("port_cd", "");
	//$("#"+divId).find("#"+cName+"country_plc_nm").val($("#"+arg.id+" option:selected").attr("enm")+"("+arg.value+") / "+util_trim($("#"+divId).find("#"+cName+"country_cd option:selected").text()));
	$("#"+divId).find("#"+cName+"country_plc_nm").val($("#"+arg.id+" option:selected").attr("portnm"));
	$("#"+divId).find("#div_"+cName+"search").hide();
	$("#"+divId).find("#I_AS_"+cName.toUpperCase()+"CD").val(arg.value);
	$("#"+divId).find("#I_AS_"+cName.toUpperCase()+"CD").attr("enm", $("#"+arg.id+" option:selected").attr("enm"));
}

function getPLCNoCountry(arg){
	console.log("plcnocountry : "+arg.val());
	plc_params.I_AS_PLC_NM = arg.val().toUpperCase();
	plc_params.I_AS_COUNTRY_CD = '';
	$.ajax({
        type : 'post',
        contentType : 'application/json',
        url : 'common/plc_cd.pcl',
        data : JSON.stringify(plc_params),
        dataType : 'text',
        async : true,
        error: function(xhr, status, error){
            alert("error : "+error);
        },
        success : function(data){
        	getPLCNoCountryCallBack(data, arg);
        },
    });
}

function getPLCNoCountryCallBack(data, arg){
	var plcList = JSON.parse(data).list;
	console.log(plcList);
	var html = new Array();
	var cName = arg.attr("name").replace("country_plc_nm", "");
	arg.parent().find("#auto_plc_nm").html('');
	for (var i=0;i<plcList.length;i++){
		//$.plc = $("<li country_cd='"+plcList[i].COUNTRY_CD+"' plc_cd='"+plcList[i].PLC_CD+"' enm='"+plcList[i].PLC_ENM+"'><a href='#none'>"+plcList[i].PLC_ENM+"("+plcList[i].PLC_CD+") / "+plcList[i].COUNTRY_CD+"</a></li>");
		$.plc = $("<li country_cd='"+plcList[i].COUNTRY_CD+"' plc_cd='"+plcList[i].PLC_CD+"' enm='"+plcList[i].PLC_ENM+"'><a href='#none'>"+plcList[i].PORT_NM+"</a></li>");
		$.plc.click(function(){
			//arg.parent().find("#"+cName+"country_cd").val($(this).attr("country_cd")).attr("selected", "selected");
			//arg.parent().find("#"+cName+"port_cd").val($(this).attr("plc_cd")).attr("selected", "selected");
			$("#I_AS_"+cName.toUpperCase()+"CTR").val($(this).attr("country_cd"));
			$("#I_AS_"+cName.toUpperCase()+"CD").val($(this).attr("plc_cd"));
			$("#I_AS_"+cName.toUpperCase()+"CD").attr("enm", $(this).attr("enm"));
			arg.val($(this).children("a").text());
			arg.parent().find(".port-block").hide();
		});
		arg.parent().find("#auto_plc_nm").append($.plc);
		//html.push($.plc.html());
	}

	//arg.parent().find("#auto_plc_nm").html(html.join(''));
	arg.parent().find(".port-block").show();
}

function getDataWeb226CR(init){

	var params={};
	params.I_AS_USR_NO = "AAA";
	params.I_PROGRESS_GUID = "Web201";
	params.I_REQUEST_USER_ID = "USER";
	params.I_REQUEST_IP_ADDRESS = "0.0.0.0";
	params.I_REQUEST_PROGRAM_ID = "PMG";

	$.ajax({
        type : 'post',
        contentType : 'application/json',
        url : 'selectWeb226CR.pcl',
        data : JSON.stringify(params),
        dataType : 'text',
        async : true,
        error: function(xhr, status, error){
            alert("error : "+error);
        },
        success : function(data){
            //alert("");
            //window.location.reload();
        	getDataWeb226CRCallBack(data);
        },
    });
}

function getDataWeb226CRCallBack(data){
	var list = JSON.parse(data).rows;
	if (list.length==0){
		comLib.messageOut("4005","","");
		return;
	}
	var html = new Array();
	$("#myschedule > ul").html('');
	for (var i=0;i<list.length;i++){
		$.vsl = $("<li id='"+list[i].NO+"' pol_country_cd='"+list[i].POL_COUNTRY_CD+"' pol_port_cd='"+list[i].POL_PORT_CD+"' "+
							"pod_country_cd='"+list[i].POD_COUNTRY_CD+"' pod_port_cd='"+list[i].POD_PORT_CD+"' pol_country_nm='"+list[i].POL_COUNTRY_NM+"'"+
							"pol_nm='"+list[i].POL_NM+"' pod_country_nm='"+list[i].POD_COUNTRY_NM+"' pod_nm='"+list[i].POD_NM+"'><a href='#none'>"+list[i].TITLE+"</a></li>");
		$.vsl.click(function(){
			//$(opener.document).find("#"+$(opener.document).popupParams.cd).val(vsl_list[i].vsl_nm);
			$("#I_AS_POL_CD").val($(this).attr("pol_port_cd"));
			$("#I_AS_POL_CD").attr("enm", $(this).attr("pol_nm"));
			$("#I_AS_POL_CTR").val($(this).attr("pol_country_cd"));
			$("#pol_country_plc_nm").val($(this).attr("pol_nm")+"("+$(this).attr("pol_country_cd")+$(this).attr("pol_port_cd")+")/"+$(this).attr("pol_country_nm"));
			$("#I_AS_POD_CD").val($(this).attr("pod_port_cd"));
			$("#I_AS_POD_CD").attr("enm", $(this).attr("pod_nm"));
			$("#I_AS_POD_CTR").val($(this).attr("pod_country_cd"));
			$("#pod_country_plc_nm").val($(this).attr("pod_nm")+"("+$(this).attr("pod_country_cd")+$(this).attr("pod_port_cd")+")/"+$(this).attr("pod_country_nm"));
			$("#myschedule").hide();
			$("#WEB_201_INQ").trigger("click");
		});
		$("#myschedule > ul").append($.vsl);
	}

	$("#myschedule").show();
	$('#myschedule .btn-close').click(function(){
		$("#myschedule").hide();
	});
}

function setDataWeb226AC(){
	var params={};
	params.I_AS_KIND_CD = "03";
	params.I_AS_TITLE = $("#I_AS_POL_CD").attr("enm")+" - "+$("#I_AS_POD_CD").attr("enm");
	params.I_AS_NO = $("#I_AS_POL_CTR").val()+$("#I_AS_POL_CD").val()+$("#I_AS_POD_CTR").val()+$("#I_AS_POD_CD").val();
	params.I_POL_COUNTRY_CD = $("#I_AS_POL_CTR").val();
	params.I_POL_PORT_CD = $("#I_AS_POL_CD").val();
	params.I_POD_COUNTRY_CD = $("#I_AS_POD_CTR").val();
	params.I_POD_PORT_CD = $("#I_AS_POD_CD").val();

	$.ajax({
        type : 'post',
        contentType : 'application/json',
        url : 'insertMyTemplate.pcl',
        data : JSON.stringify(params),
        dataType : 'text',
        async : true,
        error: function(xhr, status, error){
            alert("error : "+error);
        },
        success : function(data){
            //alert("");
            //window.location.reload();
        	setDataWeb226ACCallBack(data);
        },
    });
}

function setDataWeb226ACCallBack(data){
	var result = JSON.parse(data);
	if (result.flag=='Y'){
		if (result.return_code=='Template_data_EXIST'){
			//alert("�대� �깅줉�� �ㅼ�伊댁엯�덈떎.");
			comLib.messageOut("4006",'');
		}else comLib.messageOut("4007",$("#WEB_201_TMPLT_SAVE").text(),'');//alert("�깅줉�� �ㅽ뙣�섏��듬땲��.");
		return;
	}else comLib.messageOut(msgLib.MSG_100,'');//alert("�깅줉�섏뿀�듬땲��.");
}
//var cur_year = '';
//var cur_month = '';

/*function setCurDate(){
	cur_year = $("#sYear").val();
	cur_month = $("#sMonth").val();
	$("#schYM").text(cur_year+". "+util_lpad(cur_month,2,'0'));
}*/
function setPrevMonth() {
	var year = Number(cur_year);
	var month = Number(cur_month);
	if (month <= 1) {
		year -= 1;
		month = 12;
	} else {
		month -= 1;
	}

	$("#schYM").text(year+". "+util_lpad(month,2,'0'));
	//setCalendarPageContent($scope, year, month);
	//$('.table.open').removeClass('open');
	//$('.selected').removeClass('selected');

}

function setNextMonth($scope) {
var year = Number($scope.year);
var month = Number($scope.month);
if (month >= 12) {
	year += 1;
	month = 1;
} else {
	month += 1;
}
}

var pcCalendar={
	id : 'calTable',
	isInit : false,
	locale : 'en',
	cur_year : '',
	cur_month : '',
	month : {
		num  : ['1','2','3','4','5','6','7','8','9','10','11','12']
    	,en : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    	,kr : ['1��','2��','3��','4��','5��','6��','7��','8��','9��','10��','11��','12��']
    	,ch : ['1��','2��','3��','4��','5��','6��','7��','8��','9��','10��','11��','12��']
		,jp : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	},
	week : {
		num  : ['0','1','2','3','4','5','6']
    	,en : ['SUN','MON','TUE','WED','THU','FRI','SAT']
    	,kr : ['��','��','��','��','紐�','湲�','��']
    	,ch : ['��','��','��','麗�','��','��','��']
		,jp : ['SUN','MON','TUE','WED','THU','FRI','SAT']
	},
	init : function(id){
		pcCalendar.id = id;
		pcCalendar.isInit = true;
		pcCalendar.setCurDate();
		pcCalendar.locale = $("#hidLang").val().toLowerCase()||'en';
		//displayCalendar();
	},
	setCurDate : function(){
		pcCalendar.cur_year = $("#sYear").val();
		pcCalendar.cur_month = $("#sMonth").val();
		$("#schYM").text(pcCalendar.cur_year+". "+util_lpad(pcCalendar.cur_month,2,'0'));
		$("#pol_pod_info").html('');
		$(document).find("div[id*=cond]").each(function(){
			if ($(this).find("#I_AS_POL_CD").attr("enm")!=''){
				//$.direction = $("<li><a href='#none' class='first'>"+$(this).find("#pol_port_cd option:selected").attr("enm")+" <i class='icon-arrow'></i> "+$(this).find("#pod_port_cd option:selected").attr("enm")+"</a></li>");
				$.direction = $("<li><a href='#none' class='first'>"+$(this).find("#I_AS_POL_CD").attr("enm")+" <i class='icon-arrow'></i> "+$(this).find("#I_AS_POD_CD").attr("enm")+"</a></li>");
				$.direction.click(function(){
					getSchedule();
				});
				$("#pol_pod_info").append($.direction);
			}
		});
	},
	changeLocale : function(loc){
		pcCalendar.locale = loc;
		pcCalendar.displayCalendarHead();
	},
	displayCalendar : function(init){
		if (init || init==undefined) pcCalendar.init(pcCalendar.id);
		pcCalendar.displayCalendarHead();
		pcCalendar.displayCalendarDay();
	},
	displayCalendarHead : function(){
		$("#"+pcCalendar.id+" thead tr th").each(function(index){
			$(this).text(eval("pcCalendar.week."+pcCalendar.locale+"[index]"));
		});
	},
	displayCalendarDay : function(){
		var cY = pcCalendar.cur_year;
		var cM = pcCalendar.cur_month;

		var st = getDateSt(cY, cM);
		var ed = getDateEd(cY, cM);
		var preEd = getPreDateEd(cY, cM);

		var html = new Array();
		if (st.week>0){
			html.push("<tr>");
			for (var i=st.week;i>0;i--){
				html.push("<td>");
				html.push("<div class='calenter-data'>");
				html.push("<span class='day none'>"+(preEd.date-i+1)+"</span>");
				//html.push("<div class='selected'><span class='today'>5</span><span class="ym-data">2017.01 (��)</span></div>
				//<a href="#none" class="close">Close</a>
				html.push("</div>");
				html.push("</td>");
			}
		}

		var dayCss = 'day';
		for (var i=1;i<=ed.date;i++){
			var day = getDay(cY, cM, i);
			if (day==0) html.push("<tr>");

			if (isToday(cY, cM, i)){
				dayCss = 'day today';
			}else if (day==6){
				dayCss = 'day sat';
			}else if (day==0){
				dayCss = 'day sun';
			}else dayCss = 'day';

			html.push("<td>");
			html.push("<div class='calenter-data'>");
			html.push("<span class='"+dayCss+"'>"+i+"</span>");
			html.push("<ul class='list' id='"+pcCalendar.id+"_"+i+"_date'>");
			html.push("</ul>");
			html.push("<div class='selected'><span class='bigDay'>"+i+"</span><span class='ym-data'>"+cY+". "+util_lpad(cM, 2, '0')+" ("+eval('pcCalendar.week.'+pcCalendar.locale+'[day]')+")</span></div>");
			html.push("<a href='#none' class='close'>Close</a>");
			html.push("</div>");
			html.push("</td>");

			if (day==6){

			html.push("</tr>");

			html.push("<!-- �곸꽭 由ъ뒪�� �곸뿭 -->");
			html.push("<tr class='cover-hide' id='detail'>");
			html.push("<td colspan='7' class='detail-section'>");
			html.push("<!-- �섏엯 -->");
			html.push("<div class='detail-cont' id='im_detail'>");
			html.push("<div class='detail-cont-sub' id='im_detail_1'>");
			html.push("<p class='tt fL'><span id='WEB_201_C_VSL'></span> : <span id='vsl_nm'></span></p>");
			html.push("<p class='tt fL mg-l10 hidden' id='REM4'><font color='red'><span id='WEB_201_C_REM1'></span></font></p>");
			html.push("<div class='r-cover'><span class='data'><span id='WEB_201_C_DDS'>�뚯슂�쒓컙</span> : <span id='dds'></span></span><span class='data mg-l10' id='span_delay'><font color='red'><span id='WEB_201_C_DELAY'>Delay Hours</span> : <span id='delay'></span></font></span><!--<a href='#none' class='btn-ms-type btn-min3' id='WEB_201_C_IMP_BL'>�섏엯 B/L 議고쉶</a>--></div>");
			html.push("<table class='ui-tb-box2'>");
			html.push("<caption>�섏엯�� ���� 異쒕컻吏�紐�, 異쒕컻�쒓컙, �꾩갑吏�紐�, �꾩갑�쒓컙,  EDI �좉퀬留덇컧, �μ튂�μ퐫��, �곕���, MRN No, Call Sign �쒖엯�덈떎.</caption>");
			html.push("<colgroup>");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("</colgroup>");
			html.push("<tbody>");
			html.push("<tr>");
			html.push("<th scope='col' id='WEB_201_C_POL'>異쒕컻吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_C_POL_ETD_TM'>異쒕컻�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_C_POD'>�꾩갑吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_C_POD_ETA_TM'>�꾩갑�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_C_MF_EDI_CLS_DTM'>EDI �좉퀬 留덇컧</th>");
			html.push("<th scope='col' id='WEB_201_C_NBRD_CD'>�μ튂�� 肄붾뱶</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td id='pol'></td>");
			html.push("<td id='pol_etd_tm'></td>");
			html.push("<td id='pod'></td>");
			html.push("<td id='pod_eta_tm'></td>");
			html.push("<td id='mf_edi_cls_dtm'></td>");
			html.push("<td id='pol_edi_cd'></td>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<th scope='col' colspan='2' id='WEB_201_C_POL_TMN'>�곕���</th>");
			html.push("<th scope='col' colspan='2' id='WEB_201_C_POD_TMN'>�곕���</th>");
			html.push("<th scope='col' id='WEB_201_C_MRN'>MRN No.</th>");
			html.push("<th scope='col' id='WEB_201_C_CALL'>Call Sign</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td colspan='2' class='tl' id='pol_tmn'></td>");
			html.push("<td colspan='2' class='tl' id='pod_tmn'></td>");
			html.push("<td id='mrn'></td>");
			html.push("<td id='call_sign_no'></td>");
			html.push("</tr>");
			html.push("</tbody>");
			html.push("</table>");
			html.push("</div>");
			html.push("</div>");
			html.push("<!-- //�섏엯 -->");
			html.push("<!-- �섏텧 -->");
			html.push("<div class='detail-cont' id='ex_detail'>");
			html.push("<div class='detail-cont-sub' id='ex_detail_1'>");
			html.push("<p class='tt fL'><span id='WEB_201_B_VSL'></span> : <span id='vsl_nm'></span></p>");
			html.push("<p class='tt fL mg-l10 hidden' id='REM4'><font color='red'><span id='WEB_201_B_REM4'></span></font></p>");
			html.push("<div class='r-cover'><span class='data'><span id='WEB_201_B_DDS'>�뚯슂�쒓컙</span> : <span id='dds'></span></span><span class='data mg-l10' id='span_delay'><font color='red'><span id='WEB_201_B_DELAY'>�뚯슂�쒓컙</span> : <span id='delay'></span></font></span><a href='#none' class='btn-ms-type btn-min' id='WEB_201_B_SCH_NOTICE'>NOTICE</a><a href='#none' class='btn-ms-type btn-min' id='WEB_201_B_NEW_BKG'>New Booking</a></div>");
			html.push("<table class='ui-tb-box2'>");
			html.push("<caption>�섏텧�� ���� 異쒕컻吏�紐�, 異쒕컻�쒓컙, �꾩갑吏�紐�, �꾩갑�쒓컙,  �쒕쪟/VGM/EDI, 而⑦뀒�대꼫 諛섏엯, CFS諛섏엯, �곕���, MRN No, CALL SIGN, �μ튂�μ퐫�� �쒖엯�덈떎.</caption>");
			html.push("<colgroup>");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("</colgroup>");
			html.push("<tbody>");
			html.push("<tr>");
			html.push("<th scope='col' id='WEB_201_B_POL'>異쒕컻吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_B_POL_ETD_TM'>異쒕컻�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_B_POD'>�꾩갑吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_B_POD_ETA_TM'>�꾩갑�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_B_DOC_CLS_DTM'>�쒕쪟/VGM/EDI</th>");
			html.push("<th scope='col' id='WEB_201_B_CGO_CLS_DTM'>而⑦뀒�대꼫 諛섏엯</th>");
			html.push("<th scope='col' id='WEB_201_B_CFS_EDI_CLS_DTM'>CFS 諛섏엯</th>");
			html.push("<th scope='col' id='WEB_201_B_CTR_CD'>CTR_CD</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td id='pol'></td>");//異뷀썑 援�� 異붽�
			html.push("<td id='pol_etd_tm'></td>");//yyyy/mm/dd hh24:mi
			html.push("<td id='pod'></td>");
			html.push("<td id='pod_eta_tm'></td>");
			html.push("<td id='doc_cls_dtm'></td>");
			html.push("<td id='cgo_cls_dtm'></td>");
			html.push("<td id='cfs_cls_dtm'></td>");
			html.push("<td id='ctr_cd'></td>");
			html.push("</tr>");
			html.push("</tbody>");
			html.push("</table>");
			html.push("<table class='ui-tb-box2' style='margin-top:0px;'>");
			html.push("<caption>�섏텧�� ���� 異쒕컻吏�紐�, 異쒕컻�쒓컙, �꾩갑吏�紐�, �꾩갑�쒓컙,  �쒕쪟/VGM/EDI, 而⑦뀒�대꼫 諛섏엯, CFS諛섏엯, �곕���, MRN No, CALL SIGN, �μ튂�μ퐫�� �쒖엯�덈떎.</caption>");
			html.push("<colgroup>");
			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:14.285%' />");
			html.push("</colgroup>");
			html.push("<tbody>");
			html.push("<tr>");
			html.push("<th scope='col' colspan='2' id='WEB_201_B_POL_TMN'>�곕���</th>");
			html.push("<th scope='col' colspan='2' id='WEB_201_B_POD_TMN'>�곕���</th>");
			html.push("<th scope='col' id='WEB_201_B_MRN'>MRN No.</th>");
			html.push("<th scope='col' id='WEB_201_B_CALL_SIGN_NO'>Call Sign</th>");
			html.push("<th scope='col' id='WEB_201_B_POL_EDI_CD'>�μ튂�μ퐫��</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td colspan='2' class='tl' id='pol_tmn'></td>");
			html.push("<td colspan='2' class='tl' id='pod_tmn'></td>");
			html.push("<td id='mrn'></td>");
			html.push("<td id='call_sign_no'></td>");
			html.push("<td id='pol_edi_cd'></td>");
			html.push("</tr>");
			html.push("</tbody>");
			html.push("</table>");
			html.push("<input type='hidden' name='mf_edi_cls_dtm' id='mf_edi_cls_dtm'/>");
			html.push("<input type='hidden' name='vgm_cls_dtm' id='vgm_cls_dtm'/>");
			html.push("</div>");
			html.push("</div>");
			html.push("<!-- //�섏텧 -->");
			html.push("</td>");
			html.push("</tr>");
			}
		}

		if (ed.week<6){
			for (var i=ed.week;i<6;i++){
				html.push("<td>");
				html.push("<div class='calenter-data'>");
				html.push("<span class='day none'>"+(1+i-ed.week)+"</span>");
				//html.push("<div class='selected'><span class='today'>5</span><span class="ym-data">2017.01 (��)</span></div>
				//<a href="#none" class="close">Close</a>
				html.push("</div>");
				html.push("</td>");
			}
			html.push("</tr>");
			html.push("<!-- �곸꽭 由ъ뒪�� �곸뿭 -->");
			html.push("<tr class='cover-hide' id='detail'>");
			html.push("<td colspan='7' class='detail-section'>");
			html.push("<!-- �섏엯 -->");
			html.push("<div class='detail-cont' id='im_detail'>");
			html.push("<div class='detail-cont-sub' id='im_detail_1'>");
			html.push("<p class='tt fL'><span id='WEB_201_C_VSL'></span> : <span id='vsl_nm'></span></p>");
			html.push("<p class='tt fL mg-l10 hidden' id='REM4'><font color='red'><span id='WEB_201_C_REM1'></span></font></p>");
			html.push("<div class='r-cover'><span class='data'><span id='WEB_201_C_DDS'>�뚯슂�쒓컙</span> : <span id='dds'></span></span><span class='data mg-l10' id='span_delay'><font color='red'><span id='WEB_201_C_DELAY'>�뚯슂�쒓컙</span> : <span id='delay'></span></font></span><!--<a href='#none' class='btn-ms-type btn-min3' id='WEB_201_C_IMP_BL'>�섏엯 B/L 議고쉶</a>--></div>");
			html.push("<table class='ui-tb-box2'>");
			html.push("<caption>�섏엯�� ���� 異쒕컻吏�紐�, 異쒕컻�쒓컙, �꾩갑吏�紐�, �꾩갑�쒓컙,  EDI �좉퀬留덇컧, �μ튂�μ퐫��, �곕���, MRN No, Call Sign �쒖엯�덈떎.</caption>");
			html.push("<colgroup>");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("<col style='width:16.666%' />");
			html.push("</colgroup>");
			html.push("<tbody>");
			html.push("<tr>");
			html.push("<th scope='col' id='WEB_201_C_POL'>異쒕컻吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_C_POL_ETD_TM'>異쒕컻�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_C_POD'>�꾩갑吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_C_POD_ETA_TM'>�꾩갑�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_C_MF_EDI_CLS_DTM'>EDI �좉퀬 留덇컧</th>");
			html.push("<th scope='col' id='WEB_201_C_NBRD_CD'>�μ튂�� 肄붾뱶</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td id='pol'></td>");
			html.push("<td id='pol_etd_tm'></td>");
			html.push("<td id='pod'></td>");
			html.push("<td id='pod_eta_tm'></td>");
			html.push("<td id='mf_edi_cls_dtm'></td>");
			html.push("<td id='pol_edi_cd'></td>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<th scope='col' colspan='2' id='WEB_201_C_POL_TMN'>�곕���</th>");
			html.push("<th scope='col' colspan='2' id='WEB_201_C_POD_TMN'>�곕���</th>");
			html.push("<th scope='col' id='WEB_201_C_MRN'>MRN No.</th>");
			html.push("<th scope='col' id='WEB_201_C_CALL'>Call Sign</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td colspan='2' class='tl' id='pol_tmn'></td>");
			html.push("<td colspan='2' class='tl' id='pod_tmn'></td>");
			html.push("<td id='mrn'></td>");
			html.push("<td id='call_sign_no'></td>");
			html.push("</tr>");
			html.push("</tbody>");
			html.push("</table>");
			html.push("</div>");
			html.push("</div>");
			html.push("<!-- //�섏엯 -->");
			html.push("<!-- �섏텧 -->");
			html.push("<div class='detail-cont' id='ex_detail'>");
			html.push("<div class='detail-cont-sub' id='ex_detail_1'>");
			html.push("<p class='tt fL'><span id='WEB_201_B_VSL'></span> : <span id='vsl_nm'></span></p>");
			html.push("<p class='tt fL mg-l10' id='REM4'><font color='red'><span id='WEB_201_B_REM4'></span></font></p>");
			html.push("<div class='r-cover'><span class='data'><span id='WEB_201_B_DDS'>�뚯슂�쒓컙</span> : <span id='dds'></span></span><span class='data mg-l10' id='span_delay'><font color='red'><span id='WEB_201_B_DELAY'>�뚯슂�쒓컙</span> : <span id='delay'></span></font></span><a href='#none' class='btn-ms-type btn-min' id='WEB_201_B_SCH_NOTICE'>NOTICE</a><a href='#none' class='btn-ms-type btn-min' id='WEB_201_B_NEW_BKG'>New Booking</a></div>");
			html.push("<table class='ui-tb-box2' style='margin-top:0px;'>");
			html.push("<caption>�섏텧�� ���� 異쒕컻吏�紐�, 異쒕컻�쒓컙, �꾩갑吏�紐�, �꾩갑�쒓컙,  �쒕쪟/VGM/EDI, 而⑦뀒�대꼫 諛섏엯, CFS諛섏엯, �곕���, MRN No, CALL SIGN, �μ튂�μ퐫�� �쒖엯�덈떎.</caption>");
			html.push("<colgroup>");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
//			html.push("<col style='width:14.285%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("<col style='width:12.5%' />");
			html.push("</colgroup>");
			html.push("<tbody>");
			html.push("<tr>");
			html.push("<th scope='col' id='WEB_201_B_POL'>異쒕컻吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_B_POL_ETD_TM'>異쒕컻�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_B_POD'>�꾩갑吏�紐�</th>");
			html.push("<th scope='col' id='WEB_201_B_POD_ETA_TM'>�꾩갑�쒓컙</th>");
			html.push("<th scope='col' id='WEB_201_B_DOC_CLS_DTM'>�쒕쪟/VGM/EDI</th>");
			html.push("<th scope='col' id='WEB_201_B_CGO_CLS_DTM'>而⑦뀒�대꼫 諛섏엯</th>");
			html.push("<th scope='col' id='WEB_201_B_CFS_EDI_CLS_DTM'>CFS 諛섏엯</th>");
			html.push("<th scope='col' id='WEB_201_B_CTR_CD'>CTR_CD</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td id='pol'></td>");//異뷀썑 援�� 異붽�
			html.push("<td id='pol_etd_tm'></td>");//yyyy/mm/dd hh24:mi
			html.push("<td id='pod'></td>");
			html.push("<td id='pod_eta_tm'></td>");
			html.push("<td id='doc_cls_dtm'></td>");
			html.push("<td id='cgo_cls_dtm'></td>");
			html.push("<td id='cfs_cls_dtm'></td>");
			html.push("<td id='ctr_cd'></td>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<th scope='col' colspan='2' id='WEB_201_B_POL_TMN'>�곕���</th>");
			html.push("<th scope='col' colspan='2' id='WEB_201_B_POD_TMN'>�곕���</th>");
			html.push("<th scope='col' id='WEB_201_B_MRN'>MRN No.</th>");
			html.push("<th scope='col' id='WEB_201_B_CALL_SIGN_NO'>Call Sign</th>");
			html.push("<th scope='col' id='WEB_201_B_POL_EDI_CD'>�μ튂�μ퐫��</th>");
			html.push("</tr>");
			html.push("<tr>");
			html.push("<td colspan='2' class='tl' id='pol_tmn'></td>");
			html.push("<td colspan='2' class='tl' id='pod_tmn'></td>");
			html.push("<td id='mrn'></td>");
			html.push("<td id='call_sign_no'></td>");
			html.push("<td id='pol_edi_cd'></td>");
			html.push("</tr>");
			html.push("</tbody>");
			html.push("</table>");
			html.push("<input type='hidden' name='mf_edi_cls_dtm' id='mf_edi_cls_dtm'/>");
			html.push("<input type='hidden' name='vgm_cls_dtm' id='vgm_cls_dtm'/>");
			html.push("</div>");
			html.push("</div>");
			html.push("<!-- //�섏텧 -->");
			html.push("</td>");
			html.push("</tr>");
		}
		$("#"+pcCalendar.id+" tbody").html(html.join(''));
		$('.calender-cover td .close').click(function(){
			$('.calender-cover td').removeClass('active');
			$(this).parents('tr').next().find('.detail-cont').slideUp();
		});
	},
	setPrevMonth : function(){
		if (!validate()) return;
		var prev = addMonths(pcCalendar.cur_year, parseInt(pcCalendar.cur_month)-1, -1);
		pcCalendar.cur_year = prev.year;
		pcCalendar.cur_month = prev.month;
		$("#schYM").text(pcCalendar.cur_year+". "+util_lpad(pcCalendar.cur_month,2,'0'));
		/*pcCalendar.displayCalendarHead();
		pcCalendar.displayCalendarDay();*/
		getSchedule(false);
	},
	setNextMonth : function(){
		if (!validate()) return;
		var prev = addMonths(pcCalendar.cur_year, parseInt(pcCalendar.cur_month)-1, 1);
		pcCalendar.cur_year = prev.year;
		pcCalendar.cur_month = prev.month;
		$("#schYM").text(pcCalendar.cur_year+". "+util_lpad(pcCalendar.cur_month,2,'0'));
		getSchedule(false);
	},
	setToday : function(){
		if (!validate()) return;
		var now = getToday();
		pcCalendar.cur_year = now.year;
		pcCalendar.cur_month = now.month;
		$("#schYM").text(pcCalendar.cur_year+". "+util_lpad(pcCalendar.cur_month,2,'0'));
		getSchedule(true);
	}
};

var inq_ing = false;
function getSchedule(init){
	if (inq_ing){
		//alert("議고쉶以묒엯�덈떎. �좎떆留� 湲곕떎�� 二쇱꽭��.");
		comLib.messageOut('2','');
		return;
	}else inq_ing = true;

	$("#loading-bar").show();
	pcCalendar.displayCalendar(init);

	var params={};
	//params.I_AS_DATE = $("#sYear").val()+util_lpad($("#sMonth").val(), 2, '0');
	params.I_AS_DATE = pcCalendar.cur_year+util_lpad(pcCalendar.cur_month,2,'0');
	params.I_AS_POL_CD = $("#I_AS_POL_CD").val();
	params.I_AS_POL_CTR = $("#I_AS_POL_CTR").val();
	params.I_AS_POD_CD = $("#I_AS_POD_CD").val();
	params.I_AS_POD_CTR = $("#I_AS_POD_CTR").val();
	params.I_AS_IN_OUT_CD = $("input:radio[name=rd_apdpDate]:checked").val();
	params.I_PROGRESS_GUID = "Web201";
	params.I_REQUEST_USER_ID = "USER";
	params.I_REQUEST_IP_ADDRESS = "0.0.0.0";
	params.I_REQUEST_PROGRAM_ID = "PMG";

	params.rd_apdpDate = $("input:radio[name=rd_apdpDate]:checked").val();


	//var itemData = $("form[name=sForm]").serialize();
	//console.log(itemData);

	$.ajax({
        type : 'post',
        contentType : 'application/json',
        url : 'selectWeb201.pcl',
        data : JSON.stringify(params),
        dataType : 'text',
        async : true,
        error: function(xhr, status, error){
            alert("error : "+error);
            $("#loading-bar").hide();
            inq_ing = false;
        },
        success : function(data){
            //alert("");
            //window.location.reload();
        	getScheduleCallBack(data);
        },
    });
}

function getScheduleCallBack(data, arg, divId){
	//console.log();
	//alert(data);
	var sch = JSON.parse(data).schedule;
	console.log(sch);
	var schList = sch.O_RESULT_CURSOR;
	console.log(schList);
	var apdp = sch.rd_apdpDate;
	var tsList = getTSSchSort(schList);
	console.log(tsList);
	var newList = new Array();
	var newItem;
	if (isSearch && sch.O_ERROR_FLAG=='Y') comLib.messageOut(sch.O_MESSAGE_CODE);
	if (isSearch && schList.length==0) comLib.messageOut("0",'Schedule');

	for (var i=0;i<schList.length;i++){
		console.log(schList[i].POL_REVISED_APDP_DATE+' '+schList[i].GUBUN+' '+schList[i].SEC_SEQ);
		if (parseInt(schList[i].SEC_SEQ)>1) continue;
		var apdp_date = '';
		var detail_cont_id = '';
		var voy_no = '';
		if (apdp=='O'){
			apdp_date = schList[i].POL_REVISED_APDP_DATE;
			detail_cont_id = 'ex_detail';
			voy_no = schList[i].EXP_VOY_NO;
		}else if (apdp=='I'){
			apdp_date = schList[i].POD_REVISED_APDP_DATE;
			detail_cont_id = 'im_detail';
			voy_no = schList[i].IMP_VOY_NO;
		}

		if (apdp_date.substring(0,6)!=pcCalendar.cur_year+util_lpad(pcCalendar.cur_month,2,'0')) continue;

			newItem = schList[i];
			apdp_date_day = apdp_date.substring(6,8);
			var closeYN = schList[i].CLOSED=='CLOSED'?'end':schList[i].CLOSED=='CHECK'?'end':'ing';
			var tooltip = '';
			if (closeYN == 'ing'){
				tooltip = "<span class='tooltip'><span id='WEB_201_C_VOY'>��감</span> : "+voy_no+"("+(schList[i].TS=='N'?'Direct':'TS')+")<br /> ETD : "+getDateFormat(schList[i].POL_REVISED_APDP_DATE+schList[i].POL_REVISED_APDP_TM, 'YYYY/MM/DD HH:MI')+"<br /> ETA : "+getDateFormat(schList[i].POD_REVISED_APDP_DATE+schList[i].POD_REVISED_APDP_TM, 'YYYY/MM/DD HH:MI')+"</span>";
			}else{
				if (schList[i].CLOSED=='CLOSED') tooltip = "<span class='tooltip'>"+bkg_closed_msg+"</span>";//"�대떦 �좊컯�� Booking�� 留덇컧�섏뿀�듬땲��.<br /> �ㅻⅨ �좊컯�� �좏깮�섏뿬 二쇱떆湲� 諛붾엻�덈떎.";
				else if (schList[i].CLOSED=='CHECK') tooltip = "<span class='tooltip'>"+bkg_check_msg+"</span>";
			}

			var tsSchNo = '';

			$.add_vsl = $("<li class='calendar-list' id='"+schList[i].VSL_CD+"' pol_sch_no='"+schList[i].POL_SCH_NO+"' pod_sch_no='"+schList[i].POD_SCH_NO+"' ts='"+schList[i].TS+"'><a href='#none' class='"+closeYN+"'>"+schList[i].VSL_NM+"<font color='red' size='0.5'>"+(schList[i].TS=='N'?'':'(TS)')+"</font></a>"+tooltip+"</li>");
			$.add_vsl.attr("pol_sch_no", schList[i].POL_SCH_NO);
			$.add_vsl.attr("pod_sch_no", schList[i].POD_SCH_NO);
			$.add_vsl.attr("gubun", schList[i].GUBUN);
			$.add_vsl.attr("sec_seq", schList[i].SEC_SEQ);
			$.add_vsl.attr("vsl_cd", schList[i].VSL_CD);
			$.add_vsl.attr("vsl_nm", schList[i].VSL_NM);
			$.add_vsl.attr("voy_no", voy_no);
			$.add_vsl.attr("pol_country_cd", schList[i].POL_COUNTRY_CD);
			$.add_vsl.attr("pol_port_cd", schList[i].POL_PORT_CD);
			$.add_vsl.attr("pod_country_cd", schList[i].POD_COUNTRY_CD);
			$.add_vsl.attr("pod_port_cd", schList[i].POD_PORT_CD);
			$.add_vsl.attr("closed", schList[i].CLOSED);
			$.add_vsl.attr("ts_seq", 1);

			if (schList[i].TS=='Y'){
				var tsSchArr = {};
				if (tsList.arr2.length>0){
					tsSchArr = getTSSchNo(schList[i].POD_REVISED_APDP_DATE+schList[i].POD_REVISED_APDP_TM, tsList.arr2);
					if (tsSchArr.POL_SCH_NO!=undefined){
						$.add_vsl.attr("pol_sch_no_ts2", tsSchArr.POL_SCH_NO);
						$.add_vsl.attr("pod_sch_no_ts2", tsSchArr.POD_SCH_NO);
						$.add_vsl.attr("gubun_ts2", tsSchArr.GUBUN);
						$.add_vsl.attr("sec_seq_ts2", tsSchArr.SEC_SEQ);
						$.add_vsl.attr("vsl_cd_ts2", tsSchArr.VSL_CD);
						$.add_vsl.attr("vsl_nm_ts2", tsSchArr.VSL_NM);
						$.add_vsl.attr("voy_no_ts2", tsSchArr.EXP_VOY_NO);
						$.add_vsl.attr("pol_country_cd_ts2", tsSchArr.POL_COUNTRY_CD);
						$.add_vsl.attr("pol_port_cd_ts2", tsSchArr.POL_PORT_CD);
						$.add_vsl.attr("pod_country_cd_ts2", tsSchArr.POD_COUNTRY_CD);
						$.add_vsl.attr("pod_port_cd_ts2", tsSchArr.POD_PORT_CD);
						$.add_vsl.attr("ts_seq", 2);

						newItem.TS = tsSchArr.POL;
						newItem.TT = parseInt(newItem.TT)+parseInt(tsSchArr.TT);
						newItem.POD = tsSchArr.POD;
					}
				}
				if (tsList.arr3.length>0){
					tsSchArr = getTSSchNo(schList[i].POD_REVISED_APDP_DATE+schList[i].POD_REVISED_APDP_TM, tsList.arr3);
					$.add_vsl.attr("pol_sch_no_ts3", tsSchArr.POL_SCH_NO);
					$.add_vsl.attr("pod_sch_no_ts3", tsSchArr.POD_SCH_NO);
					$.add_vsl.attr("gubun_ts3", tsSchArr.GUBUN);
					$.add_vsl.attr("sec_seq_ts3", tsSchArr.SEC_SEQ);
					$.add_vsl.attr("vsl_cd_ts3", tsSchArr.VSL_CD);
					$.add_vsl.attr("vsl_nm_ts3", tsSchArr.VSL_NM);
					$.add_vsl.attr("voy_no_ts3", tsSchArr.EXP_VOY_NO);
					$.add_vsl.attr("pol_country_cd_ts3", tsSchArr.POL_COUNTRY_CD);
					$.add_vsl.attr("pol_port_cd_ts3", tsSchArr.POL_PORT_CD);
					$.add_vsl.attr("pod_country_cd_ts3", tsSchArr.POD_COUNTRY_CD);
					$.add_vsl.attr("pod_port_cd_ts3", tsSchArr.POD_PORT_CD);
					$.add_vsl.attr("ts_seq", 3);

					newItem.TS += '<br/>'+tsSchArr.POL;
					newItem.TT = parseInt(newItem.TT)+parseInt(tsSchArr.TT);
					newItem.POD = tsSchArr.POD;
				}

				newList.push(newItem);
			}else newList.push(newItem);

			$.add_vsl.click(function(){

				var listDiv = $(this).parents('tr').next().find('.detail-cont#'+detail_cont_id);
				listDiv.children(':not(#'+detail_cont_id+'_1)').remove();
				getDataWeb201BCR($(this), apdp, detail_cont_id, 'N');
				if ($(this).attr("ts")=='Y'){
					for (var i=1;i<parseInt($(this).attr("ts_seq"));i++){
						getDataWeb201BCR($(this), apdp, detail_cont_id, 'ts'+(i+1));
					}
				}

			});
			$.add_vsl.hover(function(){
				$(this).children(".tooltip").show();
			}, function(){
				$(this).children(".tooltip").hide();
			});
			$("#"+pcCalendar.id+"_"+parseInt(apdp_date_day)+"_date").append($.add_vsl);
			//html.push("<li><a href='#none'>HEUNG-A</a></li>");
			//"+pcCalendar.id+"_"+i+"_date

	}


	/*for (var i=0;i<schList.length;i++){
		if (schList[i].)
	}*/
	var grid = $("#gridList");
	grid.jqGrid('clearGridData');
	grid.jqGrid('setGridParam',{datatype:"local",data:newList}).trigger("reloadGrid");

	comLib.getScreenIetm("WEB_201_B",null, headerNameBRCallbackFs);
	comLib.getScreenIetm("WEB_201_C",null, headerNameCRCallbackFs);
	inq_ing = false;
	$("#loading-bar").hide();
}

function getDataWeb201BCR(arg, apdp, detail_cont_id, ts){
	var params={};
	params.I_AS_AGT_NO = 'KORKOR';
	params.I_AS_POL_SCH_NO = (ts=='N')?arg.attr("pol_sch_no"):arg.attr("pol_sch_no_"+ts);
	params.I_AS_POD_SCH_NO = (ts=='N')?arg.attr("pod_sch_no"):arg.attr("pod_sch_no_"+ts);
	params.I_PROGRESS_GUID = "Web201";
	params.I_REQUEST_USER_ID = "USER";
	params.I_REQUEST_IP_ADDRESS = "0.0.0.0";
	params.I_REQUEST_PROGRAM_ID = "PMG";

	var addvsl = arg;

	$.ajax({
        type : 'post',
        contentType : 'application/json',
        url : (apdp=='O')?'selectWeb201B.pcl':'selectWeb201C.pcl',
        data : JSON.stringify(params),
        dataType : 'text',
        async : false,
        error: function(xhr, status, error){
            alert("error : "+error);
        },
        success : function(data){
        	var schDetail = JSON.parse(data).data[0];
        	console.log(schDetail);

        	if (ts=='N'){
        		$('.calender-cover td').removeClass('active');
				$('.calender-cover tr td.detail-section .detail-cont').slideUp();
				addvsl.parents('.calender-cover td').addClass('active');
        	}

			var listDiv = addvsl.parents('tr').next().find('.detail-cont#'+detail_cont_id);
			if (ts!='N'){
				$.cl = listDiv.children("#"+detail_cont_id+"_1").clone();
				$.cl.attr("id", detail_cont_id+"_"+ts);
				$.cl.find("#WEB_201_B_NEW_BKG").remove();
				$.cl.find("#REM4").removeClass("hidden");
				listDiv.append($.cl);
			}

			Object.keys(schDetail).forEach(function(key){
				console.log(key+' '+schDetail[key]);
				var targetTag = listDiv.find("#"+detail_cont_id+((ts=='N')?"_1":"_"+ts)+" #"+key.toLowerCase());
				if (targetTag){
					var newValue = schDetail[key];
					if (key=='POL_ETD_TM'||key=='POD_ETA_TM'||key=='DOC_CLS_DTM'||key=='CGO_CLS_DTM'||key=='MF_EDI_CLS_DTM'||key=='CFS_CLS_DTM'||key=='VGM_CLS_DTM'){
						newValue = getDateFormat(schDetail[key], "YYYY/MM/DD HH:MI");
					}else if (key=='DDS'){
						newValue = Math.round(parseFloat(schDetail[key])*100)/100;
					}else if (key=='DELAY'){
						if (newValue == '0' || newValue == ':') listDiv.find("#"+detail_cont_id+((ts=='N')?"_1":"_"+ts)+" #span_delay").hide();
						else listDiv.find("#"+detail_cont_id+((ts=='N')?"_1":"_"+ts)+" #span_delay").show();
					}
					targetTag.text(util_nvl(newValue, ''));
				}
			});

			listDiv.find("#WEB_201_B_SCH_NOTICE").unbind('click');
			listDiv.find('#WEB_201_B_SCH_NOTICE').click(function(){
				// 2018.01.31 理쒕퀝�� 二쇱엫 �붿껌. �ㅼ�以� 議고쉶 ��, �ㅼ�以� �명떚�� 諛붾줈 �꾩슱 �� �덈룄濡�
				var varParam = {};

				varParam.reportFile="WEB_003_D";
				varParam.I_AS_CTR_CD=$("#I_AS_CTR_CD").val();
				varParam.I_AS_AGT_NO=$("#I_AS_AGT_NO").val();
				varParam.I_PROGRESS_GUID=$("#I_PROGRESS_GUID").val();
				varParam.I_REQUEST_USER_ID=$("#I_REQUEST_USER_ID").val();
				varParam.I_REQUEST_IP_ADDRESS=$("#I_REQUEST_IP_ADDRESS").val();
				varParam.I_REQUEST_PROGRAM_ID=$("#I_REQUEST_PROGRAM_ID").val();

				varParam.I_AS_VSL_CD=addvsl.attr("vsl_cd");
				varParam.I_AS_VOY_NO=addvsl.attr("voy_no");
				varParam.I_AS_BKG_NO='';
				varParam.saveFile=addvsl.attr("vsl_cd")+"_"+addvsl.attr("voy_no")+"_"+ getTodayString();
				varParam.language=$("#hidLang").val();

				comLib.clipReportOpen(varParam, varParam.reportFile);

			});

			if (ts=='N' && apdp=='O'){
				if (addvsl.attr("closed")!='OPEN') listDiv.find("#WEB_201_B_NEW_BKG").hide();
				else listDiv.find("#WEB_201_B_NEW_BKG").show();
				listDiv.find("#WEB_201_B_NEW_BKG").unbind('click');
				listDiv.find("#WEB_201_B_NEW_BKG").click(function(){
					if (addvsl.attr("closed")=='CLOSED'){
						alert(bkg_closed_msg);
						return;
					}else if (addvsl.attr("closed")=='CHECK'){
						alert(bkg_check_msg);
						return;
					}
					//alert(addvsl.attr("pol_sch_no"));
					var $form = $('<form></form>');
					$form.attr('action', 'pageLink.pcl');
					$form.attr('method', 'post');
					$form.appendTo('body');
					var html = new Array();
					html.push("<input type='hidden' value='EXP/WEB_002' name='link'>");
					html.push("<input type='hidden' name='ts' value='"+addvsl.attr("ts")+"'>");
					html.push("<input type='hidden' name='ts_seq' value='"+addvsl.attr("ts_seq")+"'>");
					html.push("<input type='hidden' name='gubun' value='"+addvsl.attr("gubun")+"'>");
					html.push("<input type='hidden' name='pol_sch_no' value='"+addvsl.attr("pol_sch_no")+"'>");
					html.push("<input type='hidden' name='pod_sch_no' value='"+addvsl.attr("pod_sch_no")+"'>");
					html.push("<input type='hidden' name='sec_seq' value='"+addvsl.attr("sec_seq")+"'>");
					html.push("<input type='hidden' name='vsl_cd' value='"+addvsl.attr("vsl_cd")+"'>");
					html.push("<input type='hidden' name='vsl_nm' value='"+addvsl.attr("vsl_nm")+"'>");
					html.push("<input type='hidden' name='voy_no' value='"+addvsl.attr("voy_no")+"'>");
					html.push("<input type='hidden' name='pol_country_cd' value='"+addvsl.attr("pol_country_cd")+"'>");
					html.push("<input type='hidden' name='pol_port_cd' value='"+addvsl.attr("pol_port_cd")+"'>");
					html.push("<input type='hidden' name='pod_country_cd' value='"+addvsl.attr("pod_country_cd")+"'>");
					html.push("<input type='hidden' name='pod_port_cd' value='"+addvsl.attr("pod_port_cd")+"'>");
					html.push("<input type='hidden' name='pol' value='"+listDiv.find("#"+detail_cont_id+"_1 #pol").text()+"'>");
					html.push("<input type='hidden' name='pod' value='"+listDiv.find("#"+detail_cont_id+"_1 #pod").text()+"'>");
					html.push("<input type='hidden' name='pol_etd_tm' value='"+listDiv.find("#"+detail_cont_id+"_1 #pol_etd_tm").text()+"'>");
					html.push("<input type='hidden' name='pod_eta_tm' value='"+listDiv.find("#"+detail_cont_id+"_1 #pod_eta_tm").text()+"'>");
					html.push("<input type='hidden' name='doc_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_1 #doc_cls_dtm").text()+"'>");
					html.push("<input type='hidden' name='cgo_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_1 #cgo_cls_dtm").text()+"'>");
					html.push("<input type='hidden' name='cfs_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_1 #cfs_cls_dtm").text()+"'>");
					html.push("<input type='hidden' name='ctr_cd' value='"+listDiv.find("#"+detail_cont_id+"_1 #ctr_cd").text()+"'>");
					html.push("<input type='hidden' name='mf_edi_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_1 #mf_edi_cls_dtm").val()+"'>");
					html.push("<input type='hidden' name='vgm_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_1 #vgm_cls_dtm").val()+"'>");
					html.push("<input type='hidden' name='call_sign_no' value='"+listDiv.find("#"+detail_cont_id+"_1 #call_sign_no").text()+"'>");
					html.push("<input type='hidden' name='mrn' value='"+listDiv.find("#"+detail_cont_id+"_1 #mrn").text()+"'>");
					html.push("<input type='hidden' name='pol_tmn' value='"+listDiv.find("#"+detail_cont_id+"_1 #pol_tmn").text()+"'>");
					html.push("<input type='hidden' name='pod_tmn' value='"+listDiv.find("#"+detail_cont_id+"_1 #pod_tmn").text()+"'>");


					if (addvsl.attr("ts")=="Y"){
						for (var i=1;i<parseInt(addvsl.attr("ts_seq"));i++){
							html.push("<input type='hidden' name='gubun' value='"+addvsl.attr("gubun"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='pol_sch_no' value='"+addvsl.attr("pol_sch_no"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='pod_sch_no' value='"+addvsl.attr("pod_sch_no"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='sec_seq' value='"+addvsl.attr("sec_seq"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='vsl_cd' value='"+addvsl.attr("vsl_cd"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='vsl_nm' value='"+addvsl.attr("vsl_nm"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='voy_no' value='"+addvsl.attr("voy_no"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='pol_country_cd' value='"+addvsl.attr("pol_country_cd"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='pol_port_cd' value='"+addvsl.attr("pol_port_cd"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='pod_country_cd' value='"+addvsl.attr("pod_country_cd"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='pod_port_cd' value='"+addvsl.attr("pod_port_cd"+"_ts"+(i+1))+"'>");
							html.push("<input type='hidden' name='pol' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #pol").text()+"'>");
							html.push("<input type='hidden' name='pod' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #pod").text()+"'>");
							html.push("<input type='hidden' name='pol_etd_tm' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #pol_etd_tm").text()+"'>");
							html.push("<input type='hidden' name='pod_eta_tm' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #pod_eta_tm").text()+"'>");
							html.push("<input type='hidden' name='doc_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #doc_cls_dtm").text()+"'>");
							html.push("<input type='hidden' name='cgo_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #cgo_cls_dtm").text()+"'>");
							html.push("<input type='hidden' name='mf_edi_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #mf_edi_cls_dtm").val()+"'>");
							html.push("<input type='hidden' name='vgm_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #vgm_cls_dtm").val()+"'>");
							html.push("<input type='hidden' name='cfs_cls_dtm' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #cfs_cls_dtm").text()+"'>");
							html.push("<input type='hidden' name='ctr_cd' value='"+listDiv.find("#"+detail_cont_id+"_1 #ctr_cd").text()+"'>");
							html.push("<input type='hidden' name='call_sign_no' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #call_sign_no").text()+"'>");
							html.push("<input type='hidden' name='mrn' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #mrn").text()+"'>");
							html.push("<input type='hidden' name='pol_tmn' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #pol_tmn").text()+"'>");
							html.push("<input type='hidden' name='pod_tmn' value='"+listDiv.find("#"+detail_cont_id+"_ts"+(i+1)+" #pod_tmn").text()+"'>");
						}

					}

					$form.append(html.join(''));
					$form.submit();
				});
			}

			listDiv.find("#"+detail_cont_id+((ts=='N')?"_1":"_"+ts)+" #vsl_nm").text(schDetail.VSL+" "+schDetail.VOY_NO);

			if (ts=='N') listDiv.slideDown();

        },
    });
}

function getTSSchSort(arr){
	var result = {};
	var arr2 = new Array();
	var arr3 = new Array();
	result.arr2 = arr2;
	result.arr3 = arr3;

	for (var i=0;i<arr.length;i++){
		if (arr[i].GUBUN=='2' && parseInt(arr[i].SEC_SEQ)==2) arr2.push(arr[i]);
		else if (arr[i].GUBUN=='2' && parseInt(arr[i].SEC_SEQ==3)) arr3.push(arr[i]);
		else continue;
	}
	if (arr2.length!=0){
		arr2.sort(function(a, b){
			var fdtm = a.POD_REVISED_APDP_DATE+a.POD_REVISED_APDP_TM;
			var sdtm = b.POD_REVISED_APDP_DATE+b.POD_REVISED_APDP_TM;
			return fdtm<sdtm?-1:fdtm>sdtm?1:0;
		});
		result.arr2 = arr2;
	}
	if (arr3.length!=0){
		arr3.sort(function(a, b){
			var fdtm = a.POD_REVISED_APDP_DATE+a.POD_REVISED_APDP_TM;
			var sdtm = b.POD_REVISED_APDP_DATE+b.POD_REVISED_APDP_TM;
			return fdtm<sdtm?-1:fdtm>sdtm?1:0;
		});
		result.arr3 = arr3;
	}

	return result;
}

function getTSSchNo(apdp_dtm, arr){
	var result = {};
	//result.POL_SCH_NO = '';
	//result.POD_SCH_NO = '';
	for (var i=0;i<arr.length;i++){
		console.log(arr[i].POL_REVISED_APDP_DATE+arr[i].POL_REVISED_APDP_TM+' '+apdp_dtm);
		if (arr[i].POL_REVISED_APDP_DATE+arr[i].POL_REVISED_APDP_TM>=apdp_dtm){
			//result.POL_SCH_NO = arr[i].POL_SCH_NO;
			//result.POD_SCH_NO = arr[i].POD_SCH_NO;
			return arr[i];
		}
	}
	return result;
}

function headerNameBRCallbackFs(rows){
	var screenId = "WEB_201_B";
	for (var i = 0; i < rows.length; i++) {
		var ob = rows[i];
		//console.log(screenId+"_"+ob.ITEM_CD+" NM : "+ob.ITEM_NM);
		$("th[id='"+screenId+"_"+ob.ITEM_CD+"']").each(function(){
			//if (ob.ITEM_NM=='') $(this).hide();
			//else $(this).text(ob.ITEM_NM);
			$(this).text(ob.ITEM_NM);
		});

		$("span[id='"+screenId+"_"+ob.ITEM_CD+"']").each(function(){
			$(this).text(ob.ITEM_NM);
		});
	}
}

function headerNameCRCallbackFs(rows){
	var screenId = "WEB_201_C";
	for (var i = 0; i < rows.length; i++) {
		var ob = rows[i];

		$("th[id='"+screenId+"_"+ob.ITEM_CD+"']").each(function(){
			$(this).text(ob.ITEM_NM);
		});

		$("span[id='"+screenId+"_"+ob.ITEM_CD+"']").each(function(){
			$(this).text(ob.ITEM_NM);
		});
	}
}

function setItemCallbackFs(rows){
	var closed1 = '';
	var closed2 = '';
	var check1 = '';
	var check2 = '';
	var open = '';

	for (var i=0;i<rows.length;i++){
		if (rows[i].KIND_CD == '08'){
			if (rows[i].ITEM_CD == 'CLOSED1' ){
				closed1 = rows[i].ITEM_NM;
			}else if (rows[i].ITEM_CD == 'CLOSED2'){
				closed2 = rows[i].ITEM_NM;
			}else if (rows[i].ITEM_CD == 'CHECK1'){
				check1 = rows[i].ITEM_NM;
			}else if (rows[i].ITEM_CD == 'CHECK2'){
				check2 = rows[i].ITEM_NM;
			}else if (rows[i].ITEM_CD == 'OPEN'){
				open = rows[i].ITEM_NM;
			}else if (rows[i].ITEM_CD == 'POL_INP'){
				$("#pol_country_plc_nm").attr("placeholder", rows[i].ITEM_NM);
			}else if (rows[i].ITEM_CD == 'POD_INP'){
				$("#pod_country_plc_nm").attr("placeholder", rows[i].ITEM_NM);
			}
		}
	}
	bkg_closed_msg = closed1+' '+closed2;
	bkg_check_msg = check1+' '+check2;
	bkg_open_msg = open;
}

function gridHeaderNameCallbackFs(rows){
	colNames = comLib.getGridHeaderNameArray(rows, colNamesItemCd);
	setGridHeader();
	resizeJqGridWidth("gridList");
}

//珥덇린 洹몃━�� �ㅻ뜑, �ㅼ젙
function setGridHeader(){
	$("#gridList").jqGrid({
		//datatype: "json",
		//data: {},
		colNames:colNames,
		colModel:colModel,
		pager: '#pager2',
		//rowNum: 10,
		//rowList: [10, 20, 30],
		//gridview: true,
		viewrecords: true,
		autowidth:false,
		multiselect:false,
		loadonce: true,
		//height:"auto",
		mtype: "POST",
		ajaxGridOptions: {
		    type : 'POST',
		    contentType : "application/json",
		    dataType : 'jsonp',
		    async : false, },
		beforeSelectRow: function(rowid, e)
			{
			    $("#gridList").jqGrid('resetSelection');
			    return(true);
			},
		loadComplete: function() {
	        var ids = $("#gridList").getDataIDs();

	        for (var i = 0; i < ids.length; i++) {
	        	$("#gridList").setRowData(ids[i], false, { height : 40 });
	        }
	    }

	});

};
/*
* @param string grid_id �ъ씠利덈� 蹂�寃쏀븷 洹몃━�쒖쓽 �꾩씠��
* @param string div_id 洹몃━�쒖쓽 �ъ씠利덉쓽 湲곗��� �쒖떆�� div �� �꾩씠��
* @param string width 洹몃━�쒖쓽 珥덇린�� width �ъ씠利�
*/
function resizeJqGridWidth(grid_id) {
	// window�� resize �대깽�몃� 諛붿씤�� �쒕떎.
	$(window).bind('resize', function() {
		var $grid = $('#' + grid_id);
		var newWidth = $grid.closest(".ui-jqgrid").parent().width();
		//console.log('newWidth : '+newWidth+' '+window.innerWidth);
		if (newWidth==0) newWidth=window.innerWidth-70;
		$grid.jqGrid("setGridWidth", newWidth, false);
		if(window.innerHeight > 700) {
			var newHeight = window.innerHeight - $(".header").outerHeight()
						- $(".footer").outerHeight() - $(".top-fixed-block").outerHeight() - 130;
			$grid.jqGrid("setGridHeight", newHeight, false);
		}

	}).trigger('resize');

}

function validate(){
	var result = true;
	$("#searchForm div[id*='cond']").each(function(index){
		/*if ($(this).find("select[name='pol_country_cd']").val()==''){
			alert("異쒕컻援��瑜� �좏깮�댁＜�몄슂.");
			result = false;
			return;
		}else if ($(this).find("select[name='pol_port_cd']").val()==''){
			alert("異쒕컻吏���쓣 �좏깮�댁＜�몄슂.");
			result = false;
			return;
		}
		if ($(this).find("select[name='pod_country_cd']").val()==''){
			alert("�꾩갑援��瑜� �좏깮�댁＜�몄슂.");
			result = false;
			return;
		}else if ($(this).find("select[name='pod_port_cd']").val()==''){
			alert("�꾩갑吏���쓣 �좏깮�댁＜�몄슂.");
			result = false;
			return;
		}*/
		if ($(this).find("#I_AS_POL_CTR").val()==''){
			//alert("異쒕컻援��瑜� �좏깮�댁＜�몄슂.");
			//comLib.messageOut(msgLib.MSG_MINUS_71,$("#WEB_201_POL").text()+' '+$("#WEB_201_POL_COUNTRY_CD").text(), "pol_country_cd");
			comLib.messageOut("3004", "", "pol_country_cd");
			result = false;
			return;
		}else if ($(this).find("#I_AS_POL_CD").val()==''){
			//alert("異쒕컻吏���쓣 �좏깮�댁＜�몄슂.");
			//comLib.messageOut(msgLib.MSG_MINUS_71,$("#WEB_201_POL").text()+' '+$("#WEB_201_POL_PORT_CD").text(), "pol_port_cd");
			comLib.messageOut("3004", "", "pol_port_cd");
			result = false;
			return;
		}
		if ($(this).find("#I_AS_POD_CTR").val()==''){
			//alert("�꾩갑援��瑜� �좏깮�댁＜�몄슂.");
			//comLib.messageOut(msgLib.MSG_MINUS_71,$("#WEB_201_POD").text()+' '+$("#WEB_201_POD_COUNTRY_CD").text(), "pod_country_cd");
			comLib.messageOut("3004", "", "pod_country_cd");
			result = false;
			return;
		}else if ($(this).find("#I_AS_POD_CD").val()==''){
			//alert("�꾩갑吏���쓣 �좏깮�댁＜�몄슂.");
			//comLib.messageOut(msgLib.MSG_MINUS_71,$("#WEB_201_POD").text()+' '+$("#WEB_201_POD_PORT_CD").text(), "pod_port_cd");
			comLib.messageOut("3004", "", "pod_port_cd");
			result = false;
			return;
		}
	});
	return result;
}

/*setCalendarPageContent($scope, year, month);
$('.table.open').removeClass('open');
$('.selected').removeClass('selected');
};*/

function setCalendarPageContent($scope, year, month) {
	var date = new Date();
	var thisYear = date.getFullYear();
	var thisMonth = date.getMonth() + 1;
	var today = date.getDate();

	if (!year) year = thisYear;
	if (!month) month = thisMonth;
	$scope.year = year;
	$scope.month = LPAD(month, '0', 2);

	var lastMonLastDay = new Date(year, month - 1, 0);
	var firstDay = new Date(year, month - 1, 1);
	var lastDay = new Date(year, month, 0);

	$scope.days = new Array(6);

	$scope.days[0] = new Array();
	$scope.days[1] = new Array();
	$scope.days[2] = new Array();
	$scope.days[3] = new Array();
	$scope.days[4] = new Array();
	$scope.days[5] = new Array();

	for (var i = 0 ; i < firstDay.getDay() ; i++) {
		var day = new Date(new Date(year, month - 1, 1).setDate(-firstDay.getDay() + 1 + i));
		$scope.days[0].push({year: day.getFullYear(), month: LPAD(String(day.getMonth() + 1), '0', 2), date: LPAD(String(day.getDate()), '0', 2), day: getDayStr(day.getDay()), dayClass: 'gray'});
	}

	for (var i = firstDay.getDay() ; i < 7 ; i++) {
		var day = new Date(new Date(year, month - 1, 1).setDate(i - firstDay.getDay() + 1));
		$scope.days[0].push({year: day.getFullYear(), month: LPAD(String(day.getMonth() + 1), '0', 2), date: LPAD(String(day.getDate()), '0', 2), day: getDayStr(day.getDay())});
	}

	for (var week = 1 ; week < $scope.days.length ; week++) {
		for (var i = 0 ; i < 7 ; i++) {
			var day = new Date(new Date(year, month - 1, 1).setDate(7 - firstDay.getDay() + 1 + ((week - 1) * 7) + i));
			var dayItem = {year: day.getFullYear(), month: LPAD(String(day.getMonth() + 1), '0', 2), date: LPAD(String(day.getDate()), '0', 2), day: getDayStr(day.getDay())};
			if (day.getMonth() + 1 != month) dayItem.dayClass = 'gray';
			$scope.days[week].push(dayItem);
		}
	}

}


function closeCalTable(e) {
var weeks = $('.week');
var days = weeks.children('div');
days.removeClass('selected');
weeks.children('.table').removeClass('open');

var evt = e || window.event;
if(evt.stopPropagation) {
    evt.stopPropagation();  // W3C �쒖�
}
else {
    evt.cancelBubble = true; // �명꽣�� �듭뒪�뚮줈�� 諛⑹떇
}
}