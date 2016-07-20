var mytable;

function getData(period,code) {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/valuationJson',
    data:{
             period : period,
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
    var pe = {'name':'市盈率',marker: {enabled: false}};
    pe['data'] = result.data.pe;
    var ps = {'name':'市净率',marker: {enabled: false}};
    ps['data'] = result.data.ps;
    var pcf = {'name':'市现率',marker: {enabled: false}};
    pcf['data'] = result.data.pcf;
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
            { title: "市净率" },
            { title: "市现率" },
            { title: "每股收益TTM" },
            { title: "每股净资产" },
            { title: "每股经营现金流TTM" }
        ]
    } );


    $('#valuation').highcharts({
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: '最近'+result.period+'年历史估值'
        },
        xAxis: {
            categories: []
        },
        credits: {enabled: false},
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
        tooltip: {
            crosshairs: true,
            shared: true
        },
        plotOptions: {
            area: {
                fillColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                },
                lineWidth: 1,
                marker: {
                    enabled: false
                },
                shadow: false,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            }
        },
        series: [pe,ps,pcf,close]
    });
}

