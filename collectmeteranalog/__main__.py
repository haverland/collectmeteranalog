import argparse
import sys

from collectmeteranalog import glob
from collectmeteranalog.collect import collect
from collectmeteranalog.labeling import label
from collectmeteranalog.predict import load_interpreter



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--collect', help='collect all images. The edgeAI meter server name must be set')
    parser.add_argument('--days', type=int, default=3, help='count of days back to read. (default: 3)')
    parser.add_argument('--labeling', default='', help='labelpath if you want label the images')
    parser.add_argument('--keepdownloads', action='store_true', help='Normally all downloaded data will be deleted. If set it keeps the images.')
    parser.add_argument('--nodownload', action='store_true', help='Do not download pictures. Only remove duplicates and labeling.')
    parser.add_argument('--startlabel', type=float, default=0.0, help='only images >= startlabel. (default: all)')
    parser.add_argument('--saveduplicates', action='store_true', help='Save the duplicates in an intermediate subdirectory in raw_images.')
    parser.add_argument('--labelfile', default=None, help='file with list of image urls if you want label specific images.')
    parser.add_argument('--model', default=None, help='model file path if a external model should be used or off if shoudl not be used')
    parser.add_argument('--ticksteps',type=int, default=1, help='how often ticks shown 1=0.1 steps, 2=0.2 steps, max=5')
    parser.add_argument('--similiarbits', type=int, default=2, help='how many pixes must be different if a image is not similiar to others')

    # print help message if no argument is given
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    args = parser.parse_args()

    if (args.ticksteps<1 or args.ticksteps>5):
        args.ticksteps = 1

    if (args.model!=None):
        glob.model_path = args.model
        load_interpreter(args.model)
    
    if (args.labeling==''):
        if (args.labelfile != None):
            label(args.labeling, args.startlabel, args.labelfile, ticksteps=args.ticksteps)    
        else:
            collect(args.collect, args.days, keepolddata=args.keepdownloads, download=not args.nodownload,
                    startlabel=args.startlabel, ticksteps=args.ticksteps, similarbits=args.similiarbits,
                    saveduplicates=args.saveduplicates)
    else:
        label(args.labeling, args.startlabel, ticksteps=args.ticksteps)    

if __name__ == '__main__':
    main()