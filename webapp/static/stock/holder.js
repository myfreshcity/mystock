var holderPage = {
  report_date:'',
  forward_dirc:''
}
//加载完毕自动执行
$(function(){

    var code = $stock.code // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.

    var modal = $(this)
    modal.find('#holderModalLabel').text('机构持股情况 -' +code );
    var valuation_chart = modal.find('.modal-body #valuation_chart');
    var value_chart = modal.find('.modal-body #value_chart');
    var holder_data_table = modal.find('.modal-body #data_table');

    modal.find('.modal-body #m1_link').on("click",updateHolderData);
    modal.find('.modal-body #m1_link_pre').on("click",preData);
    modal.find('.modal-body #m1_link_next').on("click",nextData);

    var holder_ajax_option =  {
    url:$SCRIPT_ROOT + '/detail/holderJson',
    data:{
             code : code,
             report_date: holderPage.report_date,
             forward_dirc: holderPage.forward_dirc
    },
    type:'get',
    cache:false,
    dataType:'json',
    success:valuation
    };

    function updateHolderData(){
        var aj = $.ajax( {
        url:$SCRIPT_ROOT + '/setting/updateHolder/',
        data:{
                 code : code
        },
        type:'get',
        cache:false,
        dataType:'json',
        success:function(result){
             if(result.msg == true){
                 $.ajax(holder_ajax_option);
             }else{
                console.error(result.msg);
             }
            }
        });

     };

    function  preData(){
      holderPage.forward_dirc = 'pre';
      holder_ajax_option.data = {
             code : code,
             report_date: holderPage.report_date,
             forward_dirc: holderPage.forward_dirc
      };
      $.ajax(holder_ajax_option);
    }

    function  nextData(){
      holderPage.forward_dirc = 'next';
      holder_ajax_option.data = {
             code : code,
             report_date: holderPage.report_date,
             forward_dirc: holderPage.forward_dirc
      };
      $.ajax(holder_ajax_option);
    }

    $.ajax(holder_ajax_option);

  function valuation(res){
    var result = res.data;
    modal.find('#holderModalLabel').text('机构持股情况 -' + $stock.name);

    for(var i = 0; i　< result.length; i++) {
        var r_date = result[i]['r_date'];
        var data = result[i]['data'];
        var $h1=$('<h4>'+r_date+'</h4>');
        var $table1 = $('<table class="display" cellspacing="0" width="90%"></table>');
        render_table($table1,data)
        $('#table_div').prepend($table1).prepend($h1)
    }

  }

  function render_table(ele,table_data){
        ele.DataTable( {
            paging: false,
            data: table_data,
            "ordering": false,
            searching: false,
            columns: [
                { title: "报告日期"},
                { title: "流通股东" },
                { title: "流通股东编码" },
                { title: "持有比例(%)" },
                { title: "持有数量" },
                { title: "持股变动(%)" },
                { title: "持股变动(%)" }
            ],
            columnDefs: [
                      {
                          "targets": [0],
                          "width": "12%"
                      },
                      {
                          "targets": [1],
                          "render": function(data, type, full) {
                              return '<a href="'+$SCRIPT_ROOT + '/holder/'+full[2]+'" target="_blank">'+ data +'</a>';
                              //return '<a href="#holderTrackModal" data-stock="'+code+'" data-holder-name="'+full[1]+'" data-holder-code="'+full[2]+'" data-toggle="modal">'+data+'</a>';
                          }
                      },
                      {
                        "targets": [2],
                        "visible": false
                      },
                      {
                        "targets": [5],
                        "render": function(data, type, full){
                            var var_ele;
                            if(data=='-'){
                                var_ele = '<i class="glyphicon glyphicon-arrow-down" style="color:#FF0000;"></i>';
                            }else if(data=='+'){
                                var_ele = '<i class="glyphicon glyphicon-arrow-up" style="color:#008000;"></i>';
                            }else if(data=='0'){
                                var_ele = '-';
                            }else{
                                if(/^\-+/.test(data) && /^\-+/.test(full[6])){ //同为负数
                                    var_ele = '<span style="color:#FF0000;">'+data+'</span>';
                                 }else if(!/^\-+/.test(data) && !/^\-+/.test(full[6])){ //同为正数
                                    var_ele = '<span  style="color:#008000;">'+data+'</span>';
                                 }else{
                                    var_ele = '<span  style="color:#D2691E;">'+data+'('+full[6]+')</span>';
                                 }
                            }
                            return var_ele;
                        }
                      },
                       {
                        "targets": [6],
                        "visible": false
                      },
            ]
        } )
  }

});