# -*- coding: utf-8 -*-

import arcpy
import random
from arcpy.arcobjects.arcobjects import Value
from arcpy.management import ImportXMLWorkspaceDocument

# Prepopulate parameters for easy testing
testing = True

# CreateXmlWorkspace test paths
usgsGdbvalue = r'C:\GeoScripts\Input\usgsGems.gdb'
symbologyCsvvalue = r'C:\GeoScripts\Input\cfsymbology.csv'
outPathXmlvalue = r'C:\GeoScripts\Output\Template.xml'

# Create Geodatabase test paths
authFilevalue = r"C:\GeoScripts\Input\keycodes"
importXMLvalue = r"C:\GeoScripts\Input\GEMS_IMPORT.xml"
sdeOutputPathvalue = r"C:\GeoScripts\Output\\"

# ImportGeodatabase

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CreateXmlWorkspace, CreatePGGeodatabase, CreateSQLGeodatabase, ImportGeodatabase]

class CreateXmlWorkspace(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create AZGS GeMS XML Workspace"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # USGS GeMS Geodatabase
        usgsGdb = arcpy.Parameter(
            displayName="USGS GeMS Geodatabase",
            name="usgsGdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
 
        # CF Symbology CSV
        symbologyCsv = arcpy.Parameter(
            displayName="CF Symbology CSV",
            name="in_cfcsv",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # Output XML workspace document
        outPathXml = arcpy.Parameter(
            displayName="XML Export Location",
            name="outPathXml",
            datatype="DEFile",
            parameterType="Required",
            direction="Output",
        )

        symbologyCsv.filter.list = ['csv']
        outPathXml.filter.list = ['xml']

        if (testing):
            usgsGdb.value = usgsGdbvalue 
            symbologyCsv.value = symbologyCsvvalue
            outPathXml.value = outPathXmlvalue

        params = [usgsGdb, symbologyCsv, outPathXml]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        usgsGdb = parameters[0].valueAsText
        symbologyCsv = parameters[1].valueAsText
        outPathXml = parameters[2].valueAsText

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT") 

        # Temp gdb will be created in the project folder
        tmpGDB = aprx.homeFolder + "\\" + "tempXmlExport.gdb"

        arcpy.SetProgressorLabel("Making a temporary copy of the geodatabase.")

        # Make a temp copy of the USGS gdb
        arcpy.Copy_management(usgsGdb, tmpGDB)

        arcpy.env.workspace = tmpGDB

        ### Make updates to the temp gdb

        arcpy.SetProgressorLabel("Creating cfsymbology table.")

        arcpy.TableToTable_conversion(symbologyCsv, tmpGDB, "cfsymbology")

        # Export XML workspace  
        arcpy.SetProgressorLabel("Exporting geodatabase contents.")

        arcpy.ExportXMLWorkspaceDocument_management(tmpGDB, outPathXml )

        arcpy.SetProgressorLabel("Removing temporary geodatabase.")

        #arcpy.Delete_management(tmpGDB)

        arcpy.ResetProgressor()

        return

class CreatePGGeodatabase(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create PostgreSQL Enterprise Geodatabase"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        # Instance
        instance = arcpy.Parameter(
            displayName="Instance",
            name="instance",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        # Geodatabase Name
        database = arcpy.Parameter(
            displayName="Geodatabase Name",
            name="database",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        # Database Administrator
        dbAdmin = arcpy.Parameter(
            displayName="Database Administrator",
            name="dbadmin",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        # Database Administrator Password
        dbAdminPwd = arcpy.Parameter(
            displayName="Database Administrator Password",
            name="dbadminpwd",
            datatype="GPStringHidden",
            parameterType="Required",
            direction="Input",
        )

        # Geodatabase Administrator Password
        gdbadminpwd = arcpy.Parameter(
            displayName="Sde Password",
            name="gdbadminpwd",
            datatype="GPStringHidden",
            parameterType="Required",
            direction="Input",
        )

        # Authorization File
        authFile = arcpy.Parameter(
            displayName="Authorization File",
            name="authFile",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )

        # Import XML Workspace
        importXML = arcpy.Parameter(
            displayName="Import XML Workspace",
            name="importXmlFile",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )

        # SDE Output Path
        sdeOutputPath = arcpy.Parameter(
            displayName="SDE Output Path",
            name="sdeOutputPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        )

        # List of Versions
        versions = arcpy.Parameter(
            displayName="Versions",
            name="versions",
            datatype="string",
            parameterType="Optional",
            direction="Input",
            multiValue=True
        )

        if (testing):
            instance.value = "127.0.0.1" 
            database.value = "database{}".format(random.randint(0,999))
            dbAdmin.value = "postgres"
            dbAdminPwd.value =  "password"
            gdbadminpwd.value =  "password"
            authFile.value = authFilevalue
            importXML.value = importXMLvalue
            sdeOutputPath.value = sdeOutputPathvalue
            versions.values = ["MC", "LB", "AZ"]

        params = [instance, database, dbAdmin,
                  dbAdminPwd, gdbadminpwd, authFile, importXML, sdeOutputPath, versions]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        instance = parameters[0].valueAsText
        database = parameters[1].valueAsText
        dbAdmin = parameters[2].valueAsText
        dbAdminPwd = parameters[3].valueAsText
        gdbadminpwd = parameters[4].valueAsText
        authFile = parameters[5].valueAsText
        importXML = parameters[6].valueAsText
        sdeOutputPath = parameters[7].valueAsText
        versions = parameters[8].values

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")    

        # Start progressor
        arcpy.SetProgressorLabel("Creating Enterprise Geodatabase..")

        # Create Enterprise Geodatabase
        createGDB_result = arcpy.CreateEnterpriseGeodatabase_management(database_platform="POSTGRESQL",
                                                                        instance_name=instance,
                                                                        database_name=database,
                                                                        account_authentication="DATABASE_AUTH",
                                                                        database_admin=dbAdmin,
                                                                        database_admin_password=dbAdminPwd,
                                                                        gdb_admin_name="sde",
                                                                        gdb_admin_password=gdbadminpwd,
                                                                        authorization_file=authFile
                                                                        )

        # Stop execution if CreateEnterpriseGeodatabase fails
        if createGDB_result == False:
            arcpy.AddError("Enterprise Geodatabase Creation Failed")
            return

        arcpy.SetProgressorLabel("Creating Database Connection..")

        # Create Database Connection
        gdbWorkspace = arcpy.CreateDatabaseConnection_management(out_folder_path=sdeOutputPath,
                                                  out_name=database + "_geomapmaker.sde",
                                                  database_platform="POSTGRESQL",
                                                  instance=instance,
                                                  account_authentication="DATABASE_AUTH",
                                                  username="sde",
                                                  password=gdbadminpwd,
                                                  save_user_pass="SAVE_USERNAME",
                                                  database=database,
                                                  )

        arcpy.SetProgressorLabel("Importing XML Workspace Document..")

        # Import XML Workspace Document
        updatedGdbWorkspace = arcpy.ImportXMLWorkspaceDocument_management(target_geodatabase=gdbWorkspace, 
                                            in_file=importXML, 
                                            )                                    

        arcpy.SetProgressorLabel("Setting Datasets As Versioned..")

        # Set enterprise gdb as the workspace
        arcpy.env.workspace = updatedGdbWorkspace.getOutput(0)

        # Register datasets as versioned
        for dataset in arcpy.ListDatasets():
            arcpy.SetProgressorLabel("Registering {0} as versioned..".format(dataset))
            arcpy.RegisterAsVersioned_management(dataset)

        # Register tables as versioned
        for table in arcpy.ListTables():
            arcpy.SetProgressorLabel("Registering {0} as versioned..".format(table))
            arcpy.RegisterAsVersioned_management(table)

        arcpy.SetProgressor("Creating Versions..")

        # Create versions
        for version in versions:
            arcpy.SetProgressorLabel("Creating {0} version..".format(version))
            arcpy.CreateVersion_management(arcpy.env.workspace, "sde.DEFAULT", version, "PUBLIC")

        arcpy.ResetProgressor()

        return

class CreateSQLGeodatabase(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create SQL Server Enterprise Geodatabase"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        # Instance
        instance = arcpy.Parameter(
            displayName="Instance",
            name="instance",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        # Geodatabase Name
        database = arcpy.Parameter(
            displayName="Geodatabase Name",
            name="database",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        # Authorization File
        authFile = arcpy.Parameter(
            displayName="Authorization File",
            name="authFile",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )

        # Import XML Workspace
        importXML = arcpy.Parameter(
            displayName="Import XML Workspace",
            name="importXML",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )

        # SDE Output Path
        sdeOutputPath = arcpy.Parameter(
            displayName="SDE Output Path",
            name="sdeOutputPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        )

        # List of Versions
        versions = arcpy.Parameter(
            displayName="Versions",
            name="versions",
            datatype="string",
            parameterType="Optional",
            direction="Input",
            multiValue=True
        )

        if (testing):
            instance.value = "MCAMP-DT\SQLEXPRESS"
            database.value = "database{}".format(random.randint(0,999))
            authFile.value = authFilevalue 
            importXML.value = importXMLvalue 
            sdeOutputPath.value = sdeOutputPathvalue
            versions.values = ["MC", "LB", "AZ"]

        params = [instance, database, authFile, importXML, sdeOutputPath, versions]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        instance = parameters[0].valueAsText
        database = parameters[1].valueAsText
        authFile = parameters[2].valueAsText
        importXML = parameters[3].valueAsText
        sdeOutputPath = parameters[4].valueAsText
        versions = parameters[5].values

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")    

        # Start progressor
        arcpy.SetProgressorLabel("Creating Enterprise Geodatabase..")

        # Create Enterprise Geodatabase
        createGDB_result = arcpy.CreateEnterpriseGeodatabase_management(
            "SQL_SERVER", instance, database, "OPERATING_SYSTEM_AUTH", "", "", 
            "DBO_SCHEMA", "", "", "", authFile) 
                                                              
        # Stop execution if CreateEnterpriseGeodatabase fails
        if createGDB_result == False:
            arcpy.AddError("Enterprise Geodatabase Creation Failed")
            return

        arcpy.SetProgressorLabel("Creating Database Connection..")

        # Create Database Connection
        gdbWorkspace = arcpy.CreateDatabaseConnection_management(sdeOutputPath,
                                                  database + "_geomapmaker.sde",
                                                  database_platform="SQL_SERVER",
                                                  instance=instance,
                                                  account_authentication="OPERATING_SYSTEM_AUTH",
                                                  username="",
                                                  password="",
                                                  database=database,
                                                  )

        arcpy.SetProgressorLabel("Importing XML Workspace Document..")

        # Import XML Workspace Document
        updatedGdbWorkspace = arcpy.ImportXMLWorkspaceDocument_management(target_geodatabase=gdbWorkspace, 
                                            in_file=importXML, 
                                            )                                    

        arcpy.SetProgressorLabel("Setting Datasets As Versioned..")

        # Set enterprise gdb as the workspace
        arcpy.env.workspace = updatedGdbWorkspace.getOutput(0)

        # Register datasets as versioned
        for dataset in arcpy.ListDatasets():
            arcpy.SetProgressorLabel("Registering {0} as versioned..".format(dataset))
            arcpy.RegisterAsVersioned_management(dataset)

        # Register tables as versioned
        for table in arcpy.ListTables():
            arcpy.SetProgressorLabel("Registering {0} as versioned..".format(table))
            arcpy.RegisterAsVersioned_management(table)

        arcpy.SetProgressor("Creating Versions..")

        # Create versions
        for version in versions:
            arcpy.SetProgressorLabel("Creating {0} version..".format(version))
            arcpy.CreateVersion_management(arcpy.env.workspace, "DEFAULT", version, "PUBLIC")

        arcpy.ResetProgressor()

        return

class ImportGeodatabase(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Import GeMS Enterprise Geodatabase"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # SDE File
        sde = arcpy.Parameter(
            displayName="SDE File",
            name="sde",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )

        version = arcpy.Parameter(
            displayName="Version",
            name="version",
            datatype="String",
            parameterType="Required",
            direction="Input",
        )

        version.filter.type = "ValueList"
        #version.filter.list = ["MC", "LB"]

        params = [sde, version]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        parameters[1].filter.list = arcpy.ListVersions(parameters[0].valueAsText)

        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""




        return