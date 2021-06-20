import sys

import os

import subprocess

from pathlib import Path

import shutil

import xml.etree.ElementTree as ET

from PyQt5 import QtCore, QtGui, QtWidgets

#Folders
class Folder():
    def __init__(self, path):
        '''constructor for basic folder class'''
        
        self.dir = Path(path).parent # parent directory
        self.name = os.path.basename(path) # folder name
        self.path = path # full directory path

        # create the folder if it doesn't exist
        if not os.path.exists(self.path):
            self.create()

    def delete(self):
        ''' delete the folder'''
        # recursively deletes folder and children directories
        shutil.rmtree(self.path)

    def rename(self, newName):
        '''rename the folder'''
        # temporarily store old path
        oldPath = self.path

        # update name and path variables with new name
        self.name = newName
        self.path = os.path.join(self.dir, self.name)

        # rename folder
        os.rename(oldPath, self.path)

    def create(self):
        ''' Create the folder'''
        # create folder
        os.mkdir(self.path)

        # create util subfolders
        self.newUtilitySubfolders(self.path)

    def newUtilitySubfolders(self, path):
        ''' Create the utility subfolders'''
        # make Temp folder
        os.mkdir(os.path.join(path, "Temp"))

        # make tools folder
        toolsFolder = os.path.join(path, "Tools")
        os.mkdir(toolsFolder)

        # In tools folder, make config file
        configTemplate = os.path.join( os.getcwd(), "ConfigFileTemplate.xml")
        configTarget = os.path.join(toolsFolder, "config.xml")
        shutil.copyfile(configTemplate, configTarget)

class Project(Folder):
    def __init__(self, path):
        # initialize project folder
        super().__init__(path)

        self.createDirectory()

    def createDirectory(self):
        # parse xml Directory file
        projectConfig = os.path.join(os.getcwd(), "ProjectConfig.xml")
        projectDirectory = ET.parse(projectConfig)
        root = projectDirectory.getroot()
        
        for elem in root:
            self.createSubFolder(self.path, elem)

        self.createUEProject()


    def createSubFolder(self, pardir, elem):
        # recursive function to create folders for everything in the xml directory file
        # get the name of the element and make that a folder in the specified directory
        subFolderPath = os.path.join(pardir, elem.get('name'))
        Folder(subFolderPath)

        # if there are subelements, do the function for them
        if len(list(elem)):
            for subelem in elem:
                self.createSubFolder(subFolderPath, subelem)

    def createUEProject(self):
        # copy the UE4 project
        UESource = os.path.join(os.getcwd(), "UE4Project")
        UE4Project = "UE4Project"

        UESource = os.path.join(os.getcwd(), UE4Project)
        UERoot= os.path.join(self.path, "UE4")
        UEPath = os.path.join(UERoot, "{}".format(self.name))
        shutil.copytree(UESource, UEPath)

        # rename the uproject file
        UEProject = os.path.join(UEPath, "{}.uproject".format(UE4Project))
        UEProjectName = os.path.join(UEPath, "{}.uproject".format(self.name))
        os.rename(UEProject, UEProjectName)

        UEDirs = []

        #make the config folder setup
        # get the folder directories in the UE4 project
        for root, dirs, files in os.walk(UERoot, topdown = True):
            '''print("the root:")
            print(root)
            print("The directories are: ")
            print(dirs)'''
            if dirs:
                for folder in dirs:
                    UEDirs.append(os.path.join(root, folder))
                    # self.newUtilitySubfolders(os.path.join(root, folder))
        
        # make the config folders            
        for folder in UEDirs:
            self.newUtilitySubfolders(folder)
class Asset():
    def __init__(self, path, app=None, assetType=None):
        '''constructor for basic asset class'''

        self.dir = Path(path).parent # parent directory
        self.name = os.path.basename(path) # asset name
        self.path = path # full path

        # if there's an application, store it
        if app != None:
            self.app = app

        # if there's an assetType, store it
        if assetType != None:
            self.assetType = assetType

        # create template if it doesn't exist
        if not os.path.exists(self.path):
            self.create()
    def create(self):
        ''' create template asset '''
        # parse config and search for asset type
        configFile = ET.parse(os.path.join(self.dir, "Tools\\config.xml"))
        configRoot = configFile.getroot()

        # search config for dcc, and get first filetype
        fileType = configRoot.find("./applications/dcc[@name = '{}']/fileType".format(self.app)).text

        self.path += fileType

        # find matching template file from tool configuration
        # check if this works, else find the first one without name
        # try/except? for the name thing
        fileTemplate = configRoot.find("./applications/dcc[@name = '{}']/template[@name = '{}']".format(self.app, self.assetType)).text
        fileTemplatePath = os.path.join(os.getcwd(), fileTemplate)

        
        # copy into proper directory with the proper name
        shutil.copyfile(fileTemplatePath, self.path)

    def delete(self):
        ''' delete the asset '''
        os.remove(self.path)
    def rename(self, newName):
        '''rename the asset'''
        # temporarily store old path
        oldPath = self.path

        # update name and path variables with new name
        self.name = newName
        self.path = os.path.join(self.dir, self.name)

        # rename asset
        os.rename(oldPath, self.path)
    def open(self):
        ''' open asset'''
        # isolate filetype ext from asset path
        pathFileType = os.path.splitext(self.path)[1]

        # parse config and search for asset type
        configFile = ET.parse(os.path.join(self.dir, "Tools\\config.xml"))
        configRoot = configFile.getroot()

        # find the matching asset filetype, find what dcc that belongs to, and the matching version
        application = configRoot.find("./applications/dcc/[fileType='{}']".format(pathFileType))
        applicationPath = application.find("./version").text

        # open the file using the version
        subprocess.Popen("%s %s" % (applicationPath, self.path))

'''*** Code converted from QT Designer ***'''
# GUI Class
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        '''sets up the ui'''
        # Main Window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(343, 513)

        # Main widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        #Tab Widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())

        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")


        '''*******Projects tab********'''
        self.projectsTab = QtWidgets.QWidget()
        self.projectsTab.setObjectName("projectsTab")

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.projectsTab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.projectsLayout = QtWidgets.QVBoxLayout()
        self.projectsLayout.setObjectName("projectsLayout")

        # New Project Box
        self.newProjectBox = QtWidgets.QGroupBox(self.projectsTab)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newProjectBox.sizePolicy().hasHeightForWidth())
        self.newProjectBox.setSizePolicy(sizePolicy)
        self.newProjectBox.setMinimumSize(QtCore.QSize(0, 86))
        self.newProjectBox.setObjectName("newProjectBox")

        self.newProjectLayout = QtWidgets.QGridLayout(self.newProjectBox)
        self.newProjectLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.newProjectLayout.setObjectName("newProjectLayout")

        self.newProjectBoxLayout = QtWidgets.QVBoxLayout()
        self.newProjectBoxLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.newProjectBoxLayout.setObjectName("newProjectBoxLayout")

        self.newProjectNameLayout = QtWidgets.QHBoxLayout()
        self.newProjectNameLayout.setObjectName("newProjectNameLayout")

        self.newProjectLabel = QtWidgets.QLabel(self.newProjectBox)
        self.newProjectLabel.setObjectName("newProjectLabel")
        self.newProjectNameLayout.addWidget(self.newProjectLabel, 0, QtCore.Qt.AlignVCenter)

        self.newProjectField = QtWidgets.QLineEdit(self.newProjectBox)
        self.newProjectField.setMinimumSize(QtCore.QSize(0, 20))
        self.newProjectField.setObjectName("newProjectField")
        self.newProjectNameLayout.addWidget(self.newProjectField)
        self.newProjectBoxLayout.addLayout(self.newProjectNameLayout)

        self.createProject = QtWidgets.QPushButton(self.newProjectBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.createProject.sizePolicy().hasHeightForWidth())
        self.createProject.setSizePolicy(sizePolicy)
        self.createProject.setMinimumSize(QtCore.QSize(100, 23))
        self.createProject.setObjectName("createProject")
        self.createProject.clicked.connect(self.newProjectClicked)

        self.newProjectBoxLayout.addWidget(self.createProject, 0, QtCore.Qt.AlignHCenter)
        self.newProjectLayout.addLayout(self.newProjectBoxLayout, 2, 0, 1, 1)
        self.projectsLayout.addWidget(self.newProjectBox)

        # Existing Project Box
        self.existingProjectBox = QtWidgets.QGroupBox(self.projectsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.existingProjectBox.sizePolicy().hasHeightForWidth())
        self.existingProjectBox.setSizePolicy(sizePolicy)
        self.existingProjectBox.setMinimumSize(QtCore.QSize(0, 0))
        self.existingProjectBox.setObjectName("existingProjectBox")

        self.newProjectLayout_4 = QtWidgets.QGridLayout(self.existingProjectBox)
        self.newProjectLayout_4.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.newProjectLayout_4.setObjectName("newProjectLayout_4")

        self.existingProjectLayout = QtWidgets.QVBoxLayout()
        self.existingProjectLayout.setObjectName("existingProjectLayout")
        
        # Project Directory
        self.projectDirectory = QtWidgets.QTreeView(self.existingProjectBox)

        # self.projectDirectory = QtWidgets.QTreeWidget(self.existingProjectBox)

        '''**********adding project directory code here********'''
        self.model = QtWidgets.QFileSystemModel() # file directory
        self.model.setRootPath("C:\\PMTTemp") #set root of path 'C:\\dev'
        # self.model.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.projectDirectory.setModel(self.model) #ties file directory to tree view
        self.projectDirectory.setRootIndex(self.model.index(self.model.rootPath())) # set the base of tree to base of file directory
        self.projectDirectory.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # allow multiple things selected
        self.projectDirectory.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems) # selects by path

        
        self.projectDirectory.setObjectName("projectDirectory")
        self.existingProjectLayout.addWidget(self.projectDirectory)

        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.existingProjectLayout.addItem(spacerItem)

        # Delete Selected Button
        self.deleteSelectedButton = QtWidgets.QPushButton(self.existingProjectBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteSelectedButton.sizePolicy().hasHeightForWidth())
        self.deleteSelectedButton.setSizePolicy(sizePolicy)
        self.deleteSelectedButton.setMinimumSize(QtCore.QSize(100, 0))
        self.deleteSelectedButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.deleteSelectedButton.setObjectName("deleteSelectedButton")
        self.deleteSelectedButton.clicked.connect(self.deleteFolderClicked)
        self.existingProjectLayout.addWidget(self.deleteSelectedButton, 0, QtCore.Qt.AlignHCenter)

        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.existingProjectLayout.addItem(spacerItem1)

        self.renameSelectedField = QtWidgets.QLineEdit(self.existingProjectBox)
        self.renameSelectedField.setObjectName("renameSelectedField")
        self.existingProjectLayout.addWidget(self.renameSelectedField)

        # Rename Selected Button
        self.renameSelectedButton = QtWidgets.QPushButton(self.existingProjectBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.renameSelectedButton.sizePolicy().hasHeightForWidth())
        self.renameSelectedButton.setSizePolicy(sizePolicy)
        self.renameSelectedButton.setMinimumSize(QtCore.QSize(100, 0))
        self.renameSelectedButton.setObjectName("renameSelectedButton")
        self.renameSelectedButton.clicked.connect(self.renameFolderClicked)

        self.existingProjectLayout.addWidget(self.renameSelectedButton, 0, QtCore.Qt.AlignHCenter)

        spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.existingProjectLayout.addItem(spacerItem2)

        self.newFolderField = QtWidgets.QLineEdit(self.existingProjectBox)
        self.newFolderField.setObjectName("newFolderField")
        self.existingProjectLayout.addWidget(self.newFolderField)

        # New Folder Button
        self.newFolderButton = QtWidgets.QPushButton(self.existingProjectBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newFolderButton.sizePolicy().hasHeightForWidth())
        self.newFolderButton.setSizePolicy(sizePolicy)
        self.newFolderButton.setMinimumSize(QtCore.QSize(100, 0))
        self.newFolderButton.setObjectName("newFolderButton")
        self.newFolderButton.clicked.connect(self.newFolderClicked)

        self.existingProjectLayout.addWidget(self.newFolderButton, 0, QtCore.Qt.AlignHCenter)

        self.newProjectLayout_4.addLayout(self.existingProjectLayout, 0, 0, 1, 1)
        self.projectsLayout.addWidget(self.existingProjectBox)
        self.verticalLayout_4.addLayout(self.projectsLayout)
        self.tabWidget.addTab(self.projectsTab, "")

        '''********* Assets Tab ********'''
        self.assetsTab = QtWidgets.QWidget()
        self.assetsTab.setObjectName("assetsTab")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.assetsTab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.assetsLayout = QtWidgets.QVBoxLayout()
        self.assetsLayout.setObjectName("assetsLayout")

        # Directory Box
        self.directoryBox = QtWidgets.QGroupBox(self.assetsTab)
        self.directoryBox.setObjectName("directoryBox")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.directoryBox)
        self.verticalLayout_8.setObjectName("verticalLayout_8")

        self.assetDirectory = QtWidgets.QTreeView(self.directoryBox)
        self.assetDirectory.setObjectName("assetDirectory")

        '''***** added for folder directory****'''
        self.assetDirectory.setModel(self.model)
        self.assetDirectory.setRootIndex(self.model.index(self.model.rootPath()))

        self.assetDirectory.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # allow multiple things selected
        self.assetDirectory.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems) # selects by path
        
        self.verticalLayout_8.addWidget(self.assetDirectory)
        self.assetsLayout.addWidget(self.directoryBox)

        # New Asset Box
        self.newAssetBox = QtWidgets.QGroupBox(self.assetsTab)
        self.newAssetBox.setObjectName("newAssetBox")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.newAssetBox)
        self.verticalLayout_9.setObjectName("verticalLayout_9")

        self.assetTypeLabel = QtWidgets.QLabel(self.newAssetBox)
        self.assetTypeLabel.setObjectName("assetTypeLabel")
        self.verticalLayout_9.addWidget(self.assetTypeLabel)

        self.newAssetType = QtWidgets.QComboBox(self.newAssetBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newAssetType.sizePolicy().hasHeightForWidth())
        self.newAssetType.setSizePolicy(sizePolicy)
        self.newAssetType.setMinimumSize(QtCore.QSize(100, 0))
        self.newAssetType.setObjectName("newAssetType")
        self.newAssetType.addItem("")
        self.newAssetType.addItem("")
        self.newAssetType.addItem("")
        self.verticalLayout_9.addWidget(self.newAssetType, 0, QtCore.Qt.AlignHCenter)

        spacerItem3 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_9.addItem(spacerItem3)

        """**************Adding in asset software type*************"""
        self.assetAppLabel = QtWidgets.QLabel(self.newAssetBox)
        self.assetAppLabel.setObjectName("assetAppLabel")
        self.verticalLayout_9.addWidget(self.assetAppLabel)

        self.newAssetApp = QtWidgets.QComboBox(self.newAssetBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newAssetApp.sizePolicy().hasHeightForWidth())
        self.newAssetApp.setSizePolicy(sizePolicy)
        self.newAssetApp.setMinimumSize(QtCore.QSize(100, 0))
        self.newAssetApp.setObjectName("newAssetType")
        self.newAssetApp.addItem("")
        self.newAssetApp.addItem("")
        self.newAssetApp.addItem("")
        self.verticalLayout_9.addWidget(self.newAssetApp, 0, QtCore.Qt.AlignHCenter)

        spacerItem6 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_9.addItem(spacerItem6)

        self.newAssetNameField = QtWidgets.QLineEdit(self.newAssetBox)
        self.newAssetNameField.setText("")
        self.newAssetNameField.setObjectName("newAssetNameField")
        self.verticalLayout_9.addWidget(self.newAssetNameField)

        self.createAsset = QtWidgets.QPushButton(self.newAssetBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.createAsset.sizePolicy().hasHeightForWidth())
        self.createAsset.setSizePolicy(sizePolicy)
        self.createAsset.setMinimumSize(QtCore.QSize(100, 0))
        self.createAsset.setObjectName("createAsset")
        self.createAsset.clicked.connect(self.newAssetClicked)

        self.verticalLayout_9.addWidget(self.createAsset, 0, QtCore.Qt.AlignHCenter)

        self.assetsLayout.addWidget(self.newAssetBox)

        # Selected Asset Box
        self.selectedAssetBox = QtWidgets.QGroupBox(self.assetsTab)
        self.selectedAssetBox.setObjectName("selectedAssetBox")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.selectedAssetBox)
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.openAssetButton = QtWidgets.QPushButton(self.selectedAssetBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openAssetButton.sizePolicy().hasHeightForWidth())
        self.openAssetButton.setSizePolicy(sizePolicy)
        self.openAssetButton.setMinimumSize(QtCore.QSize(100, 0))
        self.openAssetButton.setObjectName("openAssetButton")
        self.openAssetButton.clicked.connect(self.openAssetClicked)

        self.verticalLayout_10.addWidget(self.openAssetButton, 0, QtCore.Qt.AlignHCenter)

        spacerItem4 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_10.addItem(spacerItem4)

        self.renameAssetField = QtWidgets.QLineEdit(self.selectedAssetBox)
        self.renameAssetField.setObjectName("renameAssetField")
        self.verticalLayout_10.addWidget(self.renameAssetField)

        self.renameAssetButton = QtWidgets.QPushButton(self.selectedAssetBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.renameAssetButton.sizePolicy().hasHeightForWidth())
        self.renameAssetButton.setSizePolicy(sizePolicy)
        self.renameAssetButton.setMinimumSize(QtCore.QSize(100, 0))
        self.renameAssetButton.setObjectName("renameAssetButton")
        self.renameAssetButton.clicked.connect(self.renameAssetClicked)

        self.verticalLayout_10.addWidget(self.renameAssetButton, 0, QtCore.Qt.AlignHCenter)

        spacerItem5 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_10.addItem(spacerItem5)

        self.deleteAssetButton = QtWidgets.QPushButton(self.selectedAssetBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteAssetButton.sizePolicy().hasHeightForWidth())
        self.deleteAssetButton.setSizePolicy(sizePolicy)
        self.deleteAssetButton.setMinimumSize(QtCore.QSize(100, 0))
        self.deleteAssetButton.setObjectName("deleteAssetButton")
        self.deleteAssetButton.clicked.connect(self.deleteAssetClicked)

        self.verticalLayout_10.addWidget(self.deleteAssetButton, 0, QtCore.Qt.AlignHCenter)

        self.assetsLayout.addWidget(self.selectedAssetBox)
        self.verticalLayout_5.addLayout(self.assetsLayout)

        self.tabWidget.addTab(self.assetsTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        '''***** Status Bar *****'''''
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setEnabled(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate

        '''***** Main Window *****'''
        MainWindow.setWindowTitle(_translate("MainWindow", "Project Management Tool"))

        '''***** Projects Tab *****'''
        # New Project
        self.newProjectBox.setTitle(_translate("MainWindow", "New Project"))
        self.newProjectLabel.setText(_translate("MainWindow", "Name:"))
        self.newProjectField.setPlaceholderText(_translate("MainWindow", "ProjectName"))
        self.createProject.setText(_translate("MainWindow", "Create Project"))

        # Existing Project
        self.existingProjectBox.setTitle(_translate("MainWindow", "Existing Projects"))
        self.deleteSelectedButton.setText(_translate("MainWindow", "Delete Selected"))
        self.renameSelectedField.setPlaceholderText(_translate("MainWindow", "NewProjectName"))
        self.renameSelectedButton.setText(_translate("MainWindow", "Rename Selected"))
        self.newFolderField.setPlaceholderText(_translate("MainWindow", "NewFolder"))
        self.newFolderButton.setText(_translate("MainWindow", "Create New Folder"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.projectsTab), _translate("MainWindow", "Projects"))

        '''***** Asset Tab *****'''
        # Directory
        self.directoryBox.setTitle(_translate("MainWindow", "Directory:"))

        # New Asset
        self.newAssetBox.setTitle(_translate("MainWindow", "New Asset:"))
        self.assetTypeLabel.setText(_translate("MainWindow", "Asset Type:"))
        self.newAssetType.setItemText(0, _translate("MainWindow", "Model"))
        self.newAssetType.setItemText(1, _translate("MainWindow", "Rig"))
        self.newAssetType.setItemText(2, _translate("MainWindow", "Animation"))
        self.assetAppLabel.setText(_translate("MainWindow", "Asset Application:"))
        self.newAssetApp.setItemText(0, _translate("MainWindow", "Maya"))
        self.newAssetApp.setItemText(1, _translate("MainWindow", "Zbrush"))
        self.newAssetApp.setItemText(2, _translate("MainWindow", "Houdini"))
        self.newAssetNameField.setPlaceholderText(_translate("MainWindow", "AssetName"))
        self.createAsset.setText(_translate("MainWindow", "Create Asset"))

        # Selected Assets
        self.selectedAssetBox.setTitle(_translate("MainWindow", "Selected Asset(s):"))
        self.openAssetButton.setText(_translate("MainWindow", "Open"))
        self.renameAssetField.setPlaceholderText(_translate("MainWindow", "NewAssetName"))
        self.renameAssetButton.setText(_translate("MainWindow", "Rename"))
        self.deleteAssetButton.setText(_translate("MainWindow", "Delete"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.assetsTab), _translate("MainWindow", "Assets"))

    def getPaths(self, treeView):
        paths = []

        # get selected indexes
        indexes = [item for item in treeView.selectedIndexes() if item.column() == 0]

        if len(indexes)>0:
            # get the file path per index
            for index in indexes:
                paths.append(self.model.filePath(index))
                # print(self.model.filePath(index))
                # print(index)
        else:
            paths.append(self.model.filePath(self.projectDirectory.rootIndex()))
        return paths

    def newProjectClicked(self, *args):
        # create new project
        rootDir = self.model.filePath(self.projectDirectory.rootIndex())
        projectName = self.newProjectField.text()
        path = os.path.join(rootDir, projectName)

        Project(path)

        #clear
        self.newProjectField.clear()

    def deleteFolderClicked(self, *args):
        # function for deleting paths
        for path in self.getPaths(self.projectDirectory):
            Folder(path).delete()
    
    def renameFolderClicked(self, *args):
        # rename folder

        # get selected folders
        folders = self.getPaths(self.projectDirectory)

        # do this for each folder selected
        for index, path in enumerate(folders):
            # generate new name
            newName = self.renameSelectedField.text()

            # if renaming multiple folders, number them
            if len(folders) > 1:
                newName += str(index + 1)

            # rename
            Folder(path).rename(newName)
        
        # clear the field
        self.renameSelectedField.clear()

    def newFolderClicked(self, *args):
        # create new folder

        # get new folder name
        name = self.newFolderField.text()

        # get path
        path = self.getPaths(self.projectDirectory)[0]

        # make new folder- automatically makes tools,temp folders with config file
        Folder(os.path.join(path,name))

        # Clear the field
        self.newFolderField.clear()

    def newAssetClicked(self, *args):
        # get new asset name
        name = self.newAssetNameField.text()

        # get new asset type
        assetType = self.newAssetType.currentText()

        assetApp = self.newAssetApp.currentText()
       
       #make temp asset from file type/filepath

        path = self.getPaths(self.assetDirectory)[0]

        Asset(os.path.join(path,name), assetApp, assetType)

    def openAssetClicked(self, *args):
        assets = self.getPaths(self.assetDirectory)
        for asset in assets:
            # subprocess.Popen("%s %s" % ("C:\\Program Files\\Autodesk\\Maya2020\\bin\\maya.exe", asset))
            Asset(asset).open()


    def renameAssetClicked(self, *args):
        # rename asset
        assets = self.getPaths(self.assetDirectory)

        for index, path in enumerate(assets):
            filetype = os.path.splitext(path)[1]
            newName = self.renameAssetField.text()
            # parentPath = os.pardir(Path(path))
            parentPath = Path(path).parent
            newPath = os.path.join(parentPath, newName)
            #if renaming multiple folders, number them
            if len(assets) > 1:
                newPath += str(index + 1)

            newPath += filetype

            # os.rename(path, newPath)
            Asset(path).rename(newPath)
        
        # clear the field
        self.renameAssetField.clear()

    def deleteAssetClicked(self, *args):
        for path in self.getPaths(self.assetDirectory):
            Asset(path).delete()



# check for root folder
Folder("C:\\PMTTemp")

# Launch GUI
if __name__ == "__main__":
    import sys
    # Launch GUI
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
