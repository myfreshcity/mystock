var mytable = $('#example').DataTable({
            columns: [
            { title: "日期" },
            { title: "收盘价" },
            { title: "市盈率" },
            { title: "市销率" },
            { title: "市现率" },
            { title: "每股收益TTM" },
            { title: "每股营业收入TTM" },
            { title: "每股经营现金流TTM" }
        ]

});

function getData(category,price,code) {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/valuationJson',
    data:{
             category : category,
             price : price,
             code : code
    },
    type:'post',
    cache:false,
    dataType:'json',
    success:valuation
    });

  }

//估值
function valuation(result){
    var pe = {'name':'市盈率'};
    pe['data'] = result.data.pe;
    var ps = {'name':'市销率'};
    ps['data'] = result.data.ps;
    var pcf = {'name':'市现率'};
    pcf['data'] = result.data.pcf;
    var close = {'name':'股价','type':'spline','yAxis':1 };
    close['data'] = result.data.close;

    //显示数据
    mytable.destroy();
    mytable = $('#example').DataTable( {
        data: result.data.tableData,
        "order": [[ 0, "desc" ]],
        searching: false,
        columns: [
            { title: "日期" },
            { title: "收盘价" },
            { title: "市盈率" },
            { title: "市销率" },
            { title: "市现率" },
            { title: "每股收益TTM" },
            { title: "每股营业收入TTM" },
            { title: "每股经营现金流TTM" }
        ]
    } );


    $('#valuation').highcharts({
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: '历史估值'
        },
        xAxis: {
            categories: []
        },

        yAxis: [{ // Primary yAxis
            title: {
                text: '估值',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            labels: {
                format: '{value}',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            }
        }, { // Secondary yAxis
            title: {
                text: '股价',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            labels: {
                format: '{value} ',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            opposite: true
        }],
        series: [pe,ps,pcf,close]
    });
}

//加载完毕自动执行

