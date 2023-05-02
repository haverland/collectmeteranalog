from glob import glob
import os
from PIL import Image
import matplotlib
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.figure as fig
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
import shutil
import pandas as pd
from collectmeteranalog.predict import predict
from numpy import pi

def ziffer_data_files(input_dir):
    '''return a list of all images in given input dir in all subdirectories'''
    imgfiles = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if (file.endswith(".jpg")):
                imgfiles.append(root + "/" + file)
    
    imgfiles = sorted(imgfiles, key=lambda x : os.path.basename(x))
    return  imgfiles


def label(path, startlabel=0, imageurlsfile=None, ticksteps=1):
    global filename
    global i
    global im
    global filelabel
    global ax
    global ax2
    global slabel
    global files
    global predbox
    global plotedValue
    global usegrid 
    global ticksteps_s

    ticksteps_s = ticksteps
    usegrid = True

    print(f"Startlabel", startlabel)

    if (imageurlsfile!=None):
        files = pd.read_csv(imageurlsfile, index_col=0).to_numpy().reshape(-1)
        for file in files:
            if (not os.path.exists(file)):
              files = files[~np.isin(files, file)]
    else: 
        files = ziffer_data_files(path)

    if (len(files)==0):
        print("No images found in path")
        exit(1)
        
    i = 0
    img, filelabel, filename, i = load_image(files, i, startlabel)

    # disable toolbar
    matplotlib.rcParams['toolbar'] = 'None'
 
    # set window title
    fig = plt.gcf()
    
    fig.canvas.manager.set_window_title('1 of ' + str(len(files)) + ' images')
    ax0 = fig.add_subplot(111)
    ax0.axis("off")

    #plt.polar()
    #plt.yticks(np.arange(0, 1, step=0.1))
    
    im = ax0.imshow(img, extent=[0, 1, 0, 1])
    
    ax2 = fig.add_subplot(111, polar=True, label="polar")
    ax2.set_facecolor("None")
    # suppress the radial labels
    plt.setp(ax2.get_yticklabels(), visible=False)
   
    # set the circumference labels
    ax2.set_xticks(np.linspace(0, 2*pi, int(100/ticksteps), endpoint=False))
    ax2.set_xticklabels(np.arange(0, 10, step=float(ticksteps)/10.0).round(2),fontsize=7)
    # Rotating the labels would be nice, but seems not to be trivial, see https://stackoverflow.com/questions/46719340/how-to-rotate-tick-labels-in-polar-matplotlib-plot
    
    #ax2.grid(False)
    #ax2.grid(linewidth=2, drawstyle='steps-post')
    # make the labels go clockwise
    ax2.set_theta_direction(-1)
    # place 0 at the top
    ax2.set_theta_offset(pi/2.0)    
    ax2.set_yticklabels([])
    #ax2.spines['polar'].set_visible(False)
    #plt.text(1.1, 0.9, "You can use cursor key controll also:\n\nleft/right = prev/next\nup/down=in/decrease value\ndelete=remove.", fontsize=6)
    prediction = predict(img)
    ax=plt.gca()

    axp = plt.axes([0.05, 0.5, 0.1, 0.2])
    predbox = TextBox(axp, label='', initial='Pred.:\n{:.1f}'.format(prediction), textalignment='center')
    
    axlabel =  plt.axes([0.22, 0.025, 0.58, 0.03])
    slabel = Slider(axlabel, label='Label',valmin= 0.0, valmax=9.9, valstep=0.1, 
                    valinit=filelabel,
                    orientation='horizontal')
    
    # Show value in plot
    plotedValue, = ax2.plot([0, 2*pi * filelabel / 10], [0, 2], 'g', linewidth=5)    
    
    previousax = plt.axes([0.87, 0.225, 0.1, 0.04])
    bprevious = Button(previousax, 'previous', hovercolor='0.975')
    nextax = plt.axes([0.87, 0.025, 0.1, 0.04])
    bnext = Button(nextax, 'update', hovercolor='0.975')
    removeax = plt.axes([0.87, 0.4, 0.1, 0.04])
    bremove = Button(removeax, 'delete', hovercolor='0.975')
    
    increase0_1_label = plt.axes([0.93, 0.1, 0.05, 0.04])
    bincrease0_1_label = Button(increase0_1_label, '+0.1', hovercolor='0.975')
    increase1_label = plt.axes([0.93, 0.15, 0.05, 0.04])
    bincrease1_label = Button(increase1_label, '+1.0', hovercolor='0.975')
    
    decrease0_1_label = plt.axes([0.87, 0.1, 0.05, 0.04])
    bdecrease0_1_label = Button(decrease0_1_label, '-0.1', hovercolor='0.975')
    decrease1_label = plt.axes([0.87, 0.15, 0.05, 0.04])
    bdecrease1_label = Button(decrease1_label, '-1.0', hovercolor='0.975')

    toggle_grid_label = plt.axes([0.87, 0.95, 0.1, 0.04])
    toggle_grid_btn = Button(toggle_grid_label, 'grid', hovercolor='0.975')

    def load_previous():
        global im
        global i
        global filelabel
        global filename
        global predbox

        i = (i - 1) % len(files)
        img, filelabel, filename, i = load_image(files, i)
        im.set_data(img)
        plotedValue.set_xdata([0, 2*pi * filelabel / 10])        
        slabel.set_val(filelabel)
        fig = plt.gcf()
        fig.canvas.manager.set_window_title(str(i+1) + ' of ' + str(len(files)) + ' images')
        predbox.set_val("{:.1f}".format(predict(img)))
        


    def load_next(increaseindex = True):
        global im
        global i
        global filelabel
        global filename
        global predbox

        if increaseindex:
            i = (i + 1) % len(files)
        
        img, filelabel, filename, i = load_image(files, i)
        im.set_data(img)
        plotedValue.set_xdata([0, 2*pi * filelabel / 10])        
        slabel.set_val(filelabel)
        fig = plt.gcf()
        fig.canvas.manager.set_window_title(str(i+1) + ' of ' + str(len(files)) + ' images')
        predbox.set_val("Pred.:\n{:.1f}".format(predict(img)))
        
        updatePlot()
        

    def updatePlot():   
        
        plotedValue.set_xdata([0, 2*pi * filelabel / 10])  
        plt.pause(0.1)
        #fig.canvas.draw()
        #fig.canvas.flush_events()

    def increase0_1_label(event):
        global filelabel
        
        filelabel = (filelabel + 0.1) % 10
        slabel.set_val(filelabel)
        updatePlot()
        

    def increase1_label(event):
        global filelabel
        filelabel = (filelabel + 1) % 10
        slabel.set_val(filelabel)
        updatePlot()

    def decrease0_1_label(event):
        global filelabel

        filelabel = (filelabel - 0.1) % 10
        slabel.set_val(filelabel)
        updatePlot()

    def decrease1_label(event):
        global filelabel

        filelabel = (filelabel - 1) % 10
        slabel.set_val(filelabel)
        updatePlot()

    def remove(event):
        global filename
        global files
        global i
        os.remove(filename)
        files = np.delete(files,i, 0)
        load_next(False)

    def previous(event):
        load_previous()

    def l_next(event):
        global filelabel
        global filename
        
        basename = os.path.basename(filename).split('_', 1)
        basename = basename[-1]
        _zw = os.path.join(os.path.dirname(filename), "{:.1f}".format(filelabel) + "_" + basename)
        if (filename != _zw):
            files[i] = _zw
            shutil.move(filename, _zw)
        load_next()

    def on_press(event):
        #print('press', event.key)
        if event.key == 'right':
            l_next(event)
        if event.key == 'left':
            previous(event)
        if event.key == 'up':
            increase0_1_label(event);
        if event.key == 'pageup':
            increase1_label(event);
        if event.key == 'down':
            decrease0_1_label(event)
        if event.key == 'pagedown':
            decrease1_label(event)
        if event.key == 'enter':
            l_next(event)
        if event.key == 'delete':
            remove(event)



    def on_click(event):  
        global slabel      
        global filelabel
        global ax2
        if event.inaxes != ax2:
            return

        #print(event.xdata, (round(event.xdata*10 / (2*pi), 1)+ 10) %10, event.xdata+2*pi-pi/2, slabel.val)
        filelabel = (round(event.xdata*10 / (2*pi), 1)+ 10) %10
        
        slabel.set_val(filelabel) # event.xdata is directly in rad
        updatePlot()
        #print(event.xdata, slabel.val)

    def on_toggle_grid(event):  
        global ax2
        global usegrid
        usegrid = not usegrid
        ax2.grid(usegrid)

        if (usegrid):
            ax2.set_xticks(np.linspace(0, 2*pi, int(100/ticksteps_s), endpoint=False))
            ax2.set_xticklabels(np.arange(0, 10, step=float(ticksteps_s)/10.0).round(2),fontsize=7)
        else:
            ax2.set_xticks([])
            ax2.set_xticklabels([])
        plt.draw()
        #plt.pause(0.0001)
        #plt.clf()
    


    fig.canvas.mpl_connect('key_press_event', on_press)
    
    
    bnext.on_clicked(l_next)
    bprevious.on_clicked(previous)
    bremove.on_clicked(remove)
    bincrease0_1_label.on_clicked(increase0_1_label)
    bincrease1_label.on_clicked(increase1_label)
    bdecrease0_1_label.on_clicked(decrease0_1_label)
    bdecrease1_label.on_clicked(decrease1_label)
    toggle_grid_btn.on_clicked(on_toggle_grid)
    #plt.tight_layout()
    
    fig.canvas.mpl_connect('button_press_event', on_click)
    #plt.connect('button_press_event', on_click)

    # Maximize window
    # See https://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python
    def maximize():
        backend = str(plt.get_backend())
        mgr = plt.get_current_fig_manager()
        if backend == 'TkAgg':
            if os.name == 'nt':
                mgr.window.state('zoomed')
            else:
                mgr.resize(*mgr.window.maxsize())
        elif backend == 'wxAgg':
            mgr.frame.Maximize(True)
        elif backend == 'Qt4Agg':
            mgr.window.showMaximized()
            
    maximize()
    plt.show()



def load_image(files, i, startlabel = -1):

    while True:
        base = os.path.basename(files[i])
        # get label from filename (1.2_ new or 1_ old),
        if (base[1]=="."):
            target = base[0:3]
        else:
            target = base[0:1]
        
        try:
            category = float(target)
        except:
            category = 0
        if category >= startlabel:  
            break 
        else:
            i = (i + 1)

    filename = files[i]
    test_image = Image.open(filename)
    return test_image, category, filename, i
    
