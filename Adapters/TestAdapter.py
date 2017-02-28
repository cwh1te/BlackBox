### This is s kind of silly example, but it shows that an adapter can be created in just 16 lines of code. Good for testing basic functionality of a meta adapter.
stored_properties = {
	"example1" : 	"",
	"example2" : 	0,
	"example3" : 	False
}
key = 				"example1"
from Template import AdapterTemplate
class TestAdapter(AdapterTemplate):
	def __init__(self, *args):
		super(TestAdapter, self).__init__("", "", "Test", stored_properties, key, *args)
	def main(self, *args):
		output = {
			"data"  : [],
			"state" : []
		}
		return output