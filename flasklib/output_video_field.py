import os
import sys
from skimage.util import img_as_ubyte
import flask
import io
from PIL import Image
from flask import Response
from .output_field import OutputField
from time import sleep


class OutputVideoField(OutputField):
    def __init__(self, field_name, default, show_every=1):
        self.value = None
        self.show_every = show_every
        super(OutputVideoField, self).__init__(field_name, default)

    def set_output(self, value):
        self.value = value

    def generate_inputs(self):
        return f"""
        <img class="img-responsive" src="/{self.field_name}_stream" />
        """

    def add_route(self, app: flask.Flask):
        @app.route(f'/{self.field_name}_stream')
        def __tmp():
            return Response(self.__gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def __gen(self):
        while True:
            i = 0
            for val in self.value:
                i += 1
                img = Image.fromarray(img_as_ubyte(val))
                if i % self.show_every == 0:
                    file_object = io.BytesIO()
                    img.save(file_object, 'JPEG')
                    file_object.seek(0)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + file_object.read() + b'\r\n')
