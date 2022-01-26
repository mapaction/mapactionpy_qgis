import os
import logging
import re
from datetime import datetime
import pytz
from qgis.core import (
    QgsGeometry,
    QgsMapSettings,
    QgsPrintLayout,
    QgsMapSettings,
    QgsMapRendererParallelJob,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPolygon,
    QgsLayoutItemScaleBar,
    QgsLayoutExporter,
    QgsLayoutItem,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsUnitTypes,
    QgsProject,
    QgsFillSymbol,
    QgsRectangle,
    QgsCoordinateReferenceSystem
)


ESRI_DATASET_TYPES = [
    "SHAPEFILE_WORKSPACE",
    "RASTER_WORKSPACE",
    "FILEGDB_WORKSPACE",
    "ACCESS_WORKSPACE",
    "ARCINFO_WORKSPACE",
    "CAD_WORKSPACE",
    "EXCEL_WORKSPACE",
    "OLEDB_WORKSPACE",
    "PCCOVERAGE_WORKSPACE",
    "SDE_WORKSPACE",
    "TEXT_WORKSPACE",
    "TIN_WORKSPACE",
    "VPF_WORKSPACE"
]


def get_layout_Item(item_id,layout_name =None):
    qgs_project = QgsProject().instance()
    main_layout = qgs_project.layoutManager().printlayouts().pop() if(
        not layout_name) else qgs_project.layoutManager().layoutByName(layout_name)  # can use layoutByName to filter by name
    return main_layout.itemById(item_id)

def get_map_scale(qgs_project, recipe):
    """
    Returns a human-readable string representing the map scale of the
    principal map frame of the mxd.

    @param arc_mxd: The MapDocument object of the map being produced.
    @param recipe: The MapRecipe object being used to produced it.
    @returns: The string representing the map scale.
    """
    scale_str = ""
    main_map = get_layout_Item(recipe.principal_map_frame)
    scale_str = '1: {:,} (At A3)'.format(int(main_map.scale))
    return scale_str


def get_map_spatial_ref(qgs_project, recipe):
    """
    Returns a human-readable string representing the spatial reference used to display the
    principal map frame of the mxd.

    @param arc_mxd: The MapDocument object of the map being produced.
    @param recipe: The MapRecipe object being used to produced it.
    @returns: The string representing the spatial reference. If the spatial reference cannot be determined
                then the value "Unknown" is returned.
    """
    main_map = get_layout_Item(recipe.principale_map_frame)

    if not main_map:
        err_msg = 'MXD does not have a MapFrame (aka DataFrame) with the name "{}"'.format(
            recipe.principal_map_frame)
        raise ValueError(err_msg)
    
    spatial_ref_desc = main_map.crs().description()
    spatial_ref_str = "Unknown" if(not spatial_ref_desc) else spatial_ref_desc
    return spatial_ref_str


class MapChef:
    """
    Worker which creates a Map based on a predefined "recipe" from a cookbook
    """
   
    def __init__(self,
                 qgs_project,
                 crashMoveFolder,
                 eventConfiguration):
        """
        Arguments:
           mxd {MXD file} -- MXD file.
           crashMoveFolder {CrashMoveFolder} -- CrashMoveFolder Object
           eventConfiguration {Event} -- Event Object
        """
        self.qgs_project = qgs_project
        self.crashMoveFolder = crashMoveFolder

        self.eventConfiguration = eventConfiguration
        self.legendEntriesToRemove = list()

        self.replaceDataSourceOnly = False
        self.namingConvention = None

        self.dataSources = set()
        self.export = False

    def disableLayers(self):
        """
        Makes all layers invisible for all data-frames
        """ 
        pass
    def enableLayers(self):
        """
        Makes all layers visible for all data-frames
        """
        pass
    
    def removeLayers(self):
        """
        Removes all layers for all data-frames
        """
        pass
       
    def cook(self, recipe):
      
        self.disableLayers()
        self.removeLayers()

        if recipe:
            recipe.creation_time_stamp = datetime.now(pytz.utc)

            for recipe_frame in recipe.map_frames:
                layoutItemmMap = get_layout_Item(recipe_frame.name)
                for recipe_lyr in recipe_frame.layers: 
                    self.process_layer(recipe_lyr, layoutItemmMap)

                self.apply_frame_crs_and_extent(layoutItemmMap, recipe_frame)

        self.enableLayers()
      
        self.showLegendEntries()
        self.qgs_project.save()

        if recipe:
            self.updateTextElements(recipe)
            self.qgs_project.save()

    def process_layer(self, recipe_lyr, layoutItemmMap):
        """
        Updates or Adds a layer of data.  Maintains the Map Report.
        """
        self.addLayer(recipe_lyr, layoutItemmMap)

    def updateTextElements(self, recipe):
        """
        Updates Text Elements in Marginalia
        """
        update_data = {"country": self.eventConfiguration.country_name, "title": recipe.product,
                       "create_date_time": recipe.creation_time_stamp.strftime("%d-%b-%Y %H:%M"),
                       "summary": recipe.summary, "map_no": recipe.mapnumber,
                       "mxd_name": os.path.basename(self.qgs_project.filePath),
                       "scale": get_map_scale(self.qgs_project, recipe),\
                       "data_sources": "<BOL>Data Sources:</BOL>" + (2*os.linesep) + (",".join(self.dataSources)),\
                       "map_version": "v" + str(recipe.version_num).zfill(2),\
                       "spatial_reference": get_map_spatial_ref(self.qgs_project, recipe),
                       "glide_no": self.eventConfiguration.glide_number if self.eventConfiguration and self.eventConfiguration.glide_number else "",
                       "donor_credit": self.eventConfiguration.default_donor_credits if self.eventConfiguration else "",
                       "disclaimer": self.eventConfiguration.default_disclaimer_text if self.eventConfiguration else "",
                       "map_producer": "Produced by " + \
                           os.linesep.join([self.eventConfiguration.default_source_organisation, self.eventConfiguration.deployment_primary_email, self.eventConfiguration.default_source_organisation_url])}
        
        map(lambda element_id: get_layout_Item(element_id).setText(update_data[element_id]), update_data)
        self.qgs_project.write()

    def showLegendEntries(self):
      
        legend = get_layout_Item("legend")
        legend.setAutoUpdateModel(True)
        self.qgs_project.write()

    def alignLegend(self, orientation):
        pass
        

    def resizeScaleBar(self):
        scale_bar = get_layout_Item("scale")
        scale_bar.applyDataDefinedSize() 
        scale_bar.update()


    def apply_frame_crs_and_extent(self, qgs_data_frame, recipe_frame):
        """
        """
        logging.debug(
            f' Try setting QGS_Frame <{qgs_data_frame.displayName}> CRS using  {recipe_frame.crs[:5]}-{recipe_frame.crs[5:]} ')
        if not recipe_frame.crs[:5].lower() == 'epsg:':
            raise ValueError('unrecognised `recipe_frame.crs` value "{}". String does not begin with "EPSG:"'.format(
                recipe_frame.crs))

        crsString= f"“EPSG:{recipe_frame.crs[5:]}"
        targetCrs = QgsCoordinateReferenceSystem(crsString)
        qgs_data_frame.setCrs(targetCrs)

        if recipe_frame.extent:
            new_extent = QgsRectangle(*recipe_frame.extent)
            qgs_data_frame.setExtent = new_extent
        self.qgs_project.save()

    def addLayer(self, recipe_lyr, recipe_frame): 

        logging.debug('Attempting to add layer; {}'.format(recipe_lyr.layer_file_path))
        arc_lyr_to_add = arcpy.mapping.Layer(recipe_lyr.layer_file_path)
       
        try:
            self.apply_layer_visiblity(arc_lyr_to_add, recipe_lyr)
            self.apply_label_classes(arc_lyr_to_add, recipe_lyr)
            
            self.apply_definition_query(arc_lyr_to_add, recipe_lyr)
            self.addLayerWithFile(arc_lyr_to_add, recipe_lyr, recipe_frame)
            recipe_lyr.success = True
        except Exception:
            recipe_lyr.success = False

    def apply_layer_visiblity(self, arc_lyr_to_add, recipe_lyr):
        if arc_lyr_to_add.supports('VISIBLE'):
            try:
                arc_lyr_to_add.visible = recipe_lyr.visible
            except Exception as exp:
                recipe_lyr.error_messages.append('Error whilst applying layer visiblity: {}'.format(
                    exp.message))

    def apply_label_classes(self, arc_lyr_to_add, recipe_lyr):
        if arc_lyr_to_add.supports("LABELCLASSES"):
            for labelClass in recipe_lyr.label_classes:
                for lblClass in arc_lyr_to_add.labelClasses:
                    if (lblClass.className == labelClass.class_name):
                        lblClass.SQLQuery = labelClass.sql_query
                        lblClass.expression = labelClass.expression
                        lblClass.showClassLabels = labelClass.show_class_labels

    def apply_definition_query(self, arc_lyr_to_add, recipe_lyr):
        logging.debug('In method apply_definition_query for layer; {}'.format(recipe_lyr.layer_file_path))
        logging.debug('   Target layer supports DEFINITIONQUERY; {}'.format(arc_lyr_to_add.supports('DEFINITIONQUERY')))
        logging.debug('   Target DEFINITIONQUERY; {}'.format(recipe_lyr.definition_query))
        if recipe_lyr.definition_query and arc_lyr_to_add.supports('DEFINITIONQUERY'):
            try:
                logging.debug('  Attempting to apply definition query')
                arc_lyr_to_add.definitionQuery = recipe_lyr.definition_query
            except Exception as exp:
                logging.error('Error whilst applying definition query: "{}"\n{}'.format(
                    recipe_lyr.definition_query, exp.message))
                recipe_lyr.error_messages.append('Error whilst applying definition query: "{}"\n{}'.format(
                    recipe_lyr.definition_query, exp.message))

    def get_dataset_type_from_path(self, f_path):
        """
        * '.shp' at the end of a path name
        * '.img' at the end of a path name
        * '.tif' at the end of a path name
        * '.gdb\' in the middle of a path name
        """
        dataset_type_lookup = [
            (r'\.shp$', 'SHAPEFILE_WORKSPACE'),
            (r'\.img$', 'RASTER_WORKSPACE'),
            (r'\.tif$', 'RASTER_WORKSPACE'),
            (r'\.gdb\\.+', 'FILEGDB_WORKSPACE')
        ]

        for reg_ex, dataset_type in dataset_type_lookup:
            if re.search(reg_ex, f_path):
                return dataset_type

        raise ValueError('"Unsupported dataset type with path: {}'.format(f_path))

    def addLayerWithFile(self, arc_lyr_to_add, recipe_lyr, recipe_frame):
      
        try:
            recipe_lyr.data_source_path
        except AttributeError:
            return

        r_path = os.path.realpath(recipe_lyr.data_source_path)
        data_src_dir = os.path.dirname(r_path)
        dataset_type = self.get_dataset_type_from_path(r_path)

       
        if arc_lyr_to_add.supports("DATASOURCE"):
            try:
                arc_lyr_to_add.replaceDataSource(data_src_dir, dataset_type, recipe_lyr.data_name)
                arc_data_frame = arcpy.mapping.ListDataFrames(self.qgs_project, recipe_frame.name)[0]



                if recipe_lyr.add_to_legend is False:
                    self.legendEntriesToRemove.append(arc_lyr_to_add.name)
                arcpy.mapping.AddLayer(arc_data_frame, arc_lyr_to_add, "BOTTOM")
            finally:
                self.qgs_project.save()
