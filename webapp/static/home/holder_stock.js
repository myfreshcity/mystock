
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
    success:function(result){redrawTable(result.data.tableData);},
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      console.log(errorThrown.stack);
    }
    });
}

function redrawTable(resultTData){

 if(list_table){
      list_table.destroy();
      $('#backBtn').hide();
 }

 list_table = $('#example').DataTable({
    "paging": false,
    data: resultTData,
    "order": [],
    "language": {
                "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Chinese.json"
            },
    columns: [
        { "data": 'report_type' },
        { "data": 'holder_name' },
        { "data": 'holder_code' },
        { "data": 'code' },
        { "data": 'name' },
        { "data": 'stock_industry' },
        { "data": 'pcf' },
        { "data": 'pe' },
        { "data": 'pb' },
        { "data": 'mvalue' },
        { "data": 'rate' },
        { "data": 'hold_length' },
        { "data": 'ncode' }
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

$("input:radio[name='optionsRadiosinline']").change(function (){

var checkVal=$("input:radio[name='optionsRadiosinline']:checked").val();
    if(checkVal=='option3'){
    //指定股票
    //$('#bs_cname').show();
    $('#bs_cname').prop('disabled', false);
    //$('#bs_btn').prop('disabled', true);
    }else{
    //$('#bs_cname').hide();
    $('#bs_cname').prop('disabled', true);
    //$('#bs_btn').prop('disabled', false);
    }
});

getTargetStocks();


});