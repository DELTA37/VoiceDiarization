from .field import Field


class OutputField(Field):
    def __init__(self, field_name, default):
        super(OutputField, self).__init__(field_name)
        self.set_output(default)

    def set_output(self, value):
        raise NotImplementedError()

    def generate_inputs(self):
        raise NotImplementedError()
