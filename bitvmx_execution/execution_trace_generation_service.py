from bitvmx_execution.execution_trace_parsing_service import ExecutionTraceParsingService


class ExecutionTraceGenerationService:

    def __init__(self, base_path):
        self.base_path = base_path
        self.execution_trace_parsing_service = ExecutionTraceParsingService(
            base_path + "execution_trace.txt"
        )

    def __call__(self, protocol_dict):
        return self.execution_trace_parsing_service(
            self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", protocol_dict
        )
