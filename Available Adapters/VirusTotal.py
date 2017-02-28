
### Cuckoo Sandbox Adapter ###

###   ADAPTER SETTINGS   ###
output_type =		"Analysis"
input_type =		"File"
stored_properties = {
	"sha256" :		"",
	"link" :		"",
	"filename" :	"",
	"status" :		""
}
key =				"sha256"

api_key =			""
# I couldn't find a definitive list of supported filetypes, but these are all allowed - I know there are more that should be added
allowed_filetypes = ["exe", "dll", "js", "vbs", "hta", "jpg", "jpeg", "png", "doc", "docm", "pdf"]
### END ADAPTER SETTINGS ###

import requests, os, urllib, json
from Template import AdapterTemplate

class VirusTotal(AdapterTemplate):
	def __init__(self, *args):
		super(VirusTotal, self).__init__(input_type, output_type, "", stored_properties, key, *args)
		
	def main(self, input):
		output = {
			"data"  : [],
			"state" : []
		}
		
		# Check on earlier submissions
		for item in input["state"]:
			if item["status"] == "completed":
				continue
			if not item["status"] == "analyzed":
				try:
					params = {
						"apikey": api_key,
						"resource": item["sha256"]
					}
					headers = {
						"Accept-Encoding": "gzip, deflate",
						"User-Agent": "gzip, BlackBox"
					}
					res = requests.get("https://www.virustotal.com/vtapi/v2/file/report", params=params, headers=headers)
					res = res.json()
					if res == []:
						self.log("Returned empty response for {0}.".format(item["sha256"]), "warn")
					elif res["response_code"] == 1:
						self.log("Analysis of {0} is complete.".format(item["sha256"]), "success")
						item["status"] = "analyzed"
						output["state"].append(item)
					else:
						self.log("{0} status: {1}".format(item["sha256"], res["verbose_msg"]))
				except:
					self.log("Progress check of {0} didn't go so well.".format(item["sha256"]), "warn")
					if self.debug: raise

			# Gather information on completed items
			if item["status"] == "analyzed":
				data = self.output().stored_properties
				link = "https://www.virustotal.com/en/file/{0}/analysis/".format(item["sha256"])
				try:
					url = "https://www.virustotal.com/vtapi/v2/file/report"
					parameters = {"resource": item["sha256"], "apikey": api_key}
					parameters = urllib.parse.urlencode(parameters)
					res = requests.post(url, parameters)
					res = json.loads(res.text)
					if res == [] or res["response_code"] == 0:
						detection = "0/0"
						self.log("Failed to obtain detection ratio for {0}".format(item["sha256"]), "warn")
					else:
						detection = "{0}/{1}".format(str(res["positives"]), str(res["total"]))
						self.log("Obtained statistics for".format(item["sha256"]), "success")
						data["sha256"] = item["sha256"]
						data["filename"] = item["filename"]
						data["link"] = link
						data["detection"] = detection
						data["adapter"] = "VirusTotal"
						item["status"] = "completed"
						output["data"].append(data)
						output["state"].append(item)
				except:
					self.log("Failed to get statistics for {0}".format(item["sha256"]), "fail")
					if self.debug: raise
				
		seen_items = [x["sha256"] for x in input["state"]]
		
		# Submit new items
		for item in input["data"]:
			if item["sha256"] in seen_items:
				continue
			elif "." in item["filename"]:
				if item["filename"].split(".")[1] not in allowed_filetypes:
					self.log("{0} is not an allowed filetype.".format(item["sha256"]), "warn")
					continue
			else:
				self.log("{0} has no file extension. Ignoring file.".format(item["sha256"], "warn"))
			state = self.stored_properties.copy()
			state["sha256"] = item["sha256"]
			state["filename"] = item["filename"]
			self.log("Submitting {0} for analysis.".format(item["sha256"][-20:]))
			params = {"apikey": api_key}
			files = {"file": (item["filename"], open("{0}/{1}".format(item["filepath"], item["filename"]), "rb"))}
			res = requests.post("https://www.virustotal.com/vtapi/v2/file/scan", files=files, params=params)
			if res.ok and res.json()["response_code"] is not 1:
				self.log("Submission failed! Response was: {0}".format(res.json()["verbose_msg"]))
			elif not res.ok:
				self.log("Received HTTP status {0}".format(res.status_code))
			else:
				state["status"] = "pending"
				state["link"] = res.json()["permalink"]
				output["state"].append(state)
		
		return output
