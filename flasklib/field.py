

class Field(object):
    def __init__(self, field_name):
        super(Field, self).__init__()
        self.field_name = field_name

    def create_html(self):
        return f"""
        <div class="panel panel-default">
            <div class="panel-heading">
                <font color="gray">
                    <h2>{self.field_name}</h2>
                </font>
            </div>
            <div class="panel-body">
                {self.generate_inputs()}
            </div>
        </div>
        """

    def generate_inputs(self):
        raise NotImplementedError()

    def parse_request(self, data):
        raise NotImplementedError()

    def add_route(self, app):
        pass
