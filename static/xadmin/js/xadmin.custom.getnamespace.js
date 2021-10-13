$('#id_k8s_api').change(function(){
    var k8s_id = $("#id_k8s_api").val();
    $.ajax({
        url: "/api/kube/ns/getinfo",
        type: "GET",
        cache: false,
        data: {
            "kube_id": k8s_id,
            'nameonly': 'true'
        },

        //渲染返回的模块结果option
        success: function (data) {
            for (var i in data['message']) {
                console.log(i);
                $("#id_namespace").append(new Option(data['message'][i],data['message'][i]));
            }
        }
    })
});
