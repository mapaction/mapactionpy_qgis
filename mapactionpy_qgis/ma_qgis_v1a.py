"""
Notes
-----
1/  Making every path call relative to the root crash move folder.
    Structure of the CMF is a hard constraint
2/  Need to figure out whether the codes should be divided into classes.
3/  QGIS Model based off QGIS 3.4
4/  Have added ad0 and ad1 as data components to the QGIS template but these
    are NOT complete - i.e. they won't work right now.
5/  I want to use active_data_catalog_df() to update ad0 and ad1 dictionaries
    but haven't written the function to do that
"""
import logging
logger = logger = logging.getLogger(__name__)
import os
import glob
import pandas as pd
import re
import uuid
# import geopandas as gpd
# from shapely.geometry import Polygon
# from PyQt5 import QtCore
# import xml.etree.ElementTree as ET

##############################################################################
def dev_get_temp_path():
    """
    I just want a path to dump things into for the time being
    TODO: wipe this out wherever it appears!
    """
    temp_path = os.path.expanduser('~/Desktop/Metis_Test')
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    return temp_path


##############################################################################
def dev_get_model_cmf_root():
    """
    Just a path to a crash move folder during developments
    """
    cmf_root = r'/Users/leon/Documents/MapAction/Projects/Metis/' \
               + '2019-06-25 - Automation - El Salvador'
    return cmf_root


##############################################################################
##############################################################################
def get_default_cmf_root(ma_laptop_root=None):
    """
    Currently set up for lazy pointing to where the crash move folder is
    located.
    TODO: change the default path to however the MapAction laptops are set up
    TODO: could make it find a bunch of choices for cmf folders... think about

    Returns:
        The first crash move folder (i.e. has GIS and Operations folders)
        to be located under the root folder
    """
    if ma_laptop_root is None:
        cmf_root = dev_get_model_cmf_root()
    else:
        for root, dirs, files in os.walk(ma_laptop_root, topdown=True):
            if ('GIS' in dirs) and ('Operations' in dirs):
                cmf_root = root
                break

    return cmf_root


##############################################################################
def get_subfolder_path(main_path, folder_name):
    """
    Generalised function for checking whether a subfolder exists where it
    _should_ be.
    """

    subfolders = os.listdir(main_path)
    assert (folder_name in subfolders), \
        'Could not locate "%s" in folder: %s' % (folder_name, main_path)
    return main_path + os.sep + folder_name


##############################################################################
def get_cmf_gis_path(cmf_root=None):
    """
    Checks for and returns the path to GIS folder in the crash move folder
    TODO: there's a bit of circular reasoning going on with this and
          get_default_cmf_root() .. is this ok?
    """

    if cmf_root is None:
        cmf_root = get_default_cmf_root()

    cmf_gis_path = get_subfolder_path(cmf_root, 'GIS')

    return cmf_gis_path


##############################################################################
def get_gis_folder_list(cmf_root=None):
    """
    Just lists the folders in the GIS folder.
    TODO: verify this against some other lookup table/list
    """

    cmf_gis_path = get_cmf_gis_path(cmf_root=cmf_root)
    return [cmf_gis_path + os.sep + cgp for cgp in os.listdir(cmf_gis_path)]


###############################################################################
def get_active_data_path(cmf_root=None):
    """
    Checks for and returns the path to 2_Active_Data folder in the crash move
    folder.
    TODO: Model can be generalised for other folders under CMF/GIS
    """

    active_data_folder = get_subfolder_path(
            get_cmf_gis_path(cmf_root=cmf_root), '2_Active_Data')

    return active_data_folder


###############################################################################
def get_mapping_path(cmf_root=None):
    """
    Checks for and returns the path to 2_Active_Data folder in the crash move
    folder.
    TODO: Model can be generalised for other folders under CMF/GIS
    """

    mapping_folder = get_subfolder_path(
            get_cmf_gis_path(cmf_root=cmf_root), '3_Mapping')

    return mapping_folder


###############################################################################
def get_active_data_folder_list(cmf_root=None):
    """
    Lists all folders within the active data folder EXCEPT the data naming csv
    folder which isn't expected to hold geodata.
    TODO: verify this against some other lookup table/list
    """
    exclude = ['200_data_name_lookup']

    active_data_path = get_active_data_path(cmf_root=cmf_root)
    active_folder_list = [active_data_path + os.sep + subdir
                          for subdir in os.listdir(active_data_path)
                          if subdir not in exclude]

    return active_folder_list


###############################################################################
def get_data_name_lookup_path(cmf_root=None):
    """
    Fetching the data name look up path
    """

    if cmf_root is None:
        cmf_root = get_default_cmf_root()

    dn_lookup_path = get_subfolder_path(
            get_active_data_path(cmf_root=cmf_root), '200_data_name_lookup')

    return dn_lookup_path


##############################################################################
def get_qgis_template_path(cmf_root=None):
    """
    Checks for and returns the path to QGIS templates folder in the crash move
    folder
    """

    qgis_template_path = get_subfolder_path(
            get_mapping_path(cmf_root=cmf_root), '39_QGIS_Templates')

    return qgis_template_path


##############################################################################
def get_metis_ma001_qgis_template(cmf_root=None):
    """
    Picks up the path to the QGIS template being used for Metis MA001
    TODO: Pick a proper naming convention for the template
    TODO: Put in all the expected data into template (just ad0 and ad1 ATM)
    TODO: generalise this for MA001 - MA003
    """

    template_name = 'DEV_Metis_MA001.qgs'

    template_dirpath = get_qgis_template_path(cmf_root=cmf_root)
    template_path = template_dirpath + os.sep + template_name

    if not os.path.exists(template_path):
        raise IOError('Could not locate "%s" template in folder: %s' %
                      (template_name, template_dirpath))

    return template_path


###############################################################################
def get_data_naming_csv_list(cmf_root=None):
    """
    Lists the csv's used for the data naming convention
    """
    dn_lookup_path = get_data_name_lookup_path(cmf_root=cmf_root)
    # only want the csv's that start with the numeral 0
    dn_csv = [csv for csv in glob.glob(dn_lookup_path + os.sep + '*.csv')
              if os.path.basename(csv).startswith('0')]
    return dn_csv


###############################################################################
def get_ordered_data_naming_category(cmf_root=None):
    """
    TODO: Here I'm inferring the data naming order from the way the CSVs are
          numbered. Might want to fix this reference from somewhere else?
    Returns the order of the non-free data naming convention components
    """

    data_naming_csv_list = get_data_naming_csv_list(cmf_root=cmf_root)
    dn_dict = {}
    for dn_csv in data_naming_csv_list:
        dn_index, dn_category = \
            os.path.splitext(os.path.basename(dn_csv))[0].split('_')
        dn_dict[dn_index] = dn_category

    dn_keys = {int(k):dn_dict[k] for k in dn_dict.keys()}
    sorted_index = dn_keys.keys()
    sorted_index.sort()
    dn_order = [dn_keys[idx] for idx in sorted_index]

    return dn_order


###############################################################################
def get_data_naming_dict(cmf_root=None):
    """
    Constructs a dictionary of dataframes for each csv,
    Dictionary key is the name of the csv (excluding numeric prefix)
    Dictionary values are dataframes (since csv may have multiple columns
    beyond Value and Description)
    """

    data_naming_csv_list = get_data_naming_csv_list(cmf_root=cmf_root)

    data_naming_dict = {}
    for dn_csv in data_naming_csv_list:
        dn_data = pd.read_csv(dn_csv)
        dn_index, dn_category = \
            os.path.splitext(os.path.basename(dn_csv))[0].split('_')
        dn_data['data_name_idx'] = dn_index # TODO: delete if unused
        data_naming_dict[dn_category] = dn_data

    return data_naming_dict


###############################################################################
def get_data_description_from_name(data_name, cmf_root=None):
    """
    Returns a dictionary containing the descriptions of the data from the
    data naming convention
    TODO: keys suffixed "_found" say whether the file naming convention
          applies to a particular expected element of the file.
          Nothing done with this information here - can be developed.

    """

    data_naming = get_data_naming_dict(cmf_root=cmf_root)
    data_naming_category = get_ordered_data_naming_category(cmf_root=cmf_root)
    outstanding_category = data_naming_category[:]

    data_name_comp = data_name.split('_')
    data_record = {}
    free_text = []
    fixed_text = []
    naming_convention_fail = False

    # IDEALLY components in the file names appear in order...
    # this isn't necessarily true though so we'll have to be cunning
    for idx in range(len(data_name_comp)):

        if idx < len(data_naming_category):
            comp = data_name_comp[idx]
            category = data_naming_category[idx]
            if category not in outstanding_category:
                continue
            ref_record = data_naming[category][data_naming[category]['Value'] == comp]
            if len(ref_record) == 1:
                fixed_text.append(comp)
                data_record[category] = comp
                data_record[category + '_found'] = True
                data_record[category + '_description'] = ref_record['Description'].item()
                outstanding_category = [o for o in outstanding_category if o != category]
            # sanity check / fixing based on finding if naming was done out of order
            # note the failure in naming convention but try keeping the information
            elif len(ref_record) == 0:
                naming_convention_fail = True
                # search through unassigned columns
                found_elsewhere = False
                for test_cat in outstanding_category:
                    test_rec = data_naming[test_cat][data_naming[test_cat]['Value'] == comp]
                    if len(test_rec) == 1:
                        found_elsewhere = True
                        category = test_cat
                        ref_record = test_rec
                if found_elsewhere:
                    fixed_text.append(comp)
                    data_record[category] = comp
                    data_record[category + '_found'] = True
                    data_record[category + '_description'] = ref_record['Description'].item()
                    outstanding_category = [o for o in outstanding_category if o != category]
                else:
                    data_record[category] = comp
                    data_record[category + '_found'] = False
                    data_record[category + '_description'] = ''
            # sanity check that there is only one possible match in the data
            # naming convention CSV records! Fundamental failure = STOP HERE!
            elif len(ref_record) > 1:
                naming_convention_fail = True
                badvalues = ', '.join(ref_record['Description'].tolist())
                raise LookupError('%s CSV contains duplicate "%s" items: %s' %
                                  (category, comp, badvalues))
        else:
            if comp not in fixed_text:
                free_text.append(comp)
    data_record['free_text'] = '_'.join(free_text)
    data_record['follows_naming_convention'] = not naming_convention_fail

    return data_record


###############################################################################
def active_data_catalog_df(cmf_root=None):
    """
    Figure out what data we have in the active data folder
    TODO: Metis project assumes only one dataset in folder, but this routine
          collects every file with a unique naming convention applied...
          deal with this down the line.
    """

    active_data_folder_list = get_active_data_folder_list(cmf_root=cmf_root)

    active_catalog = []
    for active_folder in active_data_folder_list:
        file_list = glob.glob(active_folder + os.sep + '*.*')
        if len(file_list) == 0:
            continue
        # next bit is for lazy lookups / searching
        active_folder_name = os.path.basename(active_folder.rstrip(os.sep))
        active_idx, active_name = active_folder_name.split('_')

        # since shapefiles come along in multiple files, let's find unique
        # naming conventions in a folder.
        # Full stops appear thanks to weird GIS lock files, associated xml, etc
        # Naming convention never includes full stops but can contain free text
        # TODO: is it legit to just stip everything right of the first full stop
        #       in a filename?
        file_list = [f for f in file_list]
        data_file_name_list = list(set([os.path.basename(f).split('.')[0]
                                        for f in file_list]))

        for data_name in data_file_name_list:
            # breakdown the components of the file name
            # using the data naming convention
            data_desc = get_data_description_from_name(
                    data_name, cmf_root=cmf_root)
            data_desc['folder'] = active_folder_name
            data_desc['folder_index'] = active_idx
            data_desc['folder_description'] = active_name
            data_desc['data_name'] = data_name
            active_catalog.append(data_desc)

    return pd.DataFrame(active_catalog)


##############################################################################
###############################################################################
def get_template_ad0_dict():
    """
    Minimal dictionary of ad0 in template at the moment: El Salvador.
    TODO: Determine parameters for ad0
    """

    return None


###############################################################################
def update_ad0_dict(**kwargs):
    """
    Minimal dictionary of ad0 in template at the moment: El Salvador.
    TODO: Parameters get structured a little differently within QGIS documents
          so may need to play about with this
    """
    this_ad0 = get_template_ad0_dict()

    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if key in this_ad0.keys():
                this_ad0[key] = value

    return this_ad0


###############################################################################
def get_template_ad1_dict():
    """
    Minimal dictionary of ad1 in template at the moment: El Salvador.
    TODO: Determine parameters for ad1
    """

    return None


###############################################################################
def update_ad0_dict(**kwargs):
    """
    Minimal dictionary of ad0 in template at the moment: El Salvador.
    TODO: Parameters get structured a little differently within QGIS documents
          so may need to play about with this
    """
    this_ad1 = get_template_ad1_dict()

    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if key in this_ad1.keys():
                this_ad1[key] = value

    return this_ad1


###############################################################################
def get_template_ma001_qgis_dict(cmf_root=None):
    """
    Minimal dictionary of template for template location and template components
    TODO: make dictionary adapt to MA000 recipe

    """
    ma001_template_path = get_metis_ma001_qgis_template(cmf_root=cmf_root)

    model = {}
    model['name'] = os.path.splitext(os.path.basename(ma001_template_path))
    model['path'] = ma001_template_path
    model['ad0'] = get_template_ad0_dict()
    model['ad1'] = get_template_ad1_dict()

    return model


###############################################################################
def make_new_ma001_qgis_dict(ma001name, ad0dict, ad1dict,
                             ma001dirpath=None, cmf_root=None):
    """
    Dictionary used to update the template in the qgis doc
    TODO: tonnes!
    """

    if ma001dirpath is None:
        ma001dirpath = dev_get_temp_path()

    if not os.path.exists(ma001dirpath):
        os.makedirs(ma001dirpath)

    newma001 = {}
    newma001['path'] = ma001dirpath + os.sep + ma001name + '.qgs'
    newma001['name'] = ma001name
    newma001['ad0'] = ad0dict
    newma001['ad1'] = ad1dict

    return newma001


###############################################################################
def make_qgis_map_document(ma001name, cmf_root=None, output_path=None,
                           dataelements=None, **kwargs):
    """
    TODO:
    TODO: break this down!
    """

    if output_path is None:
        output_path = dev_get_temp_path()

    model = get_template_ma001_qgis_dict(cmf_root=cmf_root)

    with open(model['path'],'r') as model_doc:
        model_contents = model_doc.read()

    qgis_keys = ['id', 'source', 'hex', 'name']

    model_lines = model_contents.split('\n')
    relevant_line = []
    hexdict = {}
    hex_regex = '[0-9a-f]{8}_[0-9a-f]{4}_[0-9a-f]{4}_[0-9a-f]{4}_[0-9a-f]{12}'


    for mline in model_lines:
        for dataelement in dataelements:
            if model[dataelement]['name'] in mline:

                relevant_line.append(mline)
                this_dict = {q:'' for q in qgis_keys}

                # id is generated individually for each data source...
                modid = re.findall('id=".*?"', mline)
                if len(modid) > 0:
                    this_dict['id'] = modid[0][len('id="'):-len('"')]
                else:
                    modid = re.findall('<item>.*?</item>', mline)
                    if len(modid) > 0:
                        this_dict['id'] = modid[0][len('<item>'):-len('</item>')]
                    else:
                        modid = re.findall('<id>.*?</id>', mline)
                        if len(modid) > 0:
                            this_dict['id'] = modid[0][len('<id>'):-len('</id>')]

                # source is a separate entity; can't derive from other properties
                modsrc = re.findall('source=".*?"', mline)
                if len(modsrc) > 0:
                    this_dict['source'] = modsrc[0][len('source="'):-len('"')]
                else:
                    modsrc = re.findall('<datasource>.*?</datasource>', mline)
                    if len(modsrc) > 0:
                        this_dict['source'] = \
                            modsrc[0][len('<datasource>'):-len('</datasource>')]

                # if we have the source we can fetch the name directly
                # the name can be different from the id representation though
                # if this_dict['id'] != '':
                #     # can simply clip out regex of the hex code.
                #     modhex = re.findall(hex_regex, this_dict['id'])[0]
                #     this_dict['name'] = this_dict['id'].split('_' + modhex)[0]
                if this_dict['source'] != '':
                    # the layer name usually defaults to the file basename
                    this_dict['name'] = \
                        os.path.basename(os.path.splitext(this_dict['source'])[0])
                else:
                    #otherwise search the tags for name entries
                    modname = re.findall('name=".*?"', mline)
                    if len(modname) > 0:
                        this_dict['name'] = modname[0][len('name="'):-len('"')]
                    else:
                        modname = re.findall('<layername>.*?</layername>', mline)
                        if len(modname) > 0:
                            this_dict['name'] = \
                                modname[0][len('<layername>'):-len('</layername>')]

                # can pinch the hex code easily if we have the id
                if (this_dict['id'] != ''):
                    modhex = re.findall(hex_regex, this_dict['id'])
                    if len(modhex) > 0:
                        this_dict['hex'] = modhex[0]

                if this_dict['hex'] == '':
                    continue
                if this_dict['hex'] not in hexdict.keys():
                    hexdict[this_dict['hex']] = this_dict
                else:
                    for tkey in this_dict.keys():
                        if tkey == 'hex':
                            continue
                        if ((hexdict[this_dict['hex']][tkey] == '')
                                and (this_dict[tkey] != '')):
                            hexdict[this_dict['hex']][tkey] = this_dict[tkey]
                        elif ((hexdict[this_dict['hex']][tkey] != this_dict[tkey])
                                and (this_dict[tkey] != '')
                                and (hexdict[this_dict['hex']][tkey] != '')):
                            raise AssertionError('hex look ups do not match')

    replace_dict = []

    job = make_new_ma001_qgis_dict(ma001name, kwargs['ad0'], kwargs['ad1'],
                             ma001dirpath=output_path, cmf_root=cmf_root)

    for oldhex in hexdict.keys():
        this_dict = hexdict[oldhex]
        # fix the id string
        # generate new hex
        this_dict['newhex'] = str(uuid.uuid4()).replace('-', '_')
        if model['client name'] in hexdict[oldhex]['name']:
            this_dict['newname'] = job['client name']
            this_dict['newsource'] = job['client src']
            this_dict['source'] = model['client src']
            this_dict['newid'] = '_'.join(job['client name'].split(' ')
                                          + [this_dict['newhex']])
        else:
            this_dict['newname'] = hexdict[oldhex]['name'].replace(
                    model['suffix'], job['suffix']).replace(
                    model['job_name'], job['name']).replace(
                    model['results_suffix'], job['results_suffix'])
            this_dict['newsource'] = hexdict[oldhex]['source'].replace(
                    model['suffix'], job['suffix']).replace(
                    model['results_suffix'], job['results_suffix'])
            new_id = hexdict[oldhex]['id'].replace(
                    model['suffix'], job['suffix']).replace(
                    model['results_suffix'], job['results_suffix'])
            this_dict['newid'] = new_id.replace(oldhex, this_dict['newhex'])
        replace_dict.append(this_dict)

    job_contents = model_contents[:]

    for rdic in replace_dict:
        for key in qgis_keys:
            job_contents = job_contents.replace(rdic[key], rdic['new'+key])

    # Now finally change the last of the job identification items
    for thing in job.keys():
        if thing in model.keys():
            job_contents = job_contents.replace(model[thing], job[thing])

    with open(job['document'],'w') as job_doc:
        job_doc.write(job_contents)