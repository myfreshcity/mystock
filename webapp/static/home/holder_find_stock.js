
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

function search(){
    var skey = $('#bs_cname').val().replace(/\s*/g,"");
    requestServer(skey);
}

function linkSearch(ele){
    requestServer($(ele).text());
}

function requestServer(msg){
    $('#docTitle').html('');
    $.ajax({
    url:$SCRIPT_ROOT + '/holder/findHolderJson',
    data:{
             skey : msg
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
 }

 list_table = $('#example').DataTable({
    "paging": false,
    data: resultTData,
    "ordering": true,
    searching: false,
    "info": false,
    columns: [
        { title: "","data": 'code' },
        { title: "名称","data": 'name' },
        { title: "频率","data": 'size' },
        { title: "最近日期","data": 'date' },
    ],
    columnDefs: [
                  {
                      "targets": [0],
                      "visible": false
                  },
                  {
                      "targets": [1],
                      "render": function(data, type, full) {
                          return '<a href="'+$SCRIPT_ROOT + '/holder/'+full.code+'" target="_blank">'+ data +'</a>';
                      }
                  },
        ]

    });

}

//加载完毕自动执行
$(function(){


});