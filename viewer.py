#!/opt/local/bin/python2.7

import os, sys
#import Tkinter
from Tkinter import *
#import Image, ImageTk
import PIL
from PIL import Image, ImageTk
import glob
import time
import shutil

drive = '/Volumes/My HD'
camdir = drive + '/Cameras'
archivedir = drive + '/Cameras.Archive'
savedir = drive + '/saved_images'
backupdir = '/Volumes/Other HD/saved_images'
cameras = ['Camera1', 'Camera2', 'Camera3', 'Camera4', 'Camera5']

class MyApp:

  def __init__(self, parent):

    self.myParent = parent
    self.myParent.title("Image Selector")
    #self.myParent.geometry("1024x120")

    self.camera_selection = StringVar()
    self.prefix_selection = StringVar()
    self.date_selection = StringVar()

    # Top row of buttons.
    self.topContainer = Frame(self.myParent)
    self.topContainer.pack(fill=X)
    self.button_view_files = Button(self.topContainer, text="View Files", command=lambda arg1="date" : self.image_viewer(arg1))
    self.button_view_files.pack(side=LEFT, expand=NO)
    self.button_archive_files = Button(self.topContainer, text="Archive Files", command=lambda arg1="date" : self.archiveFilesWrapper(arg1))
    self.button_archive_files.pack(side=LEFT, expand=NO)
    self.button_view_all_files = Button(self.topContainer, text="View All Files", command=lambda arg1="all" : self.image_viewer(arg1))
    self.button_view_all_files.pack(side=LEFT, expand=NO)
    self.button_archive_all_files = Button(self.topContainer, text="Archive All Files", command=lambda arg1="all" : self.archiveFilesWrapper(arg1))
    self.button_archive_all_files.pack(side=LEFT, expand=NO)
    self.button_archive_all_timelapse = Button(self.topContainer, text="Archive All Timelapse Files All Cameras", command=lambda arg1="all" : self.archiveTimelapse())
    self.button_archive_all_timelapse.pack(side=LEFT, expand=NO)
    self.button_quit = Button(self.topContainer, text="Quit", command=lambda : self.quitClick(self.myParent))
    self.button_quit.pack(side=LEFT, expand=NO)

    # Second row of buttons / camera names.

    self.cameraContainer = Frame(self.myParent)
    self.cameraContainer.pack(fill=X)

    for camera in cameras:
      self.camera = Radiobutton(self.cameraContainer, text=camera, indicatoron=0, variable=self.camera_selection, value=camera, command=lambda arg1=camera : self.camera_selected(arg1)) # indicatoron=0 doesn't seem to work on Mac.
      self.camera.pack(side=LEFT, expand=NO)

  def camera_selected(self, camera):

    #print self.camera_selection.get()
    #print

    # Third row of buttons / types of images found.

    #if self.typeContainer.winfo_exists():
    try:
      self.typeContainer
    except:
      #print "typeContainer didn't exist"
      pass
    else:
      try:
	self.dateContainer
      except:
	#print "dateContainer didn't exist"
	pass
      else:
	#print "destroying dateContainer"
	self.dateContainer.destroy()

      #print "destroying typeContainer"
      self.typeContainer.destroy()

    self.typeContainer = Frame(self.myParent)
    self.typeContainer.pack(fill=X)

    #print camera + " selected"
    self.prefixes = self.getprefixes(camera)
    #print self.prefixes

    for prefix in self.prefixes:
      #print prefix
      self.button_image_type = Radiobutton(self.typeContainer, text=prefix, indicatoron=0, variable=self.prefix_selection, value=prefix, command=lambda arg1=camera, arg2=prefix : self.type_selected(arg1, arg2))
      self.button_image_type.pack(side=LEFT, expand=NO)

  def type_selected(self, camera, prefix):

    #print self.camera_selection.get()
    #print self.prefix_selection.get()
    #print

    try:
      self.dateContainer
    except:
      #print "dateContainer didn't exist"
      pass
    else:
      #print "destroying dateContainer"
      self.dateContainer.destroy()

    self.dateContainer = Frame(self.myParent)
    self.dateContainer.pack(fill=X)

    self.dates = self.getdates(camera, prefix)
    #print dates

    for date in self.dates:
      #self.button_date = Radiobutton(self.dateContainer, text=date, indicatoron=0, variable=self.date_selection, value=date, command=lambda arg1=camera, arg2=prefix, arg3=date : self.date_selected(arg1, arg2, arg3))
      self.button_date = Radiobutton(self.dateContainer, text=date, indicatoron=0, variable=self.date_selection, value=date)
      self.button_date.pack(side=LEFT, expand=NO)

#  def date_selected(self, camera, prefix, date):
#      print self.camera_selection.get()
#      print self.prefix_selection.get()
#      print self.date_selection.get()
#      print

  def image_viewer(self, run_type):

    #print run_type
    #print self.camera_selection.get()
    #print self.prefix_selection.get()
    #print self.date_selection.get()
    #print

    if not self.camera_selection.get():
      print "No camera selected."
      return

    if not self.prefix_selection.get():
      print "No prefix selected."
      return

    # If run type isn't all and date is not specified.
    if run_type != "all" and not self.date_selection.get():
      print "No date selected."
      return

    # New window.

    try:
      self.viewer
      #self.viewer.winfo_exists():
    except:
      # self.viewer didn't exist.
      pass
    else:
      self.viewer.destroy()

    self.viewer = Toplevel(master=self.myParent)
    self.viewer.title("Image Viewer")

    self.viewer.action = StringVar()
    self.viewer.direction = IntVar()
    self.viewer.skip = IntVar()
    self.viewer.count = IntVar()

    if run_type == "all":
      date = ""
    else:
      date = self.date_selection.get()
    #print "date=" + date
    self.files = self.getfiles(self.camera_selection.get(), self.prefix_selection.get(), date)
    self.viewer.total = len(self.files)

    # Button Container.

    self.viewer.buttonContainer = Frame(self.viewer)
    self.viewer.buttonContainer.pack(fill=X)

    self.viewer.button_start = Button(self.viewer.buttonContainer, text="Start", command=lambda : self.start())
    self.viewer.button_start.pack(side=LEFT, expand=NO)

    self.viewer.button_play = Radiobutton(self.viewer.buttonContainer, text="Play", indicatoron=0, variable=self.viewer.action, value="play") 
    self.viewer.button_play.pack(side=LEFT, expand=NO)
    self.viewer.button_pause = Radiobutton(self.viewer.buttonContainer, text="Pause", indicatoron=0, variable=self.viewer.action, value="pause") 
    self.viewer.button_pause.pack(side=LEFT, expand=NO)

    self.viewer.button_forward = Radiobutton(self.viewer.buttonContainer, text="Forward", indicatoron=0, variable=self.viewer.direction, value=1) 
    self.viewer.button_forward.pack(side=LEFT, expand=NO)
    self.viewer.button_reverse = Radiobutton(self.viewer.buttonContainer, text="Reverse", indicatoron=0, variable=self.viewer.direction, value=-1) 
    self.viewer.button_reverse.pack(side=LEFT, expand=NO)

    self.viewer.button_step_forward = Button(self.viewer.buttonContainer, text="Step Forward", command=lambda arg1=1 : self.step(arg1))
    self.viewer.button_step_forward.pack(side=LEFT, expand=NO)

    self.viewer.button_step_backward = Button(self.viewer.buttonContainer, text="Step Backward", command=lambda arg1=-1 : self.step(arg1))
    self.viewer.button_step_backward.pack(side=LEFT, expand=NO)

    self.viewer.button_close = Button(self.viewer.buttonContainer, text="Close", command=lambda : self.quitClick(self.viewer))
    self.viewer.button_close.pack(side=LEFT, expand=NO)

    # Speed Container.

    self.viewer.speedContainer = Frame(self.viewer, pady=10)
    self.viewer.speedContainer.pack(fill=X)

    self.viewer.speedSlower = Label(self.viewer.speedContainer, text="Slower", anchor="se")
    self.viewer.speedSlower.pack(side=LEFT, expand=YES)

    self.viewer.speedScale = Scale(self.viewer.speedContainer, orient=HORIZONTAL, from_=-20, to=20, variable=self.viewer.skip, length=540)
    self.viewer.speedScale.pack(side=LEFT, expand=NO)

    self.viewer.speedFaster = Label(self.viewer.speedContainer, text="Faster", anchor="sw")
    self.viewer.speedFaster.pack(side=LEFT, expand=YES)

    # Image counts and save buttons.

    self.viewer.countContainer = Frame(self.viewer)
    self.viewer.countContainer.pack(fill=X)


    self.viewer.leftlabel = Label(self.viewer.countContainer, text="  1", pady=10)
    self.viewer.leftlabel.pack(side=LEFT, expand=NO)

    # Save Buttons.

    self.viewer.saveContainer = Frame(self.viewer.countContainer)
    self.viewer.saveContainer.pack(side=LEFT, expand=YES)

    self.viewer.button_save = Button(self.viewer.saveContainer, text="Save Current", command=lambda : self.saveImage(self.viewer.count.get()))
    self.viewer.button_save.pack(side=LEFT, expand=NO)

    self.viewer.firstSave = IntVar()

    self.viewer.button_setFirst = Button(self.viewer.saveContainer, text="Set First", command=lambda : self.setFirst(self.viewer.count.get()))
    self.viewer.button_setFirst.pack(side=LEFT, expand=NO)

    self.viewer.lastSave = IntVar()

    self.viewer.button_setLast = Button(self.viewer.saveContainer, text="Set Last", command=lambda : self.setLast(self.viewer.count.get()))
    self.viewer.button_setLast.pack(side=LEFT, expand=NO)

    self.viewer.button_saveRange = Button(self.viewer.saveContainer, text="Save Range", command=lambda : self.saveRange())
    self.viewer.button_saveRange.pack(side=LEFT, expand=NO)

    self.viewer.button_archive = Button(self.viewer.saveContainer, text="Archive Files and Close", command=lambda : self.archiveFilesAndClose())
    self.viewer.button_archive.pack(side=LEFT, expand=NO)

    self.viewer.rightlabel = Label(self.viewer.countContainer, text=self.viewer.total)
    self.viewer.rightlabel.pack(side=RIGHT, expand=NO)


    # Image Number Scale.

    self.viewer.numberContainer = Frame(self.viewer)
    self.viewer.numberContainer.pack(fill=X)

    self.viewer.numberScale = Scale(self.viewer.numberContainer, orient=HORIZONTAL, from_=1, to=self.viewer.total, variable=self.viewer.count, length=640)
    self.viewer.numberScale.pack(side=LEFT, expand=YES)

    self.viewer.action.set("pause")
    self.viewer.direction.set(1)
    self.viewer.skip.set(1)

    self.viewer.imageContainer = Frame(self.viewer)
    self.viewer.imageContainer.pack(expand=YES, fill=BOTH)

    #print self.viewer.total
    self.viewer.count.set(1)

    image = Image.open(self.files[0])
    self.viewer.imageCanvas = Canvas(self.viewer.imageContainer, width=image.size[0], height=image.size[1])
    self.viewer.imageCanvas.grid(row=0, column=0)
    self.viewer.imageCanvas.pack(expand=YES, fill=BOTH)

    # Creating the canvas outside the loop and not destroying it seems smoother on the screen, and
    # garbage collection seems to do a good job of cleaning up.
    #self.viewer.previousCanvas = None

    while self.viewer.winfo_exists():
      #print self.viewer.count.get()
      #if self.viewer.previousCanvas is not None:
        #self.viewer.previousCanvas.destroy()
      file = self.files[self.viewer.count.get() - 1]
      image = Image.open(file)
      tkpi = ImageTk.PhotoImage(image)
      #id = self.viewer.imageCanvas.create_image(0, 0, image=tkpi, anchor="nw")
      #self.viewer.imageCanvas.create_image(0, 0, image=tkpi, anchor="nw")
      self.viewer.imageCanvas.create_image(0, 0, image=tkpi, anchor=NW)
      #self.viewer.previousCanvas = self.viewer.imageCanvas
      self.viewer.imageCanvas.update()

      if self.viewer.direction.get() == 1: # We're going forward.
	if self.viewer.count.get() == self.viewer.total: # If we're at the last file, pause.
	  self.viewer.action.set("pause")
      else: # We're in reverse.
	if self.viewer.count.get() == 1: # If we're athte first file, pause.
	  self.viewer.action.set("pause")

      prev_count = self.viewer.count.get()

      while self.viewer.winfo_exists() and self.viewer.action.get() == "pause" and prev_count == self.viewer.count.get():
	time.sleep(0.05)
	#print "Sleeping in pause loop"
	self.viewer.imageCanvas.update()
	#print self.viewer.count.get()
      else:
	if prev_count != self.viewer.count.get():
	  continue # prevent double increment.

      if self.viewer.skip.get() >= 0: # Skip images.
	if self.viewer.direction.get() == 1: # Forward
	  self.viewer.count.set(self.viewer.count.get() + self.viewer.skip.get())
	else: # Reverse
	  self.viewer.count.set(self.viewer.count.get() - self.viewer.skip.get())
      else: # Slow down.
	self.viewer.count.set(self.viewer.count.get() + self.viewer.direction.get())
	time.sleep(-self.viewer.skip.get()*0.05)
	#print "Sleeping in slowdown"
	self.viewer.imageCanvas.update()

      # Stay in bounds.
      if self.viewer.count.get() < 1:
	self.viewer.count.set(1)
      if self.viewer.count.get() > ( self.viewer.total ):
	self.viewer.count.set(self.viewer.total)

      # 0 doesn't work.
      if self.viewer.skip.get() == 0:
	self.viewer.skip.set(1)

  def step(self, direction):
    self.viewer.direction.set(direction)
    if self.viewer.skip.get() == 0:
      self.viewer.skip.set(1)
    if self.viewer.skip.get() > 0:
      self.viewer.count.set(self.viewer.count.get() + self.viewer.skip.get() * self.viewer.direction.get())
    else:
      self.viewer.count.set(self.viewer.count.get() + self.viewer.direction.get())
    self.viewer.action.set("pause")

  def start(self):
    self.viewer.direction.set("1")
    self.viewer.count.set(1)
    self.viewer.action.set("play")

  def getprefixes(self, camera):
    search_pattern = camdir + "/" + camera + "/" + camera + "*.jpg"
    #print search_pattern
    prefixes_dict = {}
    for f in glob.glob(search_pattern):
      file = os.path.basename(f)
      prefixes_dict[file.split('_')[0]] = 1
    prefixes = prefixes_dict.keys()
    prefixes.sort()
    return prefixes

  def getdates(self, camera, prefix):
    search_pattern = camdir + "/" + camera + "/" + prefix + "_" + "*.jpg"
    #print search_pattern
    dates_dict = {}
    for f in glob.glob(search_pattern):
      file = os.path.basename(f)
      dates_dict[file.split('_')[1]] = 1
    dates = dates_dict.keys()
    dates.sort()
    return dates
      
  def getfiles(self, camera, prefix, date):
    search_pattern = camdir + "/" + camera + "/" + prefix + "_" + date + "*.jpg"
    #print search_pattern
    files = glob.glob(search_pattern)
    files.sort()
    return files

  def quitClick(self, myParent):
    myParent.destroy()

  def saveImage(self, count):
    file = self.files[count - 1]
    print "Copying " + file + " to " + savedir + "..."
    shutil.copy2(file, savedir)
    print "Copying " + file + " to " + backupdir + "..."
    shutil.copy2(file, backupdir)

  def setFirst(self, count):
    self.viewer.firstSave.set(count)
    print "Selected image number " + str(count) + " as first in range."

  def setLast(self, count):
    self.viewer.lastSave.set(count)
    print "Selected image number " + str(count) + " as last in range."

  def saveRange(self):
    first = self.viewer.firstSave.get()
    last = self.viewer.lastSave.get()
    if first == 0 or last == 0:
      print "Please set both a first and last image to save range."
    elif first > last:
      print "The first in the range cannot come after the last."
    else:
      #print "Range starts at: " + str(first)
      #print "Range ends at: " + str(last)
      print "Saving " + str(last - first + 1) + " images..."
      for count in range(first, last+1):
	#print count
	self.saveImage(count)

  def archiveFiles(self):
    if len(self.files) <= 0:
      print "No files specified for deletion"
      return
    if os.path.exists(self.files[0]):
      print "Archiving " + str(len(self.files)) + " files..."
      for file in self.files:
	date = file.split('_')[1]
	camera = os.path.basename(file).split('-')[0]
	dir = archivedir + "/" + camera + "/" + date
	if not os.path.exists(dir):
	  #print "Making archive directory " + dir + "..."
	  os.mkdir(dir)
	#print "Moving " + file + " to " + dir
	shutil.move(file, dir)
    else:
      print "Files appear to have been already moved..."

  def archiveFilesAndClose(self):
    self.archiveFiles()
    self.quitClick(self.viewer)

  def archiveFilesWrapper(self, run_type):
    if run_type == "all":
      date = ""
    else:
      date = self.date_selection.get()
    if not self.camera_selection.get():
      print "No camera selected."
      return
    if not self.prefix_selection.get():
      print "No prefix selected."
      return
    self.files = self.getfiles(self.camera_selection.get(), self.prefix_selection.get(), date)
    self.archiveFiles()

  def archiveTimelapse(self):
    self.files = self.getfiles('*', "*CamUniversal-Timelapse", "")
    self.archiveFiles()


root = Tk()
myapp = MyApp(root)
root.mainloop()
