<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.40.2-Bratislava">
  <renderer-v2 type="categorizedSymbol" attr="outlier_category" enableorderby="0" referencescale="-1" forceraster="0" symbollevels="0">
    <categories>
      <category label="No outliers (under neighbor threshold)" type="string" render="true" uuid="{0ceface9-fd50-43ea-bd60-8559971546fc}" value="00" symbol="0"/>
      <category label="No outliers (equal to or above neighbor threshold)" type="string" render="true" uuid="{bba75a09-7a62-4adc-96cc-c2c18862d559}" value="01" symbol="1"/>
      <category label="Distance outlier (under neighbor threshold)" type="string" render="true" uuid="{430e07bb-67ff-4ad9-a880-bb5556452cf0}" value="10" symbol="2"/>
      <category label="Distance outlier (equal to or above neighbor threshold)" type="string" render="true" uuid="{27dcf5bc-731a-4437-8838-e459fe355c46}" value="11" symbol="3"/>
      <category label="Bearing outlier (under neighbor threshold)" type="string" render="true" uuid="{56b5db72-1d9a-4f0a-b72b-b3e0dc1f8c99}" value="20" symbol="4"/>
      <category label="Bearing outlier (equal to or above neighbor threshold)" type="string" render="true" uuid="{c3e591f1-e310-4920-8828-f67317a67481}" value="21" symbol="5"/>
      <category label="Distance &amp; bearing outliers (under neighbor threshold)" type="string" render="true" uuid="{cac7f7fb-9562-4cc8-bc60-b5342b7c5d53}" value="30" symbol="6"/>
      <category label="Distance &amp; bearing outliers (equal to or above neighbor threshold)" type="string" render="true" uuid="{68b65f6f-415e-49b6-aa05-e75261afb5cc}" value="31" symbol="7"/>
      <category label="Mahaladonis distance (under neighbor threshold)" type="string" render="true" uuid="{f788dd38-e9f9-4259-b86e-0a562be76c93}" value="40" symbol="8"/>
      <category label="Mahaladonis distance (equal to or above neighbor threshold)" type="string" render="true" uuid="{87355926-cf37-42c9-97ec-0585a8b9b743}" value="41" symbol="9"/>
    </categories>
    <symbols>
      <symbol name="0" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{30bde1ba-c75b-4756-86e2-deea1e21ff10}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@0@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{f75fc4d8-f27e-4ac2-ba52-3ee75eadc246}" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="0,255,0,255,rgb:0,1,0,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="0.5"/>
                <Option name="line_width_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="1" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@1@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" class="SimpleFill" pass="0">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="0,255,0,255,rgb:0,1,0,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0.26"/>
                <Option name="outline_width_unit" type="QString" value="MM"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="2" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@2@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{4ffc0b4f-f17b-4be2-a7e3-502e61f4504e}" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="255,0,0,255,rgb:1,0,0,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="0.5"/>
                <Option name="line_width_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="3" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@3@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" class="SimpleFill" pass="0">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="255,0,0,255,rgb:1,0,0,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0.26"/>
                <Option name="outline_width_unit" type="QString" value="MM"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="4" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@4@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{0e5efe46-53c5-4da9-a3b3-b6d28dbbd57d}" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="0,0,255,255,rgb:0,0,1,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="0.5"/>
                <Option name="line_width_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="5" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@5@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" class="SimpleFill" pass="0">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="0,0,255,255,rgb:0,0,1,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0.26"/>
                <Option name="outline_width_unit" type="QString" value="MM"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="6" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@6@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{b8d0e589-e2ff-4bfc-864f-950c6a5a61d3}" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="128,0,128,255,rgb:0.50196078431372548,0,0.50196078431372548,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="0.5"/>
                <Option name="line_width_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="7" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@7@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" class="SimpleFill" pass="0">
              <Option type="Map">
                <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="color" type="QString" value="128,0,128,255,rgb:0.50196078431372548,0,0.50196078431372548,1"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="offset" type="QString" value="0,0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="outline_color" type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0"/>
                <Option name="outline_style" type="QString" value="solid"/>
                <Option name="outline_width" type="QString" value="0.26"/>
                <Option name="outline_width_unit" type="QString" value="MM"/>
                <Option name="style" type="QString" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="8" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@8@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{b8d0e589-e2ff-4bfc-864f-950c6a5a61d3}" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="255,127,0,255,rgb:1,0.49803921568627452,0,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="0.5"/>
                <Option name="line_width_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="9" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" class="ArrowLine" pass="0">
          <Option type="Map">
            <Option name="arrow_start_width" type="QString" value="1"/>
            <Option name="arrow_start_width_unit" type="QString" value="MM"/>
            <Option name="arrow_start_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="arrow_type" type="QString" value="0"/>
            <Option name="arrow_width" type="QString" value="1"/>
            <Option name="arrow_width_unit" type="QString" value="MM"/>
            <Option name="arrow_width_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_length" type="QString" value="1.5"/>
            <Option name="head_length_unit" type="QString" value="MM"/>
            <Option name="head_length_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_thickness" type="QString" value="1.5"/>
            <Option name="head_thickness_unit" type="QString" value="MM"/>
            <Option name="head_thickness_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="head_type" type="QString" value="0"/>
            <Option name="is_curved" type="QString" value="1"/>
            <Option name="is_repeated" type="QString" value="1"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="offset_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="ring_filter" type="QString" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@9@0" type="fill" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" id="{b8d0e589-e2ff-4bfc-864f-950c6a5a61d3}" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option name="align_dash_pattern" type="QString" value="0"/>
                <Option name="capstyle" type="QString" value="square"/>
                <Option name="customdash" type="QString" value="5;2"/>
                <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="customdash_unit" type="QString" value="MM"/>
                <Option name="dash_pattern_offset" type="QString" value="0"/>
                <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
                <Option name="draw_inside_polygon" type="QString" value="0"/>
                <Option name="joinstyle" type="QString" value="bevel"/>
                <Option name="line_color" type="QString" value="255,127,0,255,rgb:1,0.49803921568627452,0,1"/>
                <Option name="line_style" type="QString" value="solid"/>
                <Option name="line_width" type="QString" value="0.5"/>
                <Option name="line_width_unit" type="QString" value="MM"/>
                <Option name="offset" type="QString" value="0"/>
                <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="offset_unit" type="QString" value="MM"/>
                <Option name="ring_filter" type="QString" value="0"/>
                <Option name="trim_distance_end" type="QString" value="0"/>
                <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_end_unit" type="QString" value="MM"/>
                <Option name="trim_distance_start" type="QString" value="0"/>
                <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
                <Option name="trim_distance_start_unit" type="QString" value="MM"/>
                <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
                <Option name="use_custom_dash" type="QString" value="0"/>
                <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol name="0" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{d21990b5-3095-4666-9f93-e5db7c86a279}" class="SimpleLine" pass="0">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="231,113,72,255,rgb:0.90588235294117647,0.44313725490196076,0.28235294117647058,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="0.26"/>
            <Option name="line_width_unit" type="QString" value="MM"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp name="[source]" type="preset">
      <Option type="Map">
        <Option name="preset_color_0" type="QString" value="250,75,60,255,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,1"/>
        <Option name="preset_color_name_0" type="QString" value="#fa4b3c"/>
        <Option name="rampType" type="QString" value="preset"/>
      </Option>
    </colorramp>
    <rotation/>
    <sizescale/>
    <data-defined-properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties"/>
        <Option name="type" type="QString" value="collection"/>
      </Option>
    </data-defined-properties>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol name="" type="line" is_animated="0" frame_rate="10" force_rhr="0" clip_to_extent="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" id="{2e7c0962-87c9-4924-b030-01e1450119b3}" class="SimpleLine" pass="0">
          <Option type="Map">
            <Option name="align_dash_pattern" type="QString" value="0"/>
            <Option name="capstyle" type="QString" value="square"/>
            <Option name="customdash" type="QString" value="5;2"/>
            <Option name="customdash_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="customdash_unit" type="QString" value="MM"/>
            <Option name="dash_pattern_offset" type="QString" value="0"/>
            <Option name="dash_pattern_offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="dash_pattern_offset_unit" type="QString" value="MM"/>
            <Option name="draw_inside_polygon" type="QString" value="0"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="line_color" type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1"/>
            <Option name="line_style" type="QString" value="solid"/>
            <Option name="line_width" type="QString" value="0.26"/>
            <Option name="line_width_unit" type="QString" value="MM"/>
            <Option name="offset" type="QString" value="0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="ring_filter" type="QString" value="0"/>
            <Option name="trim_distance_end" type="QString" value="0"/>
            <Option name="trim_distance_end_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_end_unit" type="QString" value="MM"/>
            <Option name="trim_distance_start" type="QString" value="0"/>
            <Option name="trim_distance_start_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="trim_distance_start_unit" type="QString" value="MM"/>
            <Option name="tweak_dash_pattern_on_corners" type="QString" value="0"/>
            <Option name="use_custom_dash" type="QString" value="0"/>
            <Option name="width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>1</layerGeometryType>
</qgis>
