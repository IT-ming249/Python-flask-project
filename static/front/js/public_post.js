//富文本编辑器
var PublicPostHandler = function () {
    var csrf_token = $("meta[name='csrf-token']").attr("content") //post请求上传图片需要csrf_token
    //上传图片功能
    var editor = new window.wangEditor('#editor');
    editor.config.uploadImgServer = "/post/image/upload";
    editor.config.uploadFileName = "image";  //文件名来自forms中的验证表单中
    // 1. 放到请求体中
    // 2. 放到请求头中X-CSRFToken  固定写法
    // 再和cookie中的csrf_token进行对比
    editor.config.uploadImgHeaders = {
        "X-CSRFToken": csrf_token
    }
    editor.config.uploadImgMaxSize = 1024*1024*5;
    editor.create();
    this.editor = editor;
}

//发布帖子的构造函数
PublicPostHandler.prototype.listenSubmitEvent =function(){
    var that = this;
    $("#submit-btn").on("click", function(event){
       event.preventDefault();
       var tittle = $("input[name='title']").val();
       var board_id = $("select[name='board_id']").val();
       //获取帖子内容需要查看wangEditor官网中的获取html
       var content = that.editor.txt.html();
       zlajax.post({
           url:"/post/public",
           data:{
               'tittle':tittle,
               'board_id':board_id,
               'content':content
           },
           success:function (result) {
               if(result['code']==200){
                   alert('帖子发表成功');
                   let data =result['data'];
                   let post_id = data['id'];
                   window.location="/post/detail/"+post_id;
               }else {
                   alert(result['message']);
               }
           }
       });
    });
}



PublicPostHandler.prototype.run = function () {
    this.listenSubmitEvent();
}

$(function() {
    var handler = new PublicPostHandler();
    handler.run();
});