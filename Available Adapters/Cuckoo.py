
### Cuckoo Sandbox Adapter ###

###   ADAPTER SETTINGS   ###
input_type =		"File"
output_type =		"Analysis"
stored_properties = {
	"sha256" :		"",
	"filename" :	"",
	"job_id" :		"",
	"status" :		""
}
key =				"sha256"

address =			""	# http(s)://[IP or Hostname]
port =				""	# API port
client_port =		""	# Web server port
### END ADAPTER SETTINGS ###

import requests, json
from Template import AdapterTemplate

class Cuckoo(AdapterTemplate):
	def __init__(self, *args):
		super(Cuckoo, self).__init__(input_type, output_type, "", stored_properties, key, *args)
		test = requests.get("{0}:{1}/cuckoo/status".format(address, port))
		self.cuckoo_down = False
		if not test.status_code == 200:
			self.log("Server failed status check. Adapter disabled.", "fail")
			self.cuckoo_down = True

	def main(self, input):
		if self.cuckoo_down:
			return False

		output = {
			"data"  : [],
			"state" : []
		}
		
		# Check on earlier submissions
		for item in input["state"]:
			if item["status"] == "completed":
				continue
			try:
				results = requests.get("{0}:{1}/tasks/view/{2}".format(address, port, item["job_id"]))
				if not results.status_code == 200:
					self.log("Received HTTP status {0}".format(results.status_code), "warn")
					continue
				try:
					results = results.json()
					if results["task"]["status"] == "reported":
						item["status"] = "analyzed"
						output["state"].append(item.copy())
						self.log("Analysis of {0} is {1}".format(item["sha256"][-20:], results["task"]["status"]))
						results = requests.get("{0}:{1}/tasks/report/{2}".format(address, port, item["job_id"]))
						results = results.json()
						data = self.output().stored_properties
						try:
							data["sha256"] = item["sha256"]
							data["md5"] = results["target"]["file"]["md5"]
							data["filename"] = item["filename"]
							data["filetype"] = results["target"]["file"]["type"]
							network_info = []
							for x in results["network"]:
								for y in results["network"][x]:
									if "dst" in y:
										network_info.append(y["dst"])
							network_info = list(set(network_info))
							data["addresses"] = self.get_addresses(" ".join(z for z in network_info))
							data["domains"] = self.get_hyperlinks(" ".join(z for z in network_info))
							#data["packets"] = need to get and parse pcap
							data["link"] = "{0}:{1}/analysis/{2}".format(address, client_port, item["job_id"])
							data["adapter"] = "Cuckoo"
							output["data"].append(data.copy())
						except:
							self.log("Failed to parse report for job {0}".format(item["job_id"]))
							raise
				except:
					self.log("Unable to parse response as JSON:\n{0}".format(results), "fail", force=True)
					raise
			except:
				self.log("Something went wrong with the progress check for job {0}".format(item["job_id"]))
				raise
		
		# Submit new items
		seen_items = [x["sha256"] for x in input["state"]]
		
		for item in input["data"]:
			if item["sha256"] in seen_items:
				continue
			state = self.stored_properties.copy()
			state["sha256"] = item["sha256"]
			state["filename"] = item["filename"]
			self.log("Submitting {0} for analysis.".format(item["sha256"][-20:]))
			with open("{0}/{1}".format(item["filepath"], item["filename"]), "rb") as sample:
				file = {"file": (item["filename"], sample)}
				results = requests.post("{0}:{1}/tasks/create/file".format(address, port), files=file)
			try:
				task_id = results.json()["task_id"]
				state["job_id"] = task_id
				state["status"] = "submitted"
				output["state"].append(state)
			except:
				self.log("Submission failed for {0}".format(item["sha256"][-20:]))
		
		return output