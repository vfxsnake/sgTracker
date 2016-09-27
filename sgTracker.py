import sys
import os.path as path
import os
import datetime

from PySide import QtGui
from PySide import QtCore

from mainWindow import Ui_MainWindow
from utility_notes import Ui_DockWidget as uiDocNotes
from loginDialog import Ui_Dialog
from notesDialog import Ui_Dialog as NoteDialog
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
        self.userDic = {}
        self.tasks = None
        self.projectPath = None

    def getsgParameters(self, sgType, parameter=None):
        schema = self.sg.schema_field_read(sgType, parameter)
        print schema

    def getUserId(self, userName):

        filters = [['name', 'is', userName]]
        field = ['id', 'name', 'sg_projectpath']

        user = self.sg.find_one('HumanUser', filters, field)

        if user:
            self.userId = user['id']
            self.projectPath = user['sg_projectpath']
            self.userDic = user

            return user['id']

        else:
            print "no {0} User found ".format(userName)
            return None

    def taskByUser(self):

        if not self.userId == None:

            filter = [['task_assignees', 'is', {'type': 'HumanUser', 'id': self.userId}],
                      ['sg_status_list', 'is_not', 'fin']]

            fields = ['id']

            order = [{'field_name': 'due_date', 'direction': 'asc'}, {'field_name': 'sg_priority_1', 'direction':'asc'},
                     {'field_name': 'sg_complexity', 'direction': 'desc'}]

            taskList = self.sg.find('Task', filter, fields, order)

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
                  'sg_priority_1', 'sg_note', 'project', 'entity', 'sg_digitalmedia', 'sg_displayname']

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

    def updateProjectPath(self, projectPath):

        data = {'sg_projectpath': projectPath}

        self.sg.update('HumanUser', self.userId, data)

    def getNotes(self, sgTaskId):

        task = self.getTaskById(sgTaskId)
        if task:
            filters = [['tasks', 'is', task]]
            fields = ['content', 'created_at', 'user', 'addressings_to']
            order = [{'field_name': 'created_at', 'direction': 'asc'}]

            notes = self.sg.find('Note', filters, fields, order)

            return notes

        else:
            print 'no Task'
            return None

    def createNote(self, taskId, content):

        task = self.getTaskById(taskId)

        if task:

            data = {'project': task['project'],
                    'content': content, 'tasks': [task], 'user': self.userDic}

            note = self.sg.create('Note', data)
            return note['id']

        else:
            return None

    def uploadAttachment(self, taskId, filePath, tag):

        task = self.getTaskById(taskId)

        if task:

            entity = task['entity']
            if entity:

                entityType = entity['type']
                entityId = entity['id']

                uploadedfile = self.sg.upload(entityType, entityId, filePath)

                if uploadedfile:
                    data = {'sg_type': tag, 'sg_taskid': taskId}
                    self.sg.update('Attachment', uploadedfile, data)
                    return uploadedfile
                else:
                    return None
            else:
                print 'no entity set'
                return None

    def downloadAttachment(self, taskId, downloadPath):

        filters = [['sg_taskid', 'is', taskId]]
        fields = ['id']
        attachments = self.sg.find('Attanchment', filters, fields)

        if attachments:
            for attach in attachments:
                    dwFile = self.sg.download_attachment(True, downloadPath, attach['id'])
        else:
            print 'no attach found'


    def uploadReference(self, entityType, entityId, filePath, tag):

        uploadedfile = self.sg.upload(entityType, entityId, filePath)

        if uploadedfile:
            data = {'sg_type': tag}
            self.sg.update('Attachment', uploadedfile, data)

            return uploadedfile

        else:
            return None

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

class noteCreateDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(noteCreateDialog, self).__init__(parent)
        self.ui = NoteDialog()
        self.ui.setupUi(self)
        self.noteText = None
        self.exec_()

    def accept(self):
        self.noteText = self.ui.NoteTextEdit.toPlainText()
        self.close()


class sgTracker(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(sgTracker, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("HuevoCartoon Studio Tacker")
        self.docUtils = notesDocable(self)
        self.docUtils.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.docUtils.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.docUtils)

        ''' disble buttons'''
        self.docUtils.setProjectButton.setDisabled(True)
        self.docUtils.replayButton.setDisabled(True)
        self.docUtils.attachButton.setDisabled(True)
        self.docUtils.downloadButton.setDisabled(True)
        self.inprogressButton.setDisabled(True)
        self.apprubalButton.setDisabled(True)
        self.updateButton.setDisabled(True)


        self.docUtils.NoteTextEdit.setReadOnly(True)

        ''' show window'''
        self.show()

        self.sgUtils = ShotgunUtils()

        self.projectPath = None

        ''' button conection'''

        self.updateButton.clicked.connect(self.task2Table)
        self.loginButton.clicked.connect(self.logIn)
        self.inprogressButton.clicked.connect(self.setInProgress)
        self.apprubalButton.clicked.connect(self.submitApproval)
        self.docUtils.setProjectButton.clicked.connect(self.setProject)
        self.docUtils.replayButton.clicked.connect(self.replayNote)
        self.docUtils.attachButton.clicked.connect(self.uploadAttachments)

        '''Qtable change selection signal'''
        model = self.taskTable.selectionModel()
        model.selectionChanged.connect(self.clearNote)

        '''qtable vertical header conection'''

        self.taskTable.verticalHeader().sectionClicked.connect(self.displayNotes)

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
                    taskName = QtGui.QTableWidgetItem(currentTask['sg_displayname'])
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

            self.messageBox('Warning', 'select One status Cell')

        if not selection:
            self.messageBox('Warning', 'select One status Cell')

        else:

            for select in selection:
                row = select.row()
                status = self.taskTable.item(row, 3)

                if not (status.text() == 'hld' or select.text() == 'fin' or select.text() == 'ip'):


                    cell = self.taskTable.item(row, 8)
                    if status.text() == 'app':

                        msgBox = QtGui.QMessageBox()
                        msgBox.setParent(self)
                        msgBox.setStyleSheet('background-color : lightgrey')
                        msgBox.setText("The task has been submitted for Approval.")
                        msgBox.setInformativeText("Do you want to set to Inprogres?")
                        msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
                        msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
                        ret = msgBox.exec_()

                        if ret == QtGui.QMessageBox.Yes:
                            self.sgUtils.updateStatusFromUser(int(cell.text()), 'ip')

                        else:
                            pass

                    else:
                        self.sgUtils.updateStatusFromUser(int(cell.text()), 'ip')

                else:
                    pass

                self.task2Table()

    def submitApproval(self):

        selection = self.taskTable.selectedItems()

        if len(selection) > 1:
            self.messageBox('Warning', 'select One status Cell')

        if not selection:

            self.messageBox('Warning', 'select One status Cell')

        else:

            for select in selection:
                row = select.row()
                status = self.taskTable.item(row, 3)

                if status.text() == 'ip' or select.text() == 'app':

                    cell = self.taskTable.item(row, 8)
                    attachment = None

                    if status.text() == 'app':
                        msgBox = QtGui.QMessageBox()
                        text = "the task has been submitted for Aproval. " \
                               "If you want to add more Atachmentes select the files, if not close the browser."

                        self.messageBox('Warning', text)


                    fname, x = QtGui.QFileDialog.getOpenFileNames(self, 'Open file', self.sgUtils.projectPath)

                    if fname:

                        cell = self.taskTable.item(row, 8)

                        for f in fname:

                            attachment = self.sgUtils.uploadAttachment(int(cell.text()), str(f), 'SUBMIT')

                        if attachment:
                            self.sgUtils.updateStatusFromUser(int(cell.text()), 'app')

                        else:

                            self.messageBox('Error', 'Fale to upload attachment')

                    else:

                        self.messageBox('Error', 'no file selected.')

                else:
                    self.messageBox('Warnig', 'the status is not In progress')

            self.task2Table()

    def setProject(self):

        fname = QtGui.QFileDialog.getExistingDirectory()

        if fname:

            self.projectStructure(fname)
            self.sgUtils.updateProjectPath(self.projectPath)
            self.inprogressButton.setDisabled(False)
            self.apprubalButton.setDisabled(False)
            self.updateButton.setDisabled(False)
            self.docUtils.setProjectButton.setStyleSheet('background-color : lightgreen')
            self.docUtils.setProjectButton.setDisabled(True)
        else:

            self.messageBox('Warnig','No folder Selected')

    def projectStructure(self, userPath):

        dirSize = os.listdir(userPath)

        hcProjectFolder = path.join(userPath, 'HCP_Projects')

        if not path.exists(hcProjectFolder):

            os.mkdir(hcProjectFolder)
            print 'Project Created'
        else:
            print 'Project Allready exist'

        if not path.exists(path.join(hcProjectFolder, 'ASSETS')):
            os.mkdir(path.join(hcProjectFolder, 'ASSETS'))

            print 'Asset folder Created'

        else:
            print 'Assets Folder exist'

        if not path.exists(path.join(hcProjectFolder, 'SHOTS')):
            os.mkdir(path.join(hcProjectFolder, 'SHOTS'))

            print 'SHOTS folder Created'

        else:
            print 'SHOTS Folder exist'

        self.projectPath = hcProjectFolder

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
        self.taskTable.setSortingEnabled(False)
        self.setStyleSheet('background-color: darkgray;')
        self.docUtils.NoteTextEdit.setFontPointSize(12)

    def logIn(self):

        credencials = sgLoging(self)
        if credencials.userName:
            self.sgUtils.getUserId(credencials.userName)
            self.sgUtils.taskByUser()

            self.task2Table()
            self.loginButton.setText('logged as : {0}'.format(credencials.userName))
            self.loginButton.setStyleSheet('background-color : lightgreen')

            self.loginButton.setDisabled(True)

            '''enable buttons'''
            self.docUtils.setProjectButton.setDisabled(False)

            font = QtGui.QFont()
            font.setPointSize(10)
            font.setBold(True)

            self.loginButton.setFont(font)

            if self.sgUtils.projectPath:
                self.docUtils.setProjectButton.setDisabled(True)
                self.docUtils.setProjectButton.setStyleSheet('background-color : lightgreen')
                self.inprogressButton.setDisabled(False)
                self.apprubalButton.setDisabled(False)
                self.updateButton.setDisabled(False)


        else:
            pass

    def displayNotes(self, taskIndex):

        self.docUtils.NoteTextEdit.clear()

        self.docUtils.replayButton.setDisabled(False)
        self.docUtils.attachButton.setDisabled(False)
        self.docUtils.downloadButton.setDisabled(False)

        row = taskIndex

        item = self.taskTable.item(row, 8)

        notes = self.sgUtils.getNotes(int(item.text()))

        if notes:
            for note in notes:
                if not note['user']['name'] == self.sgUtils.userDic['name']:
                    self.docUtils.NoteTextEdit.setTextColor('red')
                    self.docUtils.NoteTextEdit.append(note['user']['name'])
                    self.docUtils.NoteTextEdit.append(note['created_at'].isoformat())
                    self.docUtils.NoteTextEdit.setTextColor('black')
                    self.docUtils.NoteTextEdit.append(note['content'])
                    self.docUtils.NoteTextEdit.append('')
                    self.docUtils.NoteTextEdit.append('')

                else:
                    self.docUtils.NoteTextEdit.setTextColor('blue')
                    self.docUtils.NoteTextEdit.append(note['user']['name'])
                    self.docUtils.NoteTextEdit.append(note['created_at'].isoformat())
                    self.docUtils.NoteTextEdit.setTextColor('black')
                    self.docUtils.NoteTextEdit.append(note['content'])
                    self.docUtils.NoteTextEdit.append('')
                    self.docUtils.NoteTextEdit.append('')

        else:
            text = 'no notes'
            self.docUtils.NoteTextEdit.append(text)

    def replayNote(self):

        noteReplay = noteCreateDialog(self)

        if noteReplay.noteText:
            rows = self.taskTable.selectionModel().selectedRows()

            if len(rows) == 1:

                for row in rows:

                    index = row.row()

                    task = self.taskTable.item(index, 8)

                    taskId = int(task.text())

                self.sgUtils.createNote(taskId, noteReplay.noteText)

                self.displayNotes(index)

            else:
                warning = self.messageBox('Warning', 'Please Select a row')

    def messageBox(self, mode, text):

        msgBox = QtGui.QMessageBox()
        msgBox.setParent(self)
        msgBox.setStyleSheet('background-color : lightgrey')
        msgBox.setWindowTitle(mode)
        msgBox.setText(text)
        msgBox.exec_()

    def clearNote(self):

        self.docUtils.NoteTextEdit.clear()
        self.docUtils.replayButton.setDisabled(True)
        self.docUtils.attachButton.setDisabled(True)
        self.docUtils.downloadButton.setDisabled(True)

    def uploadAttachments(self):

        rows = self.taskTable.selectionModel().selectedRows()

        if len(rows) == 1:

            for row in rows:

                index = row.row()

                taskId = self.taskTable.item(index, 8)

                notes = self.sgUtils.getNotes(int(taskId.text()))

                lastNote = notes[-1]

                fname, x = QtGui.QFileDialog.getOpenFileNames(self, 'Open file', self.sgUtils.projectPath)

                if fname:
                    for f in fname:

                        attachment = self.sgUtils.uploadReference(lastNote['type'], lastNote['id'], f, 'REFERENCE')

                        if not attachment:
                            self.messageBox('Error', 'Fale to upload attachment')

    def checpath(self, tableItem):

        if self.projectPath:
            project = self.projectPath



def main():
    app = QtGui.QApplication(sys.argv)
    ex = sgTracker()
    ex.setFlags()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


