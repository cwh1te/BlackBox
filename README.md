```██████╗ ██╗      █████╗  ██████╗██╗  ██╗██████╗  ██████╗ ██╗  ██╗  
██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝  
██████╔╝██║     ███████║██║     █████╔╝ ██████╔╝██║   ██║ ╚███╔╝   
██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██╔══██╗██║   ██║ ██╔██╗   
██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██████╔╝╚██████╔╝██╔╝ ██╗  
╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝```

### Table of Contents

* [Introduction](#intro)
* [Installation](#setup)
* [Definitions](#definitions)
* [Adapters](#adapters)
* [Meta Adapters](#meta)
* [Adapter Template](#template)
* [License](#license)


## <a name="intro"></a>Introduction

BlackBox is a Python workflow microframework that facilitates the
interactions of `adapters` through naïve abstraction.
`Adapters` are purpose-built modules that intake and/or output data.
The data they intake and output is structured around `definitions`.
All of the data, including historical data of `adapters`, is stored
by special `meta adapters`.

Basically, BlackBox is whatever you decide to plug into it.

I'm using it to automate malware analysis, email inbox monitoring,
reporting through project management APIs, and more. It's easy to
add and test new modules quickly. I've added a few examples from a
malware analysis workflow to get you started, but you can do just
about anything you want around the core code.

The best way to make use of this project is probably to fork it so
you can start building modules for your own purposes. Feel free to
send a pull request for anything you think other people could use!


## <a name="setup"></a>Installation

This project should work out of the box in a standard Python 3.x
environment.

I have plans to write a setup script that queries all adapters for
their dependencies.


## <a name="definitions"></a>Definitions

Definitions are simple modules containing key/value data structures
that define the inputs and outputs of adapters. Here is an example:

```python
	# The class name must be the same as the file name
	class Example(object):
		def __init__(self):
			# Stored_properties is used as a template by adapters
			self.stored_properties = {
				"text_value" :	"",
				"int_value" :	0,
				"bool_value" :	False
			}
			
		@property
		def key(self):
			# This should be a key from the stored_properties that
			#	represents a unique value
			return "text_value"
```

Note that data types are important, and if you change them you will
have some backend repairs to do. Currently, only simple data types
string, integer, and boolean are supported.


## <a name="adapters"></a>Adapters

Adapters are the functional part of your project. They can accept an
input type, and output an output type, based on the definitions that
are available. 

```python
	### Example Adapter ###

	###   ADAPTER SETTINGS   ###
	# See Definitions directory for available input/output types
	# input_type is not required, but output_type is
	input_type =		""
	output_type =		""

	# Stored properties provide state information to your adapter
	# Valid formats are string, int, and bool
	# A timestamp should be added by the metamodule
	stored_properties = {
		"example1" : "",
		"example2" : 0,
		"example3" : False
	}
	# What value from stored_properties should the meta module key on?
	key = "example1"
```

If your adapter needs API keys, locations, or any other configuration
stuff, go ahead and define variables for that next.

```python
	# Miscellaneous settings specific to this adapter
	#		...
	#			...
	### END ADAPTER SETTINGS ###
```

Now you're ready to create the class

```python
	from Template import AdapterTemplate
	
	# Class name must match filename
	class BlankAdapter(AdapterTemplate):

		# Set up class instance with default values
		def __init__(self, *args):
			super(BlankAdapter, self).__init__(input_type, output_type, "", stored_properties, key, *args)
			# Change "BlankAdapter" to the class name
```	

At this point, you can perform any initialization function necessary.
It might be testing a connection, checking that a directory exists,
or any number of other things.

On to the main function!

```python
		def main(self, input):		
			# input will be an list of instances of input_type
```
			
Here is where you interate through the `input` list, doing with it the
thing the module is supposed to do with it. If your module gets its
input from outside the workflow, you can replace `input` with `*args`.

Use your definitions as a reference when populating the output list.

```python
			###   OUTPUT OBJECT   ###
			# The output object should contain:
			#	data (list of instances of the output_type)
			#	state (list of instances of self.stored_properties)
			
			output = {
				"data"  : [],
				"state" : []
			}
			### END OUTPUT OBJECT ###
			
			return output
```

If that seemed long, it's probably because there were so many comments.
Take a look at the test adapter if you don't believe me - it's only 16
lines of code!


## <a name="meta"></a>Meta Adapters

Meta adapters are the complicated part of BlackBox that make writing
adapters so simple. They create and maintain databases with tables for
each adapter and definition.

TODO: Expand this portion of the readme extensively


## <a name="template"></a>Adapter Template

TODO: Explain what the adapter template is for


## <a name="license"></a>License

Licensed under GNU GPLv3

See license.txt for full text