import sys
import os.path as path

import datetime

from PySide import QtGui
from PySide import QtCore

from mainWindow import Ui_MainWindow
from utility_notes import Ui_DockWidget as uiDocNotes
from loginDialog import Ui_Dialog
from shotgun_api3 import Shotgun

class ShotgunUtils():
    '''
    a light version of the shotgun utils class to connect and update shotgun task for external artist
    '''

    def __init__(self):
        '''
        creates the connection to the shotgun site by api
        '''

        '''   shotgun conection '''
        SERVER_PATH = "https://hcpstudio.shotgunstudio.com"
        SCRIPT_NAME = 'Tracker'
        SCRIPT_KEY = '99b5c166044037cc2d04646b1dfd58b2f44e8a146b710b425b8f561f2a21e49d'

        self.sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
        self.userId = None
        self.tasks = None

    def getsgParameters(self, sgType, parameter=None):
        schema = self.sg.schema_field_read(sgType, parameter)
        print schema

    def getUserId(self, userName):

        filters = [['name', 'is', userName]]
        field = ['id', 'name']

        user = self.sg.find_one('HumanUser', filters)

        if user:
            self.userId = user['id']
            return user['id']

        else:
            print "no {0} User found ".format(userName)
            return None

    def taskByUser(self):

        if not self.userId == None:

            filter = [['task_assignees', 'is', {'type': 'HumanUser', 'id': self.userId}],
                      ['sg_status_list', 'is_not', 'fin']]

            fields = ['id']

            taskList = self.sg.find('Task', filter, fields)

            if taskList:
                self.tasks = taskList
                return taskList

            else:

                self.tasks = []

                print "no task Asigned to: ", self.userId
                return taskList


        else:
            taskList = []

            print "no Id found"
            return taskList

    def getTaskById(self, taskId):

        filter = [['id', 'is', taskId]]

        fields = ['id', 'content', 'sg_status_list', 'start_date', 'due_date', 'sg_complexity',
                  'sg_priority_1', 'sg_note', 'project', 'entity', 'sg_digitalmedia', 'sg_attachment']

        task = self.sg.find_one('Task', filter, fields)

        if task:
            return task

        else:
            print 'no task found'
            return None

    def updateStatusFromUser(self, taskId, status):

        task = self.getTaskById(taskId)

        if task:


            project = task['project']
            sgStatus = status


            data = {'project': project, 'sg_status_list': sgStatus}

            self.sg.update('Task', taskId, data)
            return 1

        else:
            print 'No task by this id'
            return None

    def getNote(self, sgId):

        filter = [['id', 'is', sgId]]
        fields = ['content']
        note = self.sg.find_one('Note', filter, fields)
        if note:
            return note['content']

        else:
            print 'no note'
            return 'no note'

    def updateNote(self, sgId, content):

        filter = [['id', 'is', sgId]]
        fields = ['content', 'project']
        note = self.sg.find_one('Note', filter, fields)
        if note:
            project = note['project']
            data = {'project': project, 'content': content}

            return note['content']

        else:
            print 'no note'
            return 'no note'

    def uploadAttachment(self, taskId, filePath):

        task  = self.getTaskById(taskId)

        if task:

            entity = task['entity']
            if entity:

                entityType = entity['type']
                entityId = entity['id']

                uploadedfile = self.sg.upload(entityType, entityId, filePath)

                if uploadedfile:

                    data = {'sg_file': {'type': 'Attachment', 'id': uploadedfile}}

                    self.sg.update(entityType, entityId, data)
                    return uploadedfile
            else:
                print 'no entity set'

    def downloadAttachment(self, taskId, downloadPath):

        task = self.getTaskById(taskId)

        if task:

            for attach in task['sg_attachment']:

                filePath = path.join( downloadPath,'{0}'.format(attach['name']))
                self.sg.download_attachment(attach, filePath)
                print 'fileDownloaded'

        else:
            print 'no task found'

class sgLoging(QtGui.QDialog):

    def __init__(self, parent = None):
        super(sgLoging, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.userName = None
        self.userPassword = None
        self.exec_()

    def accept(self):
        user = self.ui.userLineText.text()
        passWord = self.ui.passwordLineText.text()

        if self.validateUser(user):

            self.userName = user

            if self.validatePassword(passWord):

                self.userPassword = passWord

                self.close()

            else:
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowTitle('Login Fail')
                msgBox.setText('Incorrect Password')
                msgBox.exec_()

        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle('Login Fail')
            msgBox.setText('No user by this mame: {0}'.format(user))
            msgBox.exec_()

    def validateUser(self, userName):
        sgUtils = ShotgunUtils()

        if sgUtils.getUserId(userName):
            return True

        else:
            return False

    def validatePassword(self, passWord):
        return True

class notesDocable(QtGui.QDockWidget, uiDocNotes):

    def __init__(self, parent=None):
        super(notesDocable, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Utilities')
        self.show()

class sgTracker(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(sgTracker, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("HuevoCartoon Studio Tacker")
        self.docUtils = notesDocable(self)
        self.docUtils.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.docUtils.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.docUtils)
        self.show()

        self.sgUtils = ShotgunUtils()


        ''' button conection'''

        self.updateButton.clicked.connect(self.task2Table)
        self.loginButton.clicked.connect(self.logIn)
        self.inprogressButton.clicked.connect(self.setInProgress)
        self.apprubalButton.clicked.connect(self.submitApproval)

    def task2Table(self):

        self.sgUtils.taskByUser()


        if not self.taskTable.rowCount() == 0:

            self.taskTable.setRowCount(0)

        if self.sgUtils.tasks:

            size = len(self.sgUtils.tasks)

            self.taskTable.setRowCount(size)

            for x, task in enumerate(self.sgUtils.tasks):
                currentTask = self.sgUtils.getTaskById(task['id'])

                if currentTask:
                    entity = currentTask['entity']
                    entityType = QtGui.QTableWidgetItem(entity['type'])
                    entityName = QtGui.QTableWidgetItem(entity['name'])
                    taskName = QtGui.QTableWidgetItem(currentTask['content'])
                    status = QtGui.QTableWidgetItem(currentTask['sg_status_list'])
                    priority = QtGui.QTableWidgetItem(currentTask['sg_priority_1'])
                    endDate = QtGui.QTableWidgetItem(currentTask['due_date'])
                    complex = QtGui.QTableWidgetItem(currentTask['sg_complexity'])
                    sgId = QtGui.QTableWidgetItem(str(currentTask['id']))
                    timeLeft = QtGui.QTableWidgetItem(self.deltaTime(currentTask['due_date']))


                    entityType.setBackground(self.colorFromEntity(entity['type']))
                    entityName.setBackground(self.colorFromEntity(entity['type']))
                    taskName.setBackground(self.colorFromEntity(entity['type']))
                    sgId.setBackground(self.colorFromEntity(entity['type']))
                    timeLeft.setBackground(self.colorFromDate(currentTask['due_date']))
                    endDate.setBackground(self.colorFromDate(currentTask['due_date']))
                    status.setBackground(self.colorFromStatus(currentTask['sg_status_list']))
                    priority.setBackground(self.colorFromPriority(currentTask['sg_priority_1']))
                    complex.setBackground(self.colorFromComplex(currentTask['sg_complexity']))

                    self.taskTable.setItem(x, 0, entityType)
                    self.taskTable.setItem(x, 1, entityName)
                    self.taskTable.setItem(x, 2, taskName)
                    self.taskTable.setItem(x, 3, status)
                    self.taskTable.setItem(x, 4, priority)
                    self.taskTable.setItem(x, 5, timeLeft)
                    self.taskTable.setItem(x, 6, endDate)
                    self.taskTable.setItem(x, 7, complex)
                    self.taskTable.setItem(x, 8, sgId)

        else:

            self.taskTable.setRowCount(0)

    def setInProgress(self):

        selection = self.taskTable.selectedItems()
        if len(selection) > 1:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle('Warning')
            msgBox.setText('select just one status Cell')
            msgBox.exec_()

        else:

            for select in selection:
                row = select.row()
                status = self.taskTable.item(row, 3)

                if not status.text() == 'hld' or select.text() == 'fin':


                    cell = self.taskTable.item(row, 8)


                    self.sgUtils.updateStatusFromUser(int(cell.text()), 'ip')

                else:
                    pass

            self.task2Table()

    def submitApproval(self):

        selection = self.taskTable.selectedItems()

        if len(selection) > 1:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle('Warning')
            msgBox.setText('select just one status Cell')
            msgBox.exec_()

        else:

            for select in selection:
                row = select.row()
                status = self.taskTable.item(row, 3)

                if not status.text() == 'hld' or select.text() == 'fin':

                    cell = self.taskTable.item(row, 8)


                    fname , x = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')

                    if fname:

                        cell = self.taskTable.item(row, 8)
                        self.sgUtils.updateStatusFromUser(int(cell.text()), 'app')

                    else:
                        msgBox = QtGui.QMessageBox()
                        msgBox.setWindowTitle('Warning')
                        msgBox.setText('no file selected, please select a file to upload.')
                        msgBox.exec_()

                else:
                    pass

            self.task2Table()

    def colorFromDate(self, sgdue):

        color = QtGui.QColor('white')

        delta = int(self.deltaTime(sgdue))

        if delta >= 3:
            color  = QtGui.QColor(230, 255, 255)

        elif delta == 2:
            color = QtGui.QColor('yellow')

        elif delta == 1:
            color = QtGui.QColor(255, 122, 0)

        else:
            color = QtGui.QColor(255, 0, 0)

        return color

    def deltaTime(self, sgDue):

        today = datetime.datetime.now()
        duedate = datetime.datetime.strptime(sgDue, '%Y-%m-%d')
        delta = duedate - today

        return str(delta.days + 1)

    def colorFromStatus(self, sgStatus):


        if sgStatus == 'rdy':
            color  = QtGui.QColor('white')

        elif sgStatus == 'ip':
            color = QtGui.QColor(50, 255, 50)

        elif sgStatus == 'fin':
            color = QtGui.QColor(0, 255, 0)

        elif sgStatus == 'hld':
            color = QtGui.QColor(255, 0, 255)

        elif sgStatus == 'app':
            color = QtGui.QColor(0, 200, 255)

        elif sgStatus == 'rtk':
            color = QtGui.QColor(230, 10, 0)

        else:
            color = QtGui.QColor('white')

        return color

    def colorFromPriority(self, sgPriority):


        if sgPriority == 'LOW':
            color = QtGui.QColor(200, 250, 250)

        elif sgPriority == 'NORMAL':
            color = QtGui.QColor(250, 250, 200)

        elif sgPriority == 'HIGH':
            color = QtGui.QColor(250, 150, 0)

        elif sgPriority == 'EXTREME':
            color = QtGui.QColor(250, 100, 0)

        else:
            color = QtGui.QColor('white')

        return color

    def colorFromComplex(self, sgComplexity):

        if sgComplexity == 'A':
            color = QtGui.QColor(200, 250, 100)

        elif sgComplexity == 'B':
            color = QtGui.QColor(250, 250, 100)

        elif sgComplexity == 'C':
            color = QtGui.QColor(250, 150, 100)

        elif sgComplexity == 'D':
            color = QtGui.QColor(250, 100, 100)

        elif sgComplexity == 'E':
            color = QtGui.QColor(250, 50, 100)

        else:
            color = QtGui.QColor('white')

        return color

    def colorFromEntity(self, sgEntity):

        if sgEntity == 'Asset':
            color = QtGui.QColor(200, 250, 200)

        elif sgEntity == 'Shot':
            color = QtGui.QColor(130, 200, 255)

        else:
            color = QtGui.QColor('white')

        return color

    def setFlags(self):

        self.taskTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.taskTable.setSortingEnabled(True)
        self.setStyleSheet('background-color: darkgray;')


    def logIn(self):

        credencials = sgLoging(self)

        self.sgUtils.getUserId(credencials.userName)
        self.sgUtils.taskByUser()

        self.task2Table()
        self.loginButton.setText('logged as : {0}'.format(credencials.userName))
        self.loginButton.setStyleSheet('background-color : lightgreen')
        self.loginButton.setDisabled(True)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)

        self.loginButton.setFont(font)


def main():
    app = QtGui.QApplication(sys.argv)
    ex = sgTracker()
    ex.setFlags()
    #ex.task2Table()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



