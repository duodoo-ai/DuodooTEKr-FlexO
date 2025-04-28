-- Remove Map Box Token as it's only valid per DB url
DELETE FROM ir_config_parameter
 WHERE key = 'web_map.amap_jsapi_key';

DELETE FROM ir_config_parameter
 WHERE key = 'web_map.amap_web_service_key';

DELETE FROM ir_config_parameter
 WHERE key = 'web_map.tencent_map_key';

DELETE FROM ir_config_parameter
 WHERE key = 'web_map.token_map_box';
