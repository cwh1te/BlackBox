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
		self.force_print = global_settings.force_print
	
	# Log events to shell and/or log file
	def log(self, message, type = "info", force = False):
		if type in self.force_print:
			force = True
	
		# [adapter_name] message
		message = "{0}[{1}] {2} - {3} {4}".format(
			self.log_format[type],
			self.name,
			message,
			time.strftime(self.datetime_format),
			self.log_format["end"]
		)
		
		# Print if running in verbose mode or if "force" is true
		if self.verbose or force:
			print(message)
		
		# Log to file if appropriate
		if not os.path.isdir(os.path.join(os.getcwd(), "logs")):
			os.makedirs("logs")
		if self.keep_log:
			with open("logs/{0}.log".format(self.name), "a") as temp:
				temp.write("{0}\n".format(message))

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
			
	def extract_file(self, file, loop=True):
		import zipfile, gzip, tarfile, shutil

		out_files = []
		file = str(file)
		f_base, f_ext = os.path.splitext(file)

		# ZIP archives
		if f_ext == ".zip":
			self.log("Expanding ZIP archive {0}.".format(file))
			try:
				with zipfile.ZipFile(os.path.join(self.directory, file)) as zip:
					# testzip() returns None or name of first bad file
					if zipfile.ZipFile.testzip(zip) is not None:
						self.log("Malformed ZIP or contents corrupted! Unable to process.", "fail")
						return False
					# Not using extractall() because we don't want a tree structure
					for member in zip.infolist():
						member = self.unique_fname(member)
						zip.extract(member, self.directory)
						out_files.append(str(member))
					# Delete the zip now that we have its contents
					os.remove(os.path.join(self.directory, file))
			except:
				self.log("Unable to expand ZIP archive {0}. You should check its headers or something.".format(file), "fail")
				if self.debug:
					raise
				return False

		# GZIP compression
		elif f_ext == ".gz":
			self.log("Expanding GZIP compressed file {0}.".format(file))
			try:
				out_fname = self.unique_fname(f_base)
				with gzip.open(os.path.join(self.directory, file), "rb") as f_in, open(os.path.join(self.directory, out_fname), "wb") as f_out:
					shutil.copyfileobj(f_in, f_out)
				out_files.append(out_fname)
				# Delete the gz now that we have its contents
				os.remove(os.path.join(self.directory, file))
			except:
				self.log("Unable to expand GZIP file {0}. It's likely malformed.".format(file), "fail")
				if self.debug:
					raise
				return False

		# TAR archives
		elif f_ext == ".tar":
			self.log("Expanding TAR archive {0}.".format(file))
			try:
				with tarfile.open(os.path.join(self.directory, file), "r") as tar:
					for member in tar.getmembers():
						if member.isreg():
							# Strip any path information from members
							member.name = self.unique_fname(os.path.basename(member.name))
							tar.extract(member, self.directory)
							out_files.append(member.name)
					# Delete the tar now that we have its contents
					os.remove(os.path.join(self.directory, file))
			except:
				self.log("Unable to expand TAR archive {0}. Something is wrong with it.".format(file), "fail")
				if self.debug:
					raise
				return False
		
		# The file is not compressed or archived, or not a supported format
		else:
			out_files.append(file)
		
		if not loop:
			return out_files
		
		# Iterate back through, in case of layered archives or compressed archives (e.g. example.tar.gz)
		final_out_files = []
		for file in out_files:
			# Set loop switch to False to avoid creating blackhole
			final_out_files.append(self.extract_file(file, False))
		
		return final_out_files

	def unique_fname(self, file):
		# Rename file if necessary to avoid overwrite...
		basename, ext = self.get_fext(str(file))
		i = 0
		while os.path.exists(os.path.join(self.directory, "{0} ({1}){2}".format(basename, i, ext)) if i else "{0}/{1}".format(self.directory, file)):
			i += 1
		# Apply the filename determined by the previous step
		if i:
			file = "{0} ({1}){2}".format(basename, i, ext)
		return file
		
	def get_fext(self, file):
		basename, ext = os.path.splitext(file)
		while "." in basename[-6:]:
			basename, ext2 = os.path.splitext(basename)
			ext = ext2 + ext
		return basename, ext