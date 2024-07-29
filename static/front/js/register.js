var RegisterHandler = function (){

}

RegisterHandler.prototype.listenSendCaptchaEvent = function () {
    var callback = function (event) {
        //通过$()将原生的JS对象：this=>jQuery对象
        var $this = $(this)
        //阻止默认点击事件
        event.preventDefault();
        var email = $("input[name='email']").val();//获取输入的邮箱
        var reg = /^\w+((.\w+)|(-\w+))@[A-Za-z0-9]+((.|-)[A-Za-z0-9]+).[A-Za-z0-9]+$/;//邮箱的正则表达式
        if (!email || !reg.test(email)){
            alert("请输入正确格式的邮箱！");
            return;
        }
        //满足上述条件就发送ajax请求
        zlajax.get({
            url:"/email/captcha?email="+email,
            success: function (result) {
                if(result['code']==200){
                    console.log("邮件发送成功");
                    //取消按钮的点击事件
                    $this.off("click");
                    //添加禁用状态
                    $this.attr("disabled","disabled")
                    //开始倒计时
                    var countdown =6; //设置倒计时时间
                    var interval =setInterval(function(){
                        if(countdown>0){
                            $this.text(countdown);//倒计时大于就接着倒计时
                        }else{
                            $this.text("发送验证码");
                            $this.attr("disabled",false);//倒计时结束就返回发送验证码按钮并取消禁用状态
                            $this.on("click",callback); //重新绑定点击状态
                            clearInterval(interval) //清理定时器
                        }
                        countdown--;
                    },1000);
                }else {
                    var message = result['message'];
                    alert(message);
                }
            }

        })

    }
    $("#email-captcha-btn").on("click",callback); // 获取发送验证码的按钮   #寻找id为该符号后面内容的元素
}//创建一个类,这里功能为点击发送验证码按钮，就发送验证码，并且启动倒计时

RegisterHandler.prototype.listenGraphCaptchaEvent = function(){
    $("#captcha-img").on("click",function () {
        console.log("点击了图形验证码");
        var $this = $(this);
        var src = $this.attr("src");
        //解决老的浏览器因url相同导致图形验证码点击不会重新发送请求，导致图形验证码点击后不更新 /graph/captcha ==>/graph/captcha？sign=Math.random()
        let new_src = zlparam.setParam(src,"sign",Math.random())
        $this.attr("src",new_src);
    });
}//这个方法实现点击图形验证码就换一个图形验证码

RegisterHandler.prototype.listenSubmitEvent = function(){
    $("#submit-btn").on("click",function (event) {
        event.preventDefault();//阻止默认点击事件
        var email = $("input[name='email']").val();
        var email_captcha =$("input[name='email-captcha']").val();
        var username =$("input[name='username']").val();
        var password =$("input[name='password']").val();
        var repeat_password = $("input[name='repeat-password']").val();
        var graph_captcha =$("input[name='graph-captcha']").val();

        //如果是商业项目，一定要先验证这些数据是否正确，这里没有编写验证相关的前端代码
        zlajax.post({
            url:"/register",
            data:{
                "email":email,
                "email_captcha":email_captcha,
                "username":username,
                password,// <=>"password":password
                repeat_password,
                graph_captcha

            },//将上面获取的数据直接发送到服务器，data需要更编写表单时的名称一致
            success:function (result) {
               // console.log(result);
                if(result['code']==200){
                    window.location="/login"; //注册成功便跳转到登录页面
                }else{
                    alert (result['message']);
                }
            }
        })
    });
}


RegisterHandler.prototype.run = function () {
    this.listenSendCaptchaEvent();
    this.listenGraphCaptchaEvent();
    this.listenSubmitEvent();
}//运行类

//jQuery(function(){})<=>$(function(){})  将这个函数在整个网页加载完成以后再执行
$(function () {
    var handler = new RegisterHandler();
    handler.run()
})