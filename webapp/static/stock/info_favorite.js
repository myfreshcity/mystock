(function() {
    'use strict';

    if(infoPage.isLogin=='False') return;

    infoPage.list_table = $('#mynews_table').DataTable({
    "order": false,
    searching: false,
    info:false,
    paging: false,
    "ajax": {
          url:$SCRIPT_ROOT + '/detail/favorList/'+infoPage.code,
          type:'get',
          cache:false,
          dataType:'json',
          data:function(data) { // add request parameters before submit
                $.each(infoPage.ajaxParams, function(key, value) {
                    data[key] = value;
                });
          },
          "dataSrc": function(res) {
            return res;
          }
        },
    columns: [
            { title: "标题",data:"title" },
            { title: "链接",data:"url" },
            { title: "日期",data:"pub_date"},
            { title: "操作",data:"id"}
        ],
     columnDefs: [
              {
                  "targets": [0],
                  "render": function(data, type, full) {
                      if(full.src_type==='other'){
                      return "<a href='"+full.url+"' target='_blank'>" +full.title+ "</a>&nbsp;"
                      }else{

                      return "<a data-href='"+full.url+"' data-stock='"+full.code+"' data-toggle='modal' data-title='"
                        +full.title+"' data-datetime='"+full.pub_date+"' data-src='"+full.src_type+"' href='#infoModal'>"
                        +full.title+"</a>&nbsp;"

                      }
                   }
              },
              {
                  "targets": [1],
                  "visible": false
              },
              {
                  "targets": [3],
                  "render": function(data, type, full) {
                      return "<a href='#' onclick='javascript:removeFav(" + data + ",this);return false;'>"+'删除'+"</a>&nbsp;"
                  }
              }
        ]
    });



$('a[href="#favi_news"]').on('show.bs.tab', function (e) {


});

})();