import socket
import os
import json

def get_storage_usage(dir_path:str) -> int:
    total = 0
    for dir_path, dirnames, filenames in os.walk(dir_path):
        for f in filenames:
            fp = os.path.join(dir_path, f)
            total += os.path.getsize(fp)
    return total

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
server_address = config['server_address']
server_port = config['server_port']
max_storage = config['max_storage']
dir_path = config['storage_dir']
stream_rate = config['stream_rate']

# アドレスファミリ : socket.AF_INET
# 通信方式 : SOCK_STREAM = TCP通信（信頼性あり、順番保証、コネクション型）
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((server_address, server_port))
sock.listen(1)
print('server is starting：waiting from clients')

while True:
    connection, client_address = sock.accept()
    try:
        print(f'connecting from client')

        # 8Byte:ファイルサイズの大きさ
        header = connection.recv(9)
        print(header)
        # 最初の8バイトをファイルサイズとして取得
        file_size = int.from_bytes(header[:8], 'big')
        file_name_len = int.from_bytes(header[8:9], 'big')
        state = ''
        print(f'file size is{file_size}')

        current_usage = get_storage_usage(dir_path)
        if current_usage + file_size > max_storage:
            raise Exception('max storage over')

        if file_size == 0:
            raise Exception('No data')
        
        # 次に、クライアントからファイル名を読み取り、変数に格納します。JSONデータがある場合は、サポートされていないため、例外が発生します。受信するデータがない場合、コードは例外を発生させます。
        filename = connection.recv(file_name_len).decode('utf-8')
        if not re.match(r'^[\\w\\-.]+$', filename):
            raise Exception('Invalid filename')
        print('Filename: {}'.format(filename))
        
        # 次に、コードはクライアントから受け取ったファイル名で新しいファイルをフォルダに作成します。このファイルは、withステートメントを使用してバイナリモードで開かれ、write()関数を使用して、クライアントから受信したデータをファイルに書き込みます。データはrecv()関数を使用して塊単位で読み込まれ、データの塊を受信するたびにデータ長がデクリメントされます。
        # w+は終了しない場合はファイルを作成し、そうでない場合はデータを切り捨てます
        try:
            with open(os.path.join(dir_path, filename),'wb+') as f:
                # すべてのデータの読み書きが終了するまで、クライアントから読み込まれます
                while file_size > 0:
                    data = connection.recv(file_size if file_size <= stream_rate else stream_rate)
                    f.write(data)
                    print('recieved {} bytes'.format(len(data)))
                    file_size -= len(data)
                    print(file_size)
        except Exception as file_err:
            state = 'error in upload'
            print(f'error in uploading file :{file_err}')
        else:
            state = 'success'
            print('Finished downloading the file from client.')
        
    except Exception as e:
        state = str(e)
        print('Error: ' + state)

    finally:
        connection.send(state.encode('utf-8'))
        print("Closing current connection")
        connection.close()
        
        

    

        
