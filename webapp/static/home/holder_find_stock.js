
var skey='淡水泉';

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
    var checkVal=$("input:radio[name='optionsRadiosinline']:checked").val();
    var smsg = $('#bs_cname').val().replace(/(^s*)|(s*$)/g, "");
    if(checkVal=='option3' && smsg.length >0){
        skey = smsg;

    }else if(checkVal=='option1'){
        skey = '淡水泉';

    }else if(checkVal=='option2'){
        skey = '重阳';
    }else{
        return;
    }


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
      console.log(textStatus);
    }
    });
}

function redrawTable(resultTData){

 if(list_table){
      list_table.destroy();
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
        { "data": 'pcf' },
        { "data": 'pe' },
        { "data": 'pb' },
        { "data": 'mvalue' },
        { "data": 'rate' },
        { "data": 'ncode' }
    ],
    columnDefs: [
                  {
                      "targets": [1],
                      "render": function(data, type, full) {
                          //return '<a href="#holderTrackModal" >'+data+'</a>';
                          return '<a href="javascript:void(0);" onclick="filterByHolderName('+full.holder_code+')">'+data+'</a>';
                      }
                  },
                  {
                      "targets": [2],
                      "visible": false
                  },
                  {
                      "targets": [5,6,7],
                      "width": "2%"
                  },
                  {
                      "targets": [8],
                      "render": function(data, type, full) {
                          return '<a href="#holderTrackModal" data-stock="'+full.code+'" data-holder-name="'+full.name+'" data-holder-code="'+full.holder_code+'" data-toggle="modal">'+data+'</a>';
                      }
                  },
                  {
                      "targets": [10],
                      "render": function(data, type, full) {
                          return '<a href="/stock/valuation/'+full['ncode']+'" target="_blank">详细</a>';
                      }
                  },
        ]

    });

}

//加载完毕自动执行
$(function(){

getTargetStocks();


});