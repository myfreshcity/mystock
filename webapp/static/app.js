function toThousands(num) {
    var num = (num || 0).toString(), result = '';
    while (num.length > 3) {
        result = ',' + num.slice(-3) + result;
        num = num.slice(0, num.length - 3);
    }
    if (num) { result = num + result; }
    return result;
}

//格式化营收数据
function formatRevenceVal(num){
   return toThousands(Math.floor(num/1000000));
}

function addStock(code){
    bootbox.confirm("确认添加该股票吗？", function(result){
     /* your callback code */
      if(result==true){
            var aj = $.ajax( {
          url:$SCRIPT_ROOT + '/stock/add',
          data:{
                   code : code
          },
          type:'post',
          cache:false,
          dataType:'json',
          success:function(data) {
              if(data.msg =="true" ){
                  bootbox.alert('添加成功');
              }else{
                  bootbox.alert(data.msg);
              }
           }
          });
      }
     })
}