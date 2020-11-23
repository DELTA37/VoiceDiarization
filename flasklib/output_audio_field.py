import flask
from flask import send_file, Response, make_response
from .output_field import OutputField
import soundfile as sf
from io import StringIO, BytesIO


class OutputAudioField(OutputField):
    def __init__(self, field_name, default):
        self.value = None
        super(OutputAudioField, self).__init__(field_name, default)

    def set_output(self, value):
        self.value = value

    def generate_inputs(self):
        return f"""
<audio controls>
    <source src="/{self.field_name}_view_wav" type="audio/mpeg">
    Your browser does not support the audio element.
</audio> 
        """

    def add_route(self, app: flask.Flask):
        @app.route(f'/{self.field_name}_view_wav')
        def __tmp():
            buf = BytesIO()
            sf.write(buf, self.value[0], self.value[1], format='wav', closefd=False)
            buf.seek(0)
            response = make_response(buf.getvalue())
            buf.close()
            response.headers['Content-Type'] = 'audio/wav'
            response.headers['Content-Disposition'] = 'attachment; filename=sound.wav'
            return response
