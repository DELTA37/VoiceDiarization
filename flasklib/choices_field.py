from .field import Field


# TODO
class ChoicesField(Field):
    def __init__(self, field_name, description='', names=[], options=[]):
        super(ChoicesField, self).__init__(field_name)
        self.description = description
        self.names = names
        self.options = options

    def generate_inputs(self):
        options = '\n'.join([f'<option value="{opt}">{opt}</option>' for opt in self.options])
        selects = '\n'.join([f"""
            <select name="{self.field_name}__{name}" class="form-control" id="{self.field_name}__{name}" form="gdflask_test">
                {options}
            </select>
        """ for name in self.names])

        return f"""
        <div class="form-group">
            <label>{self.description}</label>
            {selects}
        </div> 
        """

    def parse_request(self, data):
        print(data)
        return data
