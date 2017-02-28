#!/usr/bin/python3

# I use tabs, not spaces. Sorry not sorry.

import os, sys, argparse, textwrap, settings, importlib

# Handle commandline arguments
parser = argparse.ArgumentParser(
	prog="BlackBox",
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent("""\
		BlackBox v1.0
		  by Caleb White
		
		NOTE: Before use, be sure to add and configure adapters with your settings
	"""),
	epilog=textwrap.dedent("""\
		Any flags set at runtime will override the imported settings,
		but some settings do not have a corresponding flag.
	""")
)
parser.add_argument(
	"--verbose",
	help="makes the script rather talkative",
	required=False,
	action='store_true',
	dest="verbose")
parser.add_argument(
	"--debug",
	help="this will show you full, ugly errors when they happen",
	required=False,
	action='store_true',
	dest="debug")
parser.add_argument(
	"--log",
	help="this will record all output to log files",
	required=False,
	action="store_true",
	dest="log")
parser.add_argument(
	"--moo",
	help=argparse.SUPPRESS,
	required=False,
	action='store_true',
	dest="moo")
args = parser.parse_args()

# Moo - the most important part of all this nonsense
if args.moo:
	print(textwrap.dedent("""\
           ,=    ,        =.
  _  _   /'/    )\\,/,/(_   \\`\\
   `//-.|  (  ,\\\\)\\//\\)\\/_  ) |
   //___\\   `\\\\\\/\\\\/\\/\\\\///'  /
,-\"~`-._ `\"--'_   `\"\"\"`  _ \\`'\"~-,_
\\       `-.  '_`.      .'_` \\ ,-\"~`/
 `.__.-'`/   (-\\        /-) |-.__,'
   ||   |     \\O)  /^\\ (O/  |
   `\\\\  |         /   `\\    /
the  \\\\  \\       /      `\\ /
cow   `\\\\ `-.  /' .---.--.\\
says    `\\\\/`~(, '()      ()
'moo'    /(O) \\\\   _,.-.,_)
        //  \\\\ `\\'`      /
       / |  ||   `\"\"~~~\"`
     /'  |__||
           `o """))
	exit(0)

# Get default arguments from pipe or settings - whichever is true first
verbose = args.verbose if args.verbose else settings.verbose
debug = args.debug if args.debug else settings.debug
log = args.log if args.log else settings.log

### Adapter Enumeration ###

# Add Adapters directory to path to avoid layered import errors
sys.path.insert(1, os.path.join(sys.path[0], 'Adapters'))

# Set up arrays to receive adapters
adapters, meta_adapters = [], []

# Get all contents of Adapters directory
try:
	adapter_list = [f for f in os.listdir(os.path.join(sys.path[0], 'Adapters'))]
except:
	# This isn't great, but it should only ever happen once...
	print("Failed to get adapters. Have you set any up?")
	if debug:
		raise

# Iterate through the list of files
for adapter_name in adapter_list:
	# Split file into name and extension
	adapter_name = adapter_name.split(".")
	try:
		# Ignore the template, directories, and any non-python files
		if os.path.isdir(adapter_name[0]) or adapter_name[1] != "py" or adapter_name[0] == "Template":
			continue
		# Import the adapter
		adapter = importlib.import_module(adapter_name[0], "Adapters.{0}".format(adapter_name[0]))
		# Import and initialize the adapter's class
		adapter = getattr(adapter, adapter_name[0])
		adapter = adapter(verbose, debug, log)
		adapter.log("Module loaded!", "success")
		# Drop it in the proper array
		if adapter.type == "Meta":
			meta_adapters.append(adapter)
		else:
			adapters.append(adapter)
	except:
		if debug:
			raise
		continue

### Adapter Execution ###

# Iterate through available adapters
for adapter in adapters:
	# Feed modules to meta adapter(s)
	for meta in meta_adapters:
		meta.main(adapter)