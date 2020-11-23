from .output_field import OutputField
import json
import flask
from flask import Response
from flask import jsonify
from time import sleep


class OutputStreamGraphField(OutputField):
    def __init__(self, field_name, default):
        super(OutputStreamGraphField, self).__init__(field_name, default)

    def set_output(self, value):
        self.value = value

    def generate_inputs(self):
        return f"""
        <canvas id="{self.field_name}" width="400" height="400"></canvas>
        <script>

        """ + f""" 
        var {self.field_name}_request = new XMLHttpRequest();
        var {self.field_name}_readed_data = 0; 
        {self.field_name}_request.open("get", "/{self.field_name}_stream", true);
        {self.field_name}_request.send();
        """ + """ 

        """ + f""" 
        var ctx = document.getElementById('{self.field_name}').getContext('2d');
        var {self.field_name}_chart""" + """ = new Chart(ctx, {
            type: 'line',
            data: {
                "datasets": [{
                    "label": " """ + f"""{self.field_name}""" + """ ",
                    "fill": true,
                    "borderColor": "rgb(75, 192, 192)",
                    "lineTension": 0.1,
                    "data": []
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'realtime',   // x axis will auto-scroll from right to left
                        realtime: {         // per-axis options
                            duration: 20000,    // data in the past 20000 ms will be displayed
                            refresh: 1000,      // onRefresh callback will be called every 1000 ms
                            delay: 1000,        // delay of 1000 ms, so upcoming values are known before plotting a line
                            pause: false,       // chart is not paused
                            ttl: undefined,     // data will be automatically deleted as it disappears off the chart

                            // a callback to update datasets
                            onRefresh: function(chart) {
                                """ + f""" 
                                var response = {self.field_name}_request.responseText.split("\\n")
                                response = [response[{self.field_name}_readed_data]];
                                {self.field_name}_readed_data += response.length;
                                """ + """ 
                                for (var item in response) {
                                    console.log(response[item]);
                                    """ + f""" 
                                    chart.data.datasets[0].data.push(""" + """{
                                        x: Date.now(),
                                        y: JSON.parse(response[item]).value
                                    });
                                } 
                                """ + """
                                //    Array.prototype.push.apply(chart.data.datasets[0].data, data);
                            }
                        }
                    }]
                },
                plugins: {
                    streaming: {            // per-chart option
                        frameRate: 30       // chart is drawn 30 times every second
                    }
                }
            },
        });
        </script>
        """

    def add_route(self, app: flask.Flask):
        @app.route(f'/{self.field_name}_stream')
        def __tmp():
            return Response(self.__gen(), mimetype='application/json')

    def __gen(self):
        separators = (",", ":")
        while True:
            for val in self.value:
                text = json.dumps({'value': val}, separators=separators) + "\n"
                yield text
