from .field import Field
from .output_field import OutputField


class OutputTextField(OutputField):
    def __init__(self, field_name, default):
        super(OutputTextField, self).__init__(field_name, default=default)

    def set_output(self, value):
        self.value = str(value)

    def generate_inputs(self):
        return f"""
        <label id={self.field_name}>{self.value}</label>
        """
