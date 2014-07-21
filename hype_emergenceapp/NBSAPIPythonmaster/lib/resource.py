import urllib as rest
import inspect

class Resource:
  base = ".api3.nextbigsound.com/"

  # Constructor:
  def __init__(self, key, secret, ext):
    self.key = key
    self.secret = secret
    self.ext = ext

  # HTTP GET
  def get(self,url,params):
    if params == "":
      q = ""
    else:
      q = "?"
    url = url + self.ext + q + rest.urlencode(params)
    #print repr(rest.urlopen(url).geturl( ))
    return rest.urlopen(url).read()

  # HTTP POST
  def post(self,url,data):
    url = url + self.ext
    data = rest.urlencode(data)
    # print repr(data)
    # print repr(rest.urlopen(url,data).geturl( ))
    return rest.urlopen(url,data).read()

  # generates url based on method called and resource used
  #   takes the resource and method name EXACTLY as defined
  # Sean: Sometimes we do not want the generated url to end
  #   in a '/' because we may just want it to end in .json
  #   or .xml with the possibility of GET or POST variables
  #   I chose to make the trailing '/' dependent on the
  #   calling Resource rather than this function. 
  def genUrl(self):
    resource = self.__class__.__name__
    method = inspect.stack()[1][3]
    return ("http://" + self.key + Resource.base + resource + "/" + method).lower()

