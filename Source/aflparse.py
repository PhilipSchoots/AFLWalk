from aalpy.learning_algs import run_Alergia, run_EDSM
from aalpy.utils import visualize_automaton, convert_i_o_traces_for_RPNI, save_automaton_to_file
import re
from collections import defaultdict, Counter


def parse_log_file(file_path, max_traces=None):
    traces = []
    current_trace = []

    current_req = None
    total_traces = 0

    with open(file_path, 'r', errors='ignore') as f:

        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith('---'):

                if current_trace:
                    total_traces += 1

                    if max_traces is None or len(traces) < max_traces:
                        traces.append(current_trace)

                    current_trace = []

                current_req = None
                continue

            if line.startswith('REQ:'):
                current_req = line[len('REQ:'):].strip()
                continue

            if line.startswith('RESP:'):
                resp = line[len('RESP:'):].strip()

                if current_req is None:
                    continue

                current_trace.append((current_req, resp))
                current_req = None

    if current_trace:
        total_traces += 1

        if max_traces is None or len(traces) < max_traces:
            traces.append(current_trace)

    return traces, total_traces

def filter_deterministic(data):
    prefix_map = defaultdict(set)

    for inp, out in data:
        prefix_map[inp].add(out)

    return [(inp, list(outs)[0]) for inp, outs in prefix_map.items() if len(outs) == 1]


def main():
    data, total = parse_log_file("aflwalk_traces",)

    print(f"Loaded {len(data)} traces")
    print(f"Total traces in file: {total}")
    
    RPNIdata = filter_deterministic(convert_i_o_traces_for_RPNI(data))

    model = run_EDSM(
        data=RPNIdata,
        automaton_type='mealy',
        print_info=True
    )

    visualize_automaton(model, path="model_output_RPNI")
    save_automaton_to_file(model, path="model_output_RPNI")

if __name__ == "__main__":
    main()
