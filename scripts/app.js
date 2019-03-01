

  //  var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var request = new XMLHttpRequest();
    var voltage_val = 0;
    var current_val = 0;
    var freq_val = 0;
    function call() {
        request.open('GET', 'http://localhost:8080/watch', true);
        request.onload = function () {
        var voltage_val;
        var current_val;
        var freq_val;
        // console.log(this.responseText);
        var data = JSON.parse(this.responseText);
        console.log(data["voltage_reading"]);
        console.log(data["current_reading"]);
        console.log(data["frequency_reading"]);
        voltage_val = $('#voltage_log').text(data["voltage_reading"]);
        current_val = $('#current_log').text(data["current_reading"]);
        freq_val = $('#frequency_log').text(data["frequency_reading"]);
        console.log("collected_voltage :" + voltage_val);
        console.log("collected_current :" + current_val);
        console.log("collected_frequency :" + freq_val);
    }
    request.send();
}
setInterval(call, 1000);





 