from rich import traceback
from rich import progress
from pathlib import Path
import subprocess
import json
import rich
import time
import sys
import os


rich.pretty.install()
traceback.install(show_locals=True)
version = '22.0.2'
c = rich.console.Console(
    record = True
)
print = c.print
run_st = subprocess.getstatusoutput
up_one = '\x1b[1A'
erase_line = '\x1b[2K'
yt_dlp = f'{sys.executable} -m yt_dlp'
proj_dir = Path(__file__).parent.resolve()


def run(
    command: str
) -> str:
    return run_st(
        command
    )[-1]


channel_link = 'https://youtube.com/channel/UCk73U4QT3cNDvqb_PaWM8AA'
params = '--playlist-items 1 --ignore-errors --no-abort-on-error'
timeout_for_checking = 15

print(f'started stream recorder version {version}')

while True:
    print('checking latest video...')
    page_data = run(
        f'{yt_dlp} {params} {channel_link} -j'
    )
    try:
        page_data = json.loads(
            page_data
        )
    except json.JSONDecodeError as error:
        error_file_path = Path(f'{proj_dir}/error.txt')
        c.export_text()
        c.print_json(
            page_data
        )
        c.print_exception(
            show_locals=True,
            max_frames=20,
        )
        with open(
            error_file_path,
            'w'
        ) as error_file:
            error_file.write(
                c.export_text()
            )
        print(
            f'[green] error text written to [deep_sky_blue1]{error_file_path}'
        )
        sys.exit()


    id = page_data['id']
    is_live = page_data['is_live']

    print(
        f'got video [green]{id}[/green]:',
        end = ' '
    )
    if is_live:
        print('[green]this is stream,[/green] starting record!')
        os.system(f"{yt_dlp} {params} --live-from-start https://youtube.com/watch?v={id} -v")
    else:
        print(
            '[red]this is not a stream',
        )
        with progress.Progress(
            progress.TextColumn("[progress.description]{task.description}"),
            progress.BarColumn(),
            progress.TimeRemainingColumn(),
        ) as timer:
            timer1 = timer.add_task(
                f'waiting for {timeout_for_checking} seconds',
                total = timeout_for_checking
            )
            step = 0.1
            while not timer.finished:
                timer.update(
                    timer1,
                    advance = step
                )
                time.sleep(step)

        sys.stdout.write(
            erase_line + (up_one + erase_line) * 3
        )
