from .output_field import OutputField
import base64
import numpy as np
from skimage.util import img_as_ubyte
from PIL import Image
import io


class OutputImageField(OutputField):
    def __init__(self, field_name, default):
        super(OutputImageField, self).__init__(field_name, img_as_ubyte(default))

    def set_output(self, value):
        if not isinstance(value, Image.Image):
            value = Image.fromarray(img_as_ubyte(value))
        self.value = value

    def generate_inputs(self):
        img = self.value
        file_object = io.BytesIO()
        img.save(file_object, 'JPEG')
        file_object.seek(0)
        b64 = base64.b64encode(file_object.read()).decode('utf-8')
        return f"""
        <img class="img-responsive" src="data:image/jpeg;charset=utf-8;base64, {b64}" />
        """
