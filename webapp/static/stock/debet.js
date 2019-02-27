//加载完毕自动执行
$(function(){

    var code = debetModal.code; // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.

    var modal = $(this)
    modal.find('.modal-title').text('债务结构 -' + debetModal.name+'-'+code );
    var data_table = modal.find('.modal-body #data_table');

    modal.find('.modal-body #dm_q0').on("change",{q:0},getData);
    modal.find('.modal-body #dm_q1').on("change",{q:1},getData);
    modal.find('.modal-body #dm_q2').on("change",{q:2},getData);
    modal.find('.modal-body #dm_q3').on("change",{q:3},getData);
    modal.find('.modal-body #dm_q4').on("change",{q:4},getData);

  function getData(val){
   debetModal.quarter = val.data.q;
   loadData();
  }

  function loadData() {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/detail/debetJson',
    data:{
             quarter : debetModal.quarter,
             code : code
    },
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {

    var zyysr = {'name':'营业收入TTM',yAxis: 1,marker: {enabled: false}};
    zyysr['data'] = result.data.zyysr;

    var chb = {'name':'存货比',type: 'column',marker: {enabled: false}};
    chb['data'] = result.data.chb;

    var ch = {'name':'存货',yAxis: 1,marker: {enabled: false}};
    ch['data'] = result.data.ch;

    var yszkb = {'name':'应收帐款比',type: 'column',marker: {enabled: false}};
    yszkb['data'] = result.data.yszkb;

    var yszk = {'name':'应收帐款',yAxis: 1,marker: {enabled: false}};
    yszk['data'] = result.data.yszk;

    valuation(result);

    modal.find('.modal-body #chart_3').highcharts({
        chart: {zoomType: 'xy'},
        title: {text:  '存货比（存货/营业收入TTM）'},
        xAxis: {type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        yAxis: [
        {// Primary yAxis
        title: {text: '比例'},
        labels: {
                format: '{value} %'
                }
        },
        {// Secondary yAxis
        title: {text: '数值'},
        labels: {
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
        opposite: true
        }],
        credits: {enabled: false},
        series: [chb,ch,zyysr],
        tooltip:{
           xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });
    modal.find('.modal-body #chart_4').highcharts({
        chart: {zoomType: 'xy'},
        title: {text:  '应收帐款比（应收帐款/营业收入TTM）'},
        xAxis: {type: 'datetime',
            dateTimeLabelFormats: {
                month: '%Y-%m'
            }},
        yAxis: [
        {// Primary yAxis
        title: {text: '比例'},
        labels: {
                format: '{value} %'
                }
        },
        {// Secondary yAxis
        title: {text: '数值'},
        labels: {
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
        opposite: true
        }],
        credits: {enabled: false},
        series: [yszkb,yszk,zyysr],
        tooltip:{
            xDateFormat: '%Y-%m-%d',
           crosshairs: true,
           shared: true
        }
    });

    }

    });
  };

  function valuation(result){
    var valuation_data = {'name':'总负债率',type: 'column',marker: {enabled: false}};
    valuation_data['data'] = result.data.fzl;

    var dqfz = {'name':'短期负债率',type: 'column',marker: {enabled: false}};
    dqfz['data'] = result.data.dqfz;


    //显示数据
    modal.find('.modal-body').show();
    if(debetModal.datatable)debetModal.datatable.destroy();

    debetModal.datatable = data_table.DataTable( {
        scrollY: 300,
        paging: false,
        data: result.data.tableData,
        "order": [[ 0, "desc" ]],
        searching: false,
        aoColumnDefs: [
        { "sWidth": "12%", "aTargets": [ 0 ] }
        ],
        columns: [
            { title: "日期" },
            { title: "总资产(亿)" },
            { title: "总负债(亿)" },
            { title: "股东权益(亿)" },
            { title: "存货(亿)" },
            { title: "应收账款(亿)" },
            { title: "总负债率(%)" },
            { title: "短期负债率(%)" },
            { title: "流动比" }
        ]
    } );

}

  loadData(); //初始加载

});