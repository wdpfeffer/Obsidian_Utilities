#watchdog file
import watchdog.events
import watchdog.observers
import time
import sys
import tkinter as tk
from tkinter import filedialog
import json
import pathlib as pl
from dataclasses import dataclass

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

def save_config():

    global config

    watch_dir = watch_dir_text.get()
    destination_dir = dest_dir_text.get()
    config = Config(watch_dir,destination_dir)

    cf = {"watch_directory": watch_dir, "destination_directory": destination_dir}

    with open('config.json','w') as f:
        json.dump(cf,f)

def run_watchdog():

    global config

    print('Watchdog starting')

    watch_path = config.watch_dir
    event_handler = Handler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=watch_path, recursive=True)
    observer.start()
	
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    

def exit_program():
    sys.exit(0)


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
                    run_watchdog()

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

        run_button = tk.Button(text="Run", master=frame3, command=run_watchdog)
        run_button.pack(side=tk.LEFT)

        exit_button = tk.Button(text="Cancel", master=frame3, command=exit_program)
        exit_button.pack(side=tk.LEFT)





        window.mainloop()

