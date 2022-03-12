from cgi import test
from cmath import log
import logging
import os
import json
from xml.etree.ElementTree import PI
from PIL import Image
from numpy import double
from resizeimage import resizeimage
from slugify import slugify
from mapactionpy_qgis.map_chef import MapChef, get_layout_Item, get_map_scale, get_map_spatial_ref
from mapactionpy_controller.plugin_base import BaseRunnerPlugin
import sys
import ctypes
import qgis
import re
from pickle import Pickler



from qgis.core import (QgsProject ,
    QgsApplication,
    QgsGeometry,
    QgsRectangle,
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
    QgsProject,
    QgsFillSymbol)
    
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtGui import (
    QPolygonF,
    QColor,
)
from qgis.PyQt.QtCore import (
    QPointF,
    QRectF,
    QSize,
)

import psutil
from pdf2image import convert_from_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s %(message)s'
)
def dump_loaded_dlls():
    ps = psutil.Process(os.getpid())
    memMaps = ps.memory_maps()
    with open(os.path.join(os.getcwd(),"mapChef_loadedDLLs.pkl"),'wb') as f:
        Pickler(f).dump(memMaps)
    gdal_entries = [mmp[0] for mmp in memMaps if "gdal" in mmp[0]]
    logging.info(f"gdal dll locations : {gdal_entries}")


class QGisRunner(BaseRunnerPlugin):
    """
    QGisRunner - Executes the QGis automation methods
    """


    def __init__(self,
                 hum_event):
        super(QGisRunner, self).__init__(hum_event)
        QgsApplication.setPrefixPath(os.environ["QGIS_PATH"], True) 
        self.qgs = QgsApplication([], False)
        # load providers
        self.qgs.initQgis()
        self.exportMap = False
        self.minx = 0
        self.miny = 0
        self.maxx = 0
        self.maxy = 0
        self.chef = None
        self.cmf.map_templates = os.path.join(self.cmf.map_templates,"323_qgis")

    def load_print_layout(self,project,template):
        principal_layout = QgsPrintLayout(project)
        layout_name = re.findall("^\w+_\d+(.\d+)*_(.*)$",os.path.split(template)[1].replace(".qpt",""))[0][-1]
        logging.info(f"using layout name {layout_name}")
        principal_layout.setName(layout_name)
        logging.info(f"laout pages default {len(principal_layout.pageCollection().pages())}")
        principal_layout.initializeDefaults()
        logging.info(f"laout pages after init defaults {len(principal_layout.pageCollection().pages())}")
        template_content = None
        doc = None
        with open(template) as f:
            logging.info(f"reading template : {template}")
            template_content = f.read()
            doc = QDomDocument()
            logging.info(f"creating qdocument ")
            doc.setContent(template_content)
        layout_items ,status = principal_layout.loadFromTemplate(doc, QgsReadWriteContext(), True)
        logging.info(f"main map layers as it comes {[l.name() for l in principal_layout.itemById('Main map').layers()]}")
        if(status):
            #lytExporter = QgsLayoutExporter(principal_layout)
            #result = lytExporter.exportToPdf("laout-before.pdf",QgsLayoutExporter.PdfExportSettings())
            #logging.info(f"export default qpt {result}")
            return principal_layout 
        else : return None

    def build_project_files(self, **kwargs):
        # Construct a Crash Move Folder object if the cmf_description.json exists
        recipe = kwargs['state']
        qgs_project = QgsProject().instance()
        lManager = qgs_project.layoutManager()
        if(len(lManager.printLayouts())<1):
            principal_layout= self.load_print_layout(qgs_project,recipe.template_path)
            qgs_project.layoutManager().addLayout(principal_layout)
            logging.info(f"added layout with name {principal_layout.name()}")

        projectFilePath = recipe.map_project_path.replace(".qpt",".qgz")
        #qgs_project.filePath = projectFilePath 
        qgs_project.write(projectFilePath)
        self.chef = MapChef(qgs_project, self.cmf, self.hum_event)
        self.chef.cook(recipe)

        final_recipe_file = recipe.map_project_path.replace(".qgs", ".json")
        with open(final_recipe_file, 'w') as outfile:
            outfile.write(str(recipe))

        return recipe

    def get_projectfile_extension(self):
        return '.qpt'

    def get_lyr_render_extension(self):
        return '.lyr'
    
   
    def _get_largest_map_frame(self,layout_item_maps):
        """
        This returns the dataframe occupying the largest area on the page.
        * If two data frames have identical areas then the widest is returned.
        * If two data frames have identical heights and widths returned then the alphabetically last (by `.name`)
          is returned.

        @param data_frames: a list of DataFrame objects, typically returned by `arcpy.mapping.ListDataFrames(mxd, "*")`
        @return: a single DataFrame object from the list.
        @raises ValueError: if there are two DataFrames in the list, which have identical `width`, `height` and `name`.
        """

        full_details = [{
            'df': df,
            'area': df.df.extent().heigth()*df.extent().width(),
            'width': df.extent().width(),
            'name': df.displayName()} for df in layout_item_maps]

        # select just the largest if there is a single largest
        # keep drilling down using different metrics until a single aspect ratio is discovered
        for metric_key in ['area', 'width', 'name']:
            max_size = max([df_detail[metric_key] for df_detail in full_details])
            sub_list = [df_detail for df_detail in full_details if df_detail[metric_key] == max_size]
            if len(sub_list) == 1:
                return sub_list[0]['df']

            # reduce the list of possible data frames for the next iteration
            full_details = sub_list    

 

    def get_aspect_ratios_of_templates(self, possible_templates, recipe):
        """
        Calculates the aspect ratio of the principal map frame within the list of templates.

        @param possible_templates: A list of paths to possible templates.
        @param recipe: A MapRecipe which is used to determine the principal map frame.
        @returns: A list of tuples. For each tuple the first element is the path to the template. The second
                  element is the aspect ratio of the largest* map frame within that template.
                  See `_get_largest_map_frame` for the description of hour largest is determined.
        """
        logging.info(f"possible templates : {possible_templates}")
        
        results = []
        #results = list(map(lambda lyt :(lyt[0],lyt[1].extent().width() / lyt[1].extent().height()) ,\
        #      [(layout.name(),layout.itemById(recipe.principal_map_frame )) for layout in possible_templates]) )
        #logging.info(f"returning results {results}")
        #return results
        project = QgsProject.instance()
        logging.info('Calculating the aspect ratio of the largest map frame within the list of templates.')
        try :
            principal_layout = QgsPrintLayout(project)
        except Exception as e :
            logging.info(f"this happens {e}")

        for template in possible_templates:
            logging.info(f"Processing template : {template}")
             # back to outer scope ?
            logging.info(f"printLayout created")
            #principal_layout.initializeDefaults() is this needed while loading from qpt file??
            principal_layout.setName(os.path.basename(template).replace(".qpt",""))
            template_content = None
            doc = None
            with open(template) as f:
                logging.info(f"reading template : {template}")
                template_content = f.read()
                doc = QDomDocument()
                logging.info(f"creating qdocument ")
                doc.setContent(template_content)
            logging.info(f"loading document content into layout ..")
            layout_items ,status = principal_layout.loadFromTemplate(doc, QgsReadWriteContext(), True)
            logging.info(f"layout content loaded")
            main_layout_map = list(filter(lambda el:isinstance(el,QgsLayoutItemMap) and el.displayName() == recipe.principal_map_frame ,layout_items)).pop()
            logging.info(f"retrieved main map {main_layout_map.id()}")
            aspect_ratio = main_layout_map.extent().width() / main_layout_map.extent().height() 
            results.append((template, aspect_ratio))
            logging.info('Calculated aspect ratio= {} for template={}'.format(aspect_ratio, template))
        # project.write(target_project_path) we can use this to create the project file for specified product  
        return results

    def haveDataSourcesChanged(self, previousReportFile):
        return True

    def _do_export(self, recipe):
        """
        Does the actual work of exporting of the PDF, Jpeg and thumbnail files.
        """
        pass
        arc_mxd = None 
        # PDF export
        pdf_path = self.export_pdf(recipe, arc_mxd)
        recipe.zip_file_contents.append(pdf_path)
        recipe.export_metadata['pdffilename'] = os.path.basename(pdf_path)

        # JPEG export
        jpeg_path = self.export_jpeg(recipe, arc_mxd)
        recipe.zip_file_contents.append(jpeg_path)
        recipe.export_metadata['jpgfilename'] = os.path.basename(jpeg_path)

        # Thumbnail
        tb_nail_path = self.export_png_thumbnail(recipe, arc_mxd)
        recipe.zip_file_contents.append(tb_nail_path)
        recipe.export_metadata['pngThumbNailFileLocation'] = tb_nail_path

        # Atlas (if required)
        if recipe.atlas:
            export_dir = recipe.export_path
            self._export_atlas(recipe, arc_mxd, export_dir)

        # Update export metadata and return
        return self._update_export_metadata(recipe, arc_mxd)

    def _update_export_metadata(self, recipe, arc_mxd):
        """
        Populates the `recipe.export_metadata` dict
        """
        recipe.export_metadata["coreFileName"] = recipe.core_file_name
        recipe.export_metadata["product-type"] = "mapsheet"
        recipe.export_metadata['themes'] = recipe.export_metadata.get('themes', set())

        recipe.export_metadata['mapNumber'] = recipe.mapnumber
        recipe.export_metadata['title'] = recipe.product
        recipe.export_metadata['versionNumber'] = recipe.version_num
        recipe.export_metadata['summary'] = recipe.summary
        recipe.export_metadata["xmin"] = self.minx
        recipe.export_metadata["ymin"] = self.miny
        recipe.export_metadata["xmax"] = self.maxx
        recipe.export_metadata["ymax"] = self.maxy

        recipe.export_metadata["createdate"] = recipe.creation_time_stamp.strftime("%d-%b-%Y")
        recipe.export_metadata["createtime"] = recipe.creation_time_stamp.strftime("%H:%M")
        recipe.export_metadata["scale"] = get_map_scale(arc_mxd, recipe)
        recipe.export_metadata["datum"] = get_map_spatial_ref(arc_mxd, recipe)
        return recipe

    def _export_atlas(self, recipe_with_atlas, qgs_project, export_dir):
        """
        Exports each individual page for recipes which contain an atlas definition
        """
        logging.info("exporting map using atlas")
        if not recipe_with_atlas.atlas:
            raise ValueError('Cannot export atlas. The specified recipe does not contain an atlas definition')
        recipe_frame = recipe_with_atlas.get_frame(recipe_with_atlas.atlas.map_frame)
        recipe_lyr = recipe_frame.get_layer(recipe_with_atlas.atlas.layer_name)
        queryColumn = recipe_with_atlas.atlas.column_name
        atlas_lyr_name = recipe_lyr.name
        qgs_project = QgsProject().instance()
        lManager = qgs_project.layoutManager()        
        layout  = lManager.printLayouts().pop()
        logging.info(f"getting atlas layer <{atlas_lyr_name}>")
        map_frame =  get_layout_Item(recipe_frame.name,re.findall("^\w+_\d+(.\d+)*_(.*)$",os.path.split(recipe_with_atlas.template_path)[1].replace(".qpt",""))[0][-1])
        atlas_lyr = qgs_project.mapLayersByName(atlas_lyr_name)[0]  #[l for l in map_frame.layers() if l.name() == atlas_lyr_name][0]

        if(atlas_lyr):
            
            atlas_lyr.selectAll()
            regions = set(map(lambda f:f.attribute(queryColumn), atlas_lyr.getSelectedFeatures()))
            atlas_lyr.removeSelection()
           
            for region in regions:
                query = "\"" + queryColumn + "\" = \'" + region + "\'"
                atlas_lyr.selectByExpression(query)
                selection_extent = atlas_lyr.boundingBoxOfSelected()
                map_frame.setExtent(selection_extent)
                map_frame.zoomToExtent(selection_extent)
                sub_product_title = recipe_with_atlas.category + " map of " +'\n' +\
                    "<CLR red = '255'>Sheet - " + region + "</CLR>"
                map_no =  recipe_with_atlas.mapnumber + "_Sheet_" + region.replace(' ', '_')
                get_layout_Item("title").setText(sub_product_title)
                get_layout_Item("map_no").setText(map_no)
                atlas_lyr.removeSelection()
                pdfFileName = recipe_with_atlas.core_file_name + "-" + \
                    slugify(region) + "-" + str(self.hum_event.default_pdf_res_dpi) + "dpi.pdf"
                pdfFileLocation = os.path.join(export_dir, pdfFileName)
                recipe_with_atlas.zip_file_contents.append(pdfFileLocation)
                logging.info('About to export atlas page for region; {}.'.format(region))
                exportSettings = QgsLayoutExporter.PdfExportSettings()
                exportSettings.dpi = double(self.hum_event.default_pdf_res_dpi)
                exporter = QgsLayoutExporter(layout)
                exporter.exportToPdf(pdfFileLocation,exportSettings)
                # arc_layout.exportToPDF(pdfFileLocation, resolution=int(self.hum_event.default_pdf_res_dpi))
                logging.info('Completed exporting atlas page for for region; {}.'.format(region))


    def _export_atlas_old(self, recipe_with_atlas, arc_mxd, export_dir):
        """
        Exports each individual page for recipes which contain an atlas definition
        """
        pass
        if not recipe_with_atlas.atlas:
            raise ValueError('Cannot export atlas. The specified recipe does not contain an atlas definition')



        recipe_frame = recipe_with_atlas.get_frame(recipe_with_atlas.atlas.map_frame)
        recipe_lyr = recipe_frame.get_layer(recipe_with_atlas.atlas.layer_name)
        queryColumn = recipe_with_atlas.atlas.column_name

        lyr_index = recipe_frame.layers.index(recipe_lyr)

        regions = list()

        for region in regions:
            query = "\"" + queryColumn + "\" = \'" + region + "\'"







            logging.info('About to export atlas page for region; {}.'.format(region))
            
            logging.info('Completed exporting atlas page for for region; {}.'.format(region))



    def export_jpeg(self, recipe, arc_mxd):
        # JPEG
        jpeg_fname = recipe.core_file_name+"-"+str(self.hum_event.default_jpeg_res_dpi) + "dpi.jpg"
        jpeg_fpath = os.path.join(recipe.export_path, jpeg_fname)
        recipe.export_metadata["jpgfilename"] = jpeg_fname
        pdf_fname = recipe.core_file_name+"-"+str(self.hum_event.default_pdf_res_dpi) + "dpi.pdf"
        pdf_fpath = os.path.join(recipe.export_path, pdf_fname)
        convert_from_path(pdf_fpath, 300)[0].save(jpeg_fpath, 'JPEG')
        jpeg_fsize = os.path.getsize(jpeg_fpath)
        recipe.export_metadata["jpgfilesize"] = jpeg_fsize
        return jpeg_fpath

    def export_pdf(self, recipe, arc_mxd):
        import traceback


        # PDF
        try :
            pdf_fname = recipe.core_file_name+"-"+str(self.hum_event.default_pdf_res_dpi) + "dpi.pdf"
            pdf_fpath = os.path.join(recipe.export_path, pdf_fname)
            recipe.export_metadata["pdffilename"] = pdf_fname

            qgs_project = QgsProject().instance()
            lManager = qgs_project.layoutManager()        
            layout  = lManager.printLayouts().pop()
            logging.info(f"laout pages before export {len(layout.pageCollection().pages())}")
            
            
            main_map = get_layout_Item(recipe.principal_map_frame,re.findall("^\w+_\d+(.\d+)*_(.*)$",os.path.split(recipe.template_path)[1].replace(".qpt",""))[0][-1])

            logging.info(f" mapLayer to render {[lyr.name() for lyr in main_map.layersToRender()]}")
            layers = main_map.layers()#layerTreeRoot().findLayers()
            logging.info(f"loaded main map <{main_map.displayName()}> contains layers {[lyr.name() for lyr in main_map.layers()]}")
            exportSettings = QgsLayoutExporter.PdfExportSettings()
            #map_settings = main_map.mapSettings(rect, includeLayerSettings = False) 
            exporter = QgsLayoutExporter(layout)
            logging.info(f"layout exporter created ")                  
            qgs_project.write()
            logging.info(f"layout export dpi param setted -exporting to pdf {pdf_fpath}")
            #mod br
            #tempPath = "export.pdf"
            result = exporter.exportToPdf(pdf_fpath,exportSettings) #pdf_fpath,exportSettings))")
            #result = exporter.exportToPdfs(layout.atlas(),os.getcwd(), exportSettings)
            logging.info(f"export Done status <{result}>")
            pdf_fsize = os.path.getsize(pdf_fpath)
            recipe.export_metadata["pdffilesize"] = pdf_fsize

        except Exception: 
            logging.info(f"booooooooooooooooooooooooom {traceback.format_exc()}")

        
        return pdf_fpath

    def export_png_thumbnail(self, recipe, arc_mxd):
        # PNG Thumbnail.  Need to create a larger image first.
        # If this isn't done, the thumbnail is pixelated amd doesn't look good
        tmp_fname = "tmp-thumbnail.png"
        tmp_fpath = os.path.join(recipe.export_path, tmp_fname)
        pdf_fname = recipe.core_file_name+"-"+str(self.hum_event.default_pdf_res_dpi) + "dpi.pdf"
        pdf_fpath = os.path.join(recipe.export_path, pdf_fname)
        convert_from_path(pdf_fpath, 300)[0].save(tmp_fpath, 'PNG')
        png_fname = "thumbnail.png"
        png_fpath = os.path.join(recipe.export_path, png_fname)
        # Resize the thumbnail
        fd_img = open(tmp_fpath, 'r+b')
        img = Image.open(fd_img)
        img = resizeimage.resize('thumbnail', img, [140, 99])
        img.save(png_fpath, img.format)
        fd_img.close()
        # Remove the temporary larger thumbnail
        os.remove(tmp_fpath)
        return png_fpath
