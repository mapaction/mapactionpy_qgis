import os, sys,traceback
from posixpath import basename
import logging
import re
from datetime import datetime
from pandas import options
import pytz
from qgis.core import (QgsProject ,
    QgsMapLayerType,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsApplication,
    QgsGeometry,
    QgsMapSettings,
    QgsReadWriteContext,
    QgsPrintLayout,
    QgsMapSettings, 
    QgsMapLayer,
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
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsRectangle,
    QgsFillSymbol)
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtCore import (
    QPointF,
    QRectF,
    QSize
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
    lManager = QgsProject.instance().layoutManager()
    logging.info(f"getting ittem from layout {layout_name} all layouts {[l.name() for l in lManager.printLayouts()]}")
    main_layout = lManager.printLayouts().pop() if(
        not layout_name) else lManager.layoutByName(layout_name)  # can use layoutByName to filter by name
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
    main_map = get_layout_Item(recipe.principal_map_frame,os.path.basename(recipe.template_path).replace(".qpt",""))
    scale_str = '1: {:,} (At A3)'.format(int(main_map.scale()))
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
    main_map = get_layout_Item(recipe.principal_map_frame,os.path.basename(recipe.template_path).replace(".qpt",""))

    if not main_map:
        err_msg = 'MXD does not have a MapFrame (aka DataFrame) with the name "{}"'.format(
            recipe.principal_map_frame)
        raise ValueError(err_msg)
    
    #Todo do we need this chack ??
    #if len(data_frames) > 1:
    #    err_msg = 'MXD has more than one MapFrames (aka DataFrames) with the name "{}"'.format(
    #        recipe.principal_map_frame)
    #    raise ValueError(err_msg)
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
        # self.cookbook = cookbook
        self.legendEntriesToRemove = list()

        self.replaceDataSourceOnly = False

        self.namingConvention = None
        self.layersToShow = []
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
        #for df in arcpy.mapping.ListDataFrames(self.qgs_project):
        #    for lyr in arcpy.mapping.ListLayers(self.qgs_project, "", df):
        #        lyr.visible = True

    def removeLayers(self):
        """
        Removes all layers for all data-frames
        """
        #Todo implemen all visibility functions 
        pass
        # QgsProject.instance().removeAllMapLayers() thsi will delete all mapLayers associated with the project
        # but this may not be suficient to delete LayoutItemMap.layers()
        #how to itterate over map
        
        #for df in arcpy.mapping.ListDataFrames(self.qgs_project):
        #    for lyr in arcpy.mapping.ListLayers(self.qgs_project, "", df):
        #        if (lyr.longName != "Data Driven Pages"):
        #            arcpy.mapping.RemoveLayer(df, lyr)
        #self.qgs_project.save()

    def cook(self, recipe):
        #arcpy.env.addOutputsToMap = False # whats the side effect here?? 

        self.disableLayers()
        self.removeLayers()
        self.template_name = os.path.basename(recipe.template_path).replace(".qpt","")
        # self.mapReport = MapReport(recipe.product)
        if recipe:
            recipe.creation_time_stamp = datetime.now(pytz.utc)

            for recipe_frame in recipe.map_frames:
                logging.info(f"processing mapFrame {recipe_frame.name} using layut {self.template_name}")
                layoutItemmMap = get_layout_Item(recipe_frame.name, self.template_name)              
                if(layoutItemmMap) :
                    self.apply_frame_crs_and_extent(layoutItemmMap, recipe_frame)
                    for recipe_lyr in recipe_frame.layers:
                        # Do things at an individual layer level
                        self.process_layer(recipe_lyr, recipe_frame)

                    # Do things at an map/data frame level
                    self.apply_frame_crs_and_extent(layoutItemmMap, recipe_frame)
                else :
                    logging.info(f"unfound mapFrame {recipe_frame.name}")
        # Do things at a map layout level
        self.enableLayers()
        # todo - do we need any of this ?? or its taken care of by syncronisation flags 
        #arcpy.RefreshTOC()
        #arcpy.RefreshActiveView()
        #arcpy.env.addOutputsToMap = True
        ###self.showLegendEntries()
        self.qgs_project.write()

        if recipe:
            self.updateTextElements(recipe)
            self.qgs_project.write()

    def process_layer(self, recipe_lyr, layoutItemmMap):
        """
        Updates or Adds a layer of data.  Maintains the Map Report.
        """
        # Try just using add Layer (currently no update layer option)
        self.addLayer(recipe_lyr, layoutItemmMap)

    def updateTextElements(self, recipe):
        """
        Updates Text Elements in Marginalia
        """
        update_data = {"country": self.eventConfiguration.country_name, "title": recipe.product,
                       "create_date_time": recipe.creation_time_stamp.strftime("%d-%b-%Y %H:%M"),
                       "summary": recipe.summary, "map_no": recipe.mapnumber,
                       "mxd_name": os.path.basename(self.qgs_project.absoluteFilePath()),
                       "scale": get_map_scale(self.qgs_project, recipe),\
                       "data_sources": "<BOL>Data Sources:</BOL>" + (2*os.linesep) + (",".join(self.dataSources)),\
                       "map_version": "v" + str(recipe.version_num).zfill(2),\
                       "spatial_reference": get_map_spatial_ref(self.qgs_project, recipe),
                       "glide_no": self.eventConfiguration.glide_number if self.eventConfiguration and self.eventConfiguration.glide_number else "",
                       "donor_credit": self.eventConfiguration.default_donor_credits if self.eventConfiguration else "",
                       "disclaimer": self.eventConfiguration.default_disclaimer_text if self.eventConfiguration else "",
                       "map_producer": "Produced by " + \
                           os.linesep.join([self.eventConfiguration.default_source_organisation, self.eventConfiguration.deployment_primary_email, self.eventConfiguration.default_source_organisation_url])}
        
        map(lambda element_id: get_layout_Item(element_id, self.template_name).setText(update_data[element_id]), update_data)
        self.qgs_project.write() #make sure the fileName property is set on the self.qgs_project object

    def showLegendEntries(self): # layer inclusion in the legent may be controlled by setting the autoUpdateMode to True on the legend object and seting the addToLegend flag during layers addition the project object 
       
        return
        #for legend in arcpy.mapping.ListLayoutElements(self.qgs_project, "LEGEND_ELEMENT"):
        #    layerNames = list()
        #    for lyr in legend.listLegendItemLayers():
        #        if ((lyr.name in self.legendEntriesToRemove) or (lyr.name in layerNames)):
        #            legend.removeItem(lyr)
        #        else:
        #            layerNames.append(lyr.name)
        


    def alignLegend(self, orientation):# TODO do we need this or its preset by the template
        pass
        #for legend in arcpy.mapping.ListLayoutElements(self.qgs_project, "LEGEND_ELEMENT"):
        #    if orientation == "landscape":
        #        # Resize
        #        legend.elementWidth = 60
        #        legend.elementPositionX = 248.9111
        #        legend.elementPositionY = 40
        #self.qgs_project.save()


    def resizeScaleBar(self): #TODO is this needed or preset by template data
        scale_bar = get_layout_Item("scale",self.template_name)
        scale_bar.applyDataDefinedSize() # is this block correct 
        scale_bar.update()

        ###elm = arcpy.mapping.ListLayoutElements(self.qgs_project, "MAPSURROUND_ELEMENT", "Scale Bar")[0]
        ###elm.elementWidth = 51.1585
        ###self.qgs_project.save()

    def apply_frame_crs_and_extent(self, qgs_data_frame, recipe_frame):
        """
        """
        # minx, miny, maxx, maxy = recipe_frame.extent
        # First set the spatial reference
        logging.debug(
            f' Try setting QGS_Frame <{qgs_data_frame.displayName}> CRS using  {recipe_frame.crs[:5]}-{recipe_frame.crs[5:]} ')
        if not recipe_frame.crs[:5].lower() == 'epsg:':
            raise ValueError('unrecognised `recipe_frame.crs` value "{}". String does not begin with "EPSG:"'.format(
                recipe_frame.crs))

        crsString= f"EPSG:{recipe_frame.crs[5:]}"
        targetCrs = QgsCoordinateReferenceSystem(crsString)
        qgs_data_frame.setCrs(targetCrs)

        if recipe_frame.extent:
            new_extent = QgsRectangle(*recipe_frame.extent)
            qgs_data_frame.setExtent = new_extent
        self.qgs_project.write()

    def addLayer(self, recipe_lyr, recipe_frame): #TODO make grouped injection of layers based on <addToLegend flag value>
        # addLayer(recipe_lyr, recipe_lyr.layer_file_path, recipe_lyr.name)
        # mapResult = MapResult(recipe_lyr.name)
        #logging.debug('Attempting to add layer; {}'.format(recipe_lyr.data_source_path))
        #logging.info(f"using recipelaye{recipe_lyr} path data {os.path.realpath(recipe_lyr.data_source_path)}")
        logging.info(f"adding layer <{recipe_lyr.data_source_path}>")
        try:
            if(not recipe_lyr.data_source_path or recipe_lyr.data_name == "hnd_elev_cst_ln_s0_gadm_pp_coast"):
                return 
        except AttributeError:
            return
        logging.info("passed layer source check ")
        target_layer_type = self.get_dataset_type_from_path(os.path.realpath(recipe_lyr.data_source_path))
        mapLayer_toAdd = QgsVectorLayer(recipe_lyr.data_source_path,recipe_lyr.data_name,"ogr") if(target_layer_type == QgsMapLayerType.VectorLayer) \
                            else QgsRasterLayer(recipe_lyr.data_source_path,recipe_lyr.data_name,"ogr")
        logging.info("vector layer object created")
        # self.qgs_project.addMapLayer(addToLegend=recipe_lyr.add_to_legend) TODO is this must be done here or in the addLayer_withFile 

        #arc_lyr_to_add = arcpy.mapping.Layer(recipe_lyr.layer_file_path)
        # if (".gdb/" not in recipe_lyr.reg_exp):
        #     mapResult = self.addLayerWithFile(recipe_lyr, arc_lyr_to_add,  recipe_frame)
        # else:
        #     mapResult = self.addLayerWithGdb(recipe_lyr, arc_lyr_to_add,  recipe_frame)

        # Apply Label Classes
        if(recipe_lyr.data_name in ['hnd_phys_lak_py_s0_osm_pp_waterbodies', 'hnd_phys_riv_ln_s0_osm_pp_waterways']):
            logging.info(f"layer detail : <{[recipe_lyr.data_name,recipe_lyr.extent,recipe_lyr.crs,recipe_lyr.visible]}")
        try:
            ###self.apply_layer_visiblity(mapLayer_toAdd, recipe_lyr)
            self.apply_label_classes(mapLayer_toAdd, recipe_lyr)
            # Apply Definition Query
            ###self.apply_definition_query(mapLayer_toAdd, recipe_lyr)
            logging.info(f"adding layer with file")
            self.addLayerWithFile(mapLayer_toAdd, recipe_lyr, recipe_frame)
            recipe_lyr.success = True
        except Exception as e: 
            logging.info(f"failed while processing created layer object {e}")
            logging.info(f"{traceback.format_exc()}")
            recipe_lyr.success = False

    def apply_layer_visiblity(self, qgs_lyr_to_add, recipe_lyr):
        if(recipe_lyr.visible):
            targetLayerNode = [lyrNode for lyrNode in self.qgs_project.QgsLayerTree().children() if(lyrNode.layerId() == qgs_lyr_to_add.id())][0]
            targetLayerNode.setVisible(True)
            self.layersToShow.append(qgs_lyr_to_add.name()) ## used in ms = QgsMapSettings() ;ms.setLayers([layers_to_add_to map])
        #if arc_lyr_to_add.supports('VISIBLE'):
        #    try:
        #        arc_lyr_to_add.visible = recipe_lyr.visible
        #    except Exception as exp:
        #        recipe_lyr.error_messages.append('Error whilst applying layer visiblity: {}'.format(
        #            exp.message))

    def apply_label_classes(self, qgis_lyr_to_add, recipe_lyr): #TODO this shoud be replaced by       
        styling_file_path =recipe_lyr.layer_file_path.replace(recipe_lyr.layer_file_path.split(".")[-1],"qml")
        logging.info(f"styling file path {styling_file_path}")
        if(os.path.exists(styling_file_path)):
            qgis_lyr_to_add.loadNamedStyle(styling_file_path)
        return
        if arc_lyr_to_add.supports("LABELCLASSES"):
            for labelClass in recipe_lyr.label_classes:
                for lblClass in arc_lyr_to_add.labelClasses:
                    if (lblClass.className == labelClass.class_name):
                        lblClass.SQLQuery = labelClass.sql_query
                        lblClass.expression = labelClass.expression
                        lblClass.showClassLabels = labelClass.show_class_labels

    def apply_definition_query(self, arc_lyr_to_add, recipe_lyr): #we can use this lyr_copy.setSubsetString('"%s" = %d' % (field_name, int(i))
        logging.debug(f'  Attempting to apply definition query {recipe_lyr.definition_query}')
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
            (r'\.shp$', QgsMapLayerType.VectorLayer),
            (r'\.img$', QgsMapLayerType.RasterLayer),
            (r'\.tif$',  QgsMapLayerType.RasterLayer),
            #(r'\.gdb\\.+', 'FILEGDB_WORKSPACE') this should be droped or replaced with geopackage ? 
        ]

        for reg_ex, dataset_type in dataset_type_lookup:
            if re.search(reg_ex, f_path):
                return dataset_type

        raise ValueError('"Unsupported dataset type with path: {}'.format(f_path))

    def addLayerWithFile(self, qgs_lyr_to_add, recipe_lyr, recipe_frame):
        logging.info("inside adding with file")
        try:
            recipe_lyr.data_source_path
        except AttributeError:
            return 
        r_path = os.path.realpath(recipe_lyr.data_source_path)
        data_src_dir = os.path.dirname(r_path)
        logging.info(f"using recipelaye{recipe_lyr} path data {r_path}")
        #dataset_type = self.get_dataset_type_from_path(r_path) # this can only be used during instanciation of the mapLayer object 
        # Apply Data Source
        logging.info(f"target layer <{recipe_lyr.data_name}> has capabilities : {qgs_lyr_to_add.dataProvider().capabilities()}")
        
        try:
            qgs_lyr_to_add.dataProvider().setDataSourceUri(r_path)
            layoutItemMap = get_layout_Item(recipe_frame.name,self.template_name)
            self.qgs_project.addMapLayer(qgs_lyr_to_add,addToLegend=recipe_lyr.add_to_legend)
            map_layers_set = layoutItemMap.layers()
            map_layers_set = (set(map_layers_set) if(map_layers_set) else set())
            map_layers_set.add(qgs_lyr_to_add)
            if(recipe_lyr.visible):
                layoutItemMap.setLayers(map_layers_set) #TODO do we need this or its fine to work with project layers
            logging.info("finished adding layer with file")
            
            #arc_data_frame = arcpy.mapping.ListDataFrames(self.qgs_project, recipe_frame.name)[0]
          
        except Exception as e: 
            logging.info(f"{traceback.format_exc()}")
        finally:
            self.qgs_project.write()
