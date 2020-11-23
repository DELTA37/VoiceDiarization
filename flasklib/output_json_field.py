from .output_field import OutputField
import json


class OutputJSONField(OutputField):
    def __init__(self, field_name, default):
        super(OutputJSONField, self).__init__(field_name, default)

    def set_output(self, value):
        self.value = value

    def generate_inputs(self):
        return f"""
        <div class="common protocols all" id="{self.field_name}" style="display: block;" align="left">
            <pre>
                <code id="{self.field_name}_jsondata" class="json hljs" style="background: #FFFFFF"></code>
            </pre>
            <script>
                let {self.field_name}_jsondata_content = `{json.dumps(self.value, indent=2)}`
                document.getElementById('{self.field_name}_jsondata').innerHTML = {self.field_name}_jsondata_content;	
                let snippet = document.querySelector('#{self.field_name}_jsondata.hljs'); 
                hljs.highlightBlock(snippet);
            </script>
        </div>
        """ + """
        <script>
        """ + f"""
            const {self.field_name}_blob = new Blob([{self.field_name}_jsondata_content], """ + """{ type: 'text/json' }""" + f""");
            const downloadLink = downloadBlob({self.field_name}_blob, '{self.field_name}.json');
            downloadLink.title = 'Export json';
            downloadLink.classList.add('btn-link', 'download-link');
            downloadLink.textContent = 'Export json';
            document.getElementById('{self.field_name}').appendChild(downloadLink);
        </script>
        """
