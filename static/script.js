const indexLabels = {
    'redBtn': 'red',
    'blueBtn': 'blue',
    'greenBtn': 'green',
    'rainbowBtn': 'rainbow',
    'stopBtn': 'all off',
    'defaultsBtn': 'default animation'
};
const serviceLabels = {
    'homeBtn': 'home',
    'rebootBtn': 'reboot device',
    'dashboardBtn': 'monitoring dashboard'
};

const requestIndexFunctions = {
    'redBtn': '/red',
    'blueBtn': '/blue',
    'greenBtn': '/green',
    'rainbowBtn': '/rainbow',
    'stopBtn': '/all off',
    'defaultsBtn': '/defaults'
};

// noinspection JSUnusedGlobalSymbols
function ajaxRequest(url) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url);

    xhr.onload = function () {

        if (xhr.status !== 200) {
            console.log('Request failed.  Returned status of: ' + xhr.status);
        } else {
            console.log('Response Text: ' + xhr.responseText);
        }
    };
    try {
        xhr.send();
        console.log('function status: ' + url.slice(1).toUpperCase());
        document.getElementById("status").innerHTML = url.slice(1).toUpperCase();
    } catch (e) {
        console.log(e)
    }
}

// noinspection JSUnusedGlobalSymbols
function goto(url) {
    location.href = url;
}

function setupIndexPage() {
    try {
        //document.getElementById('serviceBtn').setAttribute('onclick', "goto('/service',)");

        try {
            for (const id in requestIndexFunctions) {
                document.getElementById(id).setAttribute('onclick', "ajaxRequest(requestIndexFunctions[id], this)");
            }
        } catch (e) {
            console.log(e)
        }
        try {
            for (const id in indexLabels) {
                document.getElementById(id).innerHTML = indexLabels[id].toUpperCase();
            }
        } catch (e) {
            console.log(e)
        }
    } catch (e) {
        console.log(e)
    }
}

function setupServicePage() {
    try {
        document.getElementById('homeBtn').setAttribute('onclick', "goto('/',)");
        document.getElementById('dashboardBtn').setAttribute('onclick', "window.open('../dashboard')");
        document.getElementById('rebootBtn').setAttribute('onclick', "ajaxRequest('/reboot')");

        try {
            for (const id in serviceLabels) {
                document.getElementById(id).innerHTML = serviceLabels[id].toUpperCase();
            }
        } catch (e) {
            console.log(e)
        }
    } catch (e) {
        console.log(e)
    }
}

window.onload = function () {
    try {
        if (window.name === 'index') {
            setupIndexPage();
        }
        if (window.name === 'service') {
            setupServicePage();
        }
    } catch (e) {
        console.log(e)
    }
};
