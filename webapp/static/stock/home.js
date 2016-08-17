var mytable;

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

function getData(quarter,code) {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/revenueJson',
    data:{
             quarter : quarter,
             code : code
    },
    type:'post',
    cache:false,
    dataType:'json',
    success:revenue
    });
  };

//营收
function revenue(result){
    var yysrs = [{'name':'营业收入','data':result.data.yysr,type:'column',marker: {enabled: false}}];
    var jlrs = [{'name':'营业利润','data':result.data.jlr ,marker: {enabled: false}}];
    var jyjxjls = [{'name':'经营净现金流','data':result.data.jyjxjl,marker: {enabled: false} }];
    var roe = [{'name':'净资产收益率','data':result.data.roe,marker: {enabled: false}}];


    $('#revenue_0').highcharts({
        title: {text: '整体营收'},
        xAxis: {categories: []},
        credits: {enabled: false},
        series: yysrs.concat(jlrs).concat(jyjxjls),
        tooltip:{
           crosshairs: true,
           shared: true
        }
    });
    $('#revenue_1').highcharts({
        chart: {type: 'column'},
        title: {text: '营业收入'},
        xAxis: {categories: []},
        credits: {enabled: false},
        series: yysrs,
        tooltip:{
           formatter:function(){
              return Highcharts.numberFormat(this.y,0,".", ",")+' 万';
           }
        }
    });
    $('#revenue_2').highcharts({
        chart: {type: 'column'},
        xAxis: {categories: []},
        title: {text: '净利润'},
        credits: {enabled: false},
        series: jlrs,
        tooltip:{
           formatter:function(){
              return Highcharts.numberFormat(this.y,0,".", ",")+' 万';
           }
        }
    });
    $('#revenue_3').highcharts({
        chart: {type: 'column'},
        xAxis: {categories: []},
        title: {text: '经营净现金流'},
        credits: {enabled: false},
        series: jyjxjls,
        tooltip:{
           formatter:function(){
              return Highcharts.numberFormat(this.y,0,".", ",")+' 万';
           }
        }
    });
    $('#revenue_4').highcharts({
        chart: {type: 'column'},
        xAxis: {categories: []},
        title: {text: '净资产收益率'},
        credits: {enabled: false},
        series: roe
    });

    //显示数据
    if(mytable) mytable.destroy();
    mytable = $('#example').DataTable( {
        scrollY: 300,
        paging: false,
        data: result.tableData,
        "order": [[ 0, "desc" ]],
        searching: false,
        columns: [
            { title: "日期" },
            { title: "主营收入" },
            { title: "净利润" },
            { title: "经营性现金流" },
            { title: "营收增长率" },
            { title: "净利润增长率" },
            { title: "经营性现金流增长率" }
        ]
    } );
}

