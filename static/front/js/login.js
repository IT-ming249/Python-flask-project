var LoginHandler = function () {}

LoginHandler.prototype.listenSubmitEvent = function (){
    $("#submit-btn").on("click",function (event) {
        event.preventDefault();//阻止默认点击事件
        //然后获取邮箱账号和密码,以及是否点击“记住我”
        var email = $("input[name='email']").val();
        var password =$("input[name='password']").val();
        var remember =$("input[name='remember']").prop("checked");
        //console.log(email,password,remember) //检查上述数据是否能拿到，能拿到接下来就发送ajax请求
        zlajax.post({
            url: "/login",
            data:{
                email,
                password,
                remember: remember?1:0
            },
            success: function (result) {
                if(result['code']==200){
                    //获取jwt_tioken
                    var token= result['data']['token'];
                    //获取序列化orm传入的user数据
                    var user = result['data']['user'];
                    localStorage.setItem("JWT_TOKEN_KEY",token); //jwt_token保存到本地存储中
                    localStorage.setItem("USER_KEY",JSON.stringify(user));//user是一个js对象，需要将它变成js格式的字符串
                    console.log(user);
                    window.location = "/" //登录成功则跳转到首页
                }else {
                    alert(result['message']);
                }

            }
            })
    });
}




LoginHandler.prototype.run = function(){
    this.listenSubmitEvent();
}

$(function () {
    var handler = new LoginHandler();
    handler.run();
});