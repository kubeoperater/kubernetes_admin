window.onload = getpodlogs;
// window.setInterval(getpodlogs,1000);
function getpodlogs() {
    $.ajax(
    {
    url: '/k8sapp/getpodlog/',
    type: "GET",
    cache: false,
    data: {
        "k8s_apiport": k8s_apiport,
        'k8s_namespaces': k8s_namespaces,
        'k8s_pod': k8s_pod,
        'container_name':container_name
    },
    //渲染返回的模块结果option
    success: function(data) {
        let logpre=document.getElementById("log-container-pre");
        logpre.innerHTML='';
        logpre.append(data['message']);
    }
    })
}