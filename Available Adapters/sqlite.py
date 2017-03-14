### SQLite3 Meta Adapter ###

###   ADAPTER SETTINGS   ###
adapter_type =		"Meta"
database =			""
### END ADAPTER SETTINGS ###

import sqlite3, time

from Template import AdapterTemplate

class sqlite(AdapterTemplate): # Class name must match filename

	# Set up class instance with default values
	def __init__(self, *args):
		super(sqlite, self).__init__("", "", adapter_type, "", "", *args)
		self.conn = sqlite3.connect(database, timeout=10)
		self.c = self.conn.cursor()

	# Send work for adapters, send results to handle_output()
	def main(self, adapter):
		# adapter > get_inputs > adapter.main(), adapter > handle_output
		if not self.handle_output(adapter.main(self.get_inputs(adapter)), adapter):
			self.log("Failed to handle output of adapter: {1}".format(adapter.name), "fail")

	def get_inputs(self, adapter):
		now = time.strftime(self.date_format)
		
		# Structure data to pass to function
		stored_data = {
			"data"  : [],
			"state" : []
		}
		# Make sure the table is built for the adapter, in case it's new
		if not self.create_table(adapter.stored_properties, adapter.name.lower(), True):
			self.log("Failed creating table for {0} adapter.".format(adapter.name), "fail")
		# Make sure a table is built for the data type, in case it's new
		if adapter.input:
			objname = adapter.input().__class__.__name__ # Need data type name...
			if not self.create_table(adapter.input().stored_properties, objname.lower()):
				self.log("Failed creating table for {0} data type.".format(objname), "fail")
		
			# Get data type table columns to match with data
			self.c.execute("PRAGMA table_info({0});".format(objname))
			pragma = self.c.fetchall()
			# Get data type table data
			self.c.execute("SELECT * FROM {0} WHERE last_seen > '{1}';".format(objname.lower(), int(now) - 2))
			data = self.c.fetchall()
			# Build stored_data["data"]
			for row in data:
				# Using self.i is a terrible hack to get around Python's weird for loop scoping
				self.i = 0
				return_object = {}
				# while (i < len(pragma)):
				for column in pragma:
					return_object[pragma[self.i][1]] = row[self.i]
					self.i = self.i + 1
				stored_data["data"].append(return_object)
		
		# Get adapter table columns to match with state data
		self.c.execute("PRAGMA table_info({0});".format(adapter.name.lower()))
		pragma = self.c.fetchall()
		# Get adapter table data
		self.c.execute("SELECT * FROM {0} WHERE date > '{1}';".format(adapter.name.lower(), int(now) - 2))
		data = self.c.fetchall()
		# Build stored_data["state"]
		for row in data:
			return_object = {}
			# Using self.i is a terrible hack to get around Python's weird for loop scoping
			self.i = 0
			# while (i < len(pragma)):
			for column in pragma:
				return_object[pragma[self.i][1]] = row[self.i]
				self.i = self.i + 1
			stored_data["state"].append(return_object)
		
		return stored_data
	
	def handle_output(self, objectlist, adapter):
		# If an adapter fails, objectlist will be false
		if not objectlist:
			self.log("No output was given by {0}.".format(adapter.name), "warn")
			return True			
		statedata = objectlist["state"]
		objectlist = objectlist["data"]
		if adapter.type == "Test":
			return True
		objname = adapter.output().__class__.__name__ # Need data type name...
		# Make sure a table is there to receive data
		if not self.create_table(adapter.output().stored_properties, objname.lower()):
			self.log("Failed creating table for {0} data type.".format(objname), "fail")
		# Store values returned from the adapter
		if not self.write_data(objectlist, objname.lower(), adapter.output().key):
			self.log("Failed to record data object: {0}".format(objname), "fail")
			return False
		# Store tracking values
		if not self.write_data(statedata, adapter.name.lower(), adapter.key, True):
			self.log("Failed to save state data for {0}".format(adapter.name), "fail")
			return False
		return True
	
	### Database Methods ###
	
	# NOTE: None of these queries are parameterized, so this adapter cannot handle unsafe input.
	#		For production applications, a meta adpater should be implemented for a proper database
	#		using parameterized queries and input sanitization.
	#		This meta adapter is for development and demonstration purposes only.
	
	# Build table based on object contents
	def create_table(self, properties, objname, is_adapter = False):
		try:
			self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(objname))
			if self.c.fetchall()[0]:
				return True
		except:
			try:
				sql = "CREATE TABLE IF NOT EXISTS {0} (".format(objname)
				for var in properties:
					if type(properties[var]) is str:	vartype = "TEXT"
					elif type(properties[var]) is int:	vartype = "INT"
					elif type(properties[var]) is bool:	vartype = "BOOL"
					else:
						self.log("Input object {0} contains unsupported property of type: {1}".format(objname, type(var)), "warn")
						return False
					sql = "{0}{1} {2}, ".format(sql, var, vartype)
					
				sql = "{0}, date TEXT);".format(sql[:-2]) if is_adapter else "{0} first_seen TEXT, last_seen TEXT);".format(sql)
				self.c.execute(sql)
				self.conn.commit()
				self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(objname))
				if self.c.fetchall()[0]:
					self.log("Created table: {0}".format(objname), "success")
					return True
				# If we reach this block, table creation silently failed
				return False
			except:
				self.log("Table creation failed for: {0}".format(vartype), "fail")
				return False

	# Build dynamic queries based on object contents
	def write_data(self, objectlist, objname, key, is_adapter = False):
		now = time.strftime(self.date_format)
		# Try to update an existing entry
		for object in objectlist:
			args = []
			sql = "UPDATE {0} SET ".format(objname)
			for var in object:
				if var == "stored_properties":
					continue
				sql = "{0}{1}=?, ".format(sql, var)
				args.append(object[var])
			sql = sql[:-2] if is_adapter else "{0} last_seen='{1}'".format(sql, now)
			sql = "{0}WHERE {1}=?;".format(sql, key)
			args.append(object[key])
			self.c.execute(sql, (args))
			if not self.c.rowcount:
				args = []
				sql = "INSERT INTO {0} (".format(objname)
				sql2 = ") VALUES ("
				# Since inputs are unordered, both halves of the insert query must be built simultaneously
				for var in object:
					sql = "{0}{1}, ".format(sql, var)
					sql2 = "{0}?, ".format(sql2)
					args.append(object[var])
				sql = "{0}date{1}'{2}');".format(sql, sql2, now) if is_adapter else "{0}first_seen, last_seen{1}'{2}', '{2}');".format(sql, sql2, now)
				self.c.execute(sql, (args))
				result = self.c.fetchall()
				if not self.c.rowcount:
					self.log("SQL insert failed: {0}".format(sql), "fail")
					continue
			self.log("Executed query: {0}".format(sql), "success")
			self.conn.commit()
		return True
