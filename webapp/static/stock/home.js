
function updateData(code){
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/setting/update/',
    data:{
             code : code
    },
    type:'post',
    cache:false,
    dataType:'json',
    success:function(result){
         if(result.msg == true){
             alert('数据更新成功');
         }else{
            console.error(result.msg);
         }
        }
    });

}

function getStockData(code) {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/get_basic',
    data:{
             code : code
    },
    type:'get',
    cache:false,
    dataType:'json',
    success:function(data) {
        $("#desc").val(data.desc);
        $("#growType").val(data.grow_type);
        //$("#growType  option[value='s2'] ").attr("selected",true);
     }
    });
  };

 function updateStockData(code) {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/update_basic',
    data:{
             code : code,
             desc : $("#desc").val(),
             growType :  $("#growType").val()
    },
    type:'post',
    cache:false,
    dataType:'json',
    success:function(data) {
        alert('更新成功');
     }
    });
  };

function changePeriod(quarter){
    homePage.quarter = quarter;
    getData();
}

function changePtype(pType){
    homePage.pType = pType;
    getData();
}

function getData() {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/revenueJson',
    data:{
             code : homePage.code,
             quarter : homePage.quarter,
             pType : homePage.pType
    },
    type:'get',
    cache:false,
    dataType:'json',
    success:revenue
    });
  };

//营收
function revenue(result){
    var yysrs = [{'name':'营业收入TTM','data':result.data.yysr,marker: {enabled: false}}];
    var jlrs = [{'name':'净利润TTM','data':result.data.jlr,marker: {enabled: false}}];
    var jyjxjls = [{'name':'经营净现金流TTM','data':result.data.jyjxjl,marker: {enabled: false} }];
    var roe = [{'name':'净资产收益率','data':result.data.roe,marker: {enabled: false}}];


    $('#revenue_0').highcharts({
        chart: {zoomType: 'xy'},
        title: {text: '整体营收TTM'},
        xAxis: {type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        credits: {enabled: false},
        series: yysrs.concat(jlrs).concat(jyjxjls),
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    $('#revenue_1').highcharts({
        chart: {zoomType: 'xy',type:'column'},
        title: {text: '营业收入TTM'},
        xAxis: {type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        credits: {enabled: false},
        series: yysrs,
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    $('#revenue_2').highcharts({
        chart: {zoomType: 'xy',type:'column'},
        xAxis: {type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        title: {text: '净利润TTM'},
        credits: {enabled: false},
        series: jlrs,
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    $('#revenue_3').highcharts({
        chart: {zoomType: 'xy',type:'column'},
        xAxis: {type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        title: {text: '经营净现金流TTM'},
        credits: {enabled: false},
        series: jyjxjls,
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    $('#revenue_4').highcharts({
        chart: {type: 'column'},
        xAxis: {type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        title: {text: '净资产收益率'},
        credits: {enabled: false},
        series: roe,
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });

    //显示数据
    if(homePage.mytable) homePage.mytable.destroy();
    homePage.mytable = $('#example').DataTable( {
        scrollY: 300,
        paging: false,
        data: result.tableData,
        "order": [[ 0, "desc" ]],
        searching: false,
        columns: [
            { title: "日期" },
            { title: "主营收入(亿)" },
            { title: "营收增长率(%)" },
            { title: "净利润(亿)" },
            { title: "净利润增长率(%)" },
            { title: "经营性现金流(亿)" },
            { title: "现金流增长率(%)" },
            { title: "现金含量(经营性现金流／净利润)" },
        ],
        columnDefs: [
                  {
                      "targets": [0],
                      "width": "10%"
                  }
        ]
    } );
}

