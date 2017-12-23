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

//解析url地址
function parseURL(url) {
   var a =  document.createElement('a');
   a.href = url;
   return {
       source: url,
       protocol: a.protocol.replace(':',''),
       host: a.hostname,
       port: a.port,
       query: a.search,
       params: (function(){
           var ret = {},
               seg = a.search.replace(/^\?/,'').split('&'),
               len = seg.length, i = 0, s;
           for (;i<len;i++) {
               if (!seg[i]) { continue; }
               s = seg[i].split('=');
               ret[s[0]] = s[1];
           }
           return ret;
       })(),
       file: (a.pathname.match(/\/([^\/?#]+)$/i) || [,''])[1],
       hash: a.hash.replace('#',''),
       path: a.pathname.replace(/^([^\/])/,'/$1'),
       relative: (a.href.match(/tps?:\/\/[^\/]+(.+)/) || [,''])[1],
       segments: a.pathname.replace(/^\//,'').split('/')
   };
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


function onCommentEdit(id,pid){
      var c = $("#"+id+"").html().replace(/\<br\>/g,'\n');
      var content_em = $("div#comment textarea[name='content']");
      content_em.val(c);
      $("div#comment #comment-id").val(pid);
}

