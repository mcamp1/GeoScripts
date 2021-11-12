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
attRulesCsvvalue = r'C:\GeoScripts\Input\attributeRules.csv'
outPathXmlvalue = r'C:\GeoScripts\Output\Template.xml'

# Create Geodatabase test paths
instance = '127.0.0.1'
authFilevalue = r"C:\GeoScripts\Input\keycodes"
importXMLvalue = r"C:\GeoScripts\Input\GEMS_IMPORT.xml"
sdeOutputPathvalue = r"C:\GeoScripts\Output\\"
versions = ['LB', 'AZ', 'MC']


# ImportGeodatabase

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CreateXmlWorkspace, CreateGeodatabase, ImportGeodatabase]

class CreateXmlWorkspace(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Geomapmaker XML Workspace"
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
            name="symbologyCsv",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # DMU Attribute Rules
        dmuAttributeRules = arcpy.Parameter(
            displayName="DMU Attribute Rules",
            name="dmuAttributeRules",
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
        dmuAttributeRules.filter.list = ['csv']
        outPathXml.filter.list = ['xml']

        if (testing):
            usgsGdb.value = usgsGdbvalue 
            symbologyCsv.value = symbologyCsvvalue
            dmuAttributeRules.value = attRulesCsvvalue
            outPathXml.value = outPathXmlvalue

        params = [usgsGdb, symbologyCsv, dmuAttributeRules, outPathXml]

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
        dmuAttributeRules = parameters[2].valueAsText
        outPathXml = parameters[3].valueAsText

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT") 

        # Temp gdb will be created in the project folder
        tmpGDB = aprx.homeFolder + "\\" + "tempXmlExport.gdb"

        arcpy.SetProgressorLabel("Making a temporary copy of the geodatabase.")

        # Make a temp copy of the USGS gdb
        arcpy.Copy_management(usgsGdb, tmpGDB)

        arcpy.env.workspace = tmpGDB

        # Make updates to the temp gdb

        arcpy.SetProgressorLabel("Creating cfsymbology table.")

        arcpy.TableToTable_conversion(symbologyCsv, tmpGDB, "cfsymbology")

        arcpy.SetProgressorLabel("Importing DMU Attribute Rules.")

        arcpy.ImportAttributeRules_management("DescriptionOfMapUnits", dmuAttributeRules)

        # Export XML workspace  
        arcpy.SetProgressorLabel("Exporting geodatabase contents.")

        arcpy.ExportXMLWorkspaceDocument_management(tmpGDB, outPathXml )

        arcpy.SetProgressorLabel("Removing temporary geodatabase.")

        arcpy.Delete_management(tmpGDB)

        arcpy.ResetProgressor()

        return


class CreateGeodatabase(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Geomapmaker Enterprise Geodatabase"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        dbPlatform = arcpy.Parameter(
            displayName="Database Platform",
            name="dbPlatform",
            datatype="String",
            parameterType="Required",
            direction="Input",
        )

        dbPlatform.filter.type = "ValueList"
        dbPlatform.filter.list = ["SQL Server", "PostgreSQL"]
        dbPlatform.value = "SQL Server"

        # Instance
        instance = arcpy.Parameter(
            displayName="Instance",
            name="instance",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        # Database Administrator
        database = arcpy.Parameter(
            displayName="Database Name",
            name="datagase",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        # Database Administrator
        dbAdmin = arcpy.Parameter(
            displayName="Database Administrator",
            name="dbadmin",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
        )

        # Database Administrator Password
        dbAdminPwd = arcpy.Parameter(
            displayName="Database Administrator Password",
            name="dbadminpwd",
            datatype="GPStringHidden",
            parameterType="Optional",
            direction="Input",
            enabled=True
        )

        # Sde Administrator Password
        gdbadminpwd = arcpy.Parameter(
            displayName="Sde Password",
            name="gdbadminpwd",
            datatype="GPStringHidden",
            parameterType="Optional",
            direction="Input",
            enabled=True
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

        params = [dbPlatform, instance, database, dbAdmin,
                  dbAdminPwd, gdbadminpwd, authFile, importXML, sdeOutputPath, versions]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        if (testing and parameters[0].valueAsText == 'SQL Server'):
            parameters[1].value = "localhost\SQLEXPRESS"
            parameters[2].value = "sqlserver{}".format(random.randint(0,999))
            parameters[3].value = ""      
            parameters[3].enabled = False  
            parameters[4].value = "" 
            parameters[4].enabled = False      
            parameters[5].value = "Password12345"
            parameters[6].value = authFilevalue
            parameters[7].value = importXMLvalue
            parameters[8].value = sdeOutputPathvalue      
            parameters[9].values = versions      


        elif (testing and parameters[0].valueAsText == 'PostgreSQL'):
            parameters[1].value = instance
            parameters[2].value = "postgresql{}".format(random.randint(0,999))
            parameters[3].enabled = True
            parameters[3].value = "postgres"
            parameters[4].enabled = True
            parameters[4].value = "Password12345"
            parameters[5].value = "password"
            parameters[6].value = authFilevalue
            parameters[7].value = importXMLvalue
            parameters[8].value = sdeOutputPathvalue      
            parameters[9].values = versions  
            parameters[4].value = "Password12345"


        else:
            parameters[1].value = ""
            parameters[2].value = ""
            parameters[3].value = ""
            parameters[3].enabled = True
            parameters[4].value = ""
            parameters[4].enabled = True
            parameters[5].value = ""
            parameters[6].value = ""
            parameters[7].value = ""
            parameters[8].value = ""
            parameters[9].values = []

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        dbPlatform = parameters[0].valueAsText
        instance = parameters[1].valueAsText
        database = parameters[2].valueAsText
        dbAdmin = parameters[3].valueAsText
        dbAdminPwd = parameters[4].valueAsText
        gdbadminpwd = parameters[5].valueAsText
        authFile = parameters[6].valueAsText
        importXML = parameters[7].valueAsText
        sdeOutputPath = parameters[8].valueAsText
        versions = parameters[9].values

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")    

        # Start progressor
        arcpy.SetProgressorLabel("Creating Enterprise Geodatabase..")

        if (dbPlatform == "SQL Server"):
            createGDB_result = arcpy.CreateEnterpriseGeodatabase_management(database_platform="SQL_SERVER",
                                                                            instance_name=instance,
                                                                            database_name=database,
                                                                            account_authentication="OPERATING_SYSTEM_AUTH",
                                                                            database_admin="",
                                                                            database_admin_password="",
                                                                            sde_schema="SDE_SCHEMA",
                                                                            gdb_admin_name="sde",
                                                                            gdb_admin_password=gdbadminpwd,
                                                                            authorization_file=authFile
                                                                        )


        elif (dbPlatform == "PostgreSQL"):
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
            arcpy.ResetProgressor()
            arcpy.AddError("Enterprise Geodatabase Creation Failed")
            return

        arcpy.SetProgressorLabel("Creating Database Connection..")

        if (dbPlatform == "SQL Server"):
            gdbWorkspace = arcpy.CreateDatabaseConnection_management(sdeOutputPath,
                                                  database + "_geomapmaker.sde",
                                                  database_platform="SQL_SERVER",
                                                  instance=instance,
                                                  account_authentication="OPERATING_SYSTEM_AUTH",
                                                  username="",
                                                  password="",
                                                  database=database,
                                                  )
        elif (dbPlatform == "PostgreSQL"):    
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

        # Store the current workspace
        currentWorskpace = arcpy.env.workspace

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

        # Reset the workspace
        arcpy.env.workspace = currentWorskpace

        arcpy.ResetProgressor()

        return

class ImportGeodatabase(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Import Geomapmaker Enterprise Geodatabase"
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

        params = [sde, version]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        sde = parameters[0].valueAsText

        if sde:
            # SDE's ListVersions() as options
            parameters[1].filter.list = arcpy.ListVersions(sde)
        else:
            # Empty options
            parameters[1].filter.list = []

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

        sde = parameters[0].valueAsText
        version = parameters[1].valueAsText

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        
        # Get the current active map
        activeMap = aprx.activeMap

        # Check if there was an active map
        if not activeMap:
            arcpy.ResetProgressor()
            arcpy.AddError("No active map.")
            return

        arcpy.SetProgressorLabel("Removing layers from map..")

        # Remove all non-basemap layers 
        for layer in activeMap.listLayers():
            if not layer.isBasemapLayer: 
                activeMap.removeLayer(layer)

        arcpy.SetProgressorLabel("Removing tables from map..")

        # Remove all tables
        for table in activeMap.listTables():
            activeMap.removeTable(table)

        arcpy.env.workspace = sde

        arcpy.SetProgressorLabel("Adding features to map..")

        # Add feature classes to map
        for dataset in arcpy.ListDatasets():
            for feature in arcpy.ListFeatureClasses(feature_dataset=dataset):
                activeMap.addDataFromPath("{}\\{}\\{}".format(sde, dataset, feature))

        arcpy.SetProgressor("Adding tables to map..")

        # Add tables to map
        for table in arcpy.ListTables():
            activeMap.addDataFromPath("{}\\{}".format(sde, table))
        
        arcpy.SetProgressorLabel("Setting versions as {}..".format(version))

        # This feels a little hacky and heavy-handed,
        # but theres a when calling Change Version with the ArcPy tool
        # https://support.esri.com/en/bugs/nimbus/QlVHLTAwMDExNDAxNw==

        # Find the current version
        oldVersion = arcpy.Describe(sde).connectionProperties.version

        find_dict = {'connection_info': {'version': oldVersion}}
        replace_dict = {'connection_info': {'version': version}}

        # Change connection prop's version
        aprx.updateConnectionProperties(find_dict, replace_dict)

        arcpy.ResetProgressor()

        return
