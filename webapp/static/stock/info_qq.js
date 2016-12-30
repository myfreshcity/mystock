(function() {
    'use strict';

    var _qq_table = null;
    var _qq_i = 1;
    var _qq_data = {code:infoPage.code,index:_qq_i};
    var _qq_ajax_option =  {
    url:$SCRIPT_ROOT + '/detail/QQNews',
    data:_qq_data,
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {
    infoPage.qqLoad=true;
    if(_qq_table)_qq_table.destroy();

    _qq_table = $('#qq_table').DataTable( {
        paging: true,
        data: result.data.tableData.data,
        order: false,
        searching: false,
        columns: [
            { title: "操作",data:"url"},
            { title: "标题",data:"title" },
            { title: "日期",data:"datetime" }
        ],
        columnDefs: [
                  {
                      "targets": [0],
                      "visible": false
                  },
                  {
                      "targets": [1],
                      "render": function(data, type, full) {
                        return "<a data-toggle='modal' data-stock='"+full.symbol.substring(2)+"' data-href='" + full.url
                        + "' data-title='"+full.title+"' data-datetime='"+full.datetime+"' data-src='qq' href='#infoModal'>"+full.title+"</a>&nbsp;"
                      }
                  }
        ]
    } );

    }
};

$('#qq_news').find('.previous').on('click', function (event) {
    var modal = $(event.target);
    _qq_i = _qq_i-1;
    if(_qq_i==1)modal.addClass("disabled");
    _qq_ajax_option.data = {code:infoPage.code,index:_qq_i};
    $.ajax(_qq_ajax_option);
  });

$('#qq_news').find('.next').on('click', function (event) {
    var modal = $(event.target);
    _qq_i = _qq_i+1;
    $('#qq_news').find('.previous').removeClass("disabled");
    _qq_ajax_option.data = {code:infoPage.code,index:_qq_i};
    $.ajax(_qq_ajax_option);
  });


$('a[href="#qq_news"]').on('show.bs.tab', function (e) {
  if(infoPage.qqLoad==false){
  $.ajax(_qq_ajax_option);
  }
});



})();