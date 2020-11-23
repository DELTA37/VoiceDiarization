from .creator import Creator


class LabelMeCreator(Creator):
    def __init__(self, client_api, fields, output_fields, parse_output=lambda x: x):
        super(LabelMeCreator, self).__init__(client_api.api_name, algo_fn=self.algo_fn, fields=fields, output_fields=output_fields)
        self.client_api = client_api
        self.parse_output = parse_output

    def algo_fn(self, data):
        post_id = self.client_api.post(data)
        self.client_api.wait(post_id)
        result = self.client_api.get_result(post_id)
        return self.parse_output(result)
