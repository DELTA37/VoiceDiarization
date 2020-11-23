from .output_field import OutputField
import base64
from skimage.util import img_as_ubyte
from PIL import Image
import io


class OutputSVGField(OutputField):
    def __init__(self, field_name, download_name="result.svg", default='<svg viewBox="0 0 300 100" xmlns="http://www.w3.org/2000/svg"></svg>'):
        super(OutputSVGField, self).__init__(field_name, default)
        self.download_name = download_name

    def set_output(self, value):
        self.value = value

    def generate_inputs(self):
        return """
        <script>
        function download(filename, text) {
            var element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }
        </script>""" + f"""
        <div class="container-fluid">
            <div class="row">
                <div class="col">
                </div>
                <div class="col-8" id="output_svg_div_{self.field_name}">
                    {self.value}
                </div>
                <div class="col-1">
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <button type="button" class="btn btn-dark" onclick='download("result.svg", document.getElementById("output_svg_div_svg").innerHTML)'>Save as svg</button>
                </div>
                <div class="col-md-6">
                    <button type="button" class="btn btn-dark">Save as dxf</button>
                </div>
            </div>
        </div>
        """
