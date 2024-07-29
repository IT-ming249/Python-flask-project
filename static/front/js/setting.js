var SettingHandler = function () {}
SettingHandler.prototype.listenAvatarUploadEvent =function () {
    $("#avatar-input").on("change",function () {
        var image = this.files[0];
        //console.log(image);
        var formData = new FormData();
        formData.append("image",image);
        zlajax.post({
            url:"/avatar/upload",
            data:formData,
            // 如果适用jQury上传文件，那么还需要指定以下两个参数
            processData: false,
            contentType:false,
            success: function (result) {
                console.log(image)
                console.log(result)
                //上传成功的图片可以在media/avatar下找到
                if (result['code']==200){
                    // result = {"code":200, "data";{"avatar":"/xxx"}}
                    var avatar = result['data']['avatar'];
                    var avatar_url = "/media/avatar/"+avatar;
                    $("#avatar-img").attr("src", avatar_url);
                }
            }
        })
    });
}

SettingHandler.prototype.listenSubmitEvent = function(){
    $("#submit-btn").on("click",function(event){
        event.preventDefault();
        var signature = $("#signagure-input").val(); //$("input[name='signagure-input']").val(); 看清楚是name还是id
        if(!signature){
            alert("提交成功");
            return;
        }//如果用户没有提交新的签名说明用户不对个性签名进行修改
        if (signature && (signature.length >50 || signature.length <1)){
            alert("签名长度必须在1-50字之间");
            return;
        }
        zlajax.post({
            url: "/profile/edit",
            data: {signature},
            success:function (result) {
                if(result['code']==200){
                    alert("新的个性签名提交成功");
                }else {
                    alert(result['message']);
                }

            }
        })
    });
}


SettingHandler.prototype.run = function(){
    this.listenAvatarUploadEvent();
    this.listenSubmitEvent();
}

$(function(){
    var handler = new SettingHandler();
    handler.run();
})