### Directory Monitor Adapter ###

###   ADAPTER SETTINGS   ###
output_type =	"File"
input_type =	""
stored_properties = {
	"sha256" :	""
}
key =			"sha256"

directory =		""
### END ADAPTER SETTINGS ###

import time, os, zipfile
from Template import AdapterTemplate

class DirectoryMonitor(AdapterTemplate):

	# Set up class instance with default values
	def __init__(self, *args):
		super(DirectoryMonitor, self).__init__(input_type, output_type, "", stored_properties, key, *args)
		
		# Find or make directory for current day
		self.directory = os.path.join(directory, time.strftime(self.date_format))
		self.mkdir(self.directory)
			
	def main(self, history):
		# Enumerate files in the directory
		filelist = [f for f in os.listdir(self.directory)]
		
		# Return False if no files present
		if len(filelist) == 0:
			self.log("No files found.")
		
		else:
			# Extract any zip files in the directory
			for file in filelist:
				if file[-4:] == ".zip":
					self.log("Encountered ZIP file. Extracting and restarting enumeration.")
					try:
						with zipfile.ZipFile("{0}/{1}".format(self.directory, file)) as zip:
							# testzip() returns None or name of first bad file
							if zipfile.ZipFile.testzip(zip) is not None:
								self.log("Malformed ZIP or contents corrupted! Unable to process.", "fail")
								continue
							# Not using extractall() because we don't want a tree structure
							for member in zip.infolist():
								# Rename file if necessary to avoid overwrite...
								i = 0
								while os.path.exists("{0}/{1} ({2}){3}".format(self.directory, member[:-4], i, att.name[-4:]) if i else "{0}/{1}".format(self.directory, member)):
									i += 1
								# Apply the filename determined by the previous step
								if i:
									member = "{1} ({2}){3}".format(member[:-4], i, member[-4:])
								zip.extract(member, self.directory)
							# Delete the zip now that we have its contents
							os.remove("{0}/{1}".format(self.directory, file))
					except:
						self.log("Unable to open ZIP file {0}. You should check its headers or something.".format(file), "fail")
						continue
					
			# Rebuild filelist
			filelist = [f for f in os.listdir(self.directory)]
			self.log("Located {0} files.".format(len(filelist)))
		
		# Build output object
		output = {
			"data"  : [],
			"state" : []
		}
		
		for file in filelist:
			data = self.output().stored_properties
			data["filename"] = file
			data["filepath"] = self.directory
			data["sha256"] = self.sha256("{0}/{1}".format(self.directory, file))
			state = self.stored_properties
			state["sha256"] = data["sha256"]
			output["data"].append(data)
			output["state"].append(state)
		
		return output