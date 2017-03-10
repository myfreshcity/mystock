
var requestOption = {
  code : $('#stock_code').val(),
  quarter : 0,
  pType : 1
};

var homePage = {quarter:0};
var currentTable;
var ajaxOption;
var columnList = [{'title':'报告日期'}];

var tableOption = {
        deferRender:    true,
        scrollY:        300,
        scrollX:        true,
        scrollCollapse: true,
        scroller:       true,
        //fixedHeader: true,
        //fixedColumns: true,
        paging: false,
        ordering: false,
        searching: false
};


function clearTable(){
    if(homePage.t0table) {homePage.t0table.destroy();delete homePage.t0table;}
    if(homePage.t1table) {homePage.t1table.destroy();delete homePage.t1table;}
    if(homePage.t2table) {homePage.t2table.destroy();delete homePage.t2table;}
    if(homePage.t3table) {homePage.t3table.destroy();delete homePage.t3table;}
}

function changePeriod(quarter){
    homePage.quarter = quarter;
    renderByColumn(quarter);
    //var column = currentTable.column($(this).attr('data-column'));
    //column.visible(!column.visible());

    //clearTable();
    //homePage.getData();
    //currentTable.ajax.reload();
}

function renderByColumn(quarter){
    var cols = currentTable.columns();
    for(var c in cols[0]){
        var cc = currentTable.column(c);
        var chh = $(cc.header()).html();
        if((quarter === 4 && chh.indexOf("-12-")>0)
            || (quarter === 3 && chh.indexOf("-09-")>0)
            || (quarter === 2 && chh.indexOf("-06-")>0)
            || (quarter === 1 && chh.indexOf("-03-")>0)
            || c === '0'
            || quarter === 0){
            cc.visible(true);
         }else{
            cc.visible(false);
         }
    }
}

function changePtype(pType){
    requestOption.pType = pType;
    clearTable();
    homePage.getData();
    //currentTable.ajax.reload();
}

function getMainData() {
    homePage.getData=getMainData;
    if(homePage.t0table){
        homePage.t0table.draw();
        currentTable = homePage.t0table;
    }else{
        var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/detail/report/mainJson',
    data:requestOption,
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {
        $('#t0').html(renderNewTable(result));
        var tObject = jQuery.extend(true, {}, tableOption);
        homePage.t0table = $('#t0').DataTable(tObject);
        currentTable = homePage.t0table;
        renderByColumn(homePage.quarter);
     }
    });
    }
 }

function getAssetData() {
    homePage.getData=getAssetData;
    if(homePage.t1table){
        homePage.t1table.draw();
        currentTable = homePage.t1table;
    }else{
        var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/detail/report/assetJson',
    data:requestOption,
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {
        $('#t1').html(renderNewTable(result));
        var t1Object = jQuery.extend(true, {}, tableOption);
        homePage.t1table = $('#t1').DataTable(t1Object);
        currentTable = homePage.t1table;
        renderByColumn(homePage.quarter);
     }
    });
    }
 }

function getIncomeData() {
    homePage.getData=getIncomeData;
    if(homePage.t2table){
        homePage.t2table.draw();
        currentTable = homePage.t2table;
    }else{
        var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/detail/report/incomeJson',
    data:requestOption,
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {
        $('#t2').html(renderNewTable(result));
        var t2Object = jQuery.extend(true, {}, tableOption);
        homePage.t2table = $('#t2').DataTable(t2Object);
        //homePage.t2table.columns.adjust().draw();
        //new $.fn.dataTable.FixedColumns( homePage.t2table, {} );
        currentTable = homePage.t2table;
        renderByColumn(homePage.quarter);
     }
    });
    }
 }


function getCashData() {
    homePage.getData = getCashData;
    if(homePage.t3table){
        homePage.t3table.draw();
        currentTable = homePage.t3table;
    }else{

    var aj = $.ajax( {
    url:$SCRIPT_ROOT + '/detail/report/cashJson',
    data:requestOption,
    type:'get',
    cache:false,
    dataType:'json',
    success:function(result) {
       $('#t3').html(renderNewTable(result));
       homePage.t3table = $('#t3').DataTable(tableOption);
       currentTable = homePage.t3table;
       renderByColumn(homePage.quarter);
     }
    });
    }
 }

function renderNewTable(result){
        var newTable = '<thead><tr><th>报告日期</th>';
        // below use the first row to grab all the column names and set them in <th>s
        $.each(result.cols, function(key, value) {
            newTable += "<th>" + value + "</th>";
        });
        newTable += "</tr></thead><tbody>";

        // then load the data into the table
        $.each(result.tableData, function(key, row) {
             newTable += "<tr>";
              $.each(row, function(key, fieldValue) {
                   newTable += "<td>" + fieldValue + "</td>";
              });
             newTable += "</tr>";
        });
       newTable += '</tbody>';
        return newTable;
}


$(function(){

$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
      var key = $(e.target).attr("href");
      if(key === "#cash"){
        //homePage.t3table.draw();
        getCashData();
      }else if(key === "#income"){
        getIncomeData();
        //homePage.t2table.draw();
      }else if(key === "#asset"){
        getAssetData();
        //homePage.t1table.draw();
      }else{
        //homePage.t0table.draw();
        getMainData();
      }
});

$('#myTab a:last').tab('show');

});

