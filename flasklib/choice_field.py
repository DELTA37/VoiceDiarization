from .field import Field


class ChoiceField(Field):
    def __init__(self, field_name, description='', options=[]):
        super(ChoiceField, self).__init__(field_name)
        self.description = description
        self.options = options

    def generate_inputs(self):
        options = '\n'.join([f'<option value="{opt}">{opt}</option>' for opt in self.options])
        return f"""
        <div class="form-group">
            <label for="{self.field_name}">{self.description}</label>
            <select name="{self.field_name}" class="form-control" id="{self.field_name}" form="gdflask_test">
                {options}
            </select>
        </div> 
        """

    def parse_request(self, data):
        print(data)
        return data
