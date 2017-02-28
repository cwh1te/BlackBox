class File(object):
	def __init__(self):
		self.stored_properties = {
			"filename" :	"",
			"filepath" :	"",
			"sha256" :		""
		}
	
	@property
	def key(self):
		return "sha256"