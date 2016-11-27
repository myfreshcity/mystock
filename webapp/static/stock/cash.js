
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
    cashPage.quarter = quarter;
    getData();
}

function changePtype(pType){
    cashPage.pType = pType;
    getData();
}

function getData() {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/cashJson',
    data:{
             code : cashPage.code,
             quarter : cashPage.quarter,
             pType : cashPage.pType
    },
    type:'get',
    cache:false,
    dataType:'json',
    success:revenue
    });
  };

//营收
function revenue(result){
    var yysrs = {'name':'营业收入TTM','data':result.data.yysr,type:'column',marker: {enabled: false}};
    var jlrs = {'name':'净利润TTM','data':result.data.jlr,type:'column',marker: {enabled: false}};
    var jyjxjls = {'name':'经营净现金流TTM','data':result.data.jyjxjl,type:'column',marker: {enabled: false} };

    var cash_live_rate = {'name':'（维持率）现金余额／营收TTM','data':result.data.cash_live_rate,yAxis: 1,marker: {enabled: false}};
    var cash_produce_rate = {'name':'（产生率）经营性现金TTM／营收TTM','data':result.data.cash_produce_rate,yAxis: 1,marker: {enabled: false}};
    var cash_jlr_rate = {'name':'（现金含量）经营性现金TTM／净利润TTM','data':result.data.cash_jlr_rate,yAxis: 1,marker: {enabled: false}};

    var xjye = {'name':'现金余额','data':result.data.xjye,type:'area',marker: {enabled: false}};
    var xjjze_qt = {'name':'现金净增加额','data':result.data.xjjze_qt,type:'column',marker: {enabled: false}};
    var jyjxjl_qt = {'name':'经营现金净增加额','data':result.data.jyjxjl_qt,type:'column',marker: {enabled: false} };
    var jlr_qt = {'name':'利润净增加额','data':result.data.jlr_qt,type:'column',marker: {enabled: false}};


    $('#revenue_0').highcharts({
        title: {text: '现金变化趋势'},
        chart: {zoomType: 'x'},
        xAxis: {categories: []},
        credits: {enabled: false},
        series: [xjye,xjjze_qt,jyjxjl_qt,jlr_qt],
        tooltip:{
           crosshairs: true,
           shared: true
        }
    });
    $('#revenue_1').highcharts({
        chart: {zoomType: 'xy'},
        title: {text: '现金使用情况'},
        xAxis: {categories: []},
        yAxis: [
        {
        labels: {
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            }
        },
        {
        labels: {format: '{value} %'},
        opposite: true
        }
        ],
        credits: {enabled: false},
        series: [jlrs,jyjxjls,cash_live_rate,cash_produce_rate],
        tooltip:{
           crosshairs: true,
           shared: true
        }
    });

    $('#revenue_2').highcharts({
        chart: {zoomType: 'xy'},
        title: {text: '现金含量'},
        xAxis: {categories: []},
        yAxis: [
        {
        labels: {
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            }
        },
        {
        labels: {format: '{value} %'},
        opposite: true
        }
        ],
        credits: {enabled: false},
        series: [jlrs,jyjxjls,cash_jlr_rate]
    });

    //显示数据
    if(cashPage.mytable) cashPage.mytable.destroy();
    cashPage.mytable = $('#example').DataTable( {
        scrollY: 300,
        paging: false,
        data: result.tableData,
        "order": [[ 0, "desc" ]],
        searching: false,
        columns: [
            { title: "日期" },
            { title: "期末现金余额" },
            { title: "主营收入" },
            { title: "现金净增加额" },
            { title: "经营性现金净增加额" },
            { title: "经营性现金／现金增加额(%)" },
            { title: "经营性现金／营收(%)" },
            { title: "经营性现金／利润(%)" },
            { title: "经营性现金增长率(%)" },
            { title: "经营性现金／利润TTM(%)" }
        ],
        columnDefs: [
                  {
                      "targets": [0],
                      "width": "10%"
                  }
        ]
    } );
}

