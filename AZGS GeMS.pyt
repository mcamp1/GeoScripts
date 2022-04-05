# -*- coding: utf-8 -*-

import arcpy
import random
from arcpy.arcobjects.arcobjects import Value
from arcpy.management import ImportXMLWorkspaceDocument

# Prepopulate parameters for easy testing
prepopulate = True
baseFolder = r'C:\GeoScripts'

# Input prepopulate paths
usgsGdbvalue = r'{}\Input\usgsGems.gdb'.format(baseFolder)
symbologyCsvvalue = r'{}\Input\cfsymbology.csv'.format(baseFolder)
cfARvalue = r'{}\Input\ContactsFaultsAttributeRules.csv'.format(baseFolder)
dmuARvalue = r'{}\Input\DmuAttributeRules.csv'.format(baseFolder)

dsARvalue = r'{}\Input\DataSourceAttributeRules.csv'.format(baseFolder)
mupARvalue = r'{}\Input\MupAttributeRules.csv'.format(baseFolder)
stationARvalue = r'{}\Input\StationsAttributeRules.csv'.format(baseFolder)
opARvalue = r'{}\Input\OrientationPointsAttributeRules.csv'.format(baseFolder)

authFilevalue = r"{}\Input\keycodes".format(baseFolder)
importXMLvalue = r"{}\Input\WorkspaceTemplate.xml".format(baseFolder)

# Output prepopulate paths
outPathXmlvalue = r'{}\Output\WorkspaceTemplate.xml'.format(baseFolder)
sdeOutputPathvalue = r"{}\Output\\".format(baseFolder)

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
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
            displayName="Symbology CSV",
            name="symbologyCsv",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # CF Attribute Rules
        cfAttributeRules = arcpy.Parameter(
            displayName="ContactsAndFaults Attribute Rules",
            name="cfAttributeRules",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # DMU Attribute Rules
        dmuAttributeRules = arcpy.Parameter(
            displayName="DescriptionOfMapUnits Attribute Rules",
            name="dmuAttributeRules",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # Data Sources Attribute Rules
        dsAttributeRules = arcpy.Parameter(
            displayName="DataSources Attribute Rules",
            name="dsAttributeRules",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # Map Unit Polys Attribute Rules
        mupAttributeRules = arcpy.Parameter(
            displayName="MapUnitPolys Attribute Rules",
            name="mupAttributeRules",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # Stations Attribute Rules
        stationsAttributeRules = arcpy.Parameter(
            displayName="Stations Attribute Rules",
            name="stationsAttributeRules",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input",
        )

        # OrientationPoints Attribute Rules
        opAttributeRules = arcpy.Parameter(
            displayName="OrientationPoints Attribute Rules",
            name="opAttributeRules",
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

        usgsGdb.filter.list = ["LocalDatabase"]
        symbologyCsv.filter.list = ['csv']
        cfAttributeRules.filter.list = ['csv']
        dmuAttributeRules.filter.list = ['csv']
        dsAttributeRules.filter.list = ['csv']
        mupAttributeRules.filter.list = ['csv']
        stationsAttributeRules.filter.list = ['csv']
        opAttributeRules.filter.list = ['csv']
        outPathXml.filter.list = ['xml']

        if (prepopulate):
            usgsGdb.value = usgsGdbvalue 
            symbologyCsv.value = symbologyCsvvalue
            cfAttributeRules.value = cfARvalue
            dmuAttributeRules.value = dmuARvalue
            dsAttributeRules.value = dsARvalue
            mupAttributeRules.value = mupARvalue
            stationsAttributeRules.value = stationARvalue
            opAttributeRules.value = opARvalue
            outPathXml.value = outPathXmlvalue

        params = [usgsGdb, symbologyCsv, cfAttributeRules, dmuAttributeRules, dsAttributeRules, mupAttributeRules, stationsAttributeRules, opAttributeRules, outPathXml]

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
        cfAttributeRules = parameters[2].valueAsText
        dmuAttributeRules = parameters[3].valueAsText
        dsAttributeRules = parameters[4].valueAsText
        mupAttributeRules = parameters[5].valueAsText
        stationsAttributeRules = parameters[6].valueAsText
        opAttributeRules = parameters[7].valueAsText
        outPathXml = parameters[8].valueAsText

        arcpy.SetProgressor("default")

        # Get the current project
        aprx = arcpy.mp.ArcGISProject("CURRENT") 

        # Temp gdb will be created in the project folder
        tmpGDB = aprx.homeFolder + "\\" + "tempXmlExport.gdb"

        arcpy.SetProgressorLabel("Making a temporary copy of the geodatabase.")

        # Make a temp copy of the USGS gdb
        arcpy.Copy_management(usgsGdb, tmpGDB)

        arcpy.env.workspace = tmpGDB
        
        ####### Make updates to the temp gdb #######

        # Select the cf table
        cfTable = arcpy.ListFeatureClasses('ContactsAndFaults', feature_dataset = 'GeologicMap')

        # Add Global ID to contacts and faults
        arcpy.SetProgressorLabel("Adding Global ID to Contacts and Faults.")
        arcpy.AddGlobalIDs_management(cfTable)

        ##################
        # Add CF Domains #
        ##################

        ### IsConcealed Domain ####
        arcpy.SetProgressorLabel("Creating concealed domain for Contacts and Faults.")

        # Create domain
        arcpy.CreateDomain_management(tmpGDB, "IsConcealedDomain", "Y/N", "TEXT", "CODED")

        # Domain dictionary
        domDict = {"Y":"Y", "N":"N"}

        # Add types to the domain
        for code in domDict:        
            arcpy.AddCodedValueToDomain_management(tmpGDB, "IsConcealedDomain", code, domDict[code])

        # Constrain IsConcealed field to the domain
        arcpy.AssignDomainToField_management('ContactsAndFaults', "IsConcealed", "IsConcealedDomain")

        ### Confidence Domain ####
        arcpy.SetProgressorLabel("Creating confidence domain for Contacts and Faults.")

        # Create domain
        arcpy.CreateDomain_management(tmpGDB, "ConfidenceDomain", "Low, Medium, High", "TEXT", "CODED")

        # Domain dictionary
        domDict = {"Low":"Low", "Medium":"Medium", "High":"High"}

        # Add types to the domain
        for code in domDict:        
            arcpy.AddCodedValueToDomain_management(tmpGDB, "ConfidenceDomain", code, domDict[code])

        # Constrain IdentityConfidence field to the domain
        arcpy.AssignDomainToField_management('ContactsAndFaults', "IdentityConfidence", "ConfidenceDomain")

        # Constrain ExistenceConfidence field to the domain
        arcpy.AssignDomainToField_management('ContactsAndFaults', "ExistenceConfidence", "ConfidenceDomain")

        ### LocationConfidenceMeters Domain ####
        arcpy.SetProgressorLabel("Creating location confidence domain for Contacts and Faults.")

        # Create Domain
        arcpy.CreateDomain_management(tmpGDB, "LocationConfidenceDomain", "Location Confidence Meters", "FLOAT", "CODED")

        # Domain dictionary
        domDict = {10:10, 25:25, 50:50, 100:100, 250:250}

        # Add types to the domain
        for code in domDict:        
            arcpy.AddCodedValueToDomain_management(tmpGDB, "LocationConfidenceDomain", code, domDict[code])

        # Constrain LocationConfidenceMeters field to the domain
        arcpy.AssignDomainToField_management('ContactsAndFaults', "LocationConfidenceMeters", "LocationConfidenceDomain")

        # Add CF attribute rules
        if cfAttributeRules:
            arcpy.SetProgressorLabel("Importing Contacts and Faults Attribute Rules.")
            arcpy.ImportAttributeRules_management(cfTable[0], cfAttributeRules)

        # Select the DMU table
        dmuTable = arcpy.ListTables("DescriptionOfMapUnits")[0]
 
        if dmuAttributeRules:
            # Add Global ID to DMU
            arcpy.SetProgressorLabel("Adding Global ID to DMU table.")
            arcpy.AddGlobalIDs_management(dmuTable)

            # Import Attribute Rules for DMU
            arcpy.SetProgressorLabel("Importing DMU Attribute Rules.")
            arcpy.ImportAttributeRules_management("DescriptionOfMapUnits", dmuAttributeRules)

        # Add custom fields to DMU
        arcpy.SetProgressorLabel("Adding custom fields to DMU.")
        arcpy.AddField_management(dmuTable, "RelativeAge", "TEXT")
        arcpy.AddField_management(dmuTable, "HexColor", "TEXT")
            
        arcpy.SetProgressorLabel("Creating ParagraphStyle domain for DMU table.")

        # Create ParagraphStyle domain
        arcpy.CreateDomain_management(tmpGDB, "ParagraphStyleDomain", "Type of DMU", "TEXT", "CODED")

        # ParagraphStyle domain dictionary
        domDict = {"Heading":"Heading", "Standard":"Standard"}

        # Add dmu types to the domain
        for code in domDict:        
            arcpy.AddCodedValueToDomain_management(tmpGDB, "ParagraphStyleDomain", code, domDict[code])

        # Constrain ParagraphStyle field to the domain
        arcpy.AssignDomainToField_management(dmuTable, "ParagraphStyle", "ParagraphStyleDomain")

        # Add Data Sources Global ID and Rules
        if dsAttributeRules:
            # Select the Data Sources tables
            dsTable = arcpy.ListTables("DataSources")[0]

            # Add Global ID to Data Sources
            arcpy.SetProgressorLabel("Adding Global ID to Data Sources table.")
            arcpy.AddGlobalIDs_management(dsTable)

            # Import Attribute Rules for Data Sources
            arcpy.SetProgressorLabel("Importing Data Sources Attribute Rules.")
            arcpy.ImportAttributeRules_management("DataSources", dsAttributeRules)

        # Add MUP Global ID and Rules
        if mupAttributeRules:
            # Select the tables
            mupTable = arcpy.ListFeatureClasses('MapUnitPolys', feature_dataset = 'GeologicMap')

            # Add Global ID
            arcpy.SetProgressorLabel("Adding Global ID to Map Unit Polys table.")
            arcpy.AddGlobalIDs_management(mupTable)

            # Import Attribute Rules
            arcpy.SetProgressorLabel("Importing Map Unit Polys Attribute Rules.")
            arcpy.ImportAttributeRules_management("MapUnitPolys", mupAttributeRules)

        # Add Station Global ID and Rules
        if stationsAttributeRules:
            # Select the tables
            stationTable = arcpy.ListFeatureClasses('Stations', feature_dataset = 'GeologicMap')

            # Add Global ID
            arcpy.SetProgressorLabel("Adding Global ID to Stations table.")
            arcpy.AddGlobalIDs_management(stationTable)

            # Import Attribute Rules
            arcpy.SetProgressorLabel("Importing Stations Attribute Rules.")
            arcpy.ImportAttributeRules_management("Stations", stationsAttributeRules)

        # Add OrientationPoints Global ID and Rules
        if opAttributeRules:
            # Select the tables
            opTable = arcpy.ListFeatureClasses('OrientationPoints', feature_dataset = 'GeologicMap')

            # Add Global ID
            arcpy.SetProgressorLabel("Adding Global ID to OrientationPoints table.")
            arcpy.AddGlobalIDs_management(opTable)

            # Import Attribute Rules
            arcpy.SetProgressorLabel("Importing OrientationPoints Attribute Rules.")
            arcpy.ImportAttributeRules_management("OrientationPoints", opAttributeRules)

        # Add contacts and faults symbology table
        if symbologyCsv:
            arcpy.SetProgressorLabel("Creating cfsymbology table.")
            arcpy.TableToTable_conversion(symbologyCsv, tmpGDB, "cfsymbology")

        # Export XML workspace  
        arcpy.SetProgressorLabel("Exporting geodatabase contents.")

        arcpy.ExportXMLWorkspaceDocument_management(tmpGDB, outPathXml)

        arcpy.SetProgressorLabel("Removing temporary geodatabase.")

        # Delete the temp gbd
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
        dbPlatform.filter.list = ["PostgreSQL", "SQL Server"]
        dbPlatform.value = "PostgreSQL"

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
            parameterType="Required",
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

        importXML.filter.list = ['xml']

        # SDE Export Folder
        sdeExportFolder= arcpy.Parameter(
            displayName="SDE Export Folder",
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
            parameterType="Required",
            direction="Input",
            multiValue=True
        )

        parameters = [dbPlatform, instance, database, dbAdmin, dbAdminPwd,
         gdbadminpwd, authFile, importXML, sdeExportFolder, versions]

        if (prepopulate):
            parameters[1].value = "localhost"
            parameters[2].value = "database{}".format(random.randint(0,999))
            parameters[3].value = "postgres"
            parameters[4].value = "Password12345"
            parameters[5].value = "password"
            parameters[6].value = authFilevalue
            parameters[7].value = importXMLvalue
            parameters[8].value = sdeOutputPathvalue
            parameters[9].values = ['LB', 'AZ', 'MC'] 

        return parameters
        

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        # prepopulate values
        if (prepopulate and parameters[0].valueAsText == 'SQL Server'):
            parameters[1].value = "localhost\SQLEXPRESS"
            parameters[3].value = ""      
            parameters[4].value = "" 
            parameters[5].value = "Password12345" 
            
        elif (prepopulate and parameters[0].valueAsText == 'PostgreSQL'):
            parameters[1].value = "localhost"
            parameters[3].value = "postgres"      
            parameters[4].value = "Password12345" 
            parameters[5].value = "password" 

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
            createGDB_result = arcpy.CreateEnterpriseGeodatabase_management(
                database_platform="SQL_SERVER",
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
            createGDB_result = arcpy.CreateEnterpriseGeodatabase_management(
                database_platform="POSTGRESQL",
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
            gdbWorkspace = arcpy.CreateDatabaseConnection_management(
                sdeOutputPath,
                database + "_geomapmaker.sde",
                database_platform="SQL_SERVER",
                instance=instance,
                account_authentication="OPERATING_SYSTEM_AUTH",
                username="",
                password="",
                database=database,
            )

        elif (dbPlatform == "PostgreSQL"):    
            gdbWorkspace = arcpy.CreateDatabaseConnection_management(
                out_folder_path=sdeOutputPath,
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
        self.description = "Import Geomapmaker Enterprise Geodatabase"
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

        sde.filter.list = ["RemoteDatabase"]

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

        # List versions when a SDE is selected
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
            arcpy.AddError("Map tab must be active to import GEMS geodatabase.")
            return

        # Set SDE filea s the default gdb
        aprx.defaultGeodatabase = sde

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

        # Add feature classes to map
        for dataset in arcpy.ListDatasets():
            for feature in arcpy.ListFeatureClasses(feature_dataset=dataset):
                arcpy.SetProgressorLabel("Adding {} to map..".format(feature))
                activeMap.addDataFromPath("{}\\{}\\{}".format(sde, dataset, feature))

        arcpy.SetProgressor("Adding tables to map..")

        # Add tables to map
        for table in arcpy.ListTables():
            arcpy.SetProgressorLabel("Adding {} to map..".format(table))
            activeMap.addDataFromPath("{}\\{}".format(sde, table))
        
        arcpy.SetProgressorLabel("Setting versions as {}..".format(version))

        # This feels hacky and heavy-handed, but there is a bug when calling Change Version in the ArcPy tool
        # https://support.esri.com/en/bugs/nimbus/QlVHLTAwMDExNDAxNw==

        # Find the current version
        oldVersion = arcpy.Describe(sde).connectionProperties.version

        find_dict = {'connection_info': {'version': oldVersion}}
        replace_dict = {'connection_info': {'version': version}}

        # Change connection prop's version
        aprx.updateConnectionProperties(find_dict, replace_dict)

        arcpy.ResetProgressor()

        return
