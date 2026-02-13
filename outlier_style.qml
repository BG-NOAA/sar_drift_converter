<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.40.2-Bratislava" styleCategories="Symbology">
  <renderer-v2 attr="outlier_category" referencescale="-1" enableorderby="0" symbollevels="0" type="categorizedSymbol" forceraster="0">
    <categories>
      <category symbol="0" label="No outliers (under neighbor threshold)" type="string" value="00" render="true" uuid="{0ceface9-fd50-43ea-bd60-8559971546fc}"/>
      <category symbol="1" label="No outliers (equal to or above neighbor threshold)" type="string" value="01" render="true" uuid="{bba75a09-7a62-4adc-96cc-c2c18862d559}"/>
      <category symbol="2" label="Distance outlier (under neighbor threshold)" type="string" value="10" render="true" uuid="{430e07bb-67ff-4ad9-a880-bb5556452cf0}"/>
      <category symbol="3" label="Distance outlier (equal to or above neighbor threshold)" type="string" value="11" render="true" uuid="{27dcf5bc-731a-4437-8838-e459fe355c46}"/>
      <category symbol="4" label="Bearing outlier (under neighbor threshold)" type="string" value="20" render="true" uuid="{56b5db72-1d9a-4f0a-b72b-b3e0dc1f8c99}"/>
      <category symbol="5" label="Bearing outlier (equal to or above neighbor threshold)" type="string" value="21" render="true" uuid="{c3e591f1-e310-4920-8828-f67317a67481}"/>
      <category symbol="6" label="Distance &amp; bearing outliers (under neighbor threshold)" type="string" value="30" render="true" uuid="{cac7f7fb-9562-4cc8-bc60-b5342b7c5d53}"/>
      <category symbol="7" label="Distance &amp; bearing outliers (equal to or above neighbor threshold)" type="string" value="31" render="true" uuid="{68b65f6f-415e-49b6-aa05-e75261afb5cc}"/>
    </categories>
    <symbols>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="0" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{30bde1ba-c75b-4756-86e2-deea1e21ff10}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@0@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleLine" locked="0" id="{f75fc4d8-f27e-4ac2-ba52-3ee75eadc246}" pass="0">
              <Option type="Map">
                <Option type="QString" value="0" name="align_dash_pattern"/>
                <Option type="QString" value="square" name="capstyle"/>
                <Option type="QString" value="5;2" name="customdash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
                <Option type="QString" value="MM" name="customdash_unit"/>
                <Option type="QString" value="0" name="dash_pattern_offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
                <Option type="QString" value="0" name="draw_inside_polygon"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,255,0,255,rgb:0,1,0,1" name="line_color"/>
                <Option type="QString" value="solid" name="line_style"/>
                <Option type="QString" value="0.5" name="line_width"/>
                <Option type="QString" value="MM" name="line_width_unit"/>
                <Option type="QString" value="0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="0" name="trim_distance_end"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_end_unit"/>
                <Option type="QString" value="0" name="trim_distance_start"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_start_unit"/>
                <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
                <Option type="QString" value="0" name="use_custom_dash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="1" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@1@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleFill" locked="0" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" pass="0">
              <Option type="Map">
                <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                <Option type="QString" value="0,255,0,255,rgb:0,1,0,1" name="color"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0" name="outline_color"/>
                <Option type="QString" value="solid" name="outline_style"/>
                <Option type="QString" value="0.26" name="outline_width"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="solid" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="2" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@2@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleLine" locked="0" id="{4ffc0b4f-f17b-4be2-a7e3-502e61f4504e}" pass="0">
              <Option type="Map">
                <Option type="QString" value="0" name="align_dash_pattern"/>
                <Option type="QString" value="square" name="capstyle"/>
                <Option type="QString" value="5;2" name="customdash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
                <Option type="QString" value="MM" name="customdash_unit"/>
                <Option type="QString" value="0" name="dash_pattern_offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
                <Option type="QString" value="0" name="draw_inside_polygon"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="255,0,0,255,rgb:1,0,0,1" name="line_color"/>
                <Option type="QString" value="solid" name="line_style"/>
                <Option type="QString" value="0.5" name="line_width"/>
                <Option type="QString" value="MM" name="line_width_unit"/>
                <Option type="QString" value="0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="0" name="trim_distance_end"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_end_unit"/>
                <Option type="QString" value="0" name="trim_distance_start"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_start_unit"/>
                <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
                <Option type="QString" value="0" name="use_custom_dash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="3" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@3@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleFill" locked="0" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" pass="0">
              <Option type="Map">
                <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                <Option type="QString" value="255,0,0,255,rgb:1,0,0,1" name="color"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0" name="outline_color"/>
                <Option type="QString" value="solid" name="outline_style"/>
                <Option type="QString" value="0.26" name="outline_width"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="solid" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="4" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@4@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleLine" locked="0" id="{0e5efe46-53c5-4da9-a3b3-b6d28dbbd57d}" pass="0">
              <Option type="Map">
                <Option type="QString" value="0" name="align_dash_pattern"/>
                <Option type="QString" value="square" name="capstyle"/>
                <Option type="QString" value="5;2" name="customdash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
                <Option type="QString" value="MM" name="customdash_unit"/>
                <Option type="QString" value="0" name="dash_pattern_offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
                <Option type="QString" value="0" name="draw_inside_polygon"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,0,255,255,rgb:0,0,1,1" name="line_color"/>
                <Option type="QString" value="solid" name="line_style"/>
                <Option type="QString" value="0.5" name="line_width"/>
                <Option type="QString" value="MM" name="line_width_unit"/>
                <Option type="QString" value="0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="0" name="trim_distance_end"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_end_unit"/>
                <Option type="QString" value="0" name="trim_distance_start"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_start_unit"/>
                <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
                <Option type="QString" value="0" name="use_custom_dash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="5" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@5@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleFill" locked="0" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" pass="0">
              <Option type="Map">
                <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                <Option type="QString" value="0,0,255,255,rgb:0,0,1,1" name="color"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0" name="outline_color"/>
                <Option type="QString" value="solid" name="outline_style"/>
                <Option type="QString" value="0.26" name="outline_width"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="solid" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="6" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@6@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleLine" locked="0" id="{b8d0e589-e2ff-4bfc-864f-950c6a5a61d3}" pass="0">
              <Option type="Map">
                <Option type="QString" value="0" name="align_dash_pattern"/>
                <Option type="QString" value="square" name="capstyle"/>
                <Option type="QString" value="5;2" name="customdash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
                <Option type="QString" value="MM" name="customdash_unit"/>
                <Option type="QString" value="0" name="dash_pattern_offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
                <Option type="QString" value="0" name="draw_inside_polygon"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="128,0,128,255,rgb:0.50196078431372548,0,0.50196078431372548,1" name="line_color"/>
                <Option type="QString" value="solid" name="line_style"/>
                <Option type="QString" value="0.5" name="line_width"/>
                <Option type="QString" value="MM" name="line_width_unit"/>
                <Option type="QString" value="0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="0" name="ring_filter"/>
                <Option type="QString" value="0" name="trim_distance_end"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_end_unit"/>
                <Option type="QString" value="0" name="trim_distance_start"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
                <Option type="QString" value="MM" name="trim_distance_start_unit"/>
                <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
                <Option type="QString" value="0" name="use_custom_dash"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="7" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="ArrowLine" locked="0" id="{21dc0b2d-b199-40d9-bf09-868867eab3ad}" pass="0">
          <Option type="Map">
            <Option type="QString" value="1" name="arrow_start_width"/>
            <Option type="QString" value="MM" name="arrow_start_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_start_width_unit_scale"/>
            <Option type="QString" value="0" name="arrow_type"/>
            <Option type="QString" value="1" name="arrow_width"/>
            <Option type="QString" value="MM" name="arrow_width_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="arrow_width_unit_scale"/>
            <Option type="QString" value="1.5" name="head_length"/>
            <Option type="QString" value="MM" name="head_length_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_length_unit_scale"/>
            <Option type="QString" value="1.5" name="head_thickness"/>
            <Option type="QString" value="MM" name="head_thickness_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="head_thickness_unit_scale"/>
            <Option type="QString" value="0" name="head_type"/>
            <Option type="QString" value="1" name="is_curved"/>
            <Option type="QString" value="1" name="is_repeated"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_unit_scale"/>
            <Option type="QString" value="0" name="ring_filter"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="fill" force_rhr="0" name="@7@0" is_animated="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" class="SimpleFill" locked="0" id="{219f21cb-934f-4059-a1d6-dff8ea89e13a}" pass="0">
              <Option type="Map">
                <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                <Option type="QString" value="128,0,128,255,rgb:0.50196078431372548,0,0.50196078431372548,1" name="color"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="250,75,60,0,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,0" name="outline_color"/>
                <Option type="QString" value="solid" name="outline_style"/>
                <Option type="QString" value="0.26" name="outline_width"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="solid" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="0" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleLine" locked="0" id="{d21990b5-3095-4666-9f93-e5db7c86a279}" pass="0">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="231,113,72,255,rgb:0.90588235294117647,0.44313725490196076,0.28235294117647058,1" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.26" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="preset" name="[source]">
      <Option type="Map">
        <Option type="QString" value="250,75,60,255,rgb:0.98039215686274506,0.29411764705882354,0.23529411764705882,1" name="preset_color_0"/>
        <Option type="QString" value="#fa4b3c" name="preset_color_name_0"/>
        <Option type="QString" value="preset" name="rampType"/>
      </Option>
    </colorramp>
    <rotation/>
    <sizescale/>
    <data-defined-properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </data-defined-properties>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol frame_rate="10" clip_to_extent="1" alpha="1" type="line" force_rhr="0" name="" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleLine" locked="0" id="{2e7c0962-87c9-4924-b030-01e1450119b3}" pass="0">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="35,35,35,255,rgb:0.13725490196078433,0.13725490196078433,0.13725490196078433,1" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.26" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
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
