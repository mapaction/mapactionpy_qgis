import logging
import os
import json
from PIL import Image
from resizeimage import resizeimage
from slugify import slugify
from mapactionpy_qgis.map_chef import MapChef, get_map_scale, get_map_spatial_ref
from mapactionpy_controller.plugin_base import BaseRunnerPlugin
from qgis.core import (
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
    QgsProject,
    QgsFillSymbol,
)
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


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s %(message)s'
)


class ArcMapRunner(BaseRunnerPlugin):
    """
    ArcMapRunner - Executes the ArcMap automation methods
    """

    def __init__(self,
                 hum_event):
        super(ArcMapRunner, self).__init__(hum_event)

        self.exportMap = False
        self.minx = 0
        self.miny = 0
        self.maxx = 0
        self.maxy = 0
        self.chef = None

    def build_project_files(self, **kwargs):
        recipe = kwargs['state']
        qgs_project = QgsProject.instance()
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

        for metric_key in ['area', 'width', 'name']:
            max_size = max([df_detail[metric_key] for df_detail in full_details])
            sub_list = [df_detail for df_detail in full_details if df_detail[metric_key] == max_size]
            if len(sub_list) == 1:
                return sub_list[0]['df']

            full_details = sub_list    
    def get_layout_maps():
        pass
    def get_aspect_ratios_of_templates(self, possible_templates, recipe):
        """
        Calculates the aspect ratio of the principal map frame within the list of templates.

        @param possible_templates: A list of paths to possible templates.
        @param recipe: A MapRecipe which is used to determine the principal map frame.
        @returns: A list of tuples. For each tuple the first element is the path to the template. The second
                  element is the aspect ratio of the largest* map frame within that template.
                  See `_get_largest_map_frame` for the description of hour largest is determined.
        """
        logging.debug('Calculating the aspect ratio of the largest map frame within the list of templates.')
        results = []
        project = QgsProject.instance() 
        for template in possible_templates:
            principal_layout = QgsPrintLayout(project)
            principal_layout.setName(os.path.basename(template))
            template_content = None
            doc = None
            with open(template) as f:
                template_content = f.read()
                doc = QDomDocument()
                doc.setContent(template_content)
            layout_items ,status = principal_layout.loadFromTemplate(doc, QgsReadWriteContext(), True)
            main_layout_map = list(filter(lambda el:isinstance(el,QgsLayoutItemMap) and el.displayName() == recipe.principal_map_frame ,layout_items)).pop()
            aspect_ratio =main_layout_map.extent().width() / main_layout_map.extent().height() 
            results.append((template, aspect_ratio))
            logging.debug('Calculated aspect ratio= {} for template={}'.format(aspect_ratio, template))
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

    def _export_atlas(self, recipe_with_atlas, arc_mxd, export_dir):
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
        pass
        jpeg_fname = recipe.core_file_name+"-"+str(self.hum_event.default_jpeg_res_dpi) + "dpi.jpg"
        jpeg_fpath = os.path.join(recipe.export_path, jpeg_fname)
        recipe.export_metadata["jpgfilename"] = jpeg_fname
        jpeg_fsize = os.path.getsize(jpeg_fpath)
        recipe.export_metadata["jpgfilesize"] = jpeg_fsize
        return jpeg_fpath

    def export_pdf(self, recipe, arc_mxd):
        pass
        pdf_fname = recipe.core_file_name+"-"+str(self.hum_event.default_pdf_res_dpi) + "dpi.pdf"
        pdf_fpath = os.path.join(recipe.export_path, pdf_fname)
        recipe.export_metadata["pdffilename"] = pdf_fname
        pdf_fsize = os.path.getsize(pdf_fpath)
        recipe.export_metadata["pdffilesize"] = pdf_fsize
        return pdf_fpath

    def export_png_thumbnail(self, recipe, arc_mxd):
        pass
        tmp_fname = "tmp-thumbnail.png"
        tmp_fpath = os.path.join(recipe.export_path, tmp_fname)

        png_fname = "thumbnail.png"
        png_fpath = os.path.join(recipe.export_path, png_fname)

        fd_img = open(tmp_fpath, 'r+b')
        img = Image.open(fd_img)
        img = resizeimage.resize('thumbnail', img, [140, 99])
        img.save(png_fpath, img.format)
        fd_img.close()

        os.remove(tmp_fpath)
        return png_fpath
