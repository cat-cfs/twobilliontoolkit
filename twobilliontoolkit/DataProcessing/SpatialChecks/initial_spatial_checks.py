
"""
Program: initial_gis_checks.py
Description: A tool that performs GIS checks on the raw data
    Outputs: GDB with merged layers
Author: Andrea Nesdoly - Carbon Accouting Team | Canadian Forest Service | Natural Resources Canada
Date: April 25, 2024


Could be useful find CRS based on extent: https://community.esri.com/t5/python-questions/determine-unknown-coordinate-systems-based-on/td-p/637444
"""
#Run ArcPro clone : C:\Users\%USERNAME%\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone\python

import os, sys, re
from glob import glob
import arcpy
import numpy as np
import logging, shutil, time
import psycopg2
from psycopg2 import OperationalError, Error
from datetime import datetime
import pandas as pd
from argparse import ArgumentParser, HelpFormatter
import textwrap
import fiona
from sqlalchemy import create_engine
import configparser

#from post_processing_cleanup import prep_conversion

sys.path.append(r"\\vic-fas1\projects_a\2BT\02_Tools\spatialArcpyUtils")
from Layer import Layer
from LayerCollection import LayerCollection
import arcpy_setup as arcS
import arcpy_helpers as helper


def ingest_db_params(config_path,as_string=True):
    dbType = 'postgresql'
    config = configparser.ConfigParser()
    config.read(config_path)
    
    if as_string:
        connectString = f"postgresql://{config[dbType]['user']}:{config[dbType]['password']}@{config[dbType]['host']}:{config[dbType]['port']}/{config[dbType]['database']}"
        return connectString, config[dbType]['schema']
    else:
        connection_params = {'database':config[dbType]['database'], 
                'user':config[dbType]['user'], 'password':config[dbType]['password'], 
                'host':config[dbType]['host'], 'port':config[dbType]['port']}
        return connection_params, config[dbType]['schema']

def check_geom(collection,rawGDB):
    arcpy.env.workspace = rawGDB
    checkGeom = os.path.join(rawGDB,f'CheckGeomResults_{datetime.today().strftime("%m%d%Y")}')
    arcpy.management.CheckGeometry([c.path for c in collection.layers],checkGeom)
    return checkGeom

def insert_geom_issue(checkTable,config_path):
    checkDF = pd.DataFrame(arcpy.da.TableToNumPyArray(checkTable,[f.name for f in arcpy.ListFields(checkTable)],skip_nulls=False,null_value=np.nan))
    print(f'Check DF: {checkDF}')
    layers_issues = [os.path.basename(p).replace('proj_','') for p in checkDF.CLASS]
    print(layers_issues)

    connectDict,schema = ingest_db_params(config_path,False)

    #updateGeom = [f"""update {schema}.raw_spatial_checks set geometry_issues = True where project_spatial_id = '{lyr}';""" for lyr in layers_issues]
    #run_commands(connectDict,updateGeom,True)

    #update null geometry
    nullGeom = checkDF[checkDF.PROBLEM=='null geometry']
    layers_nulls = [os.path.basename(p).replace('proj_','') for p in nullGeom.CLASS]

    updateNulls = [f"""update {schema}.raw_spatial_checks set null_geometry = True where project_spatial_id = '{lyr}';""" for lyr in layers_nulls]
    run_commands(connectDict,updateNulls,True)

    return layers_issues

def get_layers2process(connectionString,schema):
    engine = create_engine(connectionString)
    theSQL = f"""select project_spatial_id from {schema}.raw_spatial_checks
    where checks_ran = False or checks_ran is null;"""
    with engine.connect() as conn, conn.begin():
        layers = pd.read_sql_table(theSQL,engine)
    return layers


def gather_layers_all(gdb):
    layersFound = helper.check_gdb(gdb,'featureclass')
    layers2process = LayerCollection([Layer(os.path.join(gdb,l)) for l in layersFound])
    return layers2process


def gather_layers(gdb,layers):
    layersFound = helper.check_gdb(gdb,'featureclass')
    layers2process = LayerCollection([Layer(os.path.join(gdb,l)) for l in layersFound if l.replace('proj_','') in layers.project_spatial_id.values])
    return layers2process

def run_commands(conn_params,sql_statements,verbose=False):
    """ Run SQL commands using autocommit. Only the SQL statements that fail will rollback. All others are committed.
    
        conn_params:: dictionary of PostgreSQL connection parameters to pass to psycopg2
        sql_statement:: either a single SQL command string or a variable list of SQL command strings 
    """
    conn = psycopg2.connect(**conn_params)
    conn.autocommit=True
    cur = conn.cursor()
    if isinstance(sql_statements,str):
        sql_statements = [sql_statements]
    for command in sql_statements:
        if verbose:
            print(f'Command passed: {command}')
        try:
            cur.execute(command)
            if verbose:
                print(f"\nSUCCESS! Executed:\n{command}\n")
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"\nERROR! Failed to execute:\n{command}\n{e}\n")

    # Close the cursor and connection
    cur.close()
    conn.close()

def populate_raw_tables(config_path):
    #TODO move to populate scripts
    connectDict,schema = ingest_db_params(config_path,False)
    
    add2_raw_spatial_checks = f"""insert into {schema}.raw_spatial_checks(project_spatial_id) 
    select project_spatial_id from {schema}.raw_data_tracker 
    where in_raw_gdb = True and dropped = False
    on conflict do nothing;"""  
    #TODO test what happends when adding new ids

    run_commands(connectDict,add2_raw_spatial_checks)
    print('Done populating table')

def insert_geom(collection,config_path):
    connectDict,schema = ingest_db_params(config_path,False)

    updateGeom = [f"""update {schema}.raw_spatial_checks set geometry_type = '{str(lyr.geom)}' where project_spatial_id = '{lyr.name.replace('proj_','')}';""" for lyr in collection.layers]
    run_commands(connectDict,updateGeom,True)
    """
    updateGeom = [(f"'{lyr.geom}'",f"{lyr.name}") for lyr in collection.layers]
    print(updateGeom)

    conn = psycopg2.connect(**connectDict)
    conn.autocommit=True
    cur = conn.cursor()
    try:
        cur.executemany(f'update {schema}.raw_spatial_checks set geometry_type = %s where project_spatial_id = %s', updateGeom)
    except psycopg2.Error as e:
        conn.rollback()
        print(f"\nERROR! Failed to execute:\n{command}\n{e}\n")

    # Close the cursor and connection
    cur.close()
    conn.close()"""

def get_projection(collection):
    projectionDict = {}
    for lyr in collection.layers:
        if arcpy.Describe(layer.path).spatialReference.name == 'Unknown':
            projectionDict[lyr.name.replace('proj_','')] = True
        else:
            projectionDict[lyr.name.replace('proj_','')] = False

    return projectionDict


def initial_gis_checks(raw_gdb,db_config=None,csv_tbls=None):
    #populate raw_spatial_checks with project_spatial_ids
    #TODO move to populate script
    if db_config != None:
        populate_raw_tables(db_config)

    connectString,schema = ingest_db_params(db_config)

    # gather layers to process from DB
    layers2process = get_layers2process(connectString,schema)
    print(f'Number of Layers to process: {len(layers2process)}')
    
    #gather layers from gdb
    arcpy.env.workspace = raw_gdb
    arcpy.env.overwriteOutput = False
    inputLayers = gather_layers(raw_gdb,layers2process)
    print(f'Number of layers in GDB to process: {len(inputLayers.layers)}\tto process: {len(layers2process)}')
    if len(layers2process)!=len(inputLayers.layers):
        print(f'Number of layers found in GDB do not match the number to process!')
        #sys.exit(1)

    layerNames = pd.DataFrame({'gdb_layers':[lyr.name for lyr in inputLayers.layers]})
    layerNames.to_csv(r'V:\2BT\04_Program_year\2023_planting\SpatialProcessing\working_anesdoly\layers_raw_gdb_2023_oct152024.csv',index=False)
    print('Done creating layer csv')

    insert_geom(inputLayers,db_config)
    #find geometry issues
    checkTable = check_geom(inputLayers,raw_gdb)
    
    #extract information from the checkgeometry table and insert into DB (add as inforamtion in object/dict)
    #CLASS field has the path to the feature layer impacted with the feature name - just add it to a collection, get the name and set the id for the DB
    insert_geom_issue(checkTable,db_config)

    #set processed to true for all layers
    print('Set all layers found to processed = True')
    connectDict,schema = ingest_db_params(db_config,False)
    updateGeom = [f"""update {schema}.raw_spatial_checks set checks_ran = '{str(lyr.geom)}' where project_spatial_id = '{lyr.name.replace('proj_','')}';""" for lyr in inputLayers.layers]
    run_commands(connectDict,updateGeom,True)

    #determine if there are projection issues (is CRS set)
    #if crs is unknown flag

    #TODO: determine if there are self-overlaps
    
    #TODO: determine if there are slivers


    return None


def initial_gis_checks_csv(raw_gdb, output):
    
    #gather layers from gdb
    arcpy.env.workspace = raw_gdb
    arcpy.env.overwriteOutput = False
    inputLayers = gather_layers_all(raw_gdb)
    print(f'Number of layers in GDB to process: {len(inputLayers.layers)}')

    #find geometry issues
    checkTable = check_geom(inputLayers,raw_gdb)
    df = pd.DataFrame(arcpy.da.TableToNumPyArray(checkTable,'*',skip_nulls=False,null_value=np.nan))
    print(df)

    workingDF = pd.DataFrame({'project_spatial_id':[l.name for l in inputLayers.layers],
                  'geom_type':[l.geom for l in inputLayers.layers],
                  'projection':[arcpy.Describe(l.path).spatialReference.name for l in inputLayers.layers]})
    

    return None

def main_2022(): 
    #parser = ArgumentParser(description="Run Raw Data Spatial Checks")
    #parser.add_argument("raw_gdb", type=os.path.abspath, help="Path to the raw GDB")
    #parser.add_argument('-csv',type=os.path.abspath, default=os.path.join(os.getcwd(),f'raw_data_checks{datetime.today().strftime('%m-%d-%Y')}.csv'), help="Path and csv filesname, with extension, for where to store results of checks as csv")
    #parser.add_argument('-db',type=os.path.abspath, help="Path to .ini file with PostgreSQL DB connection parameters")
    #parser.add_argument('-output_nulls', type=os.path.abspath, default=os.path.join(os.getcwd(),f'raw_data_nulls{datetime.today().strftime('%m-%d-%Y')}.csv'), help="Path and csv filesname, with extension, for where to store the list of null geometries removed. (Default is current directory and nulls.csv)")
    #parser.add_argument("-overwrite", action='store_true', help="Boolean flag to overwrite existing data") 
    #args = parser.parse_args()

    raw_gdb = r"V:\2BT\01_Data\2BT_program_data\2022\RawData\UpdatedData_18Apr2024\raw_data_2022.gdb"
    dbconfig = r'\\vic-fas1\projects_a\2BT\02_Tools\data_management\postgresql_anesdoly.ini'

    initial_gis_checks(raw_gdb, dbconfig)


def main_2023_May082024_DD1(): 

    raw_gdb = r"\\vic-fas1\projects_a\2BT\01_Data\2BT_program_data\2023\RawData\raw_data_2023.gdb"
    dbconfig = r'\\vic-fas1\projects_a\2BT\02_Tools\data_management\postgresql_anesdoly.ini'

    initial_gis_checks(raw_gdb, dbconfig)

def main_2023_May132024_DD2(): 

    raw_gdb = r"\\vic-fas1\projects_a\2BT\01_Data\2BT_program_data\2023\RawData\raw_data_2023.gdb"
    dbconfig = r'\\vic-fas1\projects_a\2BT\02_Tools\data_management\postgresql_anesdoly.ini'

    initial_gis_checks(raw_gdb, dbconfig)

def main_2023_Aug82024_DD3(): 

    raw_gdb = r"\\vic-fas1\projects_a\2BT\01_Data\2BT_program_data\2023\RawData\raw_data_2023.gdb"
    dbconfig = r'\\vic-fas1\projects_a\2BT\02_Tools\data_management\postgresql_anesdoly_Aug2024.ini'

    initial_gis_checks(raw_gdb, dbconfig)


def main_LStraining(): 

    raw_gdb = r"V:\2BT\04_Program_year\2022_planting\DataAnalysis\SpatialProcessing\07_LSHEWCHE_TRAINING\LS_raw_data_2022.gdb"
    csvOutput = r"V:\2BT\04_Program_year\2022_planting\DataAnalysis\SpatialProcessing\07_LSHEWCHE_TRAINING\raw_spatial_checks.csv"
    
    initial_gis_checks_csv(raw_gdb, csvOutput)


def main_2023_Sept27(): 

    raw_gdb = r"\\vic-fas1\projects_a\2BT\01_Data\2BT_program_data\2023\RawData\raw_data_2023.gdb"
    dbconfig = r'\\vic-fas1\projects_a\2BT\04_Program_year\2023_planting\SpatialProcessing\working_anesdoly\workstation_production.ini'

    initial_gis_checks(raw_gdb, dbconfig)


def main_2023_Oct15(): 

    raw_gdb = r"\\vic-fas1\projects_a\2BT\01_Data\2BT_program_data\2023\RawData\raw_data_2023.gdb"
    dbconfig = r'\\vic-fas1\projects_a\2BT\04_Program_year\2023_planting\SpatialProcessing\working_anesdoly\nfis_production.ini'

    initial_gis_checks(raw_gdb, dbconfig)

if __name__ == "__main__":
    main_2023_Oct15()