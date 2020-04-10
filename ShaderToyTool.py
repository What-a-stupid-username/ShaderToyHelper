import requests;
import json;
import urllib;
import os;
import socket;

url = 'https://www.shadertoy.com/shadertoy';

def DownLoad(url, path):
    socket.setdefaulttimeout(30)
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except:
        count = 1
        print('Download Time out, retry ' + str(count))
        while count <= 2:
            try:
                urllib.request.urlretrieve(url, path)                                             
                return True
            except:
                count += 1
                print('Download Time out, retry ' + str(count))
    return False

while 1:
    shader_id_str = input('Please given url\n     as \'https://www.shadertoy.com/view/4dSBDt\'\n     or \'4dSBDt\'\n')
    print('')
    if shader_id_str.find('https://www.shadertoy.com/') != -1:
        shader_id = shader_id_str.split('/')[-1]
        print('Shader ID:   ' + shader_id)
    else:
        shader_id = shader_id_str
        print('Shader ID:   ' + shader_id)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Referer': ('https://www.shadertoy.com/view/' + shader_id)
    };

    data = '{ \"shaders\" : [\"' + shader_id + '\"] }';
    data = "s=" + urllib.parse.quote(data) + "&nt=1&nl=1";
    

    try:
        r = requests.post(url, headers = headers, data = data, timeout = 20);
        jstr = r.content.decode()[1:-1];
        dct = json.loads(jstr);
        print('Name:        ' + dct['info']['name'])
        print('Author:      ' + dct['info']['username'])
        print('Description: ' + dct['info']['description'])
        print('')
        save_dir = os.getcwd() + '\\' + dct['info']['name']
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        dct = dct['renderpass']
        with open(save_dir + '\\' + 'pass_dependency.txt', "w") as dp_f:
            for render_pass in dct:
                pass_name = render_pass['name']
                inputs = render_pass['inputs']
                print("Pass name: " + pass_name)
                code = render_pass['code']
                with open(save_dir + '\\' + pass_name + '.code.txt', "w") as f:
                    _ = f.write(code)
                for input_res in inputs:
                    if input_res['type'] != 'buffer':
                        res_url = 'https://www.shadertoy.com' + input_res['filepath']
                        channel = input_res['channel']
                        print('   Channel ' + str(channel) + ": " + res_url)
                        type_name = res_url.split('.')[-1]
                        file_name = save_dir + '\\' + pass_name + '.' + str(channel) + '.' + type_name
                        if not DownLoad(res_url, file_name):
                            print("Download faild, skip it.")
                            os.remove(file_name)
                            with open(file_name + '.url.txt', "w") as f:
                                _ = f.write(res_url);
                        if (input_res['type'] == 'volume'):
                            bin_file = open(file_name,'rb').read()
                            w = int.from_bytes(bin_file[4:8], byteorder='little', signed=False)
                            h = int.from_bytes(bin_file[8:12], byteorder='little', signed=False)
                            d = int.from_bytes(bin_file[12:16], byteorder='little', signed=False)
                            channel_count = int.from_bytes(bin_file[16:20], byteorder='little', signed=False)
                            with open(file_name + '.volume.txt', "w") as f:
                                _ = f.write('Width:' + str(w) + ', Height:' + str(h) + ', Depth:' + str(d) + ', Channel:' + str(channel_count) + '\n')
                                _ = f.write('Ordered first by Channel, then u dimension, then v dimension, then depth slice.\n')
                                for x in bin_file[20:]:
                                    _ = f.write(str(x) + ', ')
                            os.remove(file_name)
                    else:
                         _ = dp_f.write(pass_name + '.' + str(input_res['channel']) + ': ' + input_res['filepath'].split('/')[-1].split('.')[-2].replace('buffer00', 'Buf A').replace('buffer01', 'Buf B').replace('buffer02', 'Buf C') + '\n')

        print('')       
        continue 
    except requests.exceptions.ConnectionError:
        print('\nConnection Error\n')
    except requests.exceptions.ChunkedEncodingError:
        print('\nChunked Encoding Error\n')
    except requests.exceptions.Timeout:
        print('\nTime Out Error\n')
    # finally:
    except:
        print('\nUnknown Error\n')