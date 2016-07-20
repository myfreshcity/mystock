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
           shared: true,
           formatter:function(){
              return Highcharts.numberFormat(this.y,0,".", ",")+' 百万';
           }
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
              return Highcharts.numberFormat(this.y,0,".", ",")+' 百万';
           }
        }
    });
    $('#revenue_2').highcharts({
        chart: {type: 'column'},
        xAxis: {categories: []},
        title: {text: '营业利润'},
        credits: {enabled: false},
        series: jlrs,
        tooltip:{
           formatter:function(){
              return Highcharts.numberFormat(this.y,0,".", ",")+' 百万';
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
              return Highcharts.numberFormat(this.y,0,".", ",")+' 百万';
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
            { title: "日期","data": "report_type" },
            { title: "每股收益","data": "mgsy" },
            { title: "每股收益(TTM)" ,"data": "mgsy_ttm" },
            { title: "每股净资产" ,"data": "mgjzc" },
            { title: "每股经营现金流" ,"data": "mgjyxjl" },
            { title: "每股经营现金流(TTM)","data": "mgjyxjl_ttm"  },
            { title: "营业收入(百万)","data": "yysr"  },
            { title: "净利润(百万)" ,"data": "kjlr" },
            { title: "经营现金流(百万)" ,"data": "jyjxjl" },
            { title: "净资产收益率(ROE)","data": "roe"  }
        ],
        "columnDefs": [
                  {
                      "targets": [6],
                      "render": function(data, type, full) {
                          return formatRevenceVal(data);
                      }
                  },
                  {
                      "targets": [7],
                      "render": function(data, type, full) {
                          return formatRevenceVal(data);
                      }
                  },
                  {
                      "targets": [8],
                      "render": function(data, type, full) {
                          return formatRevenceVal(data);
                      }
                  }
            ]
    } );
}

