var mytable;

function getData(period,code) {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/valuationJson',
    data:{
             period : period,
             code : code
    },
    type:'get',
    cache:true,
    dataType:'json',
    success:valuation
    });

  }

//估值
function valuation(result){
    var pe = {'name':'市盈率',marker: {enabled: false}};
    pe['data'] = result.data.pe;
    var ps = {'name':'市销率',marker: {enabled: false}};
    ps['data'] = result.data.ps;
    var pcf = {'name':'市现率',marker: {enabled: false}};
    pcf['data'] = result.data.pcf;
    var pb = {'name':'市净率',marker: {enabled: false}};
    pb['data'] = result.data.pb;

    var close = {'name':'股价','type':'area','yAxis':1 };
    close['data'] = result.data.close;

    //显示数据
    if(mytable)mytable.destroy();
    mytable = $('#example').DataTable( {
        scrollY: 300,
        paging: false,
        data: result.data.tableData,
        "order": [[ 0, "desc" ]],
        searching: false,
        columns: [
            { title: "日期" },
            { title: "收盘价" },
            { title: "市盈率" },
            { title: "市销率" },
            { title: "市现率" },
            { title: "市净率" },
            { title: "总股本" },
            { title: "股东权益" },
            { title: "净利润" },
            { title: "净利润TTM" }
        ]
    } );

    $('#pe').highcharts({
        chart: {zoomType: 'xy'},
        title: {text:  '最近'+result.period+'年市盈率'},
        xAxis: {
        type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        credits: {enabled: false},
        series: [pe],
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    $('#ps').highcharts({
        chart: {zoomType: 'xy'},
        title: {text:  '最近'+result.period+'年市销率'},
        xAxis: {
        type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        credits: {enabled: false},
        series: [ps],
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    $('#pcf').highcharts({
        chart: {zoomType: 'xy'},
        title: {text:  '最近'+result.period+'年市现率'},
        xAxis: {
        type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        credits: {enabled: false},
        series: [pcf],
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    $('#pb').highcharts({
        chart: {zoomType: 'xy'},
        title: {text:  '最近'+result.period+'年市净率'},
        xAxis: {
        type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        credits: {enabled: false},
        series: [pb],
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });

}

