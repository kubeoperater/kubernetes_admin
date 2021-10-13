function cleanresult() {
    document.getElementById("resultAlert").innerHTML = "";
}

function selectNamespaces() {
    var k8s_apiport = $("#select-k8s").val();
    $("#select-namesapces").find("option:not(:first)").remove();
    $.ajax({
        url: "/api/kube/ns/getinfo",
        type: "GET",
        cache: false,
        data: {
            "kube_id": k8s_apiport,
            'nameonly': 'true'
        },

        //渲染返回的模块结果option
        success: function (data) {
            for (var i in data['message']) {
                $("#select-namesapces").append(new Option(data['message'][i]));
            }
        }
    })
}

function submite_select(page_number) {
    var k8s_apiport = $("#select-k8s").val();
    var k8s_namespaces = $("#select-namesapces").val();
    var csrftoken  = $.cookie('csrftoken');
    var resource_type = $("#select-kind").val();
    switch(resource_type){
            case "pod":
                url1 = "/k8sapp/getpods/";
                break;
            case "deployment":
                url1 = "/k8sapp/getdep/";
                break;
            case "replicaset":
                url1 = "/k8sapp/getreps/";
               break;
            case "replicationcontroller":
                url1 = "/k8sapp/getrepc/";
                break;
            case "statefulset":
                url1 = "/k8sapp/getstafu/";
                break;
            case "service":
                url1 = "/k8sapp/getsvc/";
                break;
            default:
                url1 = "/k8sapp/getpods/";
                break;
        }
    $.ajax(
        {
        url: url1,
        type: "POST",
        cache: false,
        data: {
            'csrfmiddlewaretoken': csrftoken,
            "k8s_apiport": k8s_apiport,
            'k8s_namespaces': k8s_namespaces,
            'resource_type' : resource_type,
            'page': page_number,
        },
        //渲染返回的模块结果option
        success: function(data) {
            let resultListWrapper=document.getElementById("resultAlert");
            let pagelistWrapper=document.getElementById("resultPagesplit");
            resultListWrapper.innerHTML=data['record_formRendering'];
            pagelistWrapper.innerHTML=data['pagelistRendering'];
        }
    })
}

function ssh_contain() {
    // 选中ansible主机
    var k8s_apiport = $("#select-k8s").val();
    var k8s_namespaces = $("#select-namesapces").val();
    var pod_name = $("#select-pod").val();
    var csrftoken  = $.cookie('csrftoken');
    $.ajax({
        url: "/k8sapp/connectpod/",
        type: "POST",
        cache: false,
        data: {
            'csrfmiddlewaretoken': csrftoken,
            "k8s_apiport": k8s_apiport,
            'k8s_namespaces': k8s_namespaces,
            "k8s_pod" : pod_name,
        },
        //渲染返回的模块结果option
        success: function (data) {
            document.getElementById("resultAlert").innerHTML = "";
            $('#resultAlert').append(data['message']);

        }
    })
}


function searchresult(){
    var k8s_apiport = $("#select-k8s").val();
    var k8s_namespaces = $("#select-namesapces").val();
    var resource_type = $("#select-kind").val();
    var searchkeyobj = $("#search-keywords")
    var searchkey = searchkeyobj.val();
    var searchkeypre = searchkeyobj.attr('placeholder');
    if ( searchkey === ""){
        if ( searchkeypre != '搜索pod应用'){
            searchkey = searchkeypre
        }else{
            alert('请输入搜索关键字');
            return false;
        }
    }
    switch(resource_type){
            case "pod":
                url1 = "/k8sapp/getpods/";
                break;
            case "deployment":
                url1 = "/k8sapp/getdep/";
                break;
            case "replicaset":
                url1 = "/k8sapp/getreps/";
               break;
            case "replicationcontroller":
                url1 = "/k8sapp/getrepc/";
                break;
            case "statefulset":
                url1 = "/k8sapp/getstafu/";
                break;
            case "service":
                url1 = "/k8sapp/getsvc/";
                break;
            default:
                url1 = "/k8sapp/getpods/";
                break;
        }
    $.ajax(
        {
        url: url1,
        type: "GET",
        cache: false,
        data: {
            "k8s_apiport": k8s_apiport,
            'k8s_namespaces': k8s_namespaces,
            'resource_type' : resource_type,
            'searchkey': searchkey,
        },
        //渲染返回的模块结果option
        success: function(data) {
            let resultListWrapper=document.getElementById("resultAlert");
            let pagelistWrapper=document.getElementById("resultPagesplit");
            resultListWrapper.innerHTML=data['record_formRendering'];
            pagelistWrapper.innerHTML=data['pagelistRendering'];
        }
    })
}