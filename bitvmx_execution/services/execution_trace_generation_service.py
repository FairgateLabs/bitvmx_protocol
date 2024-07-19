from bitvmx_execution.services.execution_trace_parsing_service import ExecutionTraceParsingService


class ExecutionTraceGenerationService:
    # This service should execute the program and generate the txt with the trace,
    # as of now, it is done manually

    def __init__(self, base_path):
        self.base_path = base_path
        self.execution_trace_parsing_service = ExecutionTraceParsingService(
            base_path + "execution_trace.txt"
        )

    def __call__(self, protocol_dict):
        return self.execution_trace_parsing_service(
            self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", protocol_dict
        )
