from .field import Field


class IntField(Field):
    def __init__(self, field_name, default=None, min_value=None, max_value=None, step_value=None):
        super(IntField, self).__init__(field_name)
        self.min_value = min_value
        self.max_value = max_value
        self.step_value = step_value
        self.default = default

    def generate_inputs(self):
        params = ""
        if self.default is not None:
            params += f""" value="{self.default}" """
        if self.min_value is not None:
            params += f""" min="{self.min_value}" """
        if self.max_value is not None:
            params += f""" max="{self.max_value}" """
        if self.step_value is not None:
            params += f""" step="{self.step_value}" """
        else:
            params += f""" step="1" """

        return f"""
        <input type="number" id="{self.field_name}" name="{self.field_name}" class="form-control"{params}>
        """

    def parse_request(self, data):
        return int(data)
