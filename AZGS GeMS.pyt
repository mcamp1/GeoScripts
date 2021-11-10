# -*- coding: utf-8 -*-

import arcpy
from arcpy.arcobjects.arcobjects import Value
from arcpy.management import ImportXMLWorkspaceDocument

# Prepopulate parameters for easy testing
testing = True



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
        in_data = arcpy.Parameter(
            displayName="USGS GeMS Geodatabase",
            name="in_data",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
 
        # CF Symbology CSV
        in_cfcsv = arcpy.Parameter(
            displayName="CF Symbology CSV",
            name="in_cfcsv",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # Output XML workspace document
        out_file = arcpy.Parameter(
            displayName="XML Export Location",
            name="out_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Output",
        )

        in_cfcsv.filter.list = ['csv']
        out_file.filter.list = ['xml']

        if (testing):
            in_data.value = r'C:\Users\mcamp\\Desktop\ABCD\TemplateGDB.gdb'
            in_cfcsv.value = r''
            out_file.value = r'C:\Users\mcamp\Desktop\ABCD\test.xml'

        params = [in_data, in_cfcsv, out_file]

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

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT") 

        # Temp gdb will be created in the project folder
        tmpGDB = aprx.homeFolder + "\\" + "tempXmlExport.gdb"

        arcpy.SetProgressorLabel("Making a temporary copy of the geodatabase.")

        # Make a temp copy of the USGS gdb
        arcpy.Copy_management(parameters[0].valueAsText, tmpGDB)

        arcpy.env.workspace = tmpGDB

        ### Make updates to the temp gdb

        arcpy.SetProgressorLabel("Creating cfsymbology table.")

        #arcpy.CreateTable_management(tmpGDB, "cfsymbology")

        #arcpy.AddField_management("cfsymbology", "key", "TEXT")
        #arcpy.AddField_management("cfsymbology", "description", "TEXT")
        #arcpy.AddField_management("cfsymbology", "symbol", "TEXT", field_length=500)

        #cursor = arcpy.da.InsertCursor('cfsymbology', ['key', 'description', 'symbol'])

        # cursor.insertRow([ '1.1.1', 'Contact—Identity and existence certain, location accurate', '{"type":"CIMLineSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"colorLocked":true,"primitiveName":"1.0","capStyle":"Butt","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.43086614173228349,"color":{"type":"CIMCMYKColor","values":[0,0,0,100,100]}}]}' ])

        # arcpy.MakeTableView_management(r'C:\Users\mcamp\Desktop\CfSymbology.csv', "CfSymbologyTableView")

        # arcpy.TableToTable_conversion("CfSymbologyTableView", tmpGDB, "cfsymbology")

        #arcpy.da.SearchCursor()

        # Export XML workspace  
        arcpy.SetProgressorLabel("Exporting geodatabase contents.")

        arcpy.ExportXMLWorkspaceDocument_management(tmpGDB, parameters[1].valueAsText )

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
            database.value = "database1"
            dbAdmin.value = "postgres"
            dbAdminPwd.value = "password"
            gdbadminpwd.value = "password"
            authFile.value = r"C:\geomapmaker-stuff\keycodes"
            importXML.value = r"C:\geomapmaker-stuff\GEMS_IMPORT.xml"
            versions.values = ["MC", "LB", "AZ"]

        params = [instance, database, dbAdmin,
                  dbAdminPwd, gdbadminpwd, authFile, importXML, versions]

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

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")    

        # Start progressor
        arcpy.SetProgressorLabel("Creating Enterprise Geodatabase..")

        # Create Enterprise Geodatabase
        createGDB_result = arcpy.CreateEnterpriseGeodatabase_management(database_platform="POSTGRESQL",
                                                                        instance_name=parameters[0].valueAsText,
                                                                        database_name=parameters[1].valueAsText,
                                                                        account_authentication="DATABASE_AUTH",
                                                                        database_admin=parameters[2].valueAsText,
                                                                        database_admin_password=parameters[3].valueAsText,
                                                                        gdb_admin_name="sde",
                                                                        gdb_admin_password=parameters[4].valueAsText,
                                                                        authorization_file=parameters[5].valueAsText
                                                                        )

        # Stop execution if CreateEnterpriseGeodatabase fails
        if createGDB_result == False:
            arcpy.AddError("Enterprise Geodatabase Creation Failed")
            return

        arcpy.SetProgressorLabel("Creating Database Connection..")

        # Create Database Connection
        gdbWorkspace = arcpy.CreateDatabaseConnection_management(out_folder_path=aprx.homeFolder,
                                                  out_name=parameters[1].valueAsText + "_geomapmaker.sde",
                                                  database_platform="POSTGRESQL",
                                                  instance=parameters[0].valueAsText,
                                                  account_authentication="DATABASE_AUTH",
                                                  username="sde",
                                                  password=parameters[4].valueAsText,
                                                  save_user_pass="SAVE_USERNAME",
                                                  database=parameters[1].valueAsText,
                                                  )

        arcpy.SetProgressorLabel("Importing XML Workspace Document..")

        # Import XML Workspace Document
        updatedGdbWorkspace = arcpy.ImportXMLWorkspaceDocument_management(target_geodatabase=gdbWorkspace, 
                                            in_file=parameters[6].valueAsText, 
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
        for version in parameters[7].values:
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
            database.value = "database1"
            authFile.value = r"C:\geomapmaker-stuff\keycodes"
            importXML.value = r"C:\geomapmaker-stuff\GEMS_IMPORT.xml"
            versions.values = ["MC", "LB", "AZ"]

        params = [instance, database, authFile, importXML, versions]

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
        versions = parameters[4].valueAsText

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
        gdbWorkspace = arcpy.CreateDatabaseConnection_management(aprx.homeFolder,
                                                  database + "_geomapmaker.sde",
                                                  database_platform="SQL_SERVER",
                                                  instance=instance,
                                                  account_authentication="OPERATING_SYSTEM_AUTH",
                                                  username="",password="",
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
        params = None
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
        return