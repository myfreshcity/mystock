(function() {
    'use strict';


var _163_table = null;
var _163_i = 0;
var _163_data = {code:infoPage.code,index:_163_i};
var _163_ajax_option =  {
    url:$SCRIPT_ROOT + '/detail/163News',
    data:_163_data,
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {
    if(_163_table)_163_table.destroy();

    _163_table = $('#163_table').DataTable( {
        paging: false,
        data: result.data.tableData,
        "order": [[ 2, "desc" ]],
        searching: false,
        columns: [
            {},{},
            { title: "标题" },
            { title: "日期" }
        ],
        columnDefs: [
                  {
                      "targets": [0,1],
                      "visible": false
                  },
                  {
                      "targets": [2],
                      "render": function(data, type, full) {
                          return "<a data-toggle='modal' data-stock='"+full[0]+"' data-href='" + full[2] + "' data-title='"+
                          full[1]+"' data-datetime='"+full[3]+"' data-src='163' href='#infoModal'>"+full[1]+"</a>&nbsp;"
                      }
                  }
        ]
    } );

    }
};

$('#163_news').find('.previous').on('click', function (event) {
    var modal = $(event.target);
    _163_i = _163_i-1;
    if(_163_i==0)modal.addClass("disabled");
    _163_ajax_option.data = {code:infoPage.code,index:_163_i};
    $.ajax(_163_ajax_option);
  });

$('#163_news').find('.next').on('click', function (event) {
    var modal = $(event.target);
    _163_i = _163_i+1;
    $('#163_news').find('.previous').removeClass("disabled");
    _163_ajax_option.data = {code:infoPage.code,index:_163_i};
    $.ajax(_163_ajax_option);
  });

$(function(){
    $.ajax(_163_ajax_option);
});



})();