import argparse
from pathlib import Path

from rich import print, pretty

from synthetic_trace_gen import TRACE_CONF

pretty.install()


def split_results_dump(input_file: Path, output_dir: Path = None) -> None:
    recency_start = 0
    recency_end = TRACE_CONF['RECENCY']

    frequency_start = recency_end
    frequency_end = frequency_start + TRACE_CONF['FREQUENCY']

    burstiness_start = frequency_end
    burstiness_end = burstiness_start + TRACE_CONF['BURSTINESS']

    print(f'[bold cyan]Key ranges:')
    print(f'  RECENCY: [{recency_start}, {recency_end})')
    print(f'  FREQUENCY: [{frequency_start}, {frequency_end})')
    print(f'  BURSTINESS: [{burstiness_start}, {burstiness_end})')

    if output_dir is None:
        output_dir = input_file.parent
    else:
        output_dir.mkdir(exist_ok=True, parents=True)

    base_name = input_file.stem
    recency_output = output_dir / f'{base_name}_recency.results_dump'
    frequency_output = output_dir / f'{base_name}_frequency.results_dump'
    burstiness_output = output_dir / f'{base_name}_burstiness.results_dump'

    recency_count = 0
    frequency_count = 0
    burstiness_count = 0
    other_count = 0

    with input_file.open('r') as input_f, \
         recency_output.open('w') as recency_f, \
         frequency_output.open('w') as frequency_f, \
         burstiness_output.open('w') as burstiness_f:

        for line in input_f:
            parts = line.split()
            if len(parts) != 3:
                continue

            timestamp, key, result = parts
            key = int(key)

            if recency_start <= key < recency_end:
                recency_f.write(line)
                recency_count += 1
            elif frequency_start <= key < frequency_end:
                frequency_f.write(line)
                frequency_count += 1
            elif burstiness_start <= key < burstiness_end:
                burstiness_f.write(line)
                burstiness_count += 1
            else:
                other_count += 1

    print(f'\n[bold green]Processing complete:')
    print(f'  RECENCY entries: {recency_count:,}')
    print(f'  FREQUENCY entries: {frequency_count:,}')
    print(f'  BURSTINESS entries: {burstiness_count:,}')
    print(f'  OTHER entries (skipped): {other_count:,}')

    print(f'\n[bold cyan]Output files:')
    print(f'  {recency_output}')
    print(f'  {frequency_output}')
    print(f'  {burstiness_output}')


def main():
    parser = argparse.ArgumentParser(description='Split results_dump file by item type (RECENCY, FREQUENCY, BURSTINESS)')
    parser.add_argument('input', help='Input results_dump file path', type=str)
    parser.add_argument('-o', '--output-dir', help='Output directory (default: same as input file)', type=str, required=False)

    args = parser.parse_args()

    input_file = Path(args.input)

    if not input_file.exists():
        print(f'[bold red]Error: Input file {input_file} does not exist')
        return

    output_dir = Path(args.output_dir) if args.output_dir else None

    print(f'[bold]Splitting results_dump file:[/bold]')
    print(f'  Input: {input_file}')
    print(f'  Output directory: {output_dir if output_dir else input_file.parent}')
    print(f'\n[bold]Trace configuration (from synthetic_trace_gen.py):[/bold]')
    print(f'  RECENCY items: {TRACE_CONF["RECENCY"]:,}')
    print(f'  FREQUENCY items: {TRACE_CONF["FREQUENCY"]:,}')
    print(f'  BURSTINESS items: {TRACE_CONF["BURSTINESS"]:,}')
    print(f'  ONE_HIT_WONDERS items: {TRACE_CONF["ONE_HIT_WONDERS"]:,}')
    print()

    split_results_dump(input_file, output_dir)


if __name__ == '__main__':
    main()
