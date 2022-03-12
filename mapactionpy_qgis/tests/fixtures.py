# flake8: noqa
import json
from os import path

fixture_recipe_minimal = (
    '''{
      "mapnumber": "MA001",
      "category": "Reference",
      "core_file_name": "ma001-v01-overview-of-mozambique-with-topography-displayed",
      "product": "{e.country_name}: Overview Map",
      "summary": "Overview of {e.country_name} with topography displayed",
      "export": true,
      "template": "reference",
      "principal_map_frame": "Main map",
      "map_frames": [
         {
            "name": "Main map",
            "crs": "EPSG:3857",
            "layers": [
               {
                  "name": "mainmap-admn-ad1-py-s0-reference"
               }
            ]
         }
      ]
   }'''
)


_temp_recipe_processed_by_controller = (
    r'''{
    "mapnumber": "MA9999",
    "category": "Reference",
    "export": true,
    "product": "Every layer",
    "map_frames": [
        {
            "name": "Main map",
            "layers": [
                {
                    "name": "mainmap-tran-por-pt-s0-allmaps",
                    "reg_exp": "^hnd_tran_por_pt_s(u|[0-5])_(.*?)_([phm][phm])(.*?).shp$",
                    "definition_query": "",
                    "schema_definition": "null-schema.yml",
                    "display": true,
                    "add_to_legend": true,
                    "label_classes": [],
                    "layer_file_path": "C:\\Users\\BLAIT\\Desktop\\prepared-country-data\\2021_common_RDS_files\\3_Mapping\\31_Resources\\312_Layer_files\\mainmap-tran-por-pt-s0-allmaps.lyr",
                    "data_schema": true,
                    "layer_file_checksum": "5b46d795fd3fad04a9a423c87a32244a",
                    "data_source_checksum": "769c3b668e0bf483c2d54b79a5849479",
                    "error_messages": [],
                    "success": true,
                    "visible": true,
                    "crs": "epsg:4326",
                    "data_name": "hnd_tran_por_pt_s0_worldports_pp",
                    "data_source_path": "C:\\Users\\BLAIT\\Desktop\\prepared-country-data\\honduras\\GIS/2_Active_Data\\232_tran\\hnd_tran_por_pt_s0_worldports_pp.shp",
                    "extent": [
                        -87.95,
                        13.4,
                        -85.95,
                        16.316666666666666
                    ]
                },
                {
                    "name": "mainmap-stle-stl-pt-s0-allmaps",
                    "reg_exp": "^hnd_stle_stl_pt_s(u|[0-5])_(.*?)_([phm][phm])(.*?).shp$",
                    "definition_query": "",
                    "schema_definition": "settlements_pt.yml",
                    "display": true,
                    "add_to_legend": true,
                    "label_classes": [
                        {
                            "class_name": "National Capital",
                            "expression": "[name]",
                            "sql_query": "(\"fclass\" = 'national_capital')",
                            "show_class_labels": true
                        },
                        {
                            "class_name": "Admin 1 Capital",
                            "expression": "[name]",
                            "sql_query": "(\"fclass\" = 'town')",
                            "show_class_labels": true
                        }
                    ],
                    "layer_file_path": "C:\\Users\\BLAIT\\Desktop\\prepared-country-data\\2021_common_RDS_files\\3_Mapping\\31_Resources\\312_Layer_files\\mainmap-stle-stl-pt-s0-allmaps.lyr",
                    "data_schema": {
                        "required": [
                            "name",
                            "fclass"
                        ],
                        "properties": {
                            "geometry_type": {
                                "items": {
                                    "enum": [
                                        "MultiPoint",
                                        "Point"
                                    ]
                                },
                                "additionalItems": false
                            }
                        }
                    },
                    "layer_file_checksum": "ae1c9df2071e46574a2341fe4c0f3b69",
                    "data_source_checksum": "642d81f46039f5e372561ad17a8101a5",
                    "error_messages": [],
                    "success": true,
                    "visible": true,
                    "crs": "epsg:4326",
                    "data_name": "hnd_stle_stl_pt_s0_osm_pp",
                    "data_source_path": "C:\\Users\\BLAIT\\Desktop\\prepared-country-data\\honduras\\GIS/2_Active_Data\\229_stle\\hnd_stle_stl_pt_s0_osm_pp.shp",
                    "extent": [
                        -89.3587313,
                        13.0491247,
                        -83.172006,
                        16.5032013
                    ]
                }
            ],
            "crs": "epsg:4326",
            "extent": [
                -89.35664445499998,
                12.983046638000076,
                -83.02849060999999,
                16.516793322000073
            ],
            "scale_text_element": "scale",
            "spatial_ref_text_element": "spatial_reference"
        }
    ]
   }'''
)

_temp_recipe = json.loads(_temp_recipe_processed_by_controller)
_root_dir = path.abspath(path.dirname(__file__))
_shp_path = path.join(_root_dir, 'test_data', 'test_shapefile', 'aoi_elev_cst_ln_s0_gadm_pp.shp')
_lyr_path = path.join(_root_dir, 'test_data', 'test_shapefile', 'locationmap-elev-cst-ln-s0-locationmaps.lyr')
_temp_recipe['map_frames'][0]['layers'][0]['data_source_path'] = _shp_path
_temp_recipe['map_frames'][0]['layers'][0]['layer_file_path'] = _lyr_path
fixture_recipe_processed_by_controller = json.dumps(_temp_recipe)

fixture_datasource_dictionary_ma001 = r"""
{
"settlement_points": "D:\MapAction\2019-06-12-GBR\GIS\2_Active_Data\gbr_stle_stle_pt_s0_naturalearth_pp.shp"
"airports_points": "D:\MapAction\2019-06-12-GBR\GIS\2_Active_Data\232_tran\scr_tran_air_pt_s1_ourairports_pp.shp"
}
"""


fixture_layer_description_ma001 = r"""
-
   m: Main Map
   layer-group: None
   layer-name: Settlement - Places - pt
   source-folder: 229_stle
   regex: ^ XXX_stle_stl_pt_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: "SettleType" IN('national_capital', 'city')
   visable: Yes
-
   m: Main Map
   layer-group: Transport - Points
   layer-name: Transport - Airports - pt
   source-folder: 232_tran
   regex: ^ XXX_trans_air_pt_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Transport - Points
   layer-name: Transport - Seaports - pt
   source-folder: 232_tran
   regex: ^ XXX_trans_por_pt_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Admin - Lines
   layer-name: Elevation - Coastline - ln
   source-folder: 211_elev
   regex: ^ XXX_elev_cst_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: none
   visable: Yes
-
   m: Main Map
   layer-group: Admin - Lines
   layer-name: Borders - Admin1 - ln
   source-folder: 202_admn
   regex: ^ XXX_admn_ad1_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Admin - Lines
   layer-name: Borders - Admin2 - ln
   source-folder: 202_admn
   regex: ^ XXX_admn_ad2_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Transport - Lines
   layer-name: Transport - Rail - ln
   source-folder: 232_tran
   regex: ^ XXX_tran_rrd_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Transport - Lines
   layer-name: Transport - Road - ln
   source-folder: 232_tran
   regex: ^ XXX_tran_rds_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: None
   layer-name: Cartography - Feather - pt
   source-folder: 207_carto
   regex: ^ (?!(XXX))_carto_fea_py_s0_mapaction_pp(_(.+)
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Physical
   layer-name: Physical - Waterbody - py
   source-folder: 221_phys
   regex: tbd
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Physical
   layer-name: Physical - River - ln
   source-folder: 221_phys
   regex: ^ XXX_phys_riv_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Admin - Polygons
   layer-name: Admin - Admin2 - py
   source-folder: 202_admn
   regex: ^ XXX_admn_ad2_py_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Admin - Polygons
   layer-name: Admin - Admin1 - py
   source-folder: 202_admn
   regex: ^ XXX_admn_ad1_py_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Admin - Polygons
   layer-name: Admin - AffectedCountry - py
   source-folder: 202_admn
   regex: ^ XXX_admn_ad0_py_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Admin - Polygons
   layer-name: Admin - SurroundingCountry - py
   source-folder: 202_admn
   regex: ^ (?!(XXX))_admn_ad0_py_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: ADM0_NAME <> '[reference country]'
   visable: Yes
-
   m: Main Map
   layer-group: Elevation
   layer-name: Physical - Sea - py
   source-folder: 221_phys
   regex: ^ XXX_phys_ocn_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Elevation
   layer-name: Elevation - DEM - ras
   source-folder: 211_elev
   regex: ^ XXX_elev_dem_ras_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Elevation
   layer-name: Elevation - Hillshade - ras
   source-folder: 211_elev
   regex: ^ XXX_elev_hsh_ras_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Elevation
   layer-name: Elevation - Curvature - ras
   source-folder: 211_elev
   regex: tbd
   query-definition: None
   visable: Yes
-
   m: Main Map
   layer-group: Legend
   layer-name: Legend - Road - ln
   source-folder: 232_tran
   regex: ^ XXX_tran_rds_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: No
-
   m: Main Map
   layer-group: Legend
   layer-name: Legend - WaterBody - py
   source-folder: 221_phys
   regex: tbd
   query-definition: None
   visable: No
-
   m: Main Map
   layer-group: Legend
   layer-name: Elevation - Elevation - ras
   source-folder: 211_elev
   regex: ^ XXX_elev_dem_ras_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: No
-
   m: Location Map
   layer-group: None
   layer-name: Location - Coastline - ln
   source-folder: 211_elev
   regex: ^ XXX_elev_cst_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Location Map
   layer-group: None
   layer-name: Location - Admin1 - ln
   source-folder: 202_admn
   regex: ^ XXX_admn_ad1_ln_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Location Map
   layer-group: None
   layer-name: Location - AffectedCountry - py
   source-folder: 202_admn
   regex: ^ XXX_admn_ad0_py_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: None
   visable: Yes
-
   m: Location Map
   layer-group: None
   layer-name: Location - SurroundingCountry - py
   source-folder: 202_admn
   regex: ^ (?!(XXX))_admn_ad0_py_(.*?)_(.*?)_([phm][phm])(_(.+))
   query-definition: "ADM0_NAME" <> '[reference country]'
   visable: Yes
"""
