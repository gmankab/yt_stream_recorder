try:
    from setup import (
        modules_path,
        app_version,
        win_py_file,
        proj_path,
        app_name,
        bat_file,
        portable,
        yes_no,
        os_name,
    )
except ModuleNotFoundError:
    from yt_stream_recorder.setup import (  # type: ignore
        modules_path,
        app_version,
        win_py_file,
        proj_path,
        app_name,
        bat_file,
        portable,
        os_name,
        yes_no,
    )

from urllib import request as r
from betterdata import Data
from easyselect import Sel
from pathlib import Path
import rich.traceback
import rich.progress
import rich.pretty
import subprocess as sp
import datetime
import json
import rich
import time
import sys
import os


rich.pretty.install()
rich.traceback.install(
    show_locals=True
)
c = rich.console.Console(
    record = True
)
print = c.print
proj_path = Path(__file__).parent.resolve()
logs = Path(
    f'{proj_path}/{app_name}_logs'
)
config_path = Path(
    f'{modules_path}/{app_name}.yml'
)
config = Data(
    file_path = config_path
)
pip = f'{sys.executable} -m pip'
print(
    f'{app_name} [bold deep_sky_blue1]{app_version}'
)
run = sp.getoutput


def run_logged(
    command: list[str]
):
    if not logs.exists():
        logs.mkdir(
            exist_ok = True,
            parents = True,
        )
    filename = datetime.datetime.now().strftime(
        "%Y-%m-%d_%H-%M.log"
    )
    all_logs = list(logs.iterdir())
    while len(all_logs) >= config['max_log_files']:
        all_logs[0].unlink()
        all_logs.remove(all_logs[0])
    with sp.Popen(
        command,
        stdout = sp.PIPE,
        stderr = sp.PIPE,
    ).stdout as pipe:
        for line in iter(
            pipe.readline,
            b''
        ):
            with open(
                f'{logs}/{filename}',
                'a',
            ) as log:
                line = str(line)
                if line[:2] == "b'":
                    line = line[2:]
                if line[-3:] == r"\n'":
                    line = line[:-3]
                print(line)
                log.write(line + '\n')


def init_config() -> None:
#     if (
#         config['app_version']
#     ) and (
#         config['app_version'] < '22.1.21'
#     ):
#         config['app_version'] = app_version
#         # update forced because of very important bugfix
#         update_app(
#             forced=True
#         )
#     if (
#         config['app_version']
#     ) and (
#         config['app_version'] < '22.2.0'
#     ) and portable:
#         bat_file_tmp = Path(f'{bat_file}.tmp')
#         win_py_file_tmp = Path(f'{win_py_file}.tmp')
#         old_python_path = Path(f'{modules_path}/.python_3.10.7')
#         r.urlretrieve(
#             url = f'https://raw.githubusercontent.com/gmankab/{app_name}/main/launcher/{app_name}.bat',
#             filename = bat_file_tmp,
#         )
#         r.urlretrieve(
#             url = f'https://raw.githubusercontent.com/gmankab/{app_name}/main/launcher/{app_name}_win.py',
#             filename = win_py_file_tmp,
#         )
#         if (
#             win_py_file_tmp.exists()
#         ) and (
#             bat_file_tmp.exists()
#         ):
#             bat_file.unlink(
#                 missing_ok = True
#             )
#             bat_file_tmp.rename(
#                 bat_file
#             )
#             win_py_file.unlink(
#                 missing_ok = True
#             )
#             win_py_file_tmp.rename(
#                 win_py_file
#             )
#         config['app_version'] = app_version
#         restart_command = f'''\
# taskkill /f /pid {os.getpid()} && \
# rd /s /q "{old_python_path}" & \
# timeout /t 1 && \
# {bat_file}\
# '''
#         print(
#             f'restarting and updating {app_name} with command:\n{restart_command}'
#         )
#         os.system(
#             restart_command
#         )
    if config['app_version'] != app_version:
        config['app_version'] = app_version
        if portable:
            restart()

    if 'check_updates' not in config:
        if yes_no.choose(
            text='[deep_sky_blue1]do you want to check updates on start?'
        ) == 'yes':
            config['check_updates'] = True
        else:
            config['check_updates'] = False
    if config['app_version'] != app_version:
        config['app_version'] = app_version

    if not config['yt_dlp_args']:
        config[
            'yt_dlp_args'
        ] = '--playlist-items 1 --ignore-errors --no-abort-on-error --keep-video'

    if not config['yt_dlp_path']:
        yt_dlp_path1 = f'{sys.executable} {modules_path}/yt_dlp'
        yt_dlp_path2 = f'{sys.executable} -m yt_dlp'
        check_str = 'Type yt-dlp --help to see a list of all options.'
        if check_str in run(yt_dlp_path1):
            config[
                'yt_dlp_path'
            ] = yt_dlp_path1
        elif check_str in run(yt_dlp_path2):
            config[
                'yt_dlp_path'
            ] = yt_dlp_path2
        else:
            config.interactive_input('yt_dlp_path')

    if not config['timeout']:
        config['timeout'] = 15
    if not config['max_log_files']:
        config['max_log_files'] = 30
    if not config['channel']:
        channel = Sel(
            [
                'JolyGolf',
                'IzzyLaif',
                'add new channel'
            ],
            styles = [
                None,
                None,
                'green',
            ]
        ).choose(
            'please select youtube channel'
        )
        match channel:
            case 'JolyGolf':
                config['channel'] = 'https://youtube.com/channel/UCk73U4QT3cNDvqb_PaWM8AA'
            case 'IzzyLaif':
                config['channel'] = 'https://youtube.com/@IzzyLaif'
            case 'add new channel':
                config.interactive_input(
                    'channel',
                    text = '\n[bold]input channel link'
                )


def update_app(
    forced = False
):
    if not config.check_updates:
        return
    if not forced:
        print('[deep_sky_blue1]checking for updates')
        with rich.progress.Progress(
            transient = True
        ) as progr:
            progr.add_task(
                total = None,
                description = ''
            )
            packages = []
            pip_list = f'{pip} list --format=json --path {modules_path}'
            all_packages_str = run(pip_list)
            start = all_packages_str.find('[')
            end = all_packages_str.rfind(']') + 1
            all_packages_str = all_packages_str[start:end]
            try:
                all_packages = json.loads(
                    all_packages_str
                )
            except json.JSONDecodeError:
                progr.stop()
                print(
                    f'''
    {pip_list} command returned non-json output:

    {all_packages_str}
    '''
                )
                return
            for package in all_packages:
                if package['name'] != app_name:
                    packages.append(
                        package['name']
                    )

            command = f'{pip} list --outdated --format=json --path {modules_path}'
            for package in packages:
                command += f' --exclude {package}'

            updates_found_str = run(command)
            updates_found = app_name in updates_found_str
            progr.stop()

        if not updates_found:
            print('updates not found')
            return
    if not forced:
        if yes_no.choose(
            text=f'''\
    [green]found updates, do you want to update {app_name}?
    '''
        ) == 'no':
            return

    requirements = "betterdata easyselect gmanka_yml rich yt-dlp"

    match os_name:
        case 'Linux':
            update = f'''\
kill -2 {os.getpid()} && \
sleep 1 && \
{pip} install --upgrade --no-cache-dir --force-reinstall {app_name} {requirements} \
--no-warn-script-location -t {modules_path} && \
sleep 1 && \
{sys.executable} {proj_path}\
'''
        case 'Windows':
            update = f'''\
taskkill /f /pid {os.getpid()} && \
timeout /t 1 && \
{pip} install --upgrade --no-cache-dir --force-reinstall {app_name} {requirements} \
--no-warn-script-location -t {modules_path} && \
timeout /t 1 && \
{sys.executable} {proj_path}\
'''
    print(f'restarting and updating {app_name} with command:\n{update}')
    os.system(
        update
    )

def restart():
    match os_name:
        case 'Linux':
            update = f'''\
kill -2 {os.getpid()} && \
sleep 1 && \
{sys.executable} {proj_path}\
'''
        case 'Windows':
            if portable:
                update = f'''\
taskkill /f /pid {os.getpid()} && \
timeout /t 1 && \
{bat_file}\
'''
            else:
                update = f'''\
    taskkill /f /pid {os.getpid()} && \
    timeout /t 1 && \
    {sys.executable} {proj_path}\
    '''
    print(f'restarting and updating {app_name} with command:\n{update}')
    os.system(
        update
    )


def main():
    init_config()
    update_app()
    yt_dlp = f'{config.yt_dlp_path} {config.yt_dlp_args}'
    while True:
        print('checking latest video...')
        page_data_str = run(
            f'{yt_dlp} {config.channel} -j'
        )
        start = page_data_str.find('{')
        end = page_data_str.rfind('}') + 1
        page_data_str = page_data_str[start:end]
        try:
            page_data = json.loads(
                page_data_str
            )
        except Exception:
            error_path = f'{proj_path}/error.txt'
            with open(
                error_path,
                'w',
            ) as file:
                c_error = rich.console.Console(
                    width=80,
                    file=file,
                )
                c_error.print_exception(
                    show_locals=True
                )
            c.print_exception(
                show_locals=True
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
            os.system(f"{yt_dlp} --live-from-start https://youtube.com/watch?v={id} -v")
        else:
            print(
                '[red]this is not a stream',
            )
            with rich.progress.Progress(
                rich.progress.TextColumn("[progress.description]{task.description}"),
                rich.progress.BarColumn(),
                rich.progress.TimeRemainingColumn(),
            ) as timer:
                timer1 = timer.add_task(
                    f'waiting for {config.timeout} seconds',
                    total = config.timeout,
                )
                step = 0.1
                while not timer.finished:
                    timer.update(
                        timer1,
                        advance = step
                    )
                    time.sleep(step)
            c.clear()

main()
