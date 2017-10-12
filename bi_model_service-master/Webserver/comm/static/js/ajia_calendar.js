// JavaScript Document
/**
 * 双日历插件（到天）
 */

$.fn.myCalendar = function(option) {
    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var firstDayForWeek = {
        1999 : {
            1 : '5-7'
        },
        2000 : {
            1 : '6-1'
        },
        2001 : {
            1 : '1-3'
        },
        2002 : {
            1 : '2-4'
        },
        2003 : {
            1 : '3-5'
        },
        2004 : {
            1 : '4-6'
        },
        2005 : {
            1 : '6-1'
        },
        2006 : {
            1 : '7-2'
        },
        2007 : {
            1 : '1-3'
        },
        2008 : {
            1 : '2-4'
        },
        2009 : {
            1 : '4-6'
        },
        2010 : {
            1 : '5-7'
        },
        2011 : {
            1 : '6-1'
        },
        2012 : {
            1 : '7-2'
        },
        2013 : {
            1 : '2-4'
        },
        2014 : {
            1 : '3-5'
        },
        2015 : {
            1 : '4-6'
        },
        2016 : {
            1 : '5-7'
        },
        2017 : {
            1 : '7-2'
        },
        2018 : {
            1 : '1-3'
        },
        2019 : {
            1 : '2-4'
        }
    };

    var clearFloatHtml = '<div class="b_clear"></div>';

    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj, toSplit, toSplitAgain) {

        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }

        if (toSplit) {
            if (toSplitAgain) {
                var theDate = inputDate.split(setting.dateTo);
                var startDate = theDate[0].split(setting.dateSpace);
                var endDate = theDate[1].split(setting.dateSpace);
                return [startDate, endDate];
            } else {
                return inputDate.split(setting.dateTo);
            }
        } else {
            return inputDate;
        }
    }

    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var tem = _getFormatDate(_y, _m, _d);
        var inputDate = tem + setting.dateTo + tem;
        _initdateGroup();
        return inputDate;
    }

    var _initdateGroup = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var tem = _getFormatDate(_y, _m, _d);
        var inputDate1 = tem + setting.dateTo + tem;
        //console.log("inputDate1="+inputDate1);//2015/11/02 - 2015/11/02
        var _d2 = 0;
        var _m2 = 0;
        var _y2 = 0;
        if (parseInt(_d) > 1) {
            _d2 = _d - 1;
            _m2 = _m;
            _y2 = _y;
        } else {
            _m2 = (_m > 1 ? _m - 1 : 12);
            _y2 = (_m > 1 ? _y: parseInt(_y) - 1);
            _d2 = _getMonthSumDay(_m2, _y2);
        }
        var tem2 = _getFormatDate(_y2, _m2, _d2);
        var inputDate2 = tem2 + setting.dateTo + tem2;
        //console.log("inputDate2=" + inputDate2);//2015/11/01 - 2015/11/01
        var _d3 = _getMonthSumDay(_m, _y); //本月天数,返回31、30、28、29
        var tem3_0 = _getFormatDate(_y, _m, 1);
        var tem3_1 = _getFormatDate(_y, _m, _d3);
        var inputDate3 = tem3_0 + setting.dateTo + tem3_1;
        //console.log("inputDate3=" + inputDate3);//2015/11/01 - 2015/11/30
        var _m4 = 0;
        _m4 = (_m > 1 ? _m - 1 : 12);
        var _y4 = 0;
        _y4 = (_m > 1 ? _y: parseInt(_y) - 1);
        var _d4 = _getMonthSumDay(_m4, _y4); //上月天数,返回31、30、28、29
        var tem4_0 = _getFormatDate(_y4, _m4, 1);
        var tem4_1 = _getFormatDate(_y4, _m4, _d4);
        var inputDate4 = tem4_0 + setting.dateTo + tem4_1;
        //console.log("inputDate4=" + inputDate4);//2015/11/01 - 2015/11/30
        var _m5_s = 0;
        _m5_s = ((_m - 3) + 12) % 12;
        var _y5_s = 0;
        _y5_s = (_m - 3 > 1 ? _y: parseInt(_y) - 1);
        var _m5_e = 0;
        _m5_e = ((_m - 1) + 12) % 12;
        var _y5_e = 0;
        _y5_e = (_m - 1 > 1 ? _y: parseInt(_y) - 1);
        var _d5_e = _getMonthSumDay(_m5_e, _y5_e); //当月天数,返回31、30、28、29
        var tem5_0 = _getFormatDate(_y5_s, _m5_s, 1);
        var tem5_1 = _getFormatDate(_y5_e, _m5_e, _d5_e);
        var inputDate5 = tem5_0 + setting.dateTo + tem5_1;
        $("#ad-tm1").attr("data-tm", inputDate1); //今天
        $("#ad-tm2").attr("data-tm", inputDate2); //昨天
        $("#ad-tm3").attr("data-tm", inputDate3); //本月
        $("#ad-tm4").attr("data-tm", inputDate4); //上月
        $("#ad-tm5").attr("data-tm", inputDate5); //过去三个月
        var week = new Date().getDay();
        var _d6 = _d;
        var _m6 = _m;
        var _y6 = _y;
        var _endtem6 = ""; //2015/12/24
        var _starttem6 = "";
        _d6 = _d6 - week;
        if (_d6 > 0) {
            _endtem6 = _getFormatDate(_y6, _m6, _d6);
        } else {
            _m6 = (_m6 > 1 ? _m6 - 1 : 12);
            _y6 = (_m6 != 12 ? _y6: parseInt(_y6) - 1);
            _d6 = _getMonthSumDay(_m6, _y6) + _d6; //上月天数,返回31、30、28、29
            _endtem6 = _getFormatDate(_y6, _m6, _d6);
        }
        var _d6_start = _d6 - 6; //上周开始天
        if (_d6_start > 0) {
            _starttem6 = _getFormatDate(_y6, _m6, _d6_start);
        } else {
            _m6 = (_m6 > 1 ? _m6 - 1 : 12);
            _y6 = (_m6 != 12 ? _y6: parseInt(_y6) - 1);
            _d6_start = _getMonthSumDay(_m6, _y6) + _d6_start; //上月天数,返回31、30、28、29
            _starttem6 = _getFormatDate(_y6, _m6, _d6_start);
        }
        var inputDate6 = _starttem6 + setting.dateTo + _endtem6;
        $("#ad-tm6").attr("data-tm", inputDate6); //上周
        _d6_start = _d6_start - 7; //上周开始天
        var _starttem7 = "";
        if (_d6_start > 0) {
            _starttem7 = _getFormatDate(_y6, _m6, _d6_start);
        } else {
            _m6 = (_m6 > 1 ? _m6 - 1 : 12);
            _y6 = (_m6 != 12 ? _y6: parseInt(_y6) - 1);
            _d6_start = _getMonthSumDay(_m6, _y6) + _d6_start; //上月天数,返回31、30、28、29
            _starttem7 = _getFormatDate(_y6, _m6, _d6_start);
        }
        var inputDate7 = _starttem7 + setting.dateTo + _endtem6;
        $("#ad-tm7").attr("data-tm", inputDate7); //上两周
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }

    //该月份总共的天数
    var _getMonthSumDay = function(m, y) {
        m = parseInt(m);
        y = parseInt(y);
        return (m == 2) ? ((y % 4) ? 28 : 29) : (($.inArray(m, [1, 3, 5, 7, 8, 10, 12]) >= 0) ? 31 : 30);
    }

    //计算年份每个月的开始和结束日是周几
    var _getEveryMonthStartEndWeek = function(startY) {
        for (var mTem = 2; mTem <= 12; mTem++) {
            if (firstDayForWeek[startY][mTem - 1]) {
                var prevTem = firstDayForWeek[startY][mTem - 1].split("-");
                var prevE = parseInt(prevTem[1]);
            }
            var s = (prevE + 1 <= 7) ? (prevE + 1) : 1;
            var eTem = (_getMonthSumDay(mTem, startY) - (8 - s)) % 7;
            var e = (eTem == 0) ? 7 : eTem;
            firstDayForWeek[startY][mTem] = s + "-" + e;
        }
    }

    //组装成格式化的日期形式
    var _getFormatDate = function(y, m, d) {
        var m = (parseInt(m) < 10) ? "0" + m: m;
        var d = (parseInt(d) < 10) ? "0" + d: d;
        return y + setting.dateSpace + m + setting.dateSpace + d;
    }

    //根据年月获取日历
    var _getDayHtml = function(theY, theM) {
        var startLastDay = _getMonthSumDay(theM, theY); //该月份总共的天数
        var startStr = '';
        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(theY);
        var startEveryMonthStartEndWeek = firstDayForWeek[theY][theM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
        }
        for (var i = 1; i <= startLastDay; i++) {
            startStr += '<a class="acd_default">' + i + '</a>';
        }
        return startStr;
    }

    //默认显示的日历
    var _getDefaultDayHtml = function(data, $calendarObj, $calendarStartObj, $calendarEndObj) {
        var classEx = '';
        var startY = data.startY;
        var endY = data.endY;
        var startD = data.startD
        var startM = data.startM;
        var endM = data.endM;
        var endD = data.endD
        var startLastDay = _getMonthSumDay(startM, startY); //该月份总共的天数
        var endLastDay = _getMonthSumDay(endM, endY);
        var startStr = '',
        endStr = '';

        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(startY);
        if (startY != endY) {
            _getEveryMonthStartEndWeek(endY);
        }

        var startEveryMonthStartEndWeek = firstDayForWeek[startY][startM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        var endEveryMonthStartEndWeek = firstDayForWeek[startY][endM].split("-");

        //补空
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
        }

        for (var i = 1; i <= startLastDay; i++) {
            classEx = (i == startD) ? " acd_cur": "";
            startStr += '<a class="acd_default ' + classEx + '">' + i + '</a>';
        }

        for (var ii = 1; ii < endEveryMonthStartEndWeek[0]; ii++) {
            endStr += '<a class="acd_empty"></a>';
        }

        for (var i = 1; i <= endLastDay; i++) {
            classEx = (i == endD) ? " acd_cur": "";
            endStr += '<a class="acd_default ' + classEx + '">' + i + '</a>';
        }
        $calendarStartObj.find(".ac_ym .y").html(startY);
        $calendarEndObj.find(".ac_ym .y").html(endY);
        $calendarStartObj.find(".ac_ym .m").html(startM);
        $calendarEndObj.find(".ac_ym .m").html(endM);
        $calendarStartObj.find(".ac_day").html(startStr + clearFloatHtml);
        $calendarEndObj.find(".ac_day").html(endStr + clearFloatHtml);
        //经过日期
        _hoverDay($calendarObj);

    }

    //经过日期的时间段显示效果
    var _hoverDay = function($calendarObj) {
        var startY = $calendarObj.find(".ac_start_date").find(".y").html();
        var startM = $calendarObj.find(".ac_start_date").find(".m").html();
        var endY = $calendarObj.find(".ac_end_date").find(".y").html();
        var endM = $calendarObj.find(".ac_end_date").find(".m").html();
        if (startY <= endY && startM <= endM) {
            //相同年月
            if (startY == endY && startM == endM) {
                $calendarObj.find(".acd_default").hover(function() {
                    if ($calendarObj.find(".ac_start_date .acd_cur").length > 0) {
                        if ($(this).parents(".ac_end_date").length > 0) { //在结束日期上
                            var sFlag = parseInt($calendarObj.find(".ac_start_date .acd_cur").html());
                            var eFlag = $(this).html();
                            if (eFlag > sFlag) {
                                $calendarObj.find(".ac_end_date .acd_default").each(function() {
                                    var theValue = parseInt($(this).html());
                                    if (eFlag >= theValue && theValue >= sFlag) {
                                        $(this).addClass("acd_pass");
                                    }
                                });
                                $(this).addClass("acd_pass_hover");
                            }
                        }
                    }
                },
                function() {
                    $calendarObj.find(".acd_default").removeClass("acd_pass");
                    $(this).removeClass("acd_pass_hover");
                });
            } else {
                $calendarObj.find(".acd_default").hover(function() {
                    //开始日期必须选择了才有效
                    if ($calendarObj.find(".ac_start_date .acd_cur").length > 0) {
                        //经过结束日期部分才有效
                        if ($(this).parents(".ac_end_date").length > 0) {
                            var sFlag = parseInt($calendarObj.find(".ac_start_date .acd_cur").html());
                            var eFlag = $(this).html();
                            $calendarObj.find(".ac_start_date .acd_default").each(function() {
                                var theValue = parseInt($(this).html());
                                if (sFlag < theValue) {
                                    $(this).addClass("acd_pass");
                                }
                            });
                            $calendarObj.find(".ac_end_date .acd_default").each(function() {
                                var theValue = parseInt($(this).html());
                                if (eFlag > theValue) {
                                    $(this).addClass("acd_pass");
                                }
                            });
                            $(this).addClass("acd_pass_hover");
                        }
                    }
                },
                function() {
                    $calendarObj.find(".acd_default").removeClass("acd_pass");
                    $(this).removeClass("acd_pass_hover");
                });
            }
        }
    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }
    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");
    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="ac_start_date">' + '<div class="ac_title">开始日期</div>' + '<div class="ac_main">' + '<div class="ac_month">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年<font class="m">5</font>月</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_week"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span>' + '</div>' + '<div class="ac_day"></div>' + '</div>' + '</div>' + '<div class="ac_end_date">' + '<div class="ac_title">结束日期</div>' + '<div class="ac_main">' + '<div class="ac_month">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年<font class="m">5</font>月</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_week"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span>' + '</div>' + '<div class="ac_day"></div>' + '</div>' + '</div>' + '<div class="b_clear"></div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_date");
    var $calendarEndObj = $calendarObj.find(".ac_end_date");
    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 10;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {

        var currentDateArr = _getInputDate($theObj, $calendarObj, true, true);
        var paramDate = {
            startY: currentDateArr[0][0],
            startM: _deleteZero(currentDateArr[0][1]),
            startD: _deleteZero(currentDateArr[0][2]),
            endY: currentDateArr[1][0],
            endM: _deleteZero(currentDateArr[1][1]),
            endD: _deleteZero(currentDateArr[1][2])
        };

        _getDefaultDayHtml(paramDate, $calendarObj, $calendarStartObj, $calendarEndObj);

        if (theRight !== '') {
            $calendarObj.css("left", "").css({
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css("right", "").css({
                "top": theTop,
                "left": theLeft
            }).show();
        }
        var _top = $theObj.offset().top + 37;
        var _left = $theObj.offset().left - 10;
        var _id = $theObj.attr("id").split("_data_")[1];
        $("#ajia_us_data_" + _id).css("top", _top).css("left", _left);
    });

    //月份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var curY = parseInt($(this).next().find(".y").html());
        var curM = parseInt($(this).next().find(".m").html());
        var dataY = (curM == 1) ? (curY - 1) : curY;
        var dataM = (curM == 1) ? 12 : curM - 1;
        $(this).next().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
        //经过日期
        _hoverDay($calendarObj);
    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var curY = parseInt($(this).prev().find(".y").html());
        var curM = parseInt($(this).prev().find(".m").html());
        var dataY = (curM == 12) ? (curY + 1) : curY;
        var dataM = (curM == 12) ? 1 : curM + 1;

        $(this).prev().find(".y").html(dataY).end().find(".m").html(dataM);

        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
        //经过日期
        _hoverDay($calendarObj);

    });

    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj, true);
        var d = $(this).html();
        var m = $(this).parents('.ac_main').find(".ac_month").find(".m").html();
        var y = $(this).parents('.ac_main').find(".ac_month").find(".y").html();
        var formatDate = _getFormatDate(y, m, d);

        //点击的是开始日期div
        if ($(this).parents('.ac_start_date').length > 0) {
            var newDate = formatDate + setting.dateTo + curDate[1];
            $(this).parents(".ac_start_date").data("beSelected", 1);
            $(this).parents(".ac_start_date").data("theDate", formatDate);
        } else {
            var newDate = curDate[0] + setting.dateTo + formatDate;
            $(this).parents(".ac_end_date").data("beSelected", 1);
            $(this).parents(".ac_end_date").data("theDate", formatDate);
        }

        $theObj.val(newDate);
        $(this).parent().find(".acd_default").removeClass("acd_cur");
        $(this).addClass("acd_cur");
        if (($calendarObj.find(".ac_end_date").data("beSelected") == 1)) {
            $calendarObj.hide();
            setting.onClose();
            $calendarObj.find(".ac_start_date").data("beSelected", 0).end().find(".ac_end_date").data("beSelected", 0);
        }
    });

    _toClose($theObj, $calendarObj);

};

/**
 * 单日历插件
 */

$.fn.SmpCanlendar = function(option) {

    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var firstDayForWeek;

    var clearFloatHtml = '<div class="b_clear"></div>';
    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj) {
        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }
        return inputDate;
    }
    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var inputDate = _getFormatDate(_y, _m, _d);

        return inputDate;
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }

    //该月份总共的天数
    var _getMonthSumDay = function(m, y) {
        m = parseInt(m);
        y = parseInt(y);
        return (m == 2) ? ((y % 4) ? 28 : 29) : (($.inArray(m, [1, 3, 5, 7, 8, 10, 12]) >= 0) ? 31 : 30);
    }

    //计算年份每个月的开始和结束日是周几
    var _getEveryMonthStartEndWeek = function(startY) {
        //20150807添加每年第一个月第一天和最后一天是周几的自动计算
        var mydate = new Date(startY, 0, 1);
        var firstday = mydate.getDay();
        var a;
        var b;
        switch (firstday) {
        case 0:
            a = 7;
            break;
        case 1:
            a = 1;
            break;
        case 2:
            a = 2;
            break;
        case 3:
            a = 3;
            break;
        case 4:
            a = 4;
            break;
        case 5:
            a = 5;
            break;
        case 6:
            a = 6;
            break;
        }
        var lastday = new Date(startY, 0, 31).getDay();
        switch (lastday) {
        case 0:
            b = 7;
            break;
        case 1:
            b = 1;
            break;
        case 2:
            b = 2;
            break;
        case 3:
            b = 3;
            break;
        case 4:
            b = 4;
            break;
        case 5:
            b = 5;
            break;
        case 6:
            b = 6;
            break;
        }
        eval("firstDayForWeek={" + startY + ":{1:'" + a + "-" + b + "'}}");

        for (var mTem = 2; mTem <= 12; mTem++) {
            if (firstDayForWeek[startY][mTem - 1]) {
                var prevTem = firstDayForWeek[startY][mTem - 1].split("-"); //前面补得空
                var prevE = parseInt(prevTem[1]);
            }
            var s = (prevE + 1 <= 7) ? (prevE + 1) : 1; //最初那天是周几
            var eTem = (_getMonthSumDay(mTem, startY) - (8 - s)) % 7; //月份后面补得空
            var e = (eTem == 0) ? 7 : eTem; //月底那天是周几
            firstDayForWeek[startY][mTem] = s + "-" + e;
        }
    }

    //组装成格式化的日期形式
    var _getFormatDate = function(y, m, d) {
        var m = (m < 10) ? "0" + m: m;
        var d = (d < 10) ? "0" + d: d;
        return y + setting.dateSpace + m + setting.dateSpace + d;
    }

    //根据年月获取日历
    var _getDayHtml = function(theY, theM) {
        var startLastDay = _getMonthSumDay(theM, theY); //该月份总共的天数
        var startStr = '';
        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(theY);
        var startEveryMonthStartEndWeek = firstDayForWeek[theY][theM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
        }
        for (var i = 1; i <= startLastDay; i++) {
            startStr += '<a class="acd_default">' + i + '</a>';
        }
        return startStr;

    }

    //默认显示的日历
    var _getDefaultDayHtml = function(data, $calendarObj, $calendarStartObj) {
        var classEx = '';
        var startY = data.startY;
        var startD = data.startD
        var startM = data.startM;
        var startLastDay = _getMonthSumDay(startM, startY); //该月份总共的天数
        var startStr = '';

        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(startY);
        var startEveryMonthStartEndWeek = firstDayForWeek[startY][startM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
        }

        for (var i = 1; i <= startLastDay; i++) {
            classEx = (i == startD) ? " acd_cur": "";
            startStr += '<a class="acd_default ' + classEx + '">' + i + '</a>';
        }
        $calendarStartObj.find(".ac_ym .y").html(startY);
        $calendarStartObj.find(".ac_ym .m").html(startM);
        $calendarStartObj.find(".ac_day").html(startStr + clearFloatHtml);
    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");

    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="ac_start_date">' + '<div class="ac_main">' + '<div class="ac_month">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年<font class="m">5</font>月</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_week">' + '<span>一</span>' + '<span>二</span><span>三</span>' + '<span>四</span><span>五</span><span>六</span><span>日</span>' + '</div>' + '<div class="ac_day"></div>' + '</div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_date");

    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 15;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj).split(setting.dateSpace);
        var paramDate = {
            startY: currentDateArr[0],
            startM: _deleteZero(currentDateArr[1]),
            startD: _deleteZero(currentDateArr[2])
        };
        _getDefaultDayHtml(paramDate, $calendarObj, $calendarStartObj);

        if (theRight !== '') {
            $calendarObj.css("left", "").css({
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css("right", "").css({
                "top": theTop,
                "left": theLeft
            }).show();
        }
    });

    //月份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var curY = parseInt($(this).next().find(".y").html());
        var curM = parseInt($(this).next().find(".m").html());
        var dataY = (curM == 1) ? (curY - 1) : curY;
        var dataM = (curM == 1) ? 12 : curM - 1;
        $(this).next().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var curY = parseInt($(this).prev().find(".y").html());
        var curM = parseInt($(this).prev().find(".m").html());
        var dataY = (curM == 12) ? (curY + 1) : curY;
        var dataM = (curM == 12) ? 1 : curM + 1;
        $(this).prev().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
    });

    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj);
        var d = $(this).html();
        var m = $(this).parents('.ac_main').find(".ac_month").find(".m").html();
        var y = $(this).parents('.ac_main').find(".ac_month").find(".y").html();
        var formatDate = _getFormatDate(y, m, d);

        //点击的是开始日期div
        if ($(this).parents('.ac_start_date').length > 0) {
            $(this).parents(".ac_start_date").data("beSelected", 1);
            $(this).parents(".ac_start_date").data("theDate", formatDate);
        }
        $theObj.val(formatDate); //设置输入框的显示日期
        $calendarObj.hide(); //隐藏日历
        $(this).parent().find(".acd_default").removeClass("acd_cur");
        $(this).addClass("acd_cur");
            $calendarObj.hide();
            setting.onClose();
    });
    _toClose($theObj, $calendarObj);
};

/**
 * 单日历具体到上下午插件
 */

$.fn.SmpDayAB = function(option) {

    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var firstDayForWeek;

    var clearFloatHtml = '<div class="b_clear"></div>';
    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj) {
        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }
        return inputDate;
    }

    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var inputDate = _getFormatDate(_y, _m, _d) + ' - 上午';
        return inputDate;
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }

    //该月份总共的天数
    var _getMonthSumDay = function(m, y) {
        m = parseInt(m);
        y = parseInt(y);
        return (m == 2) ? ((y % 4) ? 28 : 29) : (($.inArray(m, [1, 3, 5, 7, 8, 10, 12]) >= 0) ? 31 : 30);
    }

    //计算年份每个月的开始和结束日是周几
    var _getEveryMonthStartEndWeek = function(startY) {
        //20150807添加每年第一个月第一天和最后一天是周几的自动计算
        var mydate = new Date(startY, 0, 1);
        var firstday = mydate.getDay();
        var a;
        var b;
        switch (firstday) {
        case 0:
            a = 7;
            break;
        case 1:
            a = 1;
            break;
        case 2:
            a = 2;
            break;
        case 3:
            a = 3;
            break;
        case 4:
            a = 4;
            break;
        case 5:
            a = 5;
            break;
        case 6:
            a = 6;
            break;
        }
        var lastday = new Date(startY, 0, 31).getDay();
        switch (lastday) {
        case 0:
            b = 7;
            break;
        case 1:
            b = 1;
            break;
        case 2:
            b = 2;
            break;
        case 3:
            b = 3;
            break;
        case 4:
            b = 4;
            break;
        case 5:
            b = 5;
            break;
        case 6:
            b = 6;
            break;
        }
        eval("firstDayForWeek={" + startY + ":{1:'" + a + "-" + b + "'}}");

        for (var mTem = 2; mTem <= 12; mTem++) {
            if (firstDayForWeek[startY][mTem - 1]) {
                var prevTem = firstDayForWeek[startY][mTem - 1].split("-"); //前面补得空
                var prevE = parseInt(prevTem[1]);
            }
            var s = (prevE + 1 <= 7) ? (prevE + 1) : 1; //最初那天是周几
            var eTem = (_getMonthSumDay(mTem, startY) - (8 - s)) % 7; //月份后面补得空
            var e = (eTem == 0) ? 7 : eTem; //月底那天是周几
            firstDayForWeek[startY][mTem] = s + "-" + e;
        }
    }

    //组装成格式化的日期形式
    var _getFormatDate = function(y, m, d) {
        var m = (m < 10) ? "0" + m: m;
        var d = (d < 10) ? "0" + d: d;
        return y + setting.dateSpace + m + setting.dateSpace + d;
    }

    //根据年月获取日历
    var _getDayHtml = function(theY, theM) {
        var startLastDay = _getMonthSumDay(theM, theY); //该月份总共的天数
        var startStr = '';
        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(theY);
        var startEveryMonthStartEndWeek = firstDayForWeek[theY][theM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
        }
        for (var i = 1; i <= startLastDay; i++) {
            startStr += '<a class="acd_default">' + i + '</a>';
        }
        return startStr;

    }

    //默认显示的日历
    var _getDefaultDayHtml = function(data, $calendarObj, $calendarStartObj) {
        var classEx = '';
        var startY = data.startY;
        var startD = data.startD.split(setting.dateTo)[0];
        var startM = data.startM;
        var startLastDay = _getMonthSumDay(startM, startY); //该月份总共的天数
        var startStr = '';

        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(startY);
        var startEveryMonthStartEndWeek = firstDayForWeek[startY][startM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
        }

        for (var i = 1; i <= startLastDay; i++) {
            classEx = (i == startD) ? " acd_cur": "";
            startStr += '<a class="acd_default ' + classEx + '">' + i + '</a>';
        }
        $calendarStartObj.find(".ac_ym .y").html(startY);
        $calendarStartObj.find(".ac_ym .m").html(startM);
        $calendarStartObj.find(".ac_day").html(startStr + clearFloatHtml);
    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");

    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="ac_start_date">' + '<div class="ac_main">' + '<div class="ac_month">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年<font class="m">5</font>月</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_week"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div>' + '<div class="ac_day"></div>' + '</div>' + '<div class="ac_daytime">时间段：<span data-value="1" class="ac-tx">上午</span><span data-value="2" class="ac-tx">下午</span></div>' + '</div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        var str = inputDate.split(" - ");
        $theObj.attr("data-day", str[0]);
        var ab = str[1] == "上午" ? 1 : 2;
        $theObj.attr("data-ab", ab);

        $theObj.attr("value", inputDate);
    }
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_date");

    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 15;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj).split(setting.dateSpace);
        var paramDate = {
            startY: currentDateArr[0],
            startM: _deleteZero(currentDateArr[1]),
            startD: _deleteZero(currentDateArr[2])
        };
        _getDefaultDayHtml(paramDate, $calendarObj, $calendarStartObj);

        if (theRight !== '') {
            $calendarObj.css("left", "").css({
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css("right", "").css({
                "top": theTop,
                "left": theLeft
            }).show();
        }
        var ab = currentDateArr[2].split(" - ")[1]; //上午、下午
        if (ab == "上午") {
            $calendarObj.find(".ac_daytime .ac-tx").eq(0).addClass("ac-cur");
        } else {
            $calendarObj.find(".ac_daytime .ac-tx").eq(1).addClass("ac-cur");
        }
    });

    //月份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var curY = parseInt($(this).next().find(".y").html());
        var curM = parseInt($(this).next().find(".m").html());
        var dataY = (curM == 1) ? (curY - 1) : curY;
        var dataM = (curM == 1) ? 12 : curM - 1;
        $(this).next().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var curY = parseInt($(this).prev().find(".y").html());
        var curM = parseInt($(this).prev().find(".m").html());
        var dataY = (curM == 12) ? (curY + 1) : curY;
        var dataM = (curM == 12) ? 1 : curM + 1;
        $(this).prev().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
    });

    var formatDate = $theObj.attr("data-day");
    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj);
        var d = $(this).html();
        var m = $(this).parents('.ac_main').find(".ac_month").find(".m").html();
        var y = $(this).parents('.ac_main').find(".ac_month").find(".y").html();
        formatDate = _getFormatDate(y, m, d);

        //点击的是开始日期div
        if ($(this).parents('.ac_start_date').length > 0) {
            $(this).parents(".ac_start_date").data("beSelected", 1);
            $(this).parents(".ac_start_date").data("theDate", formatDate);
        }
        var ab = $(".ac_daytime .ac-cur").html();
        var ab_value = $(".ac_daytime .ac-cur").attr("data-value");
        $theObj.attr("data-day", formatDate);
        $theObj.attr("data-ab", ab_value);
        $theObj.val(formatDate + " - " + ab); //设置输入框的显示日期
        //$calendarObj.hide(); //隐藏日历
        $(this).parent().find(".acd_default").removeClass("acd_cur");
        $(this).addClass("acd_cur");
    });

    //选择上下午
    $calendarObj.find(".ac_daytime .ac-tx").live('click',
    function() {
        $(".ac_daytime .ac-tx").removeClass("ac-cur");
        $(this).addClass("ac-cur");
        var ab = $(".ac_daytime .ac-cur").html();
        var ab_value = $(".ac_daytime .ac-cur").attr("data-value");
        $theObj.attr("data-day", formatDate);
        $theObj.attr("data-ab", ab_value);
        $theObj.val(formatDate + " - " + ab); //设置输入框的显示日期
        $calendarObj.hide(); //隐藏日历
    });

    _toClose($theObj, $calendarObj);

};

/**
 * 双月份日历插件
 */

$.fn.monthCalendar = function(option) {

    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var clearFloatHtml = '<div class="b_clear"></div>';

    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj, toSplit, toSplitAgain) {

        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }

        if (toSplit) {
            if (toSplitAgain) {
                var theDate = inputDate.split(setting.dateTo);
                var startDate = theDate[0].split(setting.dateSpace);
                var endDate = theDate[1].split(setting.dateSpace);
                return [startDate, endDate];
            } else {
                return inputDate.split(setting.dateTo);
            }
        } else {
            return inputDate;
        }
    }

    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var inputDate = _getFormatDate(_y, _m) + setting.dateTo + _getFormatDate(_y, _m);
        return inputDate;
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }
    //组装成格式化的日期形式
    var _getFormatDate = function(y, m) {
        var m = (m < 10) ? "0" + m: m;
        return y + setting.dateSpace + m;
    }
    //经过日期的时间段显示效果
    var _hoverDay = function($calendarObj) {
        var startY = $calendarObj.find(".ac_start_month").find(".y").html();
        var startM = $calendarObj.find(".ac_month").find(".acd_cur").html();
        var endY = $calendarObj.find(".ac_end_month").find(".y").html();
        var endM = $calendarObj.find(".ac_month").find(".acd_cur").html();
        if (startY <= endY && startM <= endM) {
            //相同年月
            if (startY == endY && startM == endM) {
                $calendarObj.find(".acd_default").hover(function() {
                    if ($calendarObj.find(".ac_start_month .acd_cur").length > 0) {
                        if ($(this).parents(".ac_end_month").length > 0) { //在结束月份上
                            var sFlag = parseInt($calendarObj.find(".ac_start_month .acd_cur").html());
                            var eFlag = $(this).html();
                            if (eFlag > sFlag) {
                                $calendarObj.find(".ac_end_month .acd_default").each(function() {
                                    var theValue = parseInt($(this).html());
                                    if (eFlag >= theValue && theValue >= sFlag) {
                                        $(this).addClass("acd_pass");
                                    }
                                });

                                $(this).addClass("acd_pass_hover");
                            }
                        }
                    }
                },
                function() {
                    $calendarObj.find(".acd_default").removeClass("acd_pass");
                    $(this).removeClass("acd_pass_hover");
                });

            } else {

                $calendarObj.find(".acd_default").hover(function() {

                    //开始日期必须选择了才有效
                    if ($calendarObj.find(".ac_start_month .acd_cur").length > 0) {

                        //经过结束日期部分才有效
                        if ($(this).parents(".ac_end_month").length > 0) {
                            var sFlag = parseInt($calendarObj.find(".ac_start_month .acd_cur").html());
                            var eFlag = $(this).html();

                            $calendarObj.find(".ac_start_month .acd_default").each(function() {
                                var theValue = parseInt($(this).html());
                                if (sFlag < theValue) {
                                    $(this).addClass("acd_pass");
                                }
                            });

                            $calendarObj.find(".ac_end_month .acd_default").each(function() {
                                var theValue = parseInt($(this).html());
                                if (eFlag > theValue) {
                                    $(this).addClass("acd_pass");
                                }
                            });

                            $(this).addClass("acd_pass_hover");
                        }
                    }

                },
                function() {
                    $calendarObj.find(".acd_default").removeClass("acd_pass");
                    $(this).removeClass("acd_pass_hover");
                });

            }

        }

    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");

    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="ac_start_month">' + '<div class="ac_title">开始月份</div>' + '<div class="ac_main">' + '<div class="ac_year">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_month">' + '<a class="acd_default">1</a>' + '<a class="acd_default">2</a>' + '<a class="acd_default">3</a>' + '<a class="acd_default">4</a>' + '<a class="acd_default">5</a>' + '<a class="acd_default">6</a>' + '<a class="acd_default">7</a>' + '<a class="acd_default">8</a>' + '<a class="acd_default">9</a>' + '<a class="acd_default">10</a>' + '<a class="acd_default">11</a>' + '<a class="acd_default">12</a>' + '<div class="b_clear"></div>' + '</div>' + '</div>' + '</div>' + '<div class="ac_end_month">' + '<div class="ac_title">结束月份</div>' + '<div class="ac_main">' + '<div class="ac_year">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_month">' + '<a class="acd_default">1</a>' + '<a class="acd_default">2</a>' + '<a class="acd_default">3</a>' + '<a class="acd_default">4</a>' + '<a class="acd_default">5</a>' + '<a class="acd_default">6</a>' + '<a class="acd_default">7</a>' + '<a class="acd_default">8</a>' + '<a class="acd_default">9</a>' + '<a class="acd_default">10</a>' + '<a class="acd_default">11</a>' + '<a class="acd_default">12</a>' + '<div class="b_clear"></div>' + '</div>' + '</div>' + '</div>' + '<div class="b_clear"></div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_month");
    var $calendarEndObj = $calendarObj.find(".ac_end_month");
    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 15;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj, true, true);
        if (theRight !== '') {
            $calendarObj.css("left", "").css({
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css("right", "").css({
                "top": theTop,
                "left": theLeft
            }).show();
        }
        $calendarObj.find(".ac_start_month .y").html(currentDateArr[0][0]);
        $calendarObj.find(".ac_end_month .y").html(currentDateArr[1][0]);
        $calendarObj.find(".ac_start_month .acd_default").eq(currentDateArr[0][1] - 1).addClass("acd_cur");
        $calendarObj.find(".ac_end_month .acd_default").eq(currentDateArr[1][1] - 1).addClass("acd_cur");
    });

    //年份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var curY = parseInt($(this).next().find(".y").html());
        curY = curY - 1;
        $(this).next().find(".y").html(curY);
        //经过日期
        _hoverDay($calendarObj);

    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var curY = parseInt($(this).prev().find(".y").html());
        curY = curY + 1;
        $(this).prev().find(".y").html(curY);
        //经过日期
        _hoverDay($calendarObj);

    });

    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj, true);
        var m = $(this).html();
        var y = $(this).parents('.ac_main').find(".ac_year").find(".y").html();
        var formatDate = _getFormatDate(y, m);

        //点击的是开始日期div
        if ($(this).parents('.ac_start_month').length > 0) {
            var newDate = formatDate + setting.dateTo + curDate[1];
            $(this).parents(".ac_start_month").data("beSelected", 1);
            $(this).parents(".ac_start_month").data("theDate", formatDate);

        } else {
            var newDate = curDate[0] + setting.dateTo + formatDate;
            $(this).parents(".ac_end_month").data("beSelected", 1);
            $(this).parents(".ac_end_month").data("theDate", formatDate);
        }

        $theObj.val(newDate);

        $(this).parent().find(".acd_default").removeClass("acd_cur");
        $(this).addClass("acd_cur");

        if (($calendarObj.find(".ac_end_month").data("beSelected") == 1)) {
            $calendarObj.hide();
            setting.onClose();
            $calendarObj.find(".ac_start_month").data("beSelected", 0).end().find(".ac_end_month").data("beSelected", 0);
        }
    });

    _toClose($theObj, $calendarObj);

};

/**
 * 单月份日历插件
 */

$.fn.oneMonth = function(option) {
    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var clearFloatHtml = '<div class="b_clear"></div>';

    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj) {
        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }
        return inputDate;
    }

    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var inputDate = _getFormatDate(_y, _m);
        return inputDate;
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }
    //组装成格式化的日期形式
    var _getFormatDate = function(y, m) {
        var m = (m < 10) ? "0" + m: m;
        return y + setting.dateSpace + m;
    }

    //组装成格式化的日期形式
    var _getFormatDateLab = function(y, m, d) {
        var m = (parseInt(m) < 10) ? "0" + m: m;
        var d = (parseInt(d) < 10) ? "0" + d: d;
        return y + setting.dateSpace + m + setting.dateSpace + d;
    }
    //经过日期的时间段显示效果
    var _hoverDay = function($calendarObj) {
        var startY = $calendarObj.find(".ac_start_month").find(".y").html();
        var startM = $calendarObj.find(".ac_month").find(".acd_cur").html();
        $calendarObj.find(".acd_default").hover(function() {
            $(this).addClass("acd_pass_hover");
        });

    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var showDateLabe = function(m, y) {
        var myDate = new Date();
        var _curMoth = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var _m = parseInt(m);
        var _y = parseInt(y);
        if (_m != _curMoth) {
            _d = _getMonthSumDay(_m, _y);
        }
        var _temStar = _getFormatDateLab(_y, _m, '1');
        var _temEnd = _getFormatDateLab(_y, _m, _d);
        var _lab5Date = _temStar + setting.dateTo + _temEnd;
       // $("#js_date5_lab").html(_lab5Date);
    }

    //该月份总共的天数
    var _getMonthSumDay = function(m, y) {
        m = parseInt(m);
        y = parseInt(y);
        return (m == 2) ? ((y % 4) ? 28 : 29) : (($.inArray(m, [1, 3, 5, 7, 8, 10, 12]) >= 0) ? 31 : 30);
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");

    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="ac_start_month">' + '<div class="ac_main">' + '<div class="ac_year">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_month">' + '<a class="acd_default">1月</a>' + '<a class="acd_default">2月</a>' + '<a class="acd_default">3月</a>' + '<a class="acd_default">4月</a>' + '<a class="acd_default">5月</a>' + '<a class="acd_default">6月</a>' + '<a class="acd_default">7月</a>' + '<a class="acd_default">8月</a>' + '<a class="acd_default">9月</a>' + '<a class="acd_default">10月</a>' + '<a class="acd_default">11月</a>' + '<a class="acd_default">12月</a>' + '<div class="b_clear"></div>' + '</div>' + '</div>' + '</div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var _moth_year = _initdate().split("/");
    showDateLabe(_moth_year[1], _moth_year[0]);
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_month");
    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 12;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj).split("/");
        if (theRight !== '') {
            $calendarObj.css({
                "left": "",
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css({
                "right": "",
                "top": theTop,
                "left": theLeft
            }).show();
        }
        $calendarObj.find(".ac_ym .y").html(currentDateArr[0]);
        $calendarObj.find(".acd_default").eq(currentDateArr[1] - 1).addClass("acd_cur");
    });

    //年份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var curY = parseInt($(this).next().find(".y").html());
        curY = curY - 1;
        $(this).next().find(".y").html(curY);
        //经过日期
        _hoverDay($calendarObj);

    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var curY = parseInt($(this).prev().find(".y").html());
        curY = curY + 1;
        $(this).prev().find(".y").html(curY);
        //经过日期
        _hoverDay($calendarObj);

    });

    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj);
        var m = $(this).html().replace("月", '');
        var y = $(this).parents('.ac_main').find(".ac_year").find(".y").html();
        var formatDate = _getFormatDate(y, m);
        $theObj.val(formatDate);
        $(this).parent().find(".acd_default").removeClass("acd_cur");
        $(this).addClass("acd_cur");
        showDateLabe(m, y);
        $calendarObj.hide();
        setting.onClose();
    });
    _toClose($theObj, $calendarObj);

};

/**
 * 单月份天日历插件
 */

$.fn.oneMonthDay = function(option) {
    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var clearFloatHtml = '<div class="b_clear"></div>';

    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj) {
        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }
        return inputDate;
    }

    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth())+1; //获取上月月份(0-11,0代表1月)
        var inputDate = _getFormatDate(_y, _m);
        return inputDate;
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }
    //组装成格式化的日期形式
    var _getFormatDate = function(y, m) {
        var m = (m < 10) ? "0" + m: m;
        return y + setting.dateSpace + m;
    }

    //组装成格式化的日期形式
    var _getFormatDateLab = function(y, m, d) {
        var m = (parseInt(m) < 10) ? "0" + m: m;
        var d = (parseInt(d) < 10) ? "0" + d: d;
        return y + setting.dateSpace + m + setting.dateSpace + d;
    }
    //经过日期的时间段显示效果
    var _hoverDay = function($calendarObj) {
        var startY = $calendarObj.find(".ac_start_month").find(".y").html();
        var startM = $calendarObj.find(".ac_month").find(".acd_cur").html();
        $calendarObj.find(".acd_default").hover(function() {
            $(this).addClass("acd_pass_hover");
        });

    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var showDateLabe = function(m, y) {
        var myDate = new Date();
        var _curYear = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _curMoth = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var _m = parseInt(m);
        var _y = parseInt(y);
        if(_curYear!=_y){
            _d = _getMonthSumDay(_m, _y);
        }else{
            if (_m != _curMoth) {
                _d = _getMonthSumDay(_m, _y);
            }else{
                if (_d > 1){//今天不是1号
                    _d = _d - 1;
                }else{//今天是1号
                    if(_m==1){//今天是一月1号
                        _y = _y - 1;
                        _m = 12;
                    }else{//今天是2月1号
                        _m = _m -1;
                    }
                    _d = _getMonthSumDay(_m, _y);
                }
            } 
        }
        
        var _temStar = _getFormatDateLab(_y, _m, '1');
        var _temEnd = _getFormatDateLab(_y, _m, _d);
        var _lab5Date = _temStar + setting.dateTo + _temEnd;
        //$("#js_date5_lab").html(_lab5Date);
    }

    //该月份总共的天数
    var _getMonthSumDay = function(m, y) {
        m = parseInt(m);
        y = parseInt(y);
        return (m == 2) ? ((y % 4) ? 28 : 29) : (($.inArray(m, [1, 3, 5, 7, 8, 10, 12]) >= 0) ? 31 : 30);
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");

    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="ac_start_month">' + '<div class="ac_main">' + '<div class="ac_year">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_month">' + '<a class="acd_default">1月</a>' + '<a class="acd_default">2月</a>' + '<a class="acd_default">3月</a>' + '<a class="acd_default">4月</a>' + '<a class="acd_default">5月</a>' + '<a class="acd_default">6月</a>' + '<a class="acd_default">7月</a>' + '<a class="acd_default">8月</a>' + '<a class="acd_default">9月</a>' + '<a class="acd_default">10月</a>' + '<a class="acd_default">11月</a>' + '<a class="acd_default">12月</a>' + '<div class="b_clear"></div>' + '</div>' + '</div>' + '</div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var _moth_year = _initdate().split("/");
    showDateLabe(_moth_year[1], _moth_year[0]);
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_month");
    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 12;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj).split("/");
        if (theRight !== '') {
            $calendarObj.css({
                "left": "",
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css({
                "right": "",
                "top": theTop,
                "left": theLeft
            }).show();
        }
        $calendarObj.find(".ac_ym .y").html(currentDateArr[0]);
        $calendarObj.find(".acd_default").eq(currentDateArr[1] - 1).addClass("acd_cur");
    });

    //年份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var curY = parseInt($(this).next().find(".y").html());
        curY = curY - 1;
        $(this).next().find(".y").html(curY);
        //经过日期
        _hoverDay($calendarObj);
    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var curY = parseInt($(this).prev().find(".y").html());
        curY = curY + 1;
        $(this).prev().find(".y").html(curY);
        //经过日期
        _hoverDay($calendarObj);

    });

    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj);
        var m = $(this).html().replace("月", '');
        var y = $(this).parents('.ac_main').find(".ac_year").find(".y").html();
        var formatDate = _getFormatDate(y, m);
        $theObj.val(formatDate);
        $(this).parent().find(".acd_default").removeClass("acd_cur");
        $(this).addClass("acd_cur");
        showDateLabe(m, y);
        $calendarObj.hide();
        setting.onClose();
    });
    _toClose($theObj, $calendarObj);

};

/**
 * 双年份日历插件
 */

$.fn.yearCalendar = function(option) {

    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };
    var clearFloatHtml = '<div class="b_clear"></div>';
    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj, toSplit, toSplitAgain) {

        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }

        if (toSplit) {
            if (toSplitAgain) {
                var theDate = inputDate.split(setting.dateTo);
                var startDate = theDate[0];
                var endDate = theDate[1];
                return [startDate, endDate];
            } else {
                return inputDate.split(setting.dateTo);
            }
        } else {
            return inputDate;
        }
    }

    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var inputDate = _y + setting.dateTo + _y;
        return inputDate;
    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");
    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="start_year">' + '<div class="ac_title">开始年份</div>' + '<div class="ac_main">' + '<div class="ac_year">' + '<a href="javascript:;" class="acm_prev"></a>' + '<ul class="acstart_year">' + '<li><span class="ac_ym"><font class="y">2013</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2014</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2015</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2016</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2017</font>年</span></li>' + '</ul>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '</div>' + '</div>' + '<div class="end_year">' + '<div class="ac_title">结束年份</div>' + '<div class="ac_main">' + '<div class="ac_year">' + '<a href="javascript:;" class="acm_prev"></a>' + '<ul class="acend_year">' + '<li><span class="ac_ym"><font class="y">2013</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2014</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2015</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2016</font>年</span></li>' + '<li><span class="ac_ym"><font class="y">2017</font>年</span></li>' + '</ul>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '</div>' + '</div>' + '<div class="b_clear"></div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".acstart_year");
    var $calendarEndObj = $calendarObj.find(".acend_year");
    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 15;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj, true, true);
        if (theRight !== '') {
            $calendarObj.css("left", "").css({
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css("right", "").css({
                "top": theTop,
                "left": theLeft
            }).show();
        }
        var start = parseInt(currentDateArr[0]);
        var end = parseInt(currentDateArr[1]);
        $calendarObj.find(".acstart_year li").removeClass("act").eq(0).addClass("act");
        $calendarObj.find(".acend_year li").removeClass("act").eq(0).addClass("act");
        for (var i = 0; i < 5; i++) {
            $calendarObj.find(".acstart_year .y").eq(i).html(start);
            $calendarObj.find(".acend_year .y").eq(i).html(end);
            start = start + 1;
            end = end + 1;
        }
    });

    //年份切换
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        for (var i = 0; i < 5; i++) {
            var curY = parseInt($(this).next().find(".y").eq(i).html());
            curY = curY - 1;
            $(this).next().find(".y").eq(i).html(curY);
            $(this).next().find(".act").removeClass("act");
        }
    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        for (var i = 0; i < 5; i++) {
            var curY = parseInt($(this).prev().find(".y").eq(i).html());
            curY = curY + 1;
            $(this).prev().find(".y").eq(i).html(curY);
            $(this).prev().find(".act").removeClass("act");

        }
    });

    //日期点击
    $calendarObj.find(".ac_ym").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj, true);
        var y = $(this).find(".y").html();
        //点击的是开始日期div
        if ($(this).parents('.acstart_year').length > 0) {
            var newDate = y + setting.dateTo + curDate[1];
            $(this).parents(".acstart_year").data("beSelected", 1);
            $(this).parents(".acstart_year").data("theDate", y);
        } else {
            var newDate = curDate[0] + setting.dateTo + y;
            $(this).parents(".acend_year").data("beSelected", 1);
            $(this).parents(".acend_year").data("theDate", y);
        }

        $theObj.val(newDate);
        $(this).parent().parent().find(".act").removeClass("act");
        $(this).parent().addClass("act");
        if (($calendarObj.find(".acend_year").data("beSelected") == 1)) {
            $calendarObj.hide();
            setting.onClose();
            $calendarObj.find(".acstart_year").data("beSelected", 0).end().find(".acend_year").data("beSelected", 0);
        }
    });
    _toClose($theObj, $calendarObj);
};

/**
 * 单周插件
 */

$.fn.SmpWeek = function(option) {
    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var firstDayForWeek;

    var clearFloatHtml = '<div class="b_clear"></div>';
    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj) {
        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }
        return inputDate;
    }
    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var inputDate = _getFormatDate(_y, _m, _d) + setting.dateTo + _getFormatDate(_y, _m, _d);
        return inputDate;
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }

    //该月份总共的天数
    var _getMonthSumDay = function(m, y) {
        m = parseInt(m);
        y = parseInt(y);
        return (m == 2) ? ((y % 4) ? 28 : 29) : (($.inArray(m, [1, 3, 5, 7, 8, 10, 12]) >= 0) ? 31 : 30);
    }

    //计算年份每个月的开始和结束日是周几
    var _getEveryMonthStartEndWeek = function(startY) {
        //20150807添加每年第一个月第一天和最后一天是周几的自动计算
        var mydate = new Date(startY, 0, 1);
        var firstday = mydate.getDay();
        var a;
        var b;
        switch (firstday) {
        case 0:
            a = 7;
            break;
        case 1:
            a = 1;
            break;
        case 2:
            a = 2;
            break;
        case 3:
            a = 3;
            break;
        case 4:
            a = 4;
            break;
        case 5:
            a = 5;
            break;
        case 6:
            a = 6;
            break;
        }
        var lastday = new Date(startY, 0, 31).getDay();
        switch (lastday) {
        case 0:
            b = 7;
            break;
        case 1:
            b = 1;
            break;
        case 2:
            b = 2;
            break;
        case 3:
            b = 3;
            break;
        case 4:
            b = 4;
            break;
        case 5:
            b = 5;
            break;
        case 6:
            b = 6;
            break;
        }
        eval("firstDayForWeek={" + startY + ":{1:'" + a + "-" + b + "'}}");

        for (var mTem = 2; mTem <= 12; mTem++) {
            if (firstDayForWeek[startY][mTem - 1]) {
                var prevTem = firstDayForWeek[startY][mTem - 1].split("-"); //前面补得空
                var prevE = parseInt(prevTem[1]);
            }
            var s = (prevE + 1 <= 7) ? (prevE + 1) : 1; //最初那天是周几
            var eTem = (_getMonthSumDay(mTem, startY) - (8 - s)) % 7; //月份后面补得空
            var e = (eTem == 0) ? 7 : eTem; //月底那天是周几
            firstDayForWeek[startY][mTem] = s + "-" + e;
        }
    }

    //组装成格式化的日期形式
    var _getFormatDate = function(y, m, d) {
        var m = (m < 10) ? "0" + m: m;
        var d = (d < 10) ? "0" + d: d;
        return y + setting.dateSpace + m + setting.dateSpace + d;
    }

    //根据年月获取日历
    var _getDayHtml = function(theY, theM) {
        var startLastDay = _getMonthSumDay(theM, theY); //该月份总共的天数
        var startStr = '';
        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(theY);
        var startEveryMonthStartEndWeek = firstDayForWeek[theY][theM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        var week_num = 0;
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
            week_num++;
        }
        for (var i = 1; i <= startLastDay; i++) {
            var tmp = parseInt(week_num / 7);
            startStr += '<a class="acd_default"  data-week="' + tmp + '">' + i + '</a>';
            week_num++;
        }
        return startStr;

    }

    //默认显示的日历
    var _getDefaultDayHtml = function(data, $calendarObj, $calendarStartObj) {
        var classEx = '';
        var startY = data.startY;
        var startD = data.startD
        var startM = data.startM;
        var startLastDay = _getMonthSumDay(startM, startY); //该月份总共的天数
        var startStr = '';

        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(startY);
        var startEveryMonthStartEndWeek = firstDayForWeek[startY][startM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        var week_num = 0;
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
            week_num++;
        }

        for (var i = 1; i <= startLastDay; i++) {
            var tmp = parseInt(week_num / 7);
            classEx = (i == startD) ? " acd_cur": "";
            startStr += '<a class="acd_default ' + classEx + '" data-week="' + tmp + '">' + i + '</a>';
            week_num++;
        }
        $calendarStartObj.find(".ac_ym .y").html(startY);
        $calendarStartObj.find(".ac_ym .m").html(startM);
        $calendarStartObj.find(".ac_day").html(startStr + clearFloatHtml);
    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");

    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' + '<div class="ac_start_date">' + '<div class="ac_main">' + '<div class="ac_month">' + '<a href="javascript:;" class="acm_prev"></a>' + '<span class="ac_ym"><font class="y">2015</font>年<font class="m">5</font>月</span>' + '<a href="javascript:;" class="acm_next"></a>' + '</div>' + '<div class="ac_week">' + '<span>一</span>' + '<span>二</span>' + '<span>三</span>' + '<span>四</span>' + '<span>五</span>' + '<span>六</span>' + '<span>日</span>' + '</div>' + '<div class="ac_day"></div>' + '</div>' + '</div>' + '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_date");
    var _week = 0;
    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 15;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj).split(setting.dateTo)[1].split(setting.dateSpace);
        var paramDate = {
            startY: currentDateArr[0],
            startM: _deleteZero(currentDateArr[1]),
            startD: _deleteZero(currentDateArr[2])
        };
        _getDefaultDayHtml(paramDate, $calendarObj, $calendarStartObj);
        _week = $calendarObj.find(".acd_cur").attr("data-week");
        if (theRight !== '') {
            $calendarObj.css({
                "left": "",
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css({
                "right": "",
                "top": theTop,
                "left": theLeft
            }).show();
        }
        $calendarObj.find(".acd_default[data-week='" + _week + "']").each(function() {
            $(this).addClass("acd_cur");
        })
    });

    //月份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var curY = parseInt($(this).next().find(".y").html());
        var curM = parseInt($(this).next().find(".m").html());
        var dataY = (curM == 1) ? (curY - 1) : curY;
        var dataM = (curM == 1) ? 12 : curM - 1;
        $(this).next().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var curY = parseInt($(this).prev().find(".y").html());
        var curM = parseInt($(this).prev().find(".m").html());
        var dataY = (curM == 12) ? (curY + 1) : curY;
        var dataM = (curM == 12) ? 1 : curM + 1;
        $(this).prev().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
    });

    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        _week = $(this).attr("data-week");
        var _d1 = $calendarObj.find(".acd_default[data-week='" + _week + "']:first").html();
        var _d2 = $calendarObj.find(".acd_default[data-week='" + _week + "']:last").html();
        var _m = $(this).parents('.ac_main').find(".ac_month").find(".m").html();
        var _y = $(this).parents('.ac_main').find(".ac_month").find(".y").html();
        var formatDate = _getFormatDate(_y, _m, _d1) + setting.dateTo + _getFormatDate(_y, _m, _d2);
        $theObj.val(formatDate); //设置输入框的显示日期
        $calendarObj.hide(); //隐藏日历
    });
    _toClose($theObj, $calendarObj);

};


/**
 * 双周插件
 */

$.fn.TwoWeek = function(option) {
    var defaultOption = {
        'dateSpace': '/',
        'dateTo': ' - ',
        'positionT': '',
        //自定义日历绝对值top值
        'positionL': '',
        //自定义日历绝对值左值
        'positionR': '',
        //自定义日历绝对值右值
        'iconPath': '/img/icon/u474.png',
        'onClose': function() {},
        'onTip': function(tip) {
            showWarnTipDiv(tip);
        }
    };

    var firstDayForWeek = {
        1999 : {
            1 : '5-7'
        },
        2000 : {
            1 : '6-1'
        },
        2001 : {
            1 : '1-3'
        },
        2002 : {
            1 : '2-4'
        },
        2003 : {
            1 : '3-5'
        },
        2004 : {
            1 : '4-6'
        },
        2005 : {
            1 : '6-1'
        },
        2006 : {
            1 : '7-2'
        },
        2007 : {
            1 : '1-3'
        },
        2008 : {
            1 : '2-4'
        },
        2009 : {
            1 : '4-6'
        },
        2010 : {
            1 : '5-7'
        },
        2011 : {
            1 : '6-1'
        },
        2012 : {
            1 : '7-2'
        },
        2013 : {
            1 : '2-4'
        },
        2014 : {
            1 : '3-5'
        },
        2015 : {
            1 : '4-6'
        },
        2016 : {
            1 : '5-7'
        },
        2017 : {
            1 : '7-2'
        },
        2018 : {
            1 : '1-3'
        },
        2019 : {
            1 : '2-4'
        }
    };

    var clearFloatHtml = '<div class="b_clear"></div>';

    //获取当前的选择日期
    var _getInputDate = function($theObj, $calendarObj, toSplit, toSplitAgain) {

        //触发器不存在日期值，则默认取当前日期
        if ($theObj.val() != '') {
            var inputDate = $theObj.val();
        } else {
            var inputDate = _initdate();
        }

        if (toSplit) {
            if (toSplitAgain) {
                var theDate = inputDate.split(setting.dateTo);
                var startDate = theDate[0].split(setting.dateSpace);
                var endDate = theDate[1].split(setting.dateSpace);
                return [startDate, endDate];
            } else {
                return inputDate.split(setting.dateTo);
            }
        } else {
            return inputDate;
        }
    }

    var _initdate = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        switch(myDate.getDay()){
            case 0:
                week=0;//"星期日"
                break;
            case 1:
                week=1;//"星期一"
                break;
            case 2:
                week=2;//"星期二"
                break;
            case 3:
                week=3;//"星期三"
                break;
            case 4:
                week=4;//"星期四"
                break;
            case 5:
                week=5;//"星期五"
                break;
            case 6:
                week=6;//"星期六"
                break;
        }
        var temstart='';
        var temend='';
        if(week!=1){//今天不是周一
            var s_m =  _d > week ? _m : parseInt(_m) - 1 >0 ? parseInt(_m) - 1 : 12 ;
            var s_y = (s_m != 12 ? _y: parseInt(_y) - 1);
            var s_d = (_d > week ? (_d-week+1) : (_getMonthSumDay(s_m, s_y)-(7-_d)));
            temstart = _getFormatDate(s_y, s_m, s_d);
           
            var t_m = _d+(7-week)<_getMonthSumDay(_m, _y)? _m : parseInt(_m)+1;
            var e_m = t_m>12 ? 1 : t_m;
            var e_y = parseInt(t_m)>12?parseInt(_y) + 1:_y;
            var e_d = t_m== _m ? _d+(7-week):7-week;
            temend = _getFormatDate(e_y, e_m, e_d);
        }else{//今天是周一
            temstart = _getFormatDate(_y, _m, _d);
            var t_m = _d + 6 <_getMonthSumDay(_m, _y)? _m : parseInt(_m)+1;
            var e_m = t_m>12 ? 1 : t_m;
            var e_y = parseInt(t_m)>12?parseInt(_y) + 1:_y;
            var e_d = t_m == _m ? _d + 6 : 7- (_getMonthSumDay(_m, _y)-_d);
            temend = _getFormatDate(e_y, e_m, e_d);
            temend = _getFormatDate(_y, _m, _d);
        }
        var inputDate = temstart + setting.dateTo + temend;
        _initdateGroup();
        return inputDate;
    }

    var _initdateGroup = function() {
        var myDate = new Date();
        var _y = myDate.getFullYear(); //获取完整的年份(4位,1970-????)
        var _m = parseInt(myDate.getMonth()) + 1; //获取当前月份(0-11,0代表1月)
        var _d = myDate.getDate(); //获取当前日(1-31)
        var tem = _getFormatDate(_y, _m, _d);
        var inputDate1 = tem + setting.dateTo + tem;
        //console.log("inputDate1="+inputDate1);//2015/11/02 - 2015/11/02
        var _d2 = 0;
        var _m2 = 0;
        var _y2 = 0;
        if (parseInt(_d) > 1) {
            _d2 = _d - 1;
            _m2 = _m;
            _y2 = _y;
        } else {
            _m2 = (_m > 1 ? _m - 1 : 12);
            _y2 = (_m > 1 ? _y: parseInt(_y) - 1);
            _d2 = _getMonthSumDay(_m2, _y2);
        }
        var tem2 = _getFormatDate(_y2, _m2, _d2);
        var inputDate2 = tem2 + setting.dateTo + tem2;
        //console.log("inputDate2=" + inputDate2);//2015/11/01 - 2015/11/01
        var _d3 = _getMonthSumDay(_m, _y); //本月天数,返回31、30、28、29
        var tem3_0 = _getFormatDate(_y, _m, 1);
        var tem3_1 = _getFormatDate(_y, _m, _d3);
        var inputDate3 = tem3_0 + setting.dateTo + tem3_1;
        //console.log("inputDate3=" + inputDate3);//2015/11/01 - 2015/11/30
        var _m4 = 0;
        _m4 = (_m > 1 ? _m - 1 : 12);
        var _y4 = 0;
        _y4 = (_m > 1 ? _y: parseInt(_y) - 1);
        var _d4 = _getMonthSumDay(_m4, _y4); //上月天数,返回31、30、28、29
        var tem4_0 = _getFormatDate(_y4, _m4, 1);
        var tem4_1 = _getFormatDate(_y4, _m4, _d4);
        var inputDate4 = tem4_0 + setting.dateTo + tem4_1;
        //console.log("inputDate4=" + inputDate4);//2015/11/01 - 2015/11/30
        var _m5_s = 0;
        _m5_s = ((_m - 3) + 12) % 12;
        var _y5_s = 0;
        _y5_s = (_m - 3 > 1 ? _y: parseInt(_y) - 1);
        var _m5_e = 0;
        _m5_e = ((_m - 1) + 12) % 12;
        var _y5_e = 0;
        _y5_e = (_m - 1 > 1 ? _y: parseInt(_y) - 1);
        var _d5_e = _getMonthSumDay(_m5_e, _y5_e); //当月天数,返回31、30、28、29
        var tem5_0 = _getFormatDate(_y5_s, _m5_s, 1);
        var tem5_1 = _getFormatDate(_y5_e, _m5_e, _d5_e);
        var inputDate5 = tem5_0 + setting.dateTo + tem5_1;
        $("#ad-tm1").attr("data-tm", inputDate1); //今天
        $("#ad-tm2").attr("data-tm", inputDate2); //昨天
        $("#ad-tm3").attr("data-tm", inputDate3); //本月
        $("#ad-tm4").attr("data-tm", inputDate4); //上月
        $("#ad-tm5").attr("data-tm", inputDate5); //过去三个月
        var week = new Date().getDay();
        var _d6 = _d;
        var _m6 = _m;
        var _y6 = _y;
        var _endtem6 = ""; //2015/12/24
        var _starttem6 = "";
        _d6 = _d6 - week;
        if (_d6 > 0) {
            _endtem6 = _getFormatDate(_y6, _m6, _d6);
        } else {
            _m6 = (_m6 > 1 ? _m6 - 1 : 12);
            _y6 = (_m6 != 12 ? _y6: parseInt(_y6) - 1);
            _d6 = _getMonthSumDay(_m6, _y6) + _d6; //上月天数,返回31、30、28、29
            _endtem6 = _getFormatDate(_y6, _m6, _d6);
        }
        var _d6_start = _d6 - 6; //上周开始天
        if (_d6_start > 0) {
            _starttem6 = _getFormatDate(_y6, _m6, _d6_start);
        } else {
            _m6 = (_m6 > 1 ? _m6 - 1 : 12);
            _y6 = (_m6 != 12 ? _y6: parseInt(_y6) - 1);
            _d6_start = _getMonthSumDay(_m6, _y6) + _d6_start; //上月天数,返回31、30、28、29
            _starttem6 = _getFormatDate(_y6, _m6, _d6_start);
        }
        var inputDate6 = _starttem6 + setting.dateTo + _endtem6;
        $("#ad-tm6").attr("data-tm", inputDate6); //上周
        _d6_start = _d6_start - 7; //上周开始天
        var _starttem7 = "";
        if (_d6_start > 0) {
            _starttem7 = _getFormatDate(_y6, _m6, _d6_start);
        } else {
            _m6 = (_m6 > 1 ? _m6 - 1 : 12);
            _y6 = (_m6 != 12 ? _y6: parseInt(_y6) - 1);
            _d6_start = _getMonthSumDay(_m6, _y6) + _d6_start; //上月天数,返回31、30、28、29
            _starttem7 = _getFormatDate(_y6, _m6, _d6_start);
        }
        var inputDate7 = _starttem7 + setting.dateTo + _endtem6;
        $("#ad-tm7").attr("data-tm", inputDate7); //上两周
    }

    //去除月份或日的0格式
    var _deleteZero = function(data) {
        if (data.indexOf("0") == 0) {
            return data.replace("0", "");
        } else {
            return data;
        }
    }

    //该月份总共的天数
    var _getMonthSumDay = function(m, y) {
        m = parseInt(m);
        y = parseInt(y);
        return (m == 2) ? ((y % 4) ? 28 : 29) : (($.inArray(m, [1, 3, 5, 7, 8, 10, 12]) >= 0) ? 31 : 30);
    }

    //计算年份每个月的开始和结束日是周几
    var _getEveryMonthStartEndWeek = function(startY) {
        for (var mTem = 2; mTem <= 12; mTem++) {
            if (firstDayForWeek[startY][mTem - 1]) {
                var prevTem = firstDayForWeek[startY][mTem - 1].split("-"); //前面补得空
                var prevE = parseInt(prevTem[1]);
            }
            var s = (prevE + 1 <= 7) ? (prevE + 1) : 1; //最初那天是周几
            var eTem = (_getMonthSumDay(mTem, startY) - (8 - s)) % 7; //月份后面补得空
            var e = (eTem == 0) ? 7 : eTem; //月底那天是周几
            firstDayForWeek[startY][mTem] = s + "-" + e;
        }
    }

    //组装成格式化的日期形式
    var _getFormatDate = function(y, m, d) {
        var m = (m < 10) ? "0" + m: m;
        var d = (d < 10) ? "0" + d: d;
        return y + setting.dateSpace + m + setting.dateSpace + d;
    }

    
    //根据年月获取日历
    var _getDayHtml = function(theY, theM, week_num) {
        var startLastDay = _getMonthSumDay(theM, theY); //该月份总共的天数
        var startStr = '';
        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(theY);
        var startEveryMonthStartEndWeek = firstDayForWeek[theY][theM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        //补空
        var week_tmp = week_num;
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
            week_tmp++;
        }
        for (var i = 1; i <= startLastDay; i++) {
            var tmp = parseInt((week_tmp-week_num) / 7)+week_num;
            startStr += '<a class="acd_default"  data-week="' + tmp + '">' + i + '</a>';
            week_tmp++;
        }
        return startStr;
    }

    //默认显示的日历
    var _getDefaultDayHtml = function(data, $calendarObj, $calendarStartObj, $calendarEndObj) {
        var classEx = '';
        var startY = data.startY;
        var startD = data.startD
        var startM = data.startM;
        var endY = data.endY;
        var endM = data.endM;
        var endD = data.endD
        var startLastDay = _getMonthSumDay(startM, startY); //该月份总共的天数
        var endLastDay = _getMonthSumDay(endM, endY);
        var startStr = '',
        endStr = '';

        //计算年份每个月的开始和结束日是周几
        _getEveryMonthStartEndWeek(startY);
        if (startY != endY) {
            _getEveryMonthStartEndWeek(endY);
        }

        var startEveryMonthStartEndWeek = firstDayForWeek[startY][startM].split("-"); //获取开始日期的月份1号是周几，以便于补空操作
        var endEveryMonthStartEndWeek = firstDayForWeek[endY][endM].split("-");

        //补空
        var week_start = 0;
        var week_end=200;
        for (var ii = 1; ii < startEveryMonthStartEndWeek[0]; ii++) {
            startStr += '<a class="acd_empty"></a>';
            week_start++;
        }

        for (var i = 1; i <= startLastDay; i++) {
            var tmp = parseInt(week_start / 7);
            classEx = (i == startD) ? " acd_cur": "";
            startStr += '<a class="acd_default ' + classEx + '" data-week="' + tmp + '">' + i + '</a>';
            week_start++;
       }
            
        for (var ii = 1; ii < endEveryMonthStartEndWeek[0]; ii++) {
            endStr += '<a class="acd_empty"></a>';
            week_end++;
        }

        for (var i = 1; i <= endLastDay; i++) {
            var tmp = parseInt((week_end-200) / 7)+200;
            classEx = (i == endD) ? " acd_cur": "";
            endStr += '<a class="acd_default ' + classEx + '" data-week="' + tmp + '">' + i + '</a>';
            week_end++;
        }

        $calendarStartObj.find(".ac_ym .y").html(startY);
        $calendarEndObj.find(".ac_ym .y").html(endY);
        $calendarStartObj.find(".ac_ym .m").html(startM);
        $calendarEndObj.find(".ac_ym .m").html(endM);
        $calendarStartObj.find(".ac_day").html(startStr + clearFloatHtml);
        $calendarEndObj.find(".ac_day").html(endStr + clearFloatHtml);

        //经过日期
        _hoverDay($calendarObj);

    }

    //经过日期的时间段显示效果
    var _hoverDay = function($calendarObj) {
        var startY = $calendarObj.find(".ac_start_date").find(".y").html();
        var startM = $calendarObj.find(".ac_start_date").find(".m").html();
        var endY = $calendarObj.find(".ac_end_date").find(".y").html();
        var endM = $calendarObj.find(".ac_end_date").find(".m").html();
        if (startY <= endY && startM <= endM) {
            //相同年月
            if (startY == endY && startM == endM) {
                $calendarObj.find(".acd_default").hover(function() {
                    if ($calendarObj.find(".ac_start_date .acd_cur").length > 0) {
                        if ($(this).parents(".ac_end_date").length > 0) { //在结束日期上
                            var sFlag = parseInt($calendarObj.find(".ac_start_date .acd_cur").html());
                            var eFlag = $(this).html();
                            if (eFlag > sFlag) {
                                $calendarObj.find(".ac_end_date .acd_default").each(function() {
                                    var theValue = parseInt($(this).html());
                                    if (eFlag >= theValue && theValue >= sFlag) {
                                        $(this).addClass("acd_pass");
                                    }
                                });
                                $(this).addClass("acd_pass_hover");
                            }
                        }
                    }
                },
                function() {
                    $calendarObj.find(".acd_default").removeClass("acd_pass");
                    $(this).removeClass("acd_pass_hover");
                });

            } else {
                $calendarObj.find(".acd_default").hover(function() {
                    //开始日期必须选择了才有效
                    if ($calendarObj.find(".ac_start_date .acd_cur").length > 0) {
                        //经过结束日期部分才有效
                        if ($(this).parents(".ac_end_date").length > 0) {
                            var sFlag = parseInt($calendarObj.find(".ac_start_date .acd_cur").html());
                            var eFlag = $(this).html();
                            $calendarObj.find(".ac_start_date .acd_default").each(function() {
                                var theValue = parseInt($(this).html());
                                if (sFlag < theValue) {
                                    $(this).addClass("acd_pass");
                                }
                            });
                            $calendarObj.find(".ac_end_date .acd_default").each(function() {
                                var theValue = parseInt($(this).html());
                                if (eFlag > theValue) {
                                    $(this).addClass("acd_pass");
                                }
                            });
                            $(this).addClass("acd_pass_hover");
                        }
                    }
                },
                function() {
                    $calendarObj.find(".acd_default").removeClass("acd_pass");
                    $(this).removeClass("acd_pass_hover");
                });
            }
        }
    }

    var _toClose = function($theObj, $calendarObj) {
        $("body").live('click',
        function(evt) {
            var targetId = $theObj.attr("id");
            var $theFind = $(evt.target, this); //出发click事件的target
            if ($theFind.parents(".ajia_calendar").length == 0 && ($theFind.attr("id") != targetId)) {
                $calendarObj.hide();
            }
        });
    }

    var setting = $.extend(defaultOption, option);
    var $theObj = jQuery(this);
    var cId = "ajia_" + $theObj.attr("id");
    var _calendarHtml = function(cId) {
        var str = '<div class="ajia_calendar" id="' + cId + '">' +
         '<div class="ac_start_date">' + 
             '<div class="ac_title">开始日期</div>' + 
             '<div class="ac_main">' + 
                 '<div class="ac_month">' + 
                     '<a href="javascript:;" class="acm_prev"></a>' + 
                     '<span class="ac_ym"><font class="y">2015</font>年<font class="m">5</font>月</span>' + 
                     '<a href="javascript:;" class="acm_next"></a>' + 
                 '</div>' + 
                 '<div class="ac_week">' + 
                    '<span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span>' +
                 '</div>' + 
                 '<div class="ac_day"></div>' + 
             '</div>' + 
         '</div>' + 
         '<div class="ac_end_date">' + 
             '<div class="ac_title">结束日期</div>' + 
             '<div class="ac_main">' + 
                 '<div class="ac_month">' + 
                     '<a href="javascript:;" class="acm_prev"></a>' + 
                     '<span class="ac_ym"><font class="y">2015</font>年<font class="m">5</font>月</span>' + 
                     '<a href="javascript:;" class="acm_next"></a>' + 
                 '</div>' +
                 '<div class="ac_week">' +
                    '<span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span>' + 
                 '</div>' + 
                 '<div class="ac_day"></div>' + 
             '</div>' + 
         '</div>' + 
         '<div class="b_clear"></div>' + 
     '</div>';
        return str;
    }
    $('body').append(_calendarHtml(cId));
    if ($theObj.val().length == 0) {
        var inputDate = _initdate();
        $theObj.attr("value", inputDate);
    }
    var $calendarObj = $("#" + cId);
    var $calendarStartObj = $calendarObj.find(".ac_start_date");
    var $calendarEndObj = $calendarObj.find(".ac_end_date");
    var posX = $theObj.offset().left; // x position
    var posY = $theObj.offset().top; // y position
    var theTop = (setting.positionT) ? setting.positionT: $theObj.height() + posY + 5;
    var theLeft = (setting.positionL) ? setting.positionL: posX - 10;
    var theRight = setting.positionR;
    $theObj.live("click",
    function() {
        var currentDateArr = _getInputDate($theObj, $calendarObj, true, true);
        var paramDate = {
            startY: currentDateArr[0][0],
            startM: _deleteZero(currentDateArr[0][1]),
            startD: _deleteZero(currentDateArr[0][2]),
            endY: currentDateArr[1][0],
            endM: _deleteZero(currentDateArr[1][1]),
            endD: _deleteZero(currentDateArr[1][2])
        };

        _getDefaultDayHtml(paramDate, $calendarObj, $calendarStartObj, $calendarEndObj);
        var _weekStart = $calendarStartObj.find(".acd_cur").attr("data-week");
        var _weekEnd = $calendarEndObj.find(".acd_cur").attr("data-week");
        if (theRight !== '') {
            $calendarObj.css({
                "left": "",
                "top": theTop,
                "right": theRight
            }).show();
        } else {
            $calendarObj.css({
                "right": "",
                "top": theTop,
                "left": theLeft
            }).show();
        }
        var _top = $theObj.offset().top + 37;
        var _left = $theObj.offset().left - 10;
        var _id = $theObj.attr("id").split("_data_")[1];
        $("#ajia_us_data_" + _id).css("top", _top).css("left", _left);
        $calendarStartObj.find(".acd_default[data-week='" + _weekStart + "']").each(function() {
            $(this).addClass("acd_cur");
        })
        $calendarEndObj.find(".acd_default[data-week='" + _weekEnd + "']").each(function() {
            $(this).addClass("acd_cur");
        })
    });

    //月份选择
    $calendarObj.find(".acm_prev").unbind("click").click(function() {
        var week_num= $(this).parents().is(".ac_start_date")?100:300;
        var curY = parseInt($(this).next().find(".y").html());
        var curM = parseInt($(this).next().find(".m").html());
        var dataY = (curM == 1) ? (curY - 1) : curY;
        var dataM = (curM == 1) ? 12 : curM - 1;
        $(this).next().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM, week_num);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
        //经过日期
        _hoverDay($calendarObj);
    });

    $calendarObj.find(".acm_next").unbind("click").click(function() {
        var week_num= $(this).parents().is(".ac_start_date")?100:300;
        var curY = parseInt($(this).prev().find(".y").html());
        var curM = parseInt($(this).prev().find(".m").html());
        var dataY = (curM == 12) ? (curY + 1) : curY;
        var dataM = (curM == 12) ? 1 : curM + 1;
        
        $(this).prev().find(".y").html(dataY).end().find(".m").html(dataM);
        var str = _getDayHtml(dataY, dataM, week_num);
        $(this).parents(".ac_main").find(".ac_day").html(str + clearFloatHtml);
        //经过日期
        _hoverDay($calendarObj);
    });

    //日期点击
    $calendarObj.find(".acd_default").die("click").live('click',
    function() {
        var curDate = _getInputDate($theObj, $calendarObj, true);
        $(this).parent().find(".acd_default").removeClass("acd_cur");
        //点击的是开始日期div
        if ($(this).parents('.ac_start_date').length > 0) {
            var _week = $(this).attr("data-week");
            var _m = $(this).parents('.ac_start_date').find(".ac_month").find(".m").html();
            var _y = $(this).parents('.ac_start_date').find(".ac_month").find(".y").html();
            var _d = $calendarObj.find(".acd_default[data-week='" + _week + "']:first").html();
            var _days = $calendarObj.find(".acd_default[data-week='" + _week + "']").length;//判断当前天本月所在星期的天数;
            var _dEnd = $calendarObj.find(".acd_default[data-week='" + _week + "']:last").html();//本周的最后一天是几号
            if(_dEnd<7){ //上月的天数减去差下的天数，得出上月的日期
                _m = (_m > 1 ? parseInt(_m) - 1 : 12);
                _y = (_m != 12 ? _y: parseInt(_y) - 1);
                _d = _getMonthSumDay(_m, _y)-(6-_days);
            }
            var formatDate = _getFormatDate(_y, _m, _d);
            var newDate = formatDate + setting.dateTo + curDate[1];
            $(this).parents(".ac_start_date").data("beSelected", 1);
            $(this).parents(".ac_start_date").data("theDate", formatDate);
            $calendarStartObj.find(".acd_default[data-week='" + _week + "']").each(function() {
                $(this).addClass("acd_cur");
            })
        } else {
            var week = $(this).attr("data-week");
            var days = $calendarObj.find(".acd_default[data-week='" + week + "']").length;//判断当前天本月所在星期的天数;
            var d = $calendarObj.find(".acd_default[data-week='" + week + "']:last").html();//本周的最后一天是几号
            var m = $(this).parents('.ac_end_date').find(".ac_month").find(".m").html();
            var y = $(this).parents('.ac_end_date').find(".ac_month").find(".y").html();
            if(days<7){ //上月的天数减去差下的天数，得出上月的日期
                m = (m != 12 ? parseInt(m)+1 : 1);
                y = (m != 1 ? y : parseInt(y) + 1);
                d = (7-days);
            }
            var formatDate = _getFormatDate(y, m, d);
            var newDate = curDate[0] + setting.dateTo + formatDate;
            $(this).parents(".ac_end_date").data("beSelected", 1);
            $(this).parents(".ac_end_date").data("theDate", formatDate);
        }

        $theObj.val(newDate);
        if (($calendarObj.find(".ac_end_date").data("beSelected") == 1)) {
            $calendarObj.hide();
            setting.onClose();
            $calendarObj.find(".ac_start_date").data("beSelected", 0).end().find(".ac_end_date").data("beSelected", 0);
        }
    });
    _toClose($theObj, $calendarObj);

};