from .field import Field


class TextField(Field):
    def __init__(self, field_name):
        super(TextField, self).__init__(field_name)

    def generate_inputs(self):
        return f"""
        <textarea name="{self.field_name}" class="form-control" id={self.field_name}></textarea>
        """

    def parse_request(self, data):
        return data
