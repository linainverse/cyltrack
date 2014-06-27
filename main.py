import webapp2
import jinja2
import cgi
import os
import urllib
import utils 
import logging

from google.appengine.ext import ndb
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True)

####################
#schema definitions#
####################

#each facility - godown, factory or customer location will be a facility object
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

#each cylinder will be a cylinder object
class Cylinder(ndb.Model):
  #cylinderId = ndb.IntegerProperty(required = True) #permanent id of each cyliner, can be set as key maybe
  barcode = ndb.IntegerProperty() 
  
  capacity = ndb.FloatProperty(indexed = False)
  manufacturer = ndb.StringProperty(indexed = False)
  yearOfMfg = ndb.IntegerProperty()
  tareWeight = ndb.FloatProperty(indexed = False)

  lastTestDate = ndb.DateProperty(auto_now_add = True)
  testFrequency = ndb.IntegerProperty(default = 6) #test frequency in months
  testDueDate = ndb.DateProperty(default = datetime(1970,01,01))

  added = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
  
  currentFacility = ndb.KeyProperty() 

#transactions will be tracked via transaction objects
class Transaction(ndb.Model):
  cylinderId = ndb.IntegerProperty(required = True)
  currentFacilityId = ndb.KeyProperty()
  destinationFaciltyId = ndb.IntegerProperty()
  dateOfTransaction = ndb.DateTimeProperty() #default needs to be set to current time
  typeOfTransaction = ndb.StringProperty(indexed = False)


###################
#Handler Functions#
###################

class AddFacility(webapp2.RequestHandler):
  
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
    
class AddCylinder(webapp2.RequestHandler):

  def render(self, templateValues = {}):
    template = JINJA_ENVIRONMENT.get_template("templates/cylinder.html")
    self.response.write(template.render(templateValues))
    
  def get(self):
    logging.info("in the get cylinder function")
    facilitiesQuery = ndb.gql("Select name FROM Facility")
    facilities = facilitiesQuery.fetch()

    #templateValues = {}
    #templateValues.facilities = facilities
    self.render({"facilities":facilities})

  def post(self):
    #raw inputs
    inputBarcode = utils.escapeHTML(self.request.get("barcode"))
    inputCapacity = utils.escapeHTML(self.request.get("capacity"))
    inputManufacturer = utils.escapeHTML(self.request.get("manufacturer"))
    inputYearOfMfg= utils.escapeHTML(self.request.get("yearOfMfg"))
    inputTareWeight = utils.escapeHTML(self.request.get("tareWeight"))
    inputLastTestDate = utils.escapeHTML(self.request.get("lastTestDate"))
    inputTestFrequency = utils.escapeHTML(self.request.get("testFrequency"))
    inputCurrentFacility = utils.escapeHTML(self.request.get("currentFacility"))
    
    
    #validate inputs
    logging.info ("in the cylinder post %s" %(inputCurrentFacility));
    logging.info ("in the cylinder post %s" %(inputTareWeight));
    
    #inputFacility = Facility.get_by_id(int(inputCurrentFacility))

    #logging.info("in the cylinder post %s" %(inputFacility.name))

    newCylinder = Cylinder(
      barcode = int(inputBarcode),
      capacity = float(inputCapacity),
      manufacturer = inputManufacturer,
      yearOfMfg = int(inputYearOfMfg),
      tareWeight = float(inputTareWeight),
    #  lastTestDate = inputLastTestDate,
      testFrequency = int(inputTestFrequency),
      currentFacility = ndb.Key(urlsafe = inputCurrentFacility)) 
   
    newCylinder.put()

    logging.info("new cylinder added")
  
application = webapp2.WSGIApplication([
  ('/add-cylinder', AddCylinder),
  ('/add-facility', AddFacility),
], debug=True)
