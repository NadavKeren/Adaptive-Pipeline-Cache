import argparse
import polars as pl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
from pathlib import Path
from typing import List, Tuple, Dict, Literal
from rich import print, pretty
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

pretty.install()

OUTPUT_FORMAT = 'pdf'

plt.rcParams["figure.figsize"] = (128,60)
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['hatch.linewidth'] = 1

green_color='#117733'

colors = ["#283618", "#606c38", "#FEFAE0"]

SMALL_SIZE = 16
MEDIUM_SIZE = 20
BIG_SIZE = 32
BIGGER_SIZE = 68
HUGE_SIZE = 80

DEFAULT_PART_LENGTHS = [33370453, 13193532, 5328920]


def plot_adaptions(dump_file: Path, output_path: Path, parts_length: List[int]) -> None:
    part_start_ids = [0]
    for length in parts_length:
        part_start_ids.append(part_start_ids[-1] + length)
    df: pl.Dataframe = pl.read_csv(dump_file, has_header=False, new_columns=['Event Number', 'LRU', 'LFU', 'LBU', 'Average Penalty', 
                                                           'Direction 1', 'Direction 2', 'Direction 3', 'Direction 4', 'Direction 5', 'Direction 6'],
                                   null_values=["NA"])
    print(df.describe())
    
    plt.rcParams["figure.figsize"] = (60, 19)
    plt.rc('font', size=HUGE_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=HUGE_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=HUGE_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=BIGGER_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=BIGGER_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=HUGE_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=HUGE_SIZE)  # fontsize of the figure title
    
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x / 1000000:.0f}M'))
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x / 1000000:.0f}M'))
    
    ax1.set_xlabel('Event Number')
    ax2.set_xlabel('Event Number')
    
    df = df.with_columns([
        (pl.col('LRU') * 100 / 16).alias('LRU'),
        (pl.col('LFU') * 100 / 16).alias('LFU'),
        (pl.col('LBU') * 100 / 16).alias('LBU')
    ])
    
    ax1.set_ylabel('Percentage of Cache')
    ax2.set_ylabel('ARL (ms)')
    
    
    event_numbers = df.select('Event Number').to_numpy().flatten()
    lru_values: np.array = df.select('LRU').to_numpy().flatten()
    lfu_values: np.array = df.select('LFU').to_numpy().flatten()
    lbu_values: np.array = df.select('LBU').to_numpy() .flatten()
    avg_penalty: np.array = df.select('Average Penalty').to_numpy()
    
    ax1.plot(event_numbers, lru_values, color=colors[0])
    ax1.fill_between(event_numbers, 0, lru_values, facecolor=colors[0])
    
    bottom = lru_values
    ax1.plot(event_numbers, bottom + lfu_values, color=colors[1])
    ax1.fill_between(event_numbers, bottom, bottom + lfu_values, facecolor=colors[1])
    
    bottom = bottom + lfu_values
    ax1.plot(event_numbers, bottom + lbu_values, color=colors[2])
    ax1.fill_between(event_numbers, bottom, bottom + lbu_values, facecolor=colors[2])
    
    bottom = bottom + lbu_values  
    
    LRU_handle = mpatches.Patch(facecolor=colors[0], label='LRU')
    LFU_handle = mpatches.Patch(facecolor=colors[1], label='LFU')
    LBU_handle = mpatches.Patch(facecolor=colors[2], label='LBU')
    
    ax1.legend(handles=[LRU_handle, LFU_handle, LBU_handle], loc='upper right', ncol=1, fancybox=True, shadow=True)
    ax1.grid()
    ax1.set_ylim(-10, 110)
    for part_id in part_start_ids[1:]:
        ax1.axvline(x = part_id, color='black', linewidth = 12)


    ax2.grid()
    ax2.plot(event_numbers, avg_penalty, linewidth=8, color=green_color)
    for part_id in part_start_ids[1:]:
        ax2.axvline(x = part_id, color='black', linewidth = 12)
    
    fig1.savefig(output_path / f'{dump_file.stem}-Adaption-prop.{OUTPUT_FORMAT}', bbox_inches='tight')
    fig2.savefig(output_path / f'{dump_file.stem}-Avg-latency.{OUTPUT_FORMAT}', bbox_inches='tight')
    
    
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, type=str, help='Path to the dump file')
    parser.add_argument('-o', '--output_dir', required=True, type=str, help='Path to output graphs')
    parser.add_argument('--parts-length', nargs='+', type=int, default=DEFAULT_PART_LENGTHS,
                        help='Lengths of each part (except the last). The part start IDs will be calculated cumulatively from these lengths')
    args = parser.parse_args()

    print(args)
    input_path: Path = Path(args.input)
    output_path: Path = Path(args.output_dir)

    if not input_path.exists() or input_path.is_dir():
        print(f"[bold red]Error: no such input dump: {args.input}")
        exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    plot_adaptions(input_path, output_path, args.parts_length)

if __name__ == "__main__":
    main()
