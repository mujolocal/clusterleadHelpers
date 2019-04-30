import requests, time, json, sys, os, shutil 
import matplotlib.pyplot as plt
import PIL.Image as Image

class Create():
    """
    A class thats primary purpose is to collect data from various api's and populate that data into 
    governor for cluster lead SCRAPED
    Competition in area
    tuple form = ("locationName","locationAddress")
    """
    def __init__(self,zip=19147, run = False):
        self.zip = zip
        if run:
            for type in self.ESTABLISHMENT_TYPE:
                self._1_zip_data(zip)
                self._2_google(establishment = type)
                self._3_download_current_governors()
                self._4_no_duplicates()
                self._5_post_governors()
        
    def _1_zip_data(self):
        """ 
        data from zip-codes.com 
        gets radius in miles, lat, long, 
        """
        self.zip_request = requests.get(
        "http://api.zip-codes.com/ZipCodesAPI.svc/1.0/GetZipCodeDetails/{0}?key={1}".format(
            self.zip, KEYS["zip_api_key"]
            )
        )
        if not self.zip_request.ok:
            print ("Something went wrong check stuff bro")
        else:
            print("everything ok")
            self.data = json.loads(self.zip_request.text)
            self.zip_area = self.data["item"]["AreaLand"]
            self.gps = "{0},{1}".format(self.data["item"]["Latitude"],self.data["item"]["Longitude"])
        
    
    def _2_google(self, next_page_token = None, establishment ="bar",miles=None,  ):
        """
        This function uses google to get a series of locations of whatever type you provide
        place_type: the type of place you are looking for: String
        location: is the gps location where you want the search to be from lat,long :String
        miles: defines the distance you want to search around a location : float
        """
        if miles == None:
            self.radius_in_meters = 1600*float(self.zip_area)**0.5
        else:
            self.radius_in_meters = 1600*miles
        if next_page_token == None:
            print("google none")
            self.address = """
            {4}
            location={1}
            &rankby=distance
            &keyword={0}
            &key={3}
            """.format(establishment,self.gps,self.radius_in_meters,KEYS["google_key"],
            ADDRESSES["google"])
            self.address = "".join(self.address.split())
            self.req = requests.get(self.address)
            if self.req.status_code == 200:
                self.json_dic = json.loads(self.req.text)
            else:
                print(self.req.status_code)
                sys.exit()
        else:
            print("google not none absurd 20 second wait")
            time.sleep(20)
            self.address = """
            {4}
            location={1}
            &rankby=distance
            &keyword={0}
            &key={3}
            &pagetoken={5}
            """.format(establishment,self.gps,self.radius_in_meters,KEYS["google_key"],
            ADDRESSES["google"],next_page_token)
            self.address = "".join(self.address.split())
            self.req = requests.get(self.address)
            if self.req.status_code == 200:
                self.json_dic = json.loads(self.req.text)
            else:
                print(self.req.status_code)
                sys.exit()
        self.populate_governors()
        
        
    def _2_fourSquare():
        pass
        
    def _2_bing():
        pass
        
    def _3_download_current_governors(self):
        self.loaded_governors = []
        req = requests.get(ADDRESSES["get_governors"])
        if req.ok:
            self.load = json.loads(req.text)
            for item in self.load:
                self.loaded_governors.append((item['locationName'],item['locationAddress'],item['id']))
        else:
            print(req.reason)
        
    def _4_no_duplicates(self):
        """make sure that when you upload there are no duplicate governors"""
        self.governor_set = []
        self.duplicates_set = []
        # print("old",self.loaded_governors)
        # print("new",self.new_governors)
        self.places = []
        for item in self.loaded_governors:
            self.places.append(item[0])
        for governor in self.new_governors:
            if governor[0] in self.places:
                self.duplicates_set.append( governor)
            else:
                self.governor_set.append( governor)
                
        
    def _5_post_governors(self):
        for item in self.governor_set:
            payload = {"locationName":item[0],"locationAddress":item[1],"googlePlaceid":item[4],
            "viewport":str(item[5])}
            req = requests.post(ADDRESSES["create_governor"],payload)
            if req.status_code != 201:
                print("something messed up yo")
                print(req.status_code)
                print(item)
            
    # def _5a_temp(self):
    #     """
    #     update governors to have place_id and viewport
    #     """
    #     for dup in self.duplicates_set:
    #         for gov in self.loaded_governors:
    #             if dup[0] in gov:
    #                 print(gov)
    #                 payload = {"locationName":dup[0],"locationAddress":dup[1],"googlePlaceid":dup[4],
    #                 "viewport":str(dup[5])}
    #                 tempreq = requests.put("http://127.0.0.1:8000/agent/update/governor/{0}/".format(gov[2]), payload)
                    
    # def check(self, location):
    #     for item in self.loaded_governors:
    #         if location in item[0]:
    #             print(location)
            
                          
    def populate_governors(self):
        """
        create list of locations
        """
        try:
            for location in self.json_dic["results"]:
                self.new_governors.append((location["name"],location["vicinity"],
                location["geometry"]["location"]["lat"],location["geometry"]["location"]["lng"],
                location["place_id"],location["geometry"]["viewport"],
                ))
        except:
            self.new_governors = []
            for location in self.json_dic["results"]:
                self.new_governors.append((location["name"],location["vicinity"],
                location["geometry"]["location"]["lat"],location["geometry"]["location"]["lng"],
                location["place_id"],location["geometry"]["viewport"],))
        
        if "next_page_token" in self.json_dic.keys():
            self._2_google(self.json_dic["next_page_token"])
    
    def get_area_maxcapacity(self):
        pass
            
            

    KEYS = {
    "google_key" : "scraped",
    "four_square_id" : "scraped",
    "four_square_secret" : "scraped",
    "zip_api_key" : "scraped",
    }

    gps="39.986111,-75.153340"
    ESTABLISHMENT_TYPE = [
    "bar",
    "night_club",
    ]
            

    
class Update():
    """
    update governors
    normal path just updates all the firleds from google
    alternate path updates the pictures
    download all governors
    for now just update with info
    """
    def __init__(self):
        """
        loadedgovernors == locationname, location adresss, idnumber 
        """
        self.request = requests.get("scaped")
        self.json = self.request.json()
            
    def _1_select(self, field = "googlePlaceid", value = None, printinstances = True):
        """
        gets the database instances of the object that has the specified value for
        the specifid field
        """
        self.dbInstances = []
        for instance in self.json:
            if instance[field] == value:
                self.dbInstances.append(instance)
        if printinstances:
            for item in self.dbInstances:
                print("id:",item["id"],"..locationName:",item["locationName"])
                
    def _2_update_google(self,cluster_instances = None):
        if cluster_instances == None:
            cluster_instances = self.dbInstances
        for cluster_instance in cluster_instances: 
            print("absurd 5 sec sleep time")                   
            self.address = """
            {2}
            input={0}
            &inputtype=textquery
            &fields=name,formatted_address,id,place_id
            &key={1}
            """.format(
            cluster_instance["locationName"],
            KEYS["google_key"],
            ADDRESSES["google_places"])
            self.address = self.address.replace("\n","").replace(" ","")
            self.request_google = requests.get(self.address)
            if self.request_google.json()["status"] != 'ZERO_RESULTS':
                self.update_specific_field(google_instance = self.request_google.json()["candidates"][0],
                google_paramter = "place_id",cluster_instance = cluster_instance, 
                cluster_parameter = "googlePlaceid")
            time.sleep(5)
        
    def update_specific_field(self, google_instance = None ,google_paramter = None, 
        cluster_instance=None, cluster_parameter ="googlePlaceid"):
        print(cluster_instance)
        if cluster_instance["locationAddress"] == "Before Mando Addresses":
            print("before mando addresses")
        else:
            cluster_instance[cluster_parameter] = google_instance[google_paramter]
            updated_req = requests.put("http://127.0.0.1:8000/agent/update/governor/{0}/".format(cluster_instance["id"]), cluster_instance)
            
        
class Photos:
    """
    gets photos from google then allows user to choose which photo is best
    """
    
    def __init__(self):
        """
        download governors
        should change based on some criteria instead of being entire list
        """
        self.clusterlead_request = requests.get("scraped")
        self.clusterlead_json = self.clusterlead_request.json()
        self.locations = []
        i=0
        for item in self.clusterlead_json:
            self.locations.append((item["locationName"],item["id"],item["googlePlaceid"],i))
            i+=1
            
    def get_place_detail(self, place_key = None):
        """
        should give the location of 10 pics in the self.place_json
        """
        self.place_url = "https://maps.googleapis.com/maps/api/place/details/json?placeid={place}&fields=name,vicinity,photo&key={key}".format(key=KEYS["google_key"],place=place_key)
        self.place_req = requests.get(self.place_url)
        self.place_json = self.place_req.json()
        if self.place_req.ok:
            print("get place details a o k")
        else:
            print("get place details something went wrong")
        
    def get_pic(self):
        """
        takes one pic key and downloads it
        """
        self.dirlist = os.listdir()
        if "images" in self.dirlist:
            shutil.rmtree("images")
        self.raw_pic_list = []
        if "result" in self.place_json.keys() and "photos" in self.place_json["result"].keys():
            for photo in self.place_json["result"]["photos"]:
                print("absurd 5 sec wait")
                time.sleep(5)
                pic_key = photo["photo_reference"]
                self.pic_url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo}&key={key}".format(key=KEYS["google_key"], photo = pic_key)
                self.pic_req = requests.get(self.pic_url)
                if self.pic_req.ok:
                    print("everything a o k")
                    self.raw_pic_list.append(self.pic_req.content)
                else:
                    print("something went wrong")
        else:
            print("no photos this location")
        
    def create_files(self, location = None):
        """
        takes downlaoded giberish and turn into pic files
        """
        print(location)
        self.dirlist = os.listdir()
        if "images" not in self.dirlist:
            os.mkdir("images")
        for i in range(len(self.raw_pic_list)):
            with open(f"images/{location}{i}.png".format(i=i ), "wb") as f:
                f.write(self.raw_pic_list[i])
                
    def show_pic(self, location= None):
        print(location)
        filenames = ["{location}{i}.png".format(i=I, location = location) for I in range(len(self.raw_pic_list))]
        os.chdir("images")
        fig,ax = plt.subplots(2,5)
        for i in range(len(self.raw_pic_list)):
            with open(filenames[i], "rb") as f:
                image= Image.open(f)
                ax[i%2][i//2].imshow(image)
        plt.show(block=False)
        
    def choosepic(self, id = None, list_num = None, location = None):
        print(location)
        # choose pic number
        print('\a')
        self.chosen = input("please choose pic number 0-9: ") 
        plt.close("all")
        # format file
        self.pic_pay_address = "{location}{chosen}.png".format(chosen = self.chosen, location = location)
        # get the correct clusterlead point
        self.instance = self.clusterlead_json[list_num]
        # get files to be uploaded
        files = {"pic_main": open(self.pic_pay_address,"rb")}
        self.updated_req = requests.put("scraped/".format(inline_id = str(id)), self.instance,files = files)
        
        
        
        
    def entireDb(self):
        #list of locations that this wont work for
        self.nots = [1,3,4,5,31,50,]
        for location in self.locations:
            if not self.clusterlead_json[location[3]]['pic_main']:
                if len(set(self.nots+[location[1]])) !=3:
                    name = location[0].replace(" ","_")
                    print(name)
                    self.get_place_detail(place_key = location[2])
                    self.get_pic()
                    if "result" in self.place_json.keys() and "photos" in self.place_json["result"].keys():
                        self.create_files(location = name)
                        self.show_pic(location = name)
                        self.choosepic(id = location[1], list_num = location[3], location = name)
                        
    
    
KEYS = {
"google_key" : "scraped",
"four_square_id" : "scraped",
"four_square_secret" : "scraped",
"zip_api_key" : "scraped",
}
# for real
ADDRESSES = {
"create_governor":"http://127.0.0.1:8000/scraped",
"get_governors":"http://127.0.0.1:8000/scraped",
"google":"https://maps.googleapis.com/maps/api/place/nearbysearch/json?",
"google_places":"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?",
"google_find_places":"https://maps.googleapis.com/maps/api/place/findplacefromtext/output?parameters",
}
# for play
# ADDRESSES = {
# "create_governor":"http://127.0.0.1:8000/agent/create/governor/new/",
# "get_governors":"http://127.0.0.1:8000/agent/governors/",
# "google":"https://maps.googleapis.com/maps/api/place/nearbysearch/json?",
# "update_field":"http://127.0.0.1:8000/agent/update/governor/{0}/"
# }
gps="39.986111,-75.153340"
ESTABLISHMENT_TYPE = [
"bar",
"night_club",
]
          