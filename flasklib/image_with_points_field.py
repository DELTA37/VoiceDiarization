from .field import Field
import numpy as np
import cv2


class ImageWithPointsField(Field):
    def __init__(self, field_name):
        super(ImageWithPointsField, self).__init__(field_name)

    def parse_request(self, data):
        filestr = data.read()
        npimg = np.fromstring(filestr, np.uint8)
        return cv2.cvtColor(cv2.imdecode(npimg, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    def generate_inputs(self):
        return """
            <script>
            $(document).ready(function(){
                $(":text").click(function(){
                    $(this).siblings("label").click();
                });
                $(":file").change(function(){
                    $file_name = $(this).val();
                    $(this).siblings(":text").val($file_name.replace("C:\\\\fakepath\\\\", ""));
                });
            });
        </script>

        <style>
            .input-group-file{
                width:auto;
            }

            .input-group-file input[type="text"]{
                width:70%;
                float:left;
                padding-left:5px;
                border-top-right-radius:0px;
                border-bottom-right-radius:0px;
                border-right:0px;
                cursor:default !important;
                background-color: white !important;
            }
            .input-group-file label{
                width:30%;
                float:left;
                border-top-left-radius:0px;
                border-bottom-left-radius:0px;

            }
            .input-group-file input[type="file"]{
                position: absolute !important; 
                left: -9999px !important; 
            }

        </style>
        """ + f"""
        <div class="input-group-file">
            <input type="text" class="form-control" readonly="">
            <label class="btn btn-primary" for="{self.field_name}">Choose file</label>
            <input type="file" id="{self.field_name}" name="{self.field_name}" accept="image/">
        </div>
        """
