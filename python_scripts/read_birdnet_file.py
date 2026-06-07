# Veilige reader met debug logging
FILE = '/config/www/birds/file_map_v1.json'
DEBUG = '/config/python_scripts/read_birdnet_file.debug.txt'

def _get_prev_file_map():
    prev = hass.states.get('sensor.birdnet_file_map')
    if prev and prev.attributes and 'file_map' in prev.attributes:
        return prev.attributes.get('file_map')
    return '{}'

err = ''
try:
    with open(FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content or not content.strip():
            raise Exception("Empty content")
except Exception as e:
    err = str(e)
    content = _get_prev_file_map()

state = str(len(content))
attributes = {
    'friendly_name': 'BirdNET File Map',
    'file_map': content,
    'debug_error': err
}

# probeer state te zetten en log resultaat naar debug file
try:
    hass.states.set('sensor.birdnet_file_map', state, attributes)
    with open(DEBUG, 'a') as d:
        d.write('OK: set state={}, len(file_map)={}\\n'.format(state, len(content)))
        if err:
            d.write('WARN: exception when reading file: {}\\n'.format(err))
except Exception as e:
    with open(DEBUG, 'a') as d:
        d.write('ERROR: exception when setting state: {}\\n'.format(str(e)))