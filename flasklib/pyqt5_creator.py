

class Creator(object):
    def __init__(self, algo_name, algo_fn, fields, output_fields):
        super(Creator, self).__init__()
        self.algo_name = algo_name
        self.algo_fn = algo_fn
        self.fields = {field.field_name: field for field in fields}
        self.output_fields = {output_field.field_name: output_field for output_field in output_fields}

    def start_server(self):
        from werkzeug.datastructures import ImmutableMultiDict
        from PyQt5.QtCore import QUrl
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage
        from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
        import sys
        import gevent
        import gevent.pywsgi

        class WebView(QWebView):
            def __init__(self):
                super(WebView, self).__init__()

                self.load(QUrl("http://localhost:5000/"))
                # self.connect(self, SIGNAL("clicked()"), self.closeEvent)

            def closeEvent(self, event):
                self.deleteLater()
                app.quit()
                print("closing gui")
                g.kill(gevent.GreenletExit, block=False)
                f.kill(gevent.GreenletExit, block=False)
                print("are gui and webserver alive? ", g.dead, f.dead)

        class PyQtGreenlet(gevent.Greenlet):
            def __init__(self, app):
                gevent.Greenlet.__init__(self)
                self.app = app

            def _run(self):
                while True:
                    self.app.processEvents()
                    while self.app.hasPendingEvents():
                        self.app.processEvents()
                        gevent.sleep(0.001)

        from flask import Flask, render_template, render_template_string, request, redirect, url_for
        app = Flask(self.algo_name)

        @app.route('/', methods=['GET', 'POST'])
        def main():
            if request.method == 'POST':
                data = request.files.to_dict()
                data.update(request.form.to_dict())

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

                        <!-- Latest tree.js library -->
                        <script src="https://threejs.org/build/three.js"></script>
                        <script src="http://threejs.org/examples/js/loaders/STLLoader.js"></script> 
                        <script src="https://threejs.org/examples/js/loaders/OBJLoader.js"></script>
                        <script src="https://threejs.org/examples/js/controls/OrbitControls.js"></script>

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
                            <form method=post enctype=multipart/form-data class="form-horizontal">
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

        http_server = gevent.pywsgi.WSGIServer(('', 5000), app)
        f = gevent.spawn(http_server.serve_forever)

        app = QApplication(sys.argv)
        window = WebView()
        window.show()

        g = PyQtGreenlet.spawn(app)
        gevent.joinall([f, g])
