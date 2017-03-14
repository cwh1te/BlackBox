adapter_type =		"Analysis"
input_type =		"File"
output_type =		"Analysis"
stored_properties = {
	"sha256" :	"",
	"filename" :	"",
	"job_id" :	"",
	"status" :	""
}

from MalwrAPI import MalwrAPI
from bs4 import BeautifulSoup
from Template import AdapterTemplate

class Malwr(AdapterTemplate):
	def __init__(self, *args):
		super(Malwr, self).__init__(input_type, output_type, adapter_type, stored_properties, *args)
	def main(self, input):
		output = {
			"data"  : [],
			"state" : []
		}
		
		# Check on earlier submissions
		for item in input["state"]:
			if item["status"] == "completed":
				continue
			elif not item["status"] == "analyzed":
				try:
					payload = {
						"api_key": api_key,
						"uuid": item["job_id"]
					}
					results = requests.get(
						"https://malwr.com/api/analysis/status/",
						params = payload
					)
					if results == b'Unknown analysis UUID':
						self.log("The UUID ({0}) for this submission is invalid. Please resubmit manually.".format(item["job_id"]))
					elif results.status_code is not "200":
						self.log("Received HTTP status {0}".format(results.status_code), "warn")
					else:
						try:
							results = json.loads(str(results)[2:-1])
						except:
							self.log("Unable to parse Malwr.com response as JSON:\n{0}".format(results), "fail", force=True)
							continue
						# We only need to do anything if the status is "completed"
						if results["status"] == "completed":
							item["status"] = "analyzed"
							output["state"].append(item.copy())
						self.log("Analysis of {0} is {1}.".format(item["sha256"][-20:], results["status"]))
				except:
					self.log("Progress check of job {0} didn't go so well.".format(item["job_id"]))
					if self.debug: raise

			# Gather information on completed items
			if item["status"] == "analyzed":
				data = self.output().stored_properties
				link = "http://malwr.com/analysis/{0}".format(item["job_id"])
				try:
					temp = requests.get(link)
					temp = BeautifulSoup(temp.text, "lxml")
					network = temp.find_all("div", id="network")
					
					# This shouldn't happen, but might if something changes
					if network == []:
						ret = "Error"
						self.log("Failed to obtain Malwr report for job {0}".format(item["job_id"]), "warn")
					else:
						network = network[0].find_all("div", class_="tab-content")
						self.log("Obtained report information for job {0}".format(item["job_id"]))
						data["sha256"] = item["sha256"]
						data["filename"] = item["filename"]
						data["addresses"] = self.get_addresses(network)
						data["domains"] = self.get_domains(network)
						#data["packets"] = extract the packets somehow
						data["link"] = link
						data["adapter"] = "Malwr"
						item["status"] = "completed"
						output["data"].append(data)
						output["state"].append(item)
					return network
				except:
					self.log("Failed to obtain Malwr report")
					if self.debug: raise
		
		seen_items = [x["sha256"] for x in input["state"]]
		
		# Submit new items
		for item in input["data"]:
			if item["sha256"] in seen_items:
				continue
			state = self.stored_properties
			self.log("Submitting {0} for analysis.".format(item["filename"]))
			api_authenticated = MalwrAPI(verbose=False)
			res = api_authenticated.submit_sample(filepath = "{0}/{1}".format(item["filepath"], item["filename"]))
			if not res:
				self.log("Unable to submit sample {0}".format(item["filename"]), "warn")
			elif res == "Already submitted":
				self.log("File analysis already in progress. I'll check again next run.")
			else:
				state["status"] = "pending"
				# Malwr.com only gives an analysis link, rather than giving the UUID directly
				# So we have to do silly things to get the UUID... *grumble grumble*
				uuid = str(res['analysis_link'])
				uuid = uuid[uuid.find('/',1)+1:len(uuid)-1]
				state["job_id"] = uuid[uuid.find('/')+1:]
				state["sha256"] = item["sha256"]
				state["filename"] = item["filename"]
				output["state"].append(state)
		
		return output
