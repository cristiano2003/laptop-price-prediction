import os
import sys
import subprocess

# Add the path of the project to sys.path
sys.path.append(os.getcwd())

os.chdir(os.path.join(os.getcwd(), 'src/crawler/newegg'))


def run_crawler(spider_name: str, **kwargs):
    '''
        Kwargs:
            - `filename` (str) : File will be exported to folder results. Example: 'exchange_rate.csv'
            - `save_folder` (str) : File will be exported to this directory. Default: '../results'
            - `overwrite` (bool) : If True, the file will be overwritten. If False, the file will be appended. Default: False
            - `nolog` (bool): If True, the log will not be printed. Default: False
    '''

    # Define the command as a list of strings
    command = ['scrapy', 'crawl', spider_name]

    # Set default save_folder to '../results'
    save_folder = kwargs.get('save_folder', os.path.abspath('../results'))

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Add the arguments
    filename = kwargs.get('filename')
    if filename:
        save_dir = os.path.join(save_folder, filename)
        print('Save directory: ' + save_dir)
        overwrite = kwargs.get('overwrite', False)
        command += ['-o' if overwrite is False else '-O', save_dir]

    if kwargs.get('nolog'):
        # command += ['--loglevel=ERROR']
        command += ['--nolog']

    # Use subprocess to run the command
    subprocess.run(command)


if __name__ == '__main__':
    run_crawler('newegg_urls', filename='urls.jsonl', overwrite=False, nolog=False)
