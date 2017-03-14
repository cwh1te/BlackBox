# BlackBox v1.0
# by Caleb White

# Global settings
date_format = "%y%m%d"
datetime_format = "%y%m%d %H:%M:%S"
verbose = False	# Set to True if you dislike quiet scripts
debug = False	# Set to True for troubleshooting
log = False		# Set to True to generate logs from each script

log_format = {
    "header"	: "\033[95m",	# Purple
    "info"	: "\033[94m",	# Blue
    "success"	: "\033[92m",	# Green
    "warn"	: "\033[93m",	# Yellow
    "fail"	: "\033[91m",	# Red
    "end"	: "\033[0m"	# Ends colored text
}

# List of log types to always print
force_print = ["fail"]