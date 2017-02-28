# Adapter Template

import os, sys, functools, hashlib, time, re, importlib
# Add parent directory to PATH to get main settings
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import settings as global_settings

class AdapterTemplate(object):

	# Set up class instance with default values
	def __init__(self, input_type = "", output_type = "", adapter_type = "", stored_properties = [], key = "", verbose = global_settings.verbose, debug = global_settings.debug, keep_log = global_settings.log, *args):
		# Set adapter type
		self.type = adapter_type
		# Find out my new name
		self.name = self.__class__.__name__
		# Import class definitions for input_type and output_type of templated adapter
		if input_type:
			try:
				sys.path.insert(1, os.path.join(sys.path[0], 'Definitions'))
				data = importlib.import_module(input_type)
				self.input = getattr(data, input_type)
			except:
				self.log("Unable to import input data definition: {0}".format(input_type), "fail")
		else:
			self.input = False
		if output_type:
			try:
				sys.path.insert(1, os.path.join(sys.path[0], 'Definitions'))
				data = importlib.import_module(output_type)
				self.output = getattr(data, output_type)
			except:
				self.log("Unable to import output data definition: {0}".format(output_type), "fail")
		else:
			self.output = False
		self.stored_properties = stored_properties
		self.key = key
		# Get various other settings
		self.verbose = verbose
		self.debug = debug
		self.keep_log = keep_log
		self.log_format = global_settings.log_format
		self.date_format = global_settings.date_format
		self.datetime_format = global_settings.datetime_format
	
	# Log events to shell and/or log file
	def log(self, message, type = "info", force = False):
		# [adapter_type:adapter_name] message
		message = "{0}[{1}] {2} - {3} {4}".format(
			self.log_format[type],
			self.name,
			message,
			time.strftime(global_settings.datetime_format),
			self.log_format["end"]
		)
		
		# Print if running in verbose mode or if "force" is true
		if self.verbose or force:
			print(message)
		
		# Log to file if appropriate
		if self.keep_log:
			temp = open("logs/{0}.log".format(self.type), "a")
			print(message, file=temp)
			temp.close()

	# Return SHA256 hash of file
	def sha256(self, filename):
		sha2h = hashlib.sha256()
		try:
			with open(filename, "rb") as f:
				[sha2h.update(chunk) for chunk in iter(functools.partial(f.read, 256), b"")]
		except:
			self.log("Failed to calculate SHA256 for file: {0}".format(filename), "fail")
			return False
		return sha2h.hexdigest()
	
	# Return newline-delimited list of hyperlinks from text
	def get_hyperlinks(self, text):
		try:
			regex = re.compile("(?i)(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!;:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=;~_|$])")
			# list(set()) will return only unique results, joining with "\n" converts to string for return
			hyperlinks = '\n'.join(list(set(regex.findall(text))))
			hyperlinks = hyperlinks if hyperlinks else "No hyperlinks identified"
		except:
			hyperlinks = "Failed to extract hyperlinks."
		return hyperlinks
	
	# Return newline-delimited list of IPv4 addresses from text
	def get_addresses(self, text):
		try:
			regex = re.compile("[1-2]?[0-9]{1,2}[\.][1-2]?[0-9]{1,2}[\.][1-2]?[0-9]{1,2}[\.][1-2]?[0-9]{1,2}")
			# list(set()) will return only unique results, joining with "\n" converts to string for return
			addresses = '\n'.join(list(set(regex.findall(text))))
			addresses = addresses if addresses else "No addresses identified"
		except:
			addresses = "Failed to extract IP addresses."
		return addresses
		
	def mkdir(self, dir):
		if not os.path.isdir(dir):
			try:
				os.makedirs(dir)
				self.log("Created new directory {0}".format(dir), "success")
			except OSError as exception:
				self.log("I tried to make a directory, but couldn't.", "fail")
				if self.debug:
					raise
		else:
			self.log("Directory {0} is ready.".format(dir))