
var list_table;

function clearSearch(){
    list_table.search('').columns().search('').draw();
    $('#backBtn').hide();
}

function filterByHolderName(mkey){
    list_table.columns( 2 )
        .search(mkey)
        .draw();
    console.log( 'There are'+list_table.data().length+' row(s) of data in this table' );
    $('#backBtn').show();
}

function getTargetStocks(){
    $.ajax({
    url:$SCRIPT_ROOT + '/holderFindStockJson',
    data:{
             skey : skey
    },
    type:'get',
    cache:false,
    dataType:'json',
    success:function(res){valuation(res);},
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      console.log(errorThrown.stack);
    }
    });
}

function valuation(res){
    var result = res.data;

    for(var i = 0; i　< result.length; i++) {
        var r_date = result[i]['r_date'];
        var data = result[i]['data'];
        var $h1=$('<h4>'+r_date+'</h4>');
        var $table1 = $('<table class="display" cellspacing="0" width="99%" style="margin-bottom: 80px"></table>');
        render_table($table1,data)
        $('#table_div').prepend($table1).prepend($h1)
    }
}

function render_table(ele,table_data){
     ele.DataTable({
        "paging": false,
        "searching": false,
        "info": false,
        data: table_data,
        "order": [],
    columns: [
        { "title": "报告日期", "data": 'report_type' },
        { "title": "股东", "data": 'holder_name' },
        { "title": "股东代码", "data": 'holder_code' },
        { "title": "股票代码", "data": 'code' },
        { "title": "名称", "data": 'name' },
        { "title": "所在行业", "data": 'stock_industry' },
        { "title": "市现率(PCF)", "data": 'pcf' },
        { "title": "市盈率(PE)", "data": 'pe' },
        { "title": "市净率(PB)", "data": 'pb' },
        { "title": "持有市值(亿)", "data": 'mvalue' },
        { "title": "比例", "data": 'rate' },
        { "title": "持有时长", "data": 'hold_length' },
        { "title": "操作", "data": 'ncode' }
    ],
    columnDefs: [
                  {
                      "targets": [0],
                      "width": "10%"
                  },
                  {
                      "targets": [2],
                      "width": "20%",
                      "render": function(data, type, full) {
                          //return '<a href="#holderTrackModal" >'+data+'</a>';
                          return '<a href="#holderTrackModal" data-stock="'+full.code+'" data-holder-name="'+full.holder_name+'" data-holder-code="'+full.holder_code+'" data-toggle="modal">'+full.holder_name+'</a>';
                          //return '<a href="javascript:void(0);" onclick="filterByHolderName('+full.holder_code+')">'+data+'</a>';
                      }
                  },
                  {
                      "targets": [1],
                      "visible": false
                  },
                  {
                      "targets": [9],
                      "render": function(data, type, full) {
                          return data;
                      }
                  },
                  {
                      "targets": [12],
                      "render": function(data, type, full) {
                          return '<a href="/stock/holder/'+full['ncode']+'" target="_blank">详细</a>';
                      }
                  },
        ]

    });

}

//加载完毕自动执行
$(function(){
getTargetStocks();
});