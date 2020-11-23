from .output_field import OutputField
import base64
from skimage.util import img_as_ubyte
import numpy as np
from PIL import Image
import io


class OutputGraphField(OutputField):
    def __init__(self, field_name, default):
        super(OutputGraphField, self).__init__(field_name, default)

    def set_output(self, value):
        self.value = np.array(value, dtype=np.float32)

    def generate_inputs(self):
        if self.value.ndim == 2:
            y = self.value[:, 1]
            x = self.value[:, 0]
        else:
            y = self.value
            x = np.arange(0, y.shape[0], dtype=np.float32)

        return f"""
        <canvas id="{self.field_name}" width="400" height="400"></canvas>
        <script>
        var ctx = document.getElementById('{self.field_name}').getContext('2d');
        var {self.field_name}_chart""" + """ = new Chart(ctx, {
            type: 'line',
            data: {
                "labels":  """ + f"""{x.tolist()}""" + """,
                "datasets": [{
                    "label": " """ + f"""{self.field_name}""" + """ ",
                    "fill": false,
                    "borderColor": "rgb(75, 192, 192)",
                    "lineTension": 0.1,
                    "data": """ + f"""{y.tolist()}""" + """
                }]
            },
            options: {
            }
        });
        </script>
        """
