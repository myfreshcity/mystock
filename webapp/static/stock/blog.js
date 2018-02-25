var stockCode = null;
var curPage = 1;
var totalPage = 0;
var flag = true;

var winH = $(window).height(); //页面可视区域高度
var scrollHandler = function () {
  var pageH = $(document.body).height();
  var scrollT = $(window).scrollTop(); //滚动条top
  var aa = (pageH - winH - scrollT) / winH;
  if (aa < 0.02) {//0.02是个参数
    // 避免不停调用函数 进行的加载
    if (curPage<=totalPage && flag){
      // 滑动到地部 调用函数 加载数据
      more();
      flag = false;
    }
  }
}

//股票查找
  $('#bs_cname').typeahead({

          source: function (query, process) {
            return $.ajax({
                url: $SCRIPT_ROOT + '/stock/query',
                type: 'get',
                data: { query: query },
                dataType: 'json',
                beforeSend: function () { },
                complete: function (){ },
                success: function (data) {
                    //重置数据
                    //stockCode.attr('value', '');
                    //modal.find('.modal-body #flash_msg').text('');
                    var resultList = data.result.map(function (item) {
                        var aItem = {id: item.id, name: item.name,ncode: item.ncode};
                        return JSON.stringify(aItem);
                    });
                    return process(resultList);

                }
            });

        },
            /**
         * 使用指定的方式，高亮(指出)匹配的部分
         *
         * @param obj 数据源中返回的单个实例
         * @returns {XML|void|string|*} 数据列表中数据的显示方式（如匹配内容高亮等）
         */
        highlighter: function (obj) {
            var item = JSON.parse(obj);
            var query = this.query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, '\\$&');
            return item.name.replace(new RegExp('(' + query + ')', 'ig'), function ($1, match) {
                return  '<strong>' + match + '</strong>'
            }) + '&nbsp;&nbsp;'
            + item.id.replace(new RegExp('(' + query + ')', 'ig'), function ($1, match) {
                return match
            });
        },
        /**
         * 在选中数据后的操作，这里的返回值代表了输入框的值
         *
         * @param obj
         * @return 选中后，最终输入框里的值
         */
        updater: function (obj) {
            var item = JSON.parse(obj);
            //stockCode = item.id;
            $('#bs_btn').prop('disabled', false);
            $('#bs_code').attr('value', item.id);
            return item.name+' '+item.id;
        },

        minLength:1,
        items: 10,   //显示10条
        delay: 800,  //延迟时间
});



function addBlogCallBack(data){
  console.log('success');
  $("#comment-list").prepend(makeCommentItem(data));
}



function more(){
  if(curPage<=totalPage){
    curPage++;
    appendComment();
  }
}

function appendComment() {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/queryComments',
    data:{
             code : stockCode,
             page : curPage
    },
    type:'post',
    beforeSend: function () { },
    complete: function (){ },
    cache:false,
    dataType:'json',
    success:function(result) {
       flag = true;
       for(var i=0,a;a=result.data[i++];){
          $("#comment-end-icon").before(makeCommentItem(a));
       }
     }
    });
  };


function queryComment() {
    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/stock/queryComments',
    data:{
             code : stockCode,
             page : curPage
    },
    type:'post',
    cache:false,
    dataType:'json',
    success:function(result) {

       totalPage = result.totalPage;
       if(totalPage==0){
        toastr.info('未发现新数据');
       }else{
       $('#comment-list li').not('#comment-end-icon').remove();
       }

       for(var i=0,a;a=result.data[i++];){
          $(window).scroll(scrollHandler);  //定义鼠标滚动事件
          $("#comment-end-icon").before(makeCommentItem(a));
       }
     }
    });
  };

function makeCommentItem(data){
    content =  data.content.replace(/\n/g,'<br/>');

    var _f = parseInt(data.flag);
    var _sc;

    //未指定股票时显示股票代码
    var checkVal=$("input:radio[name='optionsRadiosinline']:checked").val();
    if(checkVal=='option2'){
      _sc = data.date+' | '+ '<a href="'+$SCRIPT_ROOT +'/stock/blog/'+data.stock+'" target="_blank">'+data.stock+'</a>';
    }else{
        _sc = data.date;
    }

    var _c = '';
    if(_f<1) _c = 'class="timeline-inverted"';

    return   '<li '+_c+'>\
          <div class="timeline-badge"><i class="glyphicon glyphicon-check"></i></div>\
          <div class="timeline-panel">\
            <div class="timeline-heading">\
              <p><small class="text-muted"><i class="glyphicon glyphicon-time"></i>'+_sc+'</small></p>\
            </div>\
            <div class="timeline-body">\
              <p>'+data.content+'</p>\
            </div>\
          </div>\
        </li>'
}


function getStockComments(){
    var checkVal=$("input:radio[name='optionsRadiosinline']:checked").val() ;
    if(checkVal=='option1'){
    //指定股票
    stockCode = $('#bs_code').val();
    }else{
    //所有股票
    stockCode = null;
    curPage = 1;
    queryComment();
    }

}