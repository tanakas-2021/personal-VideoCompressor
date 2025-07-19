import socket
import os

# アドレスファミリ : socket.AF_INET
# 通信方式 : SOCK_STREAM = TCP通信（信頼性あり、順番保証、コネクション型）
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '127.0.0.1'
server_port = 9001

# mp4を保存するdirPath
dir_path = 'storage'
if not os.path.exists(dir_path):
    os.makedirs(dir_path)


# socketにソケットファイルをバインドし、listenする
sock.bind((server_address, server_port))
sock.listen(1)
print(f'サーバーが起動しました：ソケットファイルは{server_address}です。クライアントからのリクエスを待機中')

while True:
    connection, client_address = sock.accept()
    try:
        print(f'クライアント:{client_address}から接続がありました')

        # 8Byte:ファイルサイズの大きさ
        header = connection.recv(8)
        print(header)
        # 最初の8バイトをファイルサイズとして取得
        file_size = int.from_bytes(header[:8], 'big')
        stream_rate = 1400
        print(f'ファイルサイズは{file_size}')

        if file_size == 0:
            raise Exception('No data to read from client.')
        
        # 次に、コードはクライアントから受け取ったファイル名で新しいファイルをフォルダに作成します。このファイルは、withステートメントを使用してバイナリモードで開かれ、write()関数を使用して、クライアントから受信したデータをファイルに書き込みます。データはrecv()関数を使用して塊単位で読み込まれ、データの塊を受信するたびにデータ長がデクリメントされます。
        # w+は終了しない場合はファイルを作成し、そうでない場合はデータを切り捨てます
        with open(os.path.join(dir_path, 'b.mp4'),'wb+') as f:
            # すべてのデータの読み書きが終了するまで、クライアントから読み込まれます
            while file_size > 0:
                data = connection.recv(file_size if file_size <= stream_rate else stream_rate)
                f.write(data)
                print('recieved {} bytes'.format(len(data)))
                file_size -= len(data)
                print(file_size)
        
        print('Finished downloading the file from client.')

    except Exception as e:
        print('Error: ' + str(e))

    finally:
        print("Closing current connection")
        connection.close()
        
        

    

        
