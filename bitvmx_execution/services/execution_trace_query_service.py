import pandas as pd

class ExecutionTraceQueryService:

    def __init__(self, base_path):
        self.base_path = base_path

    def __call__(self, protocol_dict, index):
        trace_df = pd.read_csv(
            self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", sep=";"
        )
        return trace_df.iloc[index]
