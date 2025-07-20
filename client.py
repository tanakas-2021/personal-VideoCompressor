import socket
import sys
import os
import json

def protocol_header(file_size, file_name_len):
    return  file_size.to_bytes(8, "big") + file_name_len.to_bytes(1,"big")

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
server_address = config['server_address']
server_port = config['server_port']
stream_rate = config['stream_rate']

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('connecting to {}'.format(server_address, server_port))

try:
    # 接続後、サーバとクライアントが相互に読み書きができるようになります
    sock.connect((server_address, server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

try:
    filepath = input('Input filePath to upload\n')

    if filepath[-3:].lower() != 'mp4':
        raise Exception('file have to be mp4')

    # バイナリモードでファイルを読み込む
    with open(filepath, 'rb') as f:
        # ファイルの末尾に移動し、tellは開いているファイルの現在位置を返します。ファイルのサイズを取得するために使用します
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(0,0)

        if filesize > pow(2,32):
            raise Exception('file have to be below 4GB')

        filename = os.path.basename(f.name)
        # ファイル名からビット数
        filename_bits = filename.encode('utf-8')
        # protocol_header()関数を用いてヘッダ情報を作成し、ヘッダとファイル名をサーバに送信します。
        header = protocol_header(filesize, len(filename_bits))

        # ヘッダの送信
        sock.send(header)
        # ファイル名の送信
        sock.send(filename_bits)

        # 一度に1400バイトずつ読み出し、送信することにより、ファイルを送信します。Readは読み込んだビットを返します
        data = f.read(stream_rate)
        while data:
            print("Sending...")
            sock.send(data)
            data = f.read(stream_rate)
        
        state_msg = sock.recv(16).decode('utf-8')
        print(state_msg)

except FileNotFoundError as nofile_err:
    print('inputFile not found')

except Exception as e:
    print('Error: ' + str(e))

finally:
    print('closing socket')
    sock.close()