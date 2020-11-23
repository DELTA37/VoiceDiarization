

class Creator(object):
    def __init__(self, algo_name, algo_fn, fields, output_fields):
        super(Creator, self).__init__()
        self.algo_name = algo_name
        self.algo_fn = algo_fn
        self.fields = {field.field_name: field for field in fields}
        self.output_fields = {output_field.field_name: output_field for output_field in output_fields}

    def start_server(self, host='127.0.0.1', port=8000, debug=False, **options):
        from werkzeug.datastructures import ImmutableMultiDict
        from flask import Flask, render_template, render_template_string, request, redirect, url_for
        app = Flask(self.algo_name)

        @app.route('/', methods=['GET', 'POST'])
        def main():
            if request.method == 'POST':
                data = request.files.to_dict()
                data.update(request.form.to_dict())
                data.update(request.args.to_dict())
                if debug:
                    print(data)

                for key in data.keys():
                    data[key] = self.fields[key].parse_request(data[key])

                output_data = self.algo_fn(**data)

                for key in output_data.keys():
                    self.output_fields[key].set_output(output_data[key])

                fields = self.output_fields
                submit_button = """
                <button type="submit" class="btn btn-default btn-lg" formaction="/" formmethod="get">Home</button>
                """
            else:
                submit_button = """
                <button type="submit" class="btn btn-default btn-lg">Submit</button>
                """
                fields = self.fields

            return render_template_string(f'''
                <!doctype html>
                <html>
                    <head>
                        <title>{self.algo_name}</title>
                        <!-- Latest compiled and minified CSS -->
                        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">

                        <!-- jQuery library -->
                        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>

                        <!-- Latest compiled JavaScript -->
                        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
                        
                        <!-- Latest highlight.js library -->
                        <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/styles/default.min.css">
                        <script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/highlight.min.js"></script>

                        <!-- Font Awesome -->
                        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css">
                        <!-- Google Fonts -->
                        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap">
                       
                        <!-- Bootstrap tooltips -->
                        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.4/umd/popper.min.js"></script>
                        
                        <!-- ChartJS -->
                        <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.26.0/moment.min.js"></script>
                        <script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
                        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-streaming@1.8.0/dist/chartjs-plugin-streaming.js"></script>
                        
                        <!-- Latest tree.js library -->
                        <script src="https://threejs.org/build/three.js"></script>
                        <script src="http://threejs.org/examples/js/loaders/STLLoader.js"></script> 
                        <script src="https://threejs.org/examples/js/loaders/OBJLoader.js"></script>
                        <script src="https://threejs.org/examples/js/controls/OrbitControls.js"></script>

                    ''' + '''
                        <script>
                            function downloadBlob(blob, filename) {
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = filename || 'download';
                                const clickHandler = () => {
                                    setTimeout(() => {
                                        URL.revokeObjectURL(url);
                                        this.removeEventListener('click', clickHandler);
                                    }, 150);
                                };
                                a.addEventListener('click', clickHandler, false);
                                return a;
                            }
                        </script>
                    ''' + f'''
                    </head>
                    <body background="http://cdn.backgroundhost.com/backgrounds/subtlepatterns/starring.png">
                        <div class="container">
                        <div class="row">
                        <div class="col-sm-1"></div>
                        <div class="col-sm-10">
                        <center>
                            <p>
                                <font color="white">
                                    <h1><a href="/">{self.algo_name}</a></h1>
                                </font> 
                            </p>
                            <form method=post enctype=multipart/form-data class="form-horizontal" id="gdflask_test">
                                <div class="form-group">
                                    {"".join([field.create_html() for field in fields.values()])}
                                </div>
                                <div class="form-group">
                                    {submit_button}
                                </div>
                            </form>
                        </center>
                        </div>
                        </div>
                        <div class="col-sm-1"></div>
                        </div>
                    </body>
                </html>
            ''')

        for field in self.fields.values():
            field.add_route(app)

        for output_field in self.output_fields.values():
            output_field.add_route(app)

        @app.route('/process', methods=['POST'])
        def process():
            return {}

        app.run(host=host, port=port, debug=debug, **options)
