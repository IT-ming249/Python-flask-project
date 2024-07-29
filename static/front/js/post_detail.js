$(function(){
    //初始化代码高亮
    hljs.highlightAll() //hlijs是highlig.js自带的全局变量
    $("#comment-btn").on('click',function (event) {
        event.preventDefault();
        var $this = $(this);
        //判断用户有没有登录
        var user_id =$this.attr("data-user-id");
        if(!user_id || user_id ==" "){
            window.location="/login";
            return;
        }

        var content = $("#comment-textarea").val();
        //接下来获取帖子id
        var post_id = $this.attr("data-post-id");

        zlajax.post({
            url:"/comment",
            data:{content,post_id},
            success: function(result){
                if (result['code']==200){
                    window.location.reload();
                }else{
                    alert(result['message']);
                }
            }
        })

    });
});