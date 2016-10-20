from shotgun_api3 import Shotgun
from AssetManager_DaoMaster import DaoMaster
from bson.objectid import ObjectId
from AssetManager_Item import Item

import datetime
import ConfigParser


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

        '''   shotgun conection '''
        SERVER_PATH = "https://hcpstudio.shotgunstudio.com"
        SCRIPT_NAME = 'sgApi'
        SCRIPT_KEY = '3899a8466f2cea694c2ba5341d871da845509d18d96a4feb7fb8d147de0fa819'

        self.sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

        '''Shotgun Dictionaries for  status and Piepeline Step and Entity'''

        self.sgStatusList = {'CBB': 'cbb', 'CURRENT': 'crnt', 'DEPRECATED': 'dep', 'FINAL': 'fin', 'HOLD': 'hld',
                            'IN PROGRESS': 'ip', 'OMIT': 'omt', 'OUTDATED': 'outd', 'READY TO START': 'rdy',
                            'APPROVED': 'apr',
                            'REJECTED': 'rej', 'RETAKE': 'rtk', 'SUBMIT FOR APPROVAL': 'app', 'VARIANT': 'vari'}

        self.amStatusList = dict(map(reversed, self.sgStatusList.iteritems()))

        self.sgEntityDic = {'ITEM': 'Asset', 'DIGITALMEDIA': 'Version', 'SHOT': 'shot', 'SEQUENCE': 'Sequence'}
        self.amEntityDic = dict(map(reversed, self.sgEntityDic.iteritems()))

        ''' DAO master conection    '''

        config = ConfigParser.ConfigParser()
        config.read("__database_config.ini")

        master = DaoMaster(instance=config.get('database_connection', 'instance'), db=config.get('database_connection', 'db'))
        session = master.getSession()
        storedFunctions = master.getStoredFunctions()

        self.ItemStatusConvert = storedFunctions.getCatalogItemStatusStoredFunctions()
        self.ShotStatusConvert = storedFunctions.getCatalogShotStatusStoredFunctions()
        self.SequenceStatusConvert = storedFunctions.getCatalogSequenceStatusStoredFunctions()
        self.DMStatusConvert = storedFunctions.getCatalogDigitalMediaStatusStoredFunctions()
        self.TaskStatusConvert = storedFunctions.getCatalogTaskStatusStoredFunctions()
        self.TaskStepConvert = storedFunctions.getCatalogTaskPipelineStepStoredFunctions()

        ''' instance entities from database '''
        self.itemInstance = session.getItemDao()
        self.projectInstance = session.getProjectDao()
        self.sequenceInstance = session.getSequenceDao()
        self.shotInstance = session.getShotDao()
        self.taskInstance = session.getTaskDao()
        self.dmInstance = session.getDigitalMediaDao()
        self.userInstance = session.getUserDao()

        ''' Catalog instance '''
        self.catalogDepartment = session.getCatalogDepartmentDao()
        self.catalogDMType = session.getCatalogDigitalMediaStatusDao()
        self.catalogDMStatus = session.getCatalogDigitalMediaStatusDao()
        self.catalogItemClass = session.getCatalogItemClassDao()
        self.catalogItemComplex = session.getCatalogItemComplexDao()
        self.catalogItemFormat = session.getCatalogItemFormatDao()
        self.catalogItemStatus = session.getCatalogItemStatusDao()
        self.catalogItemType = session.getCatalogItemTypeDao()
        self.catalogSequenceComplex = session.getCatalogSequenceComplexityDao()
        self.catalogSequenceStatus = session.getCatalogSequenceStatusDao()
        self.catalogShotComplex = session.getCatalogShotComplexityDao()
        self.catalogShotPriority = session.getCatalogShotPriorityDao()
        self.catalogShotStatus = session.getCatalogShotStatusDao()
        self.catalogTaskComplex = session.getCatalogTaskComplexityDao()
        self.catalogTaskEntity = session.getCatalogTaskEntityDao()
        self.catalogTaskName = session.getCatalogTaskNameDao()
        self.catalogTaskPipelineStep = session.getCatalogTaskPipelineStepDao()
        self.catalogTaskPriority = session.getCatalogTaskPriorityDao()
        self.catalogTaskStatus = session.getCatalogTaskStatusDao()

        self.ItemStatusList = self.getCatalogItemStatus()
        self.ItemType = self.getCatalogItemType()
        self.ItemClass = self.getCatalogItemCalss()
        self.ItemComplexity = self.getCatalogItemComplex()

        self.Department = self.getCatalogDepartment()

        self.DMStatus = self.getCatalogDMStatus()
        self.DMType = self.getCatalogDMType()

        self.SequenceComplex = self.getCatalogSequenceComplex()
        self.SequenceStatus = self.getCatalogSequenceStatus()

        self.ShotComplex = self.getCatalogShotComplex()
        self.ShotPriority = self.getCatalogShotPriority()
        self.ShotStatus = self.getCatalogShotStatus()

        self.TaskEntity = self.getCatalogTaskEntity()
        self.TaskName = self.getCatalogTaskName()
        self.TaskStep = self.getCatalogTaskPipelineStep()
        self.TaskPriority = self.getCatalogTaskPriority()
        self.TaskStatus = self.getCatalogTaskStatus()
        self.TaskComplex = self.getCatalogTaskComplex()

        self.sgPiepelineStepTag2IdDic = self.getSgStepsDic()
        self.sgPiepelineStepId2TagDic = dict(map(reversed, self.sgPiepelineStepTag2IdDic.iteritems()))

    def getParameterSchema(self, fieldType, fieldName=None):
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

    def sgDicListFromDaoItemSubscription(self, itemSubscription):

        sgItemDictionaryList = []

        if itemSubscription == []:

            return sgItemDictionaryList

        else:

            for item in itemSubscription:

                subscription = self.itemInstance.readOneByProperties(self.itemInstance.Properties.Id, item)

                if self.sg.find_one('Asset', [['id', 'is', subscription.getShotgunID()]]):

                    sgDic = {'type': 'Asset', 'id': subscription.getShotgunID()}
                    sgItemDictionaryList.append(sgDic)
                else:
                    pass

            return sgItemDictionaryList

    def sgDicListFromDaoShotSubscription(self, shotSubscription):

        sgShotDictionaryList = []

        if shotSubscription == []:

            return sgShotDictionaryList

        else:

            for shot in shotSubscription:
                subscription = self.shotInstance.readOneByProperties(self.shotInstance.Properties.Id, shot)

                if self.sg.find_one('Shot', [['id', 'is', subscription.getShotgunID()]]):

                    sgDic = {'type': 'Shot', 'id': subscription.getShotgunID()}
                    sgShotDictionaryList.append(sgDic)

                else:
                    pass

            return sgShotDictionaryList

    def sgDicListFromDaoSequenceSubscription(self, sequenceSubscription):

        sgSequenceDictionaryList = []

        if sequenceSubscription == []:

            return sgSequenceDictionaryList

        else:

            for sequence in sequenceSubscription:

                subscription = self.sequenceInstance.readOneByProperties(self.sequenceInstance.Properties.Id, sequence)

                if self.sg.find_one('Sequence', [['id', 'is', subscription.getShotgunID()]]):

                    sgDic = {'type': 'Sequence', 'id': subscription.getShotgunID()}
                    sgSequenceDictionaryList.append(sgDic)

                else:
                    pass

            return sgSequenceDictionaryList

    def sgDicListFromDaoDMSubscription(self, dmSubscription):

        sgDMDictionaryList = []

        if dmSubscription == []:

            return sgDMDictionaryList

        else:

            for dm in dmSubscription:
                subscription = self.dmInstance.readOneByProperties(self.dmInstance.Properties.Id, dm)
                if self.sg.find_one('Version', [['id', 'is', subscription.getShotgunID()]]):

                    sgDic = {'type': 'Version', 'id': subscription.getShotgunID()}
                    sgDMDictionaryList.append(sgDic)

                else:
                    pass

            return sgDMDictionaryList

    def sgDicListFromDaoUserSubscription(self, userSubscription):

        sgUserDictionaryList = []

        if userSubscription == []:

            return sgUserDictionaryList

        else:

            for user in userSubscription:
                subscription = self.userInstance.readOneByProperties(self.userInstance.Properties.Id, user)

                if not subscription.getShotgunID() == 0:
                    if self.sg.find_one('HumanUser',[['id', 'is', subscription.getShotgunID()]]):
                        sgDic = {'type': 'HumanUser', 'id': subscription.getShotgunID()}
                        sgUserDictionaryList.append(sgDic)

                else:
                    pass

            return sgUserDictionaryList

    def sgDicListFromDaoTaskSubscription(self, taskSubscription):

        sgUserDictionaryList = []

        if taskSubscription == []:

            return sgUserDictionaryList

        else:

            for task in taskSubscription:
                subscription = self.taskInstance.readOneByProperties(self.taskInstance.Properties.Id, task)

                if not subscription.getShotgunID() == 0:
                    if self.sg.find_one('Task', [['id', 'is', subscription.getShotgunID()]]):
                        sgDic = {'type': 'Task', 'id': subscription.getShotgunID()}
                        sgUserDictionaryList.append(sgDic)

                else:
                    pass

            return sgUserDictionaryList

    def amItemIdListFromSgItemSubscriptionDicList(self, sgDicList):

        amSubscriptionList = []

        if sgDicList == []:
            return amSubscriptionList

        else:
            for sgDic in sgDicList:
                item = self.itemInstance.readOneByProperties(self.itemInstance.Properties.Id, sgDic['id'])

                if item:
                    amSubscriptionList.append(item.getId())

                else:
                    pass

            return amSubscriptionList

    def amShotIdListFromSgShotSubscriptionDicList(self, sgDicList):

        amSubscriptionList = []

        if sgDicList == []:
            return amSubscriptionList

        else:
            for sgDic in sgDicList:
                entity = self.shotInstance.readOneByProperties(self.shotInstance.Properties.Id, sgDic['id'])

                if entity:
                    amSubscriptionList.append(entity.getId())

                else:
                    pass

            return amSubscriptionList

    def amSequenceIdListFromSgSequenceSubscriptionDicList(self, sgDicList):

        amSubscriptionList = []

        if sgDicList == []:
            return amSubscriptionList

        else:
            for sgDic in sgDicList:
                entity = self.sequenceInstance.readOneByProperties(self.sequenceInstance.Properties.Id, sgDic['id'])

                if entity:
                    amSubscriptionList.append(entity.getId())

                else:
                    pass

            return amSubscriptionList

    def amDMIdListFromSgDMSubscriptionDicList(self, sgDicList):

        amSubscriptionList = []

        if sgDicList == []:
            return amSubscriptionList

        else:
            for sgDic in sgDicList:
                entity = self.dmInstance.readOneByProperties(self.dmInstance.Properties.Id, sgDic['id'])

                if entity:
                    amSubscriptionList.append(entity.getId())

                else:
                    pass

            return amSubscriptionList

    def amTaskIdListFromSgTaskSubscriptionDicList(self, sgDicList):

        amSubscriptionList = []

        if sgDicList == []:
            return amSubscriptionList

        else:
            for sgDic in sgDicList:
                entity = self.dmInstance.readOneByProperties(self.dmInstance.Properties.Id, sgDic['id'])

                if entity:
                    amSubscriptionList.append(entity.getId())

                else:
                    pass

            return amSubscriptionList

    def sgIdFromItemId(self, itemId):
        if not itemId == 0:
            entity = self.itemInstance.readOneByProperties(self.itemInstance.Properties.Id, itemId)
            return entity.getShotgunID()
        else:
            return 0

    def sgIdFromShotId(self, shotId):

        if not shotId == 0:
            entity = self.shotInstance.readOneByProperties(self.shotInstance.Properties.Id, shotId)
            return entity.getShotgunID()
        else:
            return 0

    def sgIdFromSquenceId(self, sequenceId):

        if not sequenceId == 0:
            entity = self.sequenceInstance.readOneByProperties(self.sequenceInstance.Properties.Id, sequenceId)
            return entity.getShotgunID()
        else:
            return 0

    def sgIdFromProjectId(self, projectId):

        if not projectId == 0:
            entity = self.projectInstance.readOneByProperties(self.projectInstance.Properties.Id, projectId)
            return entity.getShotgunID()
        else:
            return 0

    def sgIdFromDmId(self, dmId):

        if not dmId == 0:
            entity = self.dmInstance.readOneByProperties(self.dmInstance.Properties.Id, dmId)
            return entity.getShotgunID()

        else:
            return 0

    def sgIdFromTaskId(self, taskId):

        if not taskId == 0:
            entity = self.taskInstance.readOneByProperties(self.taskInstance.Properties.Id, taskId)
            return entity.getShotgunID()

        else:
            return 0

    def getCatalogDepartment(self):

        listFromCatalog = []

        catalogAll = self.catalogDepartment.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogDMStatus(self):

        listFromCatalog = []

        catalogAll = self.catalogDMStatus.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogDMType(self):

        listFromCatalog = []

        catalogAll = self.catalogDMType.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogItemCalss(self):

        listFromCatalog = []

        catalogAll = self.catalogItemClass.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogItemComplex(self):

        listFromCatalog = []

        catalogAll = self.catalogItemComplex.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def itemStatus2Dao(self, status):

        return self.ItemStatusConvert.getIdFromTag(status)

    def shotStatus2Dao(self, status):

        return self.ShotStatusConvert.getIdFromTag(status)

    def sequenceStatus2Dao(self, status):

        return self.SequenceStatusConvert.getIdFromTag(status)

    def dmStatus2Dao(self, status):

        return self.SequenceStatusConvert.getIdFromTag(status)

    def taskStatus2Dao(self, status):

        return self.TaskStatusConvert.getIdFromTag(status)

    def getCatalogItemStatus(self):

        listFromCatalog = []

        catalogAll = self.catalogItemStatus.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogItemType(self):

        listFromCatalog = []

        catalogAll = self.catalogItemType.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogSequenceComplex(self):

        listFromCatalog = []

        catalogAll = self.catalogSequenceComplex.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogSequenceStatus(self):

        listFromCatalog = []

        catalogAll = self.catalogSequenceStatus.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogShotComplex(self):

        listFromCatalog = []

        catalogAll = self.catalogShotComplex.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogShotPriority(self):

        listFromCatalog = []

        catalogAll = self.catalogShotPriority.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogShotStatus(self):

        listFromCatalog = []

        catalogAll = self.catalogShotStatus.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogTaskComplex(self):

        listFromCatalog = []

        catalogAll = self.catalogTaskComplex.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogTaskEntity(self):

        listFromCatalog = []

        catalogAll = self.catalogTaskEntity.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogTaskName(self):

        listFromCatalog = []

        catalogAll = self.catalogTaskName.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogTaskPipelineStep(self):

        listFromCatalog = []

        catalogAll = self.catalogTaskPipelineStep.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogTaskPriority(self):

        listFromCatalog = []

        catalogAll = self.catalogTaskPriority.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getCatalogTaskStatus(self):

        listFromCatalog = []

        catalogAll = self.catalogTaskStatus.readAll()

        for catalog in catalogAll:
            listFromCatalog.append(catalog.getTag())

        return listFromCatalog

    def getSgStepsDic(self):

        sgFields = ['id', 'code']
        dictionaryList = self.sg.find('Step', [], sgFields)

        stepDic = {}

        for dictionary in dictionaryList:
            stepDic.update({dictionary['code']: dictionary['id']})

        return stepDic

    def daoitem2sgDic(self, itemId):

        entity = self.itemInstance.readOneByProperties(self.itemInstance.Properties.Id, itemId)
        sgDic = {}

        if entity:
            if not entity.getShotgunID() == 0:

                sgDic = {'type': 'Asset', 'id': entity.getShotgunID()}

                return sgDic

            else:
                return None

        else:
            return None

    def daoShot2sgDic(self, itemId):

        entity = self.shotInstance.readOneByProperties(self.shotInstance.Properties.Id, itemId)
        sgDic = {}

        if entity:
            if not entity.getShotgunID() == 0:

                sgDic = {'type': 'Shot', 'id': entity.getShotgunID()}

                return sgDic

            else:
                return None

        else:
            return None

    def daoSequence2sgDic(self, itemId):

        entity = self.sequenceInstance.readOneByProperties(self.sequenceInstance.Properties.Id, itemId)
        sgDic = {}

        if entity:
            if not entity.getShotgunID() == 0:

                sgDic = {'type': 'Sequence', 'id': entity.getShotgunID()}

                return sgDic

            else:
                return None

        else:
            return None

    def daoDM2sgDic(self, itemId):

        entity = self.dmInstance.readOneByProperties(self.dmInstance.Properties.Id, itemId)
        sgDic = {}

        if entity:
            if not entity.getShotgunID() == 0:

                sgDic = {'type': 'Version', 'id': entity.getShotgunID()}

                return sgDic

            else:
                return None

        else:
            return None

    def daoHumanUser2sgDic(self, itemId):

        entity = self.userInstance.readOneByProperties(self.userInstance.Properties.Id, itemId)
        sgDic = {}

        if entity:
            if not entity.getShotgunID() == 0:

                sgDic = {'type': 'Asset', 'id': entity.getShotgunID()}

                return sgDic

            else:
                return None

        else:
            return None

    def daoTask2sgDic(self, itemId):

        entity = self.taskInstance.readOneByProperties(self.taskInstance.Properties.Id, itemId)
        sgDic = {}

        if entity:
            if not entity.getShotgunID() == 0:

                sgDic = {'type': 'Task', 'id': entity.getShotgunID()}

                return sgDic

            else:
                return None

        else:
            return None

class sgItem():

    def __init__(self, itemID, sgProjectId):
        '''Create an istance of Item of the itemID (ObjectId) and appends the shotgun connectivity '''

        self.sgUtils = ShotgunUtils()
        self.item = self.sgUtils.itemInstance.readOneByProperty(self.sgUtils.itemInstance.Properties.Id, itemID)
        self.sgProject = sgProjectId

    def item2Sg(self):
        ''' if the Dao object has no ShotgunId the creates the object in shotgun  in the specific project
            else, if the Dao object has a ShotgunId, updates the shotgun Info
        '''
        if self.item.getShotgunID() == 0:

            sgType = self.sgUtils.ItemType[self.item.getType()]

            status = self.sgUtils.ItemStatusList[self.item.getStatus()]
            sgStatus = self.sgUtils.sgStatusList[status]
            sgClass = self.sgUtils.ItemClass[self.item.getClass()]

            data = {'project': {'type': 'Project', 'id': self.sgProject},
                'code': self.item.getName(), 'sg_asset_type': sgType, 'sg_status_list': sgStatus, 'sg_class': sgClass,
                'sg_version' : self.item.getVersion(), 'sg_subversion': self.item.getSubVersion()}

            fields = ['id']
            item = self.sgUtils.sg.create('Asset', data, fields)
            self.item.setShotgunID(item['id'])
            self.sgUtils.itemInstance.update(self.item)
            return item
        else:

            print 'already in shotgun sgId is :', self.item.getShotgunID()

            return self.updateSg(self.item.getShotgunID())

    def sgFindOne(self, sgId):

        fields = ['id', 'code', 'sg_asset_type', 'sg_status_list', 'sg_assetsubscription', 'sg_class',
                  'sg_digitalmedia', 'sg_itemsubscription', 'sequences', 'shots', 'sg_superassetsubscription',
                  'sg_version', 'sg_subversion', 'sg_tasksubscriptions']
        sgFilter = [['id', 'is', sgId]]
        sgItem = self.sgUtils.sg.find_one('Asset', sgFilter, fields)

        return sgItem

    def updateSg(self, sgId,):

        sgItemSubscription = self.sgUtils.sgDicListFromDaoItemSubscription(self.item.getItemSubscriptions())
        sgAssetSubscription = self.sgUtils.sgDicListFromDaoItemSubscription(self.item.getAssetSubscriptions())
        sgSuperAssetSubscription = self.sgUtils.sgDicListFromDaoItemSubscription(self.item.getSuperAssetSubscriptions())
        sgShotSubscription = self.sgUtils.sgDicListFromDaoShotSubscription(self.item.getShotSubscriptions())
        sgSequences = self.sgUtils.sgDicListFromDaoSequenceSubscription(self.item.getSequenceSubscriptions())
        sgDM = self.sgUtils.sgDicListFromDaoDMSubscription(self.item.getDigitalMediaSubscriptions())
        sgType = self.sgUtils.ItemType[self.item.getType()]
        sgClass = self.sgUtils.ItemClass[self.item.getClass()]
        sgStatus = self.sgUtils.sgStatusList[self.sgUtils.ItemStatusList[self.item.getStatus()]]
        sgTaskSubs = self.sgUtils.sgDicListFromDaoTaskSubscription(self.item.getTaskSubscriptions())

        data = {'code': self.item.getName(),  'sg_class': sgClass,  'sg_itemsubscription': sgItemSubscription,
                'sg_assetsubscription': sgAssetSubscription, 'sg_digitalmedia': sgDM,
                'sg_superassetsubscription': sgSuperAssetSubscription, 'sg_version': self.item.getVersion(),
                'sg_subversion': self.item.getSubVersion(),
                'sg_status_list': sgStatus, 'shots': sgShotSubscription, 'sequences': sgSequences,
                'sg_asset_type': sgType, 'sg_tasksubscriptions': sgTaskSubs}
        print data

        self.sgUtils.sg.update('Asset', sgId, data)

    def pullSgData(self):

        data = self.sgFindOne(self.item.getShotgunID())

        if data:

            daoStatus = self.sgUtils.amStatusList[data['sg_status_list']]
            itemSubscription = self.sgUtils.amItemIdListFromSgItemSubscriptionDicList(data['sg_itemsubscription'])
            assSubscription = self.sgUtils.amItemIdListFromSgItemSubscriptionDicList(data['sg_assetsubscription'])
            superAssSubs = self.sgUtils.amItemIdListFromSgItemSubscriptionDicList(data['sg_superassetsubscription'])
            shotSubscription = self.sgUtils.amShotIdListFromSgShotSubscriptionDicList(data['shots'])
            sqSubscription = self.sgUtils.amSequenceIdListFromSgSequenceSubscriptionDicList(data['sequences'])
            dmSubscription = self.sgUtils.amDMIdListFromSgDMSubscriptionDicList(data['sg_digitalmedia'])
            taskSubscription = self.sgUtils.amTaskIdListFromSgTaskSubscriptionDicList(data['sg_tasksubscriptions'])

            self.item.setStatus(self.sgUtils.itemStatus2Dao(daoStatus))
            self.item.setItemSubscriptions(itemSubscription)
            self.item.setAssetSubscriptions(assSubscription)
            self.item.setSuperAssetSubscriptions(superAssSubs)
            self.item.setShotSubscriptions(shotSubscription)
            self.item.setSequenceSubscriptions(sqSubscription)
            self.item.setDigitalMediaSubscriptions(dmSubscription)
            #self.item.setTaskSubscriptions(taskSubscription)

            self.sgUtils.itemInstance.update(self.item)

        else:
            print 'no valid Object'


    def pullSgStatus(self):

        data = self.sgFindOne(self.item.getShotgunID())

        if data:

            daoStatus = self.sgUtils.amStatusList[data['sg_status_list']]

            self.item.setStatus(self.sgUtils.itemStatus2Dao(daoStatus))
            self.sgUtils.itemInstance.update(self.item)

        else:
            print 'no valid Object'


class sgTask():

    def __init__(self, taskId, sgProjectId):
        '''Create an istance of Item of the taskID (ObjectId) and appends the shotgun connectivity '''

        self.sgUtils = ShotgunUtils()
        self.entity = self.sgUtils.taskInstance.readOneByProperty(self.sgUtils.taskInstance.Properties.Id, taskId)
        self.sgProject = sgProjectId

    def task2Sg(self):
        ''' if the Dao object has no ShotgunId the creates the object in shotgun  in the specific project
            else, if the Dao object has a ShotgunId, updates the shotgun Info
        '''
        if self.entity.getShotgunID() == 0:

            sgDueDate = self.entity.getEndDate().date().isoformat()
            sgStartDate = self.entity.getStartDate().date().isoformat()
            sgComplex = self.sgUtils.TaskComplex[self.entity.getComplexity()]
            sgPreviousTask = self.sgUtils.daoTask2sgDic(self.entity.getPreviousTask())
            sgEntity = self.entitybySubscription()
            sgTaskName = self.sgUtils.TaskName[self.entity.getName()]
            sgStep = self.sgUtils.sgPiepelineStepTag2IdDic[self.sgUtils.TaskStep[self.entity.getPipelineStep()]]
            sgUserSubscription = self.sgUtils.sgDicListFromDaoUserSubscription(self.entity.getUserSubscriptions())
            sgStatus = self.sgUtils.sgStatusList[self.sgUtils.TaskStatus[self.entity.getStatus()]]
            sgDuration = self.entity.getDuration()
            sgPriority = self.sgUtils.TaskPriority[self.entity.getPriority()]
            sgNextTask = self.sgUtils.daoTask2sgDic(self.entity.getNextTask())

            data = {'project': {'type': 'Project', 'id': self.sgProject},
                    'due_date': sgDueDate, 'sg_complexity': sgComplex, 'sg_previous_task': sgPreviousTask,
                     'entity': sgEntity, 'content': sgTaskName,
                     'step': {'type': 'Step', 'id': sgStep}, 'task_assignees': sgUserSubscription,
                     'start_date': sgStartDate, 'sg_status_list': sgStatus, 'duration': sgDuration,
                     'sg_priority_1': sgPriority, 'sg_next_task': sgNextTask}

            #print data
            fields = ['id']
            task = self.sgUtils.sg.create('Task', data, fields)
            self.entity.setShotgunID(task['id'])
            self.sgUtils.taskInstance.update(self.entity)

            return task

        else:

            print 'already in shotgun sgId is :', self.entity.getShotgunID()

            return self.updateSg(self.entity.getShotgunID())

    def sgFindOne(self, sgId):

        fields = ['id', 'content', 'entity', 'sg_status_list', 'step', 'task_assignees',
                  'start_date', 'due_date', 'duration', 'sg_complexity', 'sg_next_task',
                  'sg_previous_task', 'sg_priority_1']
        sgFilter = [['id', 'is', sgId]]
        sgTask = self.sgUtils.sg.find_one('Task', sgFilter, fields)

        return sgTask

    def entitybySubscription(self):

        taskEntity = self.sgUtils.TaskEntity[self.entity.getEntity()]

        if taskEntity == 'ITEM':
            item = self.sgUtils.itemInstance.readOneByProperties(self.sgUtils.itemInstance.Properties.Id,
                                                                 self.entity.getItem())

            if item:
                sgDic = {'type': 'Asset', 'id': item.getShotgunID()}

                return sgDic

            else:
                return None

        if taskEntity == 'SHOT':
            shot = self.sgUtils.shotInstance.readOneByProperties(self.sgUtils.shotInstance.Properties.Id,
                                                                       self.entity.getShot())

            if shot:
                sgDic = {'type': 'Shot', 'id': shot.getShotgunID()}

                return sgDic
            else:
                return None

    def updateSg(self, sgId):

        sgDueDate = self.entity.getEndDate().date().isoformat()
        sgStartDate = self.entity.getStartDate().date().isoformat()
        sgComplex = self.sgUtils.TaskComplex[self.entity.getComplexity()]
        sgPreviousTask = self.sgUtils.daoTask2sgDic(self.entity.getPreviousTask())
        sgEntity = self.entitybySubscription()
        sgTaskName = self.sgUtils.TaskName[self.entity.getName()]
        sgStep = self.sgUtils.sgPiepelineStepTag2IdDic[self.sgUtils.TaskStep[self.entity.getPipelineStep()]]
        sgUserSubscription = self.sgUtils.sgDicListFromDaoUserSubscription(self.entity.getUserSubscriptions())
        sgStatus = self.sgUtils.sgStatusList[self.sgUtils.TaskStatus[self.entity.getStatus()]]
        sgDuration = self.entity.getDuration()
        sgPriority = self.sgUtils.TaskPriority[self.entity.getPriority()]
        sgNextTask = self.sgUtils.daoTask2sgDic(self.entity.getNextTask())

        data = {'project': {'type': 'Project', 'id': self.sgProject},
                'due_date': sgDueDate, 'sg_complexity': sgComplex, 'sg_previous_task': sgPreviousTask,
                'entity': sgEntity, 'content': sgTaskName,
                'step': {'type': 'Step', 'id': sgStep}, 'task_assignees': sgUserSubscription,
                'start_date': sgStartDate, 'sg_status_list': sgStatus, 'duration': sgDuration,
                'sg_priority_1': sgPriority, 'sg_next_task': sgNextTask}

        self.sgUtils.sg.update('Task', sgId, data)

    def pullSgDate(self):

        data = self.sgFindOne(self.entity.getShotgunID())

        if data:

            daoStartDate = datetime.datetime.strptime(data['start_date'], "%Y-%m-%d")
            daoEndDate = datetime.datetime.strptime(data['due_date'], "%Y-%m-%d")


            self.entity.setStartDate(daoStartDate)
            self.entity.setEndDate(daoEndDate)

            self.sgUtils.taskInstance.update(self.entity)

        else:
            print 'no valid Object'

    def pullSgStatus(self):

        data = self.sgFindOne(self.entity.getShotgunID())

        if data:

            daoStatus = self.sgUtils.amStatusList[data['sg_status_list']]

            self.entity.setStatus(self.sgUtils.taskStatus2Dao(daoStatus))
            self.sgUtils.itemInstance.update(self.entity)

        else:
            print 'no valid Object'


class sgProject():

    def __init__(self, projectId):
        '''Create an istance of Project and appends the shotgun connectivity '''

        self.sgUtils = ShotgunUtils()
        self.entity = self.sgUtils.projectInstance.readOneByProperties(self.sgUtils.projectInstance.Properties.Id,
                                                                       projectId)

    def project2Sg(self):

        if self.entity.getShotgunID() == 0:
            sgName = self.entity.getName()


            data = {'name': sgName, 'sg_status': 'Active', 'sg_type': 'Feature'}
            project = self.sg.create('Project', data)

            self.entity.setShotgunID(project['id'])
            self.sgUtils.projectInstance.update(self.entity)

        else :
            print 'Project all ready in shotgun ', self.entity.getShotgunID()
            self.updateSg(self.entity.getShotgunID())

    def updateSg(self, sgId):

        sgName = self.entity.getName()
        sgSequenceSubscription = self.sgUtils.sgDicListFromDaoSequenceSubscription(self.entity.getSequenceSubscriptions())

        data = {'name': sgName, 'sg_status': 'Active', 'sg_type': 'Feature', 'sg_sequences': sgSequenceSubscription}

        self.sgUtils.sg.update('Project', sgId, data)

class sgSequence():
    pass

class sgShot():
    pass

class sgDigitalMedia():
    pass

class sgUser():

    def __init__(self, userId):

        self.sgUtils = ShotgunUtils()

        self.entity = self.sgUtils.userInstance.readOneByProperties(self.sgUtils.userInstance.Properties.Id, userId)

    def user2Sg(self):

        if self.entity.getShotgunID() == 0:

            sgUserName = self.entity.getName()
            sgDepartment = self.entity.getDepartment()
            sgPass = self.entity.getPassword()
            sgEmail = self.entity.getEmail()
            sgActive = self.entity.getIsActive()






