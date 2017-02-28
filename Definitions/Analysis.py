class Analysis(object):
	def __init__(self):
		self.stored_properties = {
			"sha256" :		"",
			"md5" :			"",
			"filename" :	"",
			"filetype" :	"",
			"addresses" :	"",
			"domains" :		"",
			"packets" :		"",
			"link" :		"",
			"detection" :	"",
			"adapter" : 	""
		}
	
	@property
	def key(self):
		return "sha256"