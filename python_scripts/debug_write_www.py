# Debug: schrijf een file naar /config/www zodat we weten of het script draait
try:
    with open('/config/www/read_birdnet_file_ran.txt', 'a') as f:
        f.write('ran\n')
except Exception as e:
    hass.states.set('sensor.debug_write_www_error', 'ERROR', {'error': str(e)})