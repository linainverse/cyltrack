import webapp2
import jinja2
import cgi
import os
import urllib
import utils 

from google.appengine.ext import ndb
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True)

####################
#schema definitions#
####################

class Facility(ndb.Model):
  # basic details
  name = ndb.StringProperty() #name of the facility
  company = ndb.StringProperty() #name of the company that owns this facility
  ownFacility = ndb.BooleanProperty() #true if owned by one of own company, customers = false
  facilityType = ndb.StringProperty() #godown, factory etc

  # location
  streetAddress = ndb.TextProperty()
  city = ndb.StringProperty()
  state = ndb.StringProperty()
  pincode = ndb.IntegerProperty(indexed = False)

  phoneNumber = ndb.IntegerProperty(indexed = False) #list of all phone numbers
  
  added = ndb.DateTimeProperty(auto_now_add = True, indexed = False)

class Cylinder(ndb.Model):
  cylinderId = ndb.IntegerProperty(required = True) #permanent id of each cyliner, can be set as key maybe
  barcode = ndb.IntegerProperty() 
  
  capacity = ndb.FloatProperty(indexed = False)
  manufacturer = ndb.StringProperty(indexed = False)
  yearOfMfg = ndb.IntegerProperty()
  tareWeight = ndb.FloatProperty(indexed = False)

  lastTestDate = ndb.DateProperty(auto_now_add = True)
  testFrequency = ndb.IntegerProperty()
  testDueDate = ndb.DateProperty(default = datetime(1970,01,01))

  added = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
  
  currentFacility = ndb.StructuredProperty(Facility) 

###################
#Handler Functions#
###################

class FacilityHandler(webapp2.RequestHandler):
  
  def render(self, templateValues = {}):
    template = JINJA_ENVIRONMENT.get_template("templates/facility.html")
    self.response.write(template.render(templateValues))

  def post(self):
    #raw inputs
    inputFacilityName = utils.escapeHTML(self.request.get("facilityName"))
    inputCompany = utils.escapeHTML(self.request.get("company"))
    inputFacilityType = utils.escapeHTML(self.request.get("facilityType"))
    inputOwnFacility = utils.escapeHTML(self.request.get("ownFacility"))
    inputStreetAddress = utils.escapeHTML(self.request.get("streetAddress"))
    inputCity = utils.escapeHTML(self.request.get("city"))
    inputState = utils.escapeHTML(self.request.get("state"))
    inputPincode = utils.escapeHTML(self.request.get("pincode"))
    inputPhoneNumber = utils.escapeHTML(self.request.get("phoneNumber"))

    #validated inputs
    validOwnFacility = True
    if inputOwnFacility == "Customer":
      validOwnFacility = False
    
    validFacilityType = inputFacilityType
    if not (inputFacilityType == "Factory" or inputFacilityType == "Godown" or inputFacilityType == "Customer"):
      validFaclilityType = None

    newFacility = Facility(name = inputFacilityName,
                           company = inputCompany,
			   ownFacility = validOwnFacility,
			   facilityType = validFacilityType,
			   streetAddress = inputStreetAddress,
			   city = inputCity,
			   state = inputCity,
			   pincode = int(inputPincode),
			   phoneNumber = (int(inputPhoneNumber)))
    newFacility.put()
    
    self.response.write("new facility added")

  def get(self):
    self.render()
    
class CylinderHandler(webapp2.RequestHandler):

  def render(self, templateValues = {}):
    template = JINJA_ENVIRONMENT.get_template("templates/cylinder.html")
    self.response.write(template.render(templateValues))
    
  def get(self):
    #facilities = db.GqlQuery("SELECT * FROM Facility") 
    #templateValues = {}
    #templateValues.facilities = facilities
    self.render()


#    inputTitle = utils.escapeHTML(self.request.get("title"))
#    inputArt = utils.escapeHTML(self.request.get("art"))
#    
#    if inputTitle and inputArt: 
#      art = Art(title = inputTitle, art = inputArt)
#      art.put()
#      #self.redirect("/arts")
#      
#      arts = db.GqlQuery("SELECT * from Art ORDER BY created DESC")
#      self.render({"arts":arts})
#    else:
#      error = "you havent typed in everything!"
#      self.render({"error":error, "title":inputTitle})
   
application = webapp2.WSGIApplication([
  ('/cylinder', CylinderHandler),
  ('/facility', FacilityHandler),
], debug=True)
