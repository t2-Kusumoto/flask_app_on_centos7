# 細かいことは脇に置いといて、とにかくFlaskアプリを本番環境で公開出来るトコまてもっていく手順  


## Introduction  

### 容易に自作Flaskアプリを公開できるようにしたいのです  

Flaskアプリを本番環境で公開しようとWeb上の情報を頼りに作業を進めていた時「･･･原因分かってみりゃ、そりゃそうだわ」って部分でドハマりし、かなりの時間を浪費してしまいました。  

**･･･いやもう、ハマった、ハマった** :dizzy_face:

素人でオッサンの私としてはサーバーの設定などの部分には、あまり時間をかけないようにしたい。  
もうハッキリ言っちゃえば、そういった部分は、理解なんて二の次にして「正解を丸写し」してしまいたい。

**･･･だってさぁ、オッサンには時間がないんだもん** :cry:    
（アプリケーション本体の制作に時間と労力を使いたいんです）  


まぁそんなこともあって･･･「Flaskで作ったアプリを公開しよう！」と思い立った“何処かの誰か”が、その過程で私と同じ目に遭わずに済む事を願ってこのリポジトリを作ってみました。  
内容の正確さは保証できませんが、ここに記載した内容の、ほんの一部分でも“何処かの誰か”の役に立つことがあれば嬉しいです。  

## 前提

私同様の知識の乏しい素人向け（因みに私は40半ば過ぎのオッサンだ）に書いていますが、基本的なサーバの設定やFlaskの取扱については、既に一定の知識がある事を前提に説明しています

- CentOS7 x86_64がインストールされたサーバーが利用できる。
- サーバーの基本的な設定が完了している。
- (FlaskをHTTPS対応させる場合)サーバーのHTTPS対応が完了している。  


### テスト用環境及び実際に作成した本番環境  

このページで説明している内容は`virtualbox 6.0`に`CentOS-7-x86_64-Minimal-1908.iso`をインストールして作成した仮想環境で動作確認をしました。

ここでは、flaskアプリケーションを`/var/www/flaskapp/`に配置すると仮定して話を進めて行きます。（ディレクトリ名"flaskapp"部分は任意。変更する場合、後に出てくる設定ファイルの内容も置き換えてください）

```
~$ cat /etc/redhat-release
CentOS Linux release 7.7.1908 (Core)

~$ sudo httpd -V
Server version: Apache/2.4.6 (CentOS)
...
...

## rh-python3.6をインストールしたバージョン  
~$ flask --version
Python 3.6.9
Flask 1.1.2
Werkzeug 1.0.1

## ソースコードからpython3.7をビルドしたバージョン
~$ flask --version
Python 3.7.6
Flask 1.1.2
Werkzeug 1.0.1
```
参考までに、実際に[公開している](https://sakurann-oyaji.info/)本番環境（さくらのVPS）は以下  
```
~$ cat /etc/redhat-release
CentOS Linux release 7.8.2003 (Core)

~$ sudo httpd -V
Server version: Apache/2.4.6 (CentOS)
...
...

~$ flask --version
Python 3.7.6
Flask 1.1.1
Werkzeug 1.0.0
```  

因みにこの本番環境にはPython 3.6.8も導入されています  
（これは何故かと言うと...3.6をインストールしてあったのをド忘れしてしまっていて、3.7もインストールしてしまったのだ :stuck_out_tongue_closed_eyes: ）



**では、始めます。**  　　

---  

## CentOS7へのPython3系の導入    

個人的には`rh-python36`のインストールがお薦め。なんといってもかかる時間が俄然短いです。  
とはいえ（私もそうでしたが）既に本場環境にPython3系をインストールしている人もいると思われるので

- yumでrh-python36をインストールする  
- pythonをソースコードからビルド   

両方のパターンをご紹介   

### rh-python36をインストールする  

[Python 3.6 by Software Collections](https://www.softwarecollections.org/en/scls/rhscl/rh-python36/)  

Software Collections (SCL) repositoriesを導入  
```
~# yum install centos-release-scl
```

python3.6 のインストール  
```
~# yum install rh-python36  
```  

rh-python36を有効にするには
`sudo scl enable rh-python36 bash`を実行する必要がありますが、ログインのたびに入力するのは面倒なので`/etc/profile.d/`に`rh-python36.sh`を作成しました。  
（参考…というか丸写しさせていただいた[サイトはコチラ](https://mycodingjp.blogspot.com/2018/12/centos-7-python-3.html)。&emsp;ありがとうございます :bow:)  
内容は以下  

_== rh-python36&#46;sh ==_
```
#!/bin/bash
source /opt/rh/rh-python36/enable
export X_SCLS="`scl enable python33 'echo $X_SCLS'`"
```  


### pyhton3系をソースコードからビルド  


参考にさせていただいたサイトは以下（ありがとうございます:bow:）  
- [Python Japan: CentOs環境のPython](https://www.python.jp/install/centos/index.html)
- [Narito Blog: CentOS7にPython3.7をインストールする](https://narito.ninja/blog/detail/20/)  


まず、Python3 の[ソースコードを入手](https://www.python.org/downloads/source/)して、解凍しておく。（ここではPython3.7.6をダウンロードしています）

```
~$ curl https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz > Python-3.7.6.tgz

# ダウンロード出来たら解凍
~$ tar xzf Python3.7.6.tgz
```  

必要なツール類をダウンロード  
```
~$ sudo yum groupinstall "Development tools" --setopt=group_package_types=mandatory,default,optional

~$ sudo yum install bzip2-devel gdbm-devel libffi-devel \
  libuuid-devel ncurses-devel openssl-devel readline-devel \
  sqlite-devel tk-devel wget xz-devel zlib-devel
```  

完了したら解凍したディレクトリに移動して、以下のコマンドを実行していきます（時間かかります）  
```
~$ cd Python3.7.6
~$ ./configure --enable-shared
~$ make
-$ sudo make altinstall

# インストール終了後
~$ sudo sh -c "echo '/usr/local/lib' > /etc/ld.so.conf.d/custom_python3.conf"
~$ sudo ldconfig
```  

ここまででエラーがなければ、`python3.7 or python3`コマンドでpythonが起動するはずですが、私は"python3.7"と入力するのが億劫なので、`.bashrc`に以下を追記して`python3, pip3`でpythonが起動するようにしています  

_== .bashrc ==_  
```
...
...
alias sudu='sudo '
alias python3='python3.7'
alias pip3='pip3.7'
...
...
```

因みに、各コマンドについては以下など参考にどうぞ  

- [qiita: configure, make, make install とは何か](https://qiita.com/chihiro/items/f270744d7e09c58a50a5)
- [SOFTELメモ: shとsourceの違い](https://www.softel.co.jp/blogs/tech/archives/5971)
- [「分かりそう」で「分からない」でも「分かった」気になれるIT用語辞典: ldconfig【コマンド】とは](https://wa3.i-3-i.info/word13812.html)  


---  

## mod_wsgi のインストール  

### rh-python36をインストールした場合  
[参考サイト pkgs.org: rh-python36-mod_wsgi-4.5.17-2.el7.x86_64.rpm](https://centos.pkgs.org/7/centos-sclo-rh-x86_64/rh-python36-mod_wsgi-4.5.17-2.el7.x86_64.rpm.html)  

以下のコマンド実行でOKです。  

```
~# yum install rh-python36-mod_wsgi　　
```


### ソースからPythonをコンパイルした場合

まず、`httpd-devel`モジュールをインストールしておきます  

```
~$ sudo yum install httpd-devel
```  

さて･･･いざFlaskアプリを動かそうとして、問題が発生するようになるとしたら、おそらく以下の原因によるものかと思われます。　　

**`yum`でmod_wsgiをインストールするとCentOS7にデフォルトで入っているPython2系に紐付いてしまいます。**  
（改めて見直して気付いたのだけど、[コレ](https://flask.palletsprojects.com/en/1.1.x/deploying/mod_wsgi/)は2系前提の記事だったんだなぁ・・・）  

それによってpython3系にインストールされたFlaskやその他のモジュールが見つからなくて  
`ModuleNotFoundError: No module named 'flask'`とか出てしまいます(※)。  


そのことさえ解っていれば、最初からpipでしっかりPython3系に紐付けてインストールすれば良いだけです。  

```
~$ sudo pip3 install mod_wsgi
```  

既にyumでインストールしてしまっている場合、`yum remove mod_wsgi`で削除してしまってください。  

後はFlaskのインストール。  
```
~$ sudo pip3 install flask
```  


_※ 私の場合、`sys.path.append('/flask/module/path')`とか記述してFlaskを読み込めるようにしたら(これで"Hello World!"を表示させるFlaskアプリくらいなら動くようになる)、「(2系には無い) `html` モジュールが見つからん」と言われ、「（3系で動いているとしか思っていなかったので）_ :confused: _...???」って状態に陥り、更にそれも解決したと思ったら「...何故そこで "sintax error"???」って所にエラーが出るようになり･･･  
まあ、そんなこんなでさんざんハマった挙句_  _今コレを書いているというわけデス..._ :weary:

---  

## .wsgiファイルの作成　　

アプリケーションを起動させるための`.wsgi`ファイル(ここでは名前を`application.wsgi`としています)を`/var/www/flaskapp/`ディレクトリに作成します。  
ファイル名を変更した場合、後に出てくるの設定ファイルの`WSGIScriptAlias`行のファイル名を変更してください　　

ファイルに記述する内容は以下。"&lt;yourapplication&gt;"部分は作成したアプリケーション（`app`オブジェクトを含むファイルまたはパッケージ）名です。(このリポジトリに用意したサンプルの場合だと`application`になる)  


_== application&#46;py ==_
```
#!/usr/bin/env python3
# -*- coding; utf-8 -*-

import sys
sys.path.insert(0, '/var/www/flaskapp')

from <yourapplication> import app as application
```

---  

## 設定ファイルの配置  

`/etc/httpd/conf.d/`配下に`flaskapp.conf`ファイルを作成します  
ファイル名"flaskapp"部分は任意です。お好きな名前にしてください。`<your-server-name>`もあなたのサーバーに合わせて置き換えてください(テスト環境なら`exsample.com`等でもOK)

先頭行 `LoadModule wsgi_module`に続くファイルパスは`~$ pip3 show mod_wsgi`で`Location:`行に表示されるファイルパスをさらに辿っていった先にある"&#46;so"拡張子のファイルのパスです  

rh-python36-mod_wsgiをインストールした場合はファイルパスを  
`/opt/rh/httpd24/root/usr/lib64/httpd/modules/mod_rh-python36-wsgi.so`  
に置き換えてください  


_== flaskapp&#46;conf ==_
```
LoadModule wsgi_module /usr/local/lib/python3.7/site-packages/mod_wsgi/server/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so

<VirtualHost *:80>
    ServerName <your-server-name>
    WSGIDaemonProcess flaskapp user=apache group=apache threads=5
    WSGIScriptAlias / /var/www/flaskapp/application.wsgi
    <Directory /var/www/flaskapp>
        WSGIProcessGroup flaskapp
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```  


ファイルの作成が終わったら設定を反映させます  

```
~# systemctl restart httpd
```  

**お疲れ様でした** :relieved:  

後は`/var/www/flaskapp`デイレクトリにFlaskアプリケーションをを配置して、あなたのサーバーにアクセスすれば、アプリケーションが動いてくれるはずです。  

ごくシンプルな構成のサンプルをこのリポジトリに用意しましたので、動作確認用に使ってください。  
ファイルの構成は以下です。  


```
/var/www/flaskapp/
          ├── application/
          │   ├── templates/
          │   │   ├── hello.tpl
          │   │   └── index.html
          |   ├── static/
          |   |   └── styles.css
          │   ├── __init__.py
          │   └── view.py
          └── application.wsgi
```  

---  

# 【参考】FlaskアプリのHTTPS対応（Let's Encryptを導入）  

---

先々のことを考えると、HTTPS対応も「公開にあたって、やらなきゃいけない事」と考えておいた方が良いのではないでしょうか？  

サーバーのHTTPS設定は以下のサイトなどが参考になるかと思います  （私も参考にさせていただきました。ありがとうございます 🙇）

- [ネコでもわかる！さくらのVPS講座 ～第六回「無料SSL証明書 Let’s Encryptを導入しよう」](https://knowledge.sakura.ad.jp/10534/)
- [REMSYSTEM TECHLOG: CentOS 7とApacheをインストールした環境にLet's EncryptでHTTPSを設定](https://www.rem-system.com/cent-httpd-ssl/)

## FlaskをHTTPS対応させる  

参考サイトは以下（ありがとうございます :bow:）  
[意外と簡単！FlaskをHTTPS対応する方法【Let’s encrypt】](https://blog.capilano-fw.com/?p=374)  

今回は`/var/www/flaskapp`配下に`.well-known`デイレクトリ(中身は空のまま）を作成  


```
/var/www/flaskapp/
          ├──.well-known/ #これを追加
          │
          ├── application/
          │   ├── templates/
          │   │   ├── hello.tpl
          │   │   └── index.html
          │   ├── __init__.py
          │   └── view.py
          |
          └── application.wsgi
```  


先に作成した`/etc/httpd/conf.d/flaskapp.conf`のポート番号を変更、および４行追記。  

_== flaskapp&#46;conf ==_
```
LoadModule wsgi_module /usr/local/lib/python3.7/site-packages/mod_wsgi/server/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so

<VirtualHost *:443> # 80 -> 443へ変更 
    ServerName <your-server-name>
    SSLEngine on　#ここから４行が追加分
    SSLCertificateFile /etc/letsencrypt/live/<your-site-name>/cert.pem
    SSLCertificateChainFile /etc/letsencrypt/live/<your-site-name>/chain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/<your-site-name>/privkey.pem　
    WSGIDaemonProcess flaskapp user=apache group=apache threads=5
    WSGIScriptAlias / /var/www/flaskapp/application.wsgi
    <Directory /var/www/flaskapp>
        WSGIProcessGroup flaskapp
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```  

変更後保存して、httpd再起動でエラーが出なきゃOK.  

```
~# systemctl restart httpd
```
で...結局、後はFlaskのルーティングも含め、何も変更なしでOKでした。

...やたら簡単に終わってしまったのだが、これで本当にいいのだろうか？  

以上、FlaskをHTTPS対応させる方法でした。

**最後まで駄文に付き合って下さった、あなたに感謝します :bow:  
そして（本記事を参考にしてくれた）あなたが作成したアプリケーションを、いつか私が利用する日が来ることを、心から願っております** :heart:
