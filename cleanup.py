#watchdog file
import watchdog.events
import watchdog.observers
import sys
import tkinter as tk
from tkinter import filedialog
import json
import pathlib as pl
import os
from dataclasses import dataclass
import shutil
from thefuzz import fuzz
import logging



@dataclass
class Config:
    watch_dir: str
    dest_dir: str


class Handler(watchdog.events.PatternMatchingEventHandler):
	def __init__(self):
		# Set the patterns for PatternMatchingEventHandler
		watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.md'],
															ignore_directories=True, case_sensitive=False)

	def on_created(self, event):
		print("Watchdog received created event - % s." % event.src_path)
		# Event is created, you can process it now

	def on_modified(self, event):
		print("Watchdog received modified event - % s." % event.src_path)
		# Event is modified, you can process it now

def watch_directory():
    # Open a directory selection dialog
    directory_path = filedialog.askdirectory()
    # Insert the directory path into the text box
    watch_dir_text.delete(0, tk.END)
    watch_dir_text.insert(tk.END, directory_path)

def destination_directory():
    # Open a directory selection dialog
    directory_path = filedialog.askdirectory()
    # Insert the directory path into the text box
    dest_dir_text.delete(0, tk.END)
    dest_dir_text.insert(tk.END, directory_path)

def get_markdown_files(path)->list:

    os.chdir(path)
    mdfiles=[]
    for file in os.listdir():
        if file.endswith('.md'):
            mdfiles.append(pl.Path(path) / file)

    return mdfiles

def markdown_folder_exits(path: pl.Path) ->bool:
    pathstr = path.as_posix().replace('.md','')
    path = pl.Path(pathstr)
    if path.exists():
        return True
    else:
        return False

def markdown_pdf_exists(path: pl.Path)->str:
    ret_val = ''
    pathstr = path.parent
    pdf_files = list(filter(lambda x:'.pdf' in x, os.listdir(pathstr)))
    for pdf in pdf_files:
        file_name = path.name
        rat = fuzz.partial_ratio(pdf.replace('.pdf',''),file_name.replace('.md',''))
        if rat >= 97:
            ret_val = pdf
            print(f'Winner = {file_name} with a Ratio = {rat}')
            break
        
        print(f'Ratio: {rat}')

    return ret_val


def save_config():

    global config

    watch_dir = watch_dir_text.get()
    destination_dir = dest_dir_text.get()
    config = Config(watch_dir,destination_dir)

    cf = {"watch_directory": watch_dir, "destination_directory": destination_dir}

    with open('config.json','w') as f:
        json.dump(cf,f)

def change_image_links(mdfile:pl.Path):
    
    
    images = os.listdir(mdfile.parent.joinpath(mdfile.name.replace('.md','')))
    mdtext = ''
    with open(mdfile,'r') as f:
        mdtext = f.read()
        for img in images:
            end_idx = mdtext.find(img)
            begin_idx = 0
            for i in range(end_idx,0,-1):
                if mdtext[i]=='(' and mdtext[i-1]==']':
                    begin_idx=i
                    break
            
            if begin_idx >0 and end_idx>0:
                result = mdtext[:begin_idx+1] + mdtext[end_idx:]
                mdtext = result
    
    #make sure images do not have tabs in front of them
   
    mdtext = mdtext.replace('    ![','![')
    
    #make a new file
    #newfile = pl.Path(mdfile.parent).joinpath("mod_" + mdfile.name)

    with open(mdfile, 'w') as f:
        f.write(mdtext)

def run_cleanup():

    global config
    #global logging

    res_folder = '_resources'

    print('cleanup starting')
    #get markdown files
    os.chdir(config.watch_dir)
    mdfiles = get_markdown_files(config.watch_dir)
    for mdf in mdfiles:
        
        pdf = markdown_pdf_exists(mdf)
        if pdf !='':
    
            #add link to the top of the *.md file
            with open(mdf,'r') as f:
                mdf_text = f.read()
                new_text = '![['+ pdf + ']]\n' + mdf_text

            #save new mdf file
            with open(mdf,'w') as f:
                f.write(new_text)
            
            # move file to _resources
            try:
                shutil.move(config.watch_dir+'/'+pdf, config.dest_dir + '/' +res_folder +'/' +pdf)
            except Exception as e:
                logger.error('Error selecting source directory: {}'.format(e))
                
            

        bPathFolder = markdown_folder_exits(mdf)
        # run through all files in folder and adjust links in *.md file to reflect new directory structure
        if bPathFolder:
            #update links in markdown file
            change_image_links(mdf)
            # move file and folder to correct location
            try:
                # move file first
                shutil.move(mdf.as_posix(), config.dest_dir + f'/{mdf.name}')

                #next move the folder
                shutil.move(mdf.as_posix().replace('.md',''), config.dest_dir + f'/{res_folder}/{mdf.name.replace('.md','')}')
            
            except Exception as e:
                logger.error('Error selecting source directory: {}'.format(e))


        else:
            try:
                # move file first
                shutil.move(mdf.as_posix(), config.dest_dir + f'/{mdf.name}')
            except Exception as e:
                logger.error('Error selecting source directory: {}'.format(e))

    

def exit_program():
    sys.exit(0)

#setup logging
logging.basicConfig(filename='logger.log', level=logging.INFO, 
format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    config = None

    

    if len(sys.argv)>1:
        print(sys.argv)
        if sys.argv[1]=='auto':
            #we are in full auto mode
            
            if pl.Path('config.json').exists():
                #load file and run
                with open('config.json','r') as f:
                    config_data= json.load(f)
                    config = Config(config_data['watch_directory'], config_data['destination_directory'])
                    run_cleanup()

            else:
                print("No congiguraiton available, terminating")
                sys.exit(0)

    else:
        #we are interactive mode

        # does a config file exit?
        if pl.Path('config.json').exists():
            #read file into config
            with open('config.json', 'r') as f:
                config_data = json.load(f)
                config = Config(config_data["watch_directory"], config_data['destination_directory'])


        window = tk.Tk()
        frame1 = tk.Frame(master=window, width=200, height=200, pady=5)
        frame1.pack()

        watch_dir_button = tk.Button(text="Watch Dir", master=frame1, command=watch_directory)
        watch_dir_button.pack(side=tk.LEFT)

        watch_dir_text = tk.Entry(width=140, master=frame1)
        watch_dir_text.pack(side=tk.LEFT)
        if config:
            watch_dir_text.insert(tk.END, config.watch_dir)

        frame2 = tk.Frame(master=window,width=200, height=200, pady=5)
        frame2.pack()

        dest_dir_button = tk.Button(text="Destination", master=frame2, command=destination_directory)
        dest_dir_button.pack(side=tk.LEFT)
        
        dest_dir_text = tk.Entry(width=140, master=frame2)
        dest_dir_text.pack(side=tk.LEFT)
        if config:
            dest_dir_text.insert(tk.END, config.dest_dir)

        frame3 = tk.Frame(master=window, width=100,height=100, pady=10)
        frame3.pack()

        save_button = tk.Button(text="Save", master=frame3,command=save_config)
        save_button.pack(side=tk.LEFT)

        run_button = tk.Button(text="Run", master=frame3, command=run_cleanup)
        run_button.pack(side=tk.LEFT)

        exit_button = tk.Button(text="Cancel", master=frame3, command=exit_program)
        exit_button.pack(side=tk.LEFT)


        window.mainloop()

