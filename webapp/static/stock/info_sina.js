(function() {
    'use strict';

    var _sina_table = null;
    var _sina_i = 1;
    var _sina_data = {code:infoPage.code,index:_sina_i};
    var _sina_ajax_option =  {
    url:$SCRIPT_ROOT + '/detail/sinaNews',
    data:_sina_data,
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {
    infoPage.sinaLoad = true;
    if(_sina_table)_sina_table.destroy();

    _sina_table = $('#sina_table').DataTable( {
        paging: false,
        data: result.data.tableData,
        order: false,
        searching: false,
        info:false,
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
                      if(infoPage.isLogin=='True'){

                        return "<a data-toggle='modal' data-stock='"+full.symbol.substring(2)+"' data-href='" + full.url
                        + "' data-title='"+full.title+"' data-datetime='"+full.datetime+"' data-src='sina' href='#infoModal'>"+full.title+"</a>&nbsp;"

                        }else{
                        return "<a href='javascript:void(0);' onclick='request_login()'>" +full.title+ "</a>&nbsp;"
                      }
                      }
                  }
        ]
    } );

    }
};

$('#sina_news').find('.previous').on('click', function (event) {
    var modal = $(event.target);
    _sina_i = _sina_i-1;
    if(_sina_i==1)modal.addClass("disabled");
    _sina_ajax_option.data = {code:infoPage.code,index:_sina_i};
    $.ajax(_sina_ajax_option);
  });

$('#sina_news').find('.next').on('click', function (event) {
    var modal = $(event.target);
    _sina_i = _sina_i+1;
    $('#sina_news').find('.previous').removeClass("disabled");
    _sina_ajax_option.data = {code:infoPage.code,index:_sina_i};
    $.ajax(_sina_ajax_option);
  });


$('a[href="#sina_news"]').on('show.bs.tab', function (e) {
  if(infoPage.sinaLoad==false){
  $.ajax(_sina_ajax_option);
  }

});



})();