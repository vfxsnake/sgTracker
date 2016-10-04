from shotgun_api3 import Shotgun
from AssetManager_DaoMaster import DaoMaster
from bson.objectid import ObjectId



class ShotgunUtils():
    '''
    this module is a collection of functions to conect the Asset manager to shogun studio website, to update, create
    and manages all attributes and parameters from the different entities.
    '''

    def __init__(self):
        '''
        creates the connection to the server and connects to database.
        creates list of Ids form the  database collections that needs to convert to shotgun collections

        '''

        SERVER_PATH = "https://hcpstudio.shotgunstudio.com"
        SCRIPT_NAME = 'sgApi'
        SCRIPT_KEY = '3899a8466f2cea694c2ba5341d871da845509d18d96a4feb7fb8d147de0fa819'

        self.sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

        self.dbObjectID = ObjectId()

        master = DaoMaster()
        session = DaoMaster.getSession()

        self.itemInstance = session.getItemsDao()

        self.ItemStatusList = ['rdy', 'ip', 'app', 'crnt', 'outd','dep', 'vari', 'rej']

        self.ItemType = ['Source', 'Prop', 'Environment', 'Character', 'Rig', 'Fx', 'Template', 'Geometry', 'Art',
                         'Shader', 'Texture', 'Cache', 'ImageSequence', 'DCC', 'None']

        self.ItemClass = ['Item', 'Asset', 'superAsset']

    def getParameterSchema(self, fieldType, fieldName = None):
        '''
         utility function to search fields in a given entity.
        :param fieldType: entity to search parameters 'Project', 'Sequence', 'Shot', 'Asset', 'Version', etc.
        :param fieldName: name of the field to search 'id', 'name', 'coce', etc.
        :return: retruns a dictionary with the properties of given parameter
        '''

        squemaDic = self.sg.schema_field_read(fieldType, fieldName)
        print squemaDic
        for field in squemaDic:
            print field
        return squemaDic

    def getEntities(self):
        '''
        utility function to find all the Entities in shotgun for developing
        :return: renturn a list of all entities
        '''
        squemaDic = self.sg.schema_entity_read()
        for entity in squemaDic:
            print entity
        return squemaDic


    def createProject(self, sgName, sgStatus, sgType):
        ''' creates a Project using the given name, status, type,start date, end date.
            the status parameter is a list::
                Bidding
                Active
                Lost
                Hold

            the type parameter is a list:
                Feature
                Episodic
                Commercial
                Game Cinematic
                AAA Game
                Mobile Game
                Audio
                Mocap
                Misc
        '''
        data = {'name': sgName, 'sg_status': 'Active', 'sg_type': 'Feature'}
        fields = ['id']
        project = self.sg.create('Project', data, fields)
        print project
        return project

    def createSequence(self, projectID, sqName):
        '''
        creates a Sequence for the project set by the Id,
        :return: a dictionary containing the basic info of the sequence
        '''

        data = {'project': {'type': 'Project', 'id': projectID},
            'code': sqName}
        fields = ['id']
        sequence = self.sg.create('Sequence', data, fields)
        print sequence
        return sequence

    def createShot(self, projectID, shotName, sqID):

        data = {'project': {'type': 'Project', 'id': projectID},
            'code': shotName, 'sg_sequence': {'type': 'Sequence', 'id': sqID}}

        fields = ['id']
        shot = self.sg.create('Shot', data, fields)
        print shot
        return shot

    def createItem(self, projectID, itemName, itemType):
        '''
        creates an Item from an existing one inside the assetManager, use the parameters of given mongo objcet
        and updates the id of the mongo object with the shotgunId attribute of the mongo object.
        :return: a dictionary with the parameters defined in shotgun
        '''

        data = {'project': {'type': 'Project', 'id': projectID},
            'code': itemName, 'sg_asset_type': itemType}

        fields = ['id']
        item = self.sg.create('Asset', data, fields)
        print item
        return item

    def createDigitalMedia(self, projectID, dmName, dmType, taskID, entityType, entityID):

        data = {'project': {'type': 'Project', 'id': projectID},
            'code': dmName, 'sg_version_type': dmType, 'sg_task': {'type': 'Task', 'id': taskID},
            'entity': {'type': entityType, 'id': entityID}
                }

        fields = ['id']
        dm = self.sg.create('Version', data, fields)
        print dm
        return dm

    def createUser(self, firstName, lastName, userMail):

        data = {'firstname': firstName, 'lastname': lastName, 'email': userMail,
                'sg_status_list': 'dis', 'login': '{0}{1}'.format(firstName,lastName)}
        fields = ['id']
        user = self.sg.create('HumanUser', data, fields)
        print user
        return user


    def createTask(self, projectID, entityType, entityID, taskName):
        data = {'project': {'type': 'Project', 'id': projectID},
                'task_assignees': [{'type': 'HumanUser', 'id': 86, 'name': 'Huevo Cartoon'}],
                'content': taskName, 'entity': {'type': entityType, 'id': entityID}
                }

        fields = ['id']
        task = self.sg.create('Task', data, fields)
        print task
        return task


SERVER_PATH = "https://hcpstudio.shotgunstudio.com"
SCRIPT_NAME = 'sgApi'
SCRIPT_KEY = '3899a8466f2cea694c2ba5341d871da845509d18d96a4feb7fb8d147de0fa819'
sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
data = {'name': 'Test0001', 'sg_status': 'Active', 'sg_type': 'Feature'}
fields = ['id']
project = sg.create('Project', data, fields)
print project

