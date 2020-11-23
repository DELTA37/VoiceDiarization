import os
import sys
import pandas as pd
import datatable as dt
from .output_field import OutputField


class OutputTableField(OutputField):
    def __init__(self, field_name, default):
        self.value: pd.DataFrame = default
        super(OutputTableField, self).__init__(field_name, default)

    def set_output(self, value):
        if isinstance(value, pd.DataFrame):
            self.value = value
        if isinstance(value, dt.DataTable):
            self.value = value.to_pandas()

    def generate_inputs(self):
        return "<div>" + self.value.to_html(classes=["table", "table-striped"]) + "</div>"
