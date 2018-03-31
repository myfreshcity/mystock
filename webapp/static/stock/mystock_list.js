var modal_datatable;
var list_table;


function updateData(code){
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/setting/update/',
    data:{
             code : code
    },
    type:'post',
    cache:false,
    dataType:'json',
    success:function(result){
         if(result.msg == true){
             toastr.info('数据更新成功');
         }else{
            console.error(result.msg);
         }
        }
    });

};


// 从相关股清除
function delRelation(mcode,scode,el) {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/del_relation',
    data:{
             mcode: mcode,
             scode: scode
    },
    type:'post',
    cache:false,
    dataType:'json',
    success:function(data) {
        if(data.msg =="true" ){
        list_table.row($(el).parents('tr')).remove().draw(false);
            //window.location.reload();
        }else{
            console.warn("server result is:"+data.msg);
        }
     }
    });
  };

//根据title确定菜单内容
function getSubMenu(code){
     if (page_title=='自选股')
        return '<li><a href="#" onclick="javascript:unselStock(\''+code+'\',this);return false;">选为备选股</a></li>';

     if (page_title=='备选股')
        return '<li><a href="#" onclick="javascript:selStock(\''+code+'\',this);return false;">选为自选股</a></li>'+
               '<li><a href="#" onclick="javascript:delStock(\''+code+'\',this);return false;">取消关注</a></li>';

     if (page_title=='相关股' && code != default_stock)
        return '<li><a href="#" onclick="javascript:delRelation(\''+default_stock+'\',\''+code+'\',this);return false;">从相关股清除</a></li>';

     return '';
}


function valuation(result){

 if(list_table){
      list_table.destroy();
 }

 var resultTData = result.data.tableData;
 //第一次访问时，显示引导
 if(resultTData.length==0 && page_title=='备选股'){
     $("#guide").removeClass("hidden");
 }else{
     $('#example').removeClass("hidden");
 }

 list_table = $('#example').DataTable({
    "paging": false,
    data: resultTData,
    "order": [],
    "language": {
                "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Chinese.json"
            },
    columns: [
        { data: 'tag' },
        { data: 'code' },
        { data: 'name' },
        { data: 'industry' },
        { data: 'jlr_rate' },
        { data: 'roe' },
        { data: 'pcf' },
        { data: 'pe' },
        { data: 'pb' },
        { data: 'mvalue' },
        { data: 'ncode' }
    ],
    columnDefs: [
                  {
                      "targets": [0],
                      "width": "10",
                      "render": function(data, type, full) {
                          return '<span class="label label-warning">'+data+'</span>';
                      }
                  },
                  {
                      "targets": [4,5],
                      "visible": false,
                      "render": function(data, type, full) {
                          return data;
                      }
                  },
                  {
                      "targets": [6],
                      "render": function(data, type, full) {
                          return data;
                      }
                  },
                  {
                      "targets": [7],
                      "render": function(data, type, full) {
                          return data;
                      }
                  },
                  {
                      "targets": [8],
                      "render": function(data, type, full) {
                          return data;
                      }
                  },
                  {
                      "targets": [9],
                      "render": function(data, type, full) {
                          return '<a href="https://xueqiu.com/S/'+full['ncode']+'" target="_blank">'+data+'</a>';
                      }
                  },
                  {
                      "targets": [10],
                      "render": function(data, type, full) {
                          return '<a href="/stock/info/'+full['ncode']+'" target="_blank">详细</a> | <a href="#editBlogModal" data-stock="'+full['ncode']+'" data-toggle="modal">笔记</a>';
                      }
                  },
                  {
                      "targets": [11],
                      "render": function(data, type, full) {
                          return '\
                  <div class="btn-group pull-right">\
                    <button type="button" class="btn btn-default　btn-sm dropdown-toggle" data-toggle="dropdown"\
                            aria-haspopup="true" aria-expanded="false">\
                        操作 <span class="caret"></span>\
                    </button>\
                    <ul class="dropdown-menu">'
                        +getSubMenu(full['code'])+
                        '<li><a href="#editTagModal" data-stock="'+full['code']+'" data-tag="'+full['tag']+'" data-toggle="modal">标注</a></li>'+
                        '<li><a href="#relationModal" data-stock="'+full['code']+'" data-name="'+full['name']+'" data-toggle="modal">行业对比</a></li>'+
                    '</ul>\
                  </div>';

                      }
                  },
        ]

    });

}

//加载完毕自动执行
$(function(){

mystock_ajax_option.success = valuation;

$.ajax(mystock_ajax_option);

});