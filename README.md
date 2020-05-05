# 細かいことは脇に置いといて、とにかくFlaskアプリを本番環境で公開出来るトコまてもっていく手順  


## Introduction  

### 容易に自作Flaskアプリを公開できるようにしたいのです  

Flaskアプリを本番環境で公開しようとWeb上の情報を頼りに作業を進めていた時「･･･原因分かってみりゃ、そりゃそうだわ」って部分でドハマりし、かなりの時間を浪費してしまいました。  

**･･･いやもう、ハマった、ハマった** :dizzy_face:

素人でオッサンの私としては、サーバーの設定などの部分には時間をかけないようにして、極力アプリケーションそのものの制作に時間と労力を使いたいんです。  
もうハッキリ言っちゃえば、そういった部分は理解なんて二の次にして「正解」を「丸写し」してしまいたい。　　

**･･･だってさぁ、オッサンには時間がないんだもん** :cry:    

そんなわけで、このページは同じような考えを持っている人が、同じ目に遭わずに済む事を願って書きました。内容の正確さは保証できませんが、ここに記載したことがあなたの役に立つことがあれば幸いです。  

## 前提

私同様の知識の乏しい素人向け（因みに私は40半ば過ぎのオッサンだ）に書いていますが、基本的なサーバの設定やflaskの取扱については、既に一定の知識がある事を前提に説明しています

- CentOS7 x86_64がインストールされたサーバーが利用できる。
- サーバーのの基本的な設定が完了している。
- （FlaskをHTTPS対応させる場合）サーバーのHTTP設定が完了している。




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

## ソースからpython3.7をコンパイルしたバージョン

# 現在作成中
```
参考までに、実際に公開している本番環境（さくらのVPS）は以下  
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
（これは何故かと言うと...3.6をインストールしてあったのをド忘れしてしまっていて、3.7もインストールしてしまったのだ!:stuck_out_tongue_closed_eyes: ）



**では、始めます。**  　　

---  

## CentOS7へのPython3系の導入    

個人的には`rh-python36`のインストールがお薦め。なんといってもかかる時間が俄然短いです。  
とはいえ（私もそうでしたが）既に本場環境にPython3系をインストールしている人もいると思われるので

- yumでrh-python36をインストールする  
- pythonをソースコードからコンパイル   

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
`sudo scl enable rh-python36 bash`を実行する必要がありますが、ログインのたびに入力するのはめんどいので`/etc/profile.d/`に`rh-python36.sh`を作成しました。  
（参考…というか丸写しさせていただいた[サイトはコチラ](https://mycodingjp.blogspot.com/2018/12/centos-7-python-3.html)。&emsp;ありがとうございます :bow:)  
内容は  
```
#!/bin/bash
source /opt/rh/rh-python36/enable
export X_SCLS="`scl enable python33 'echo $X_SCLS'`"
```  


### pyhton3系をソースコードからコンパイル  

”両方のパターンをご紹介”と、上で書いといて何ですが…これに関しては、いろんなサイトで紹介されていますのでそちらをご覧ください  

因みに、今回私が参考にさせていただいたサイトはこちら（ありがとうございます:bow:）  
[Narito Blog: CentOS7にPython3.7をインストールする](https://narito.ninja/blog/detail/20/)  

---  

## mod_wsgi のインストール  

### rh-python36をインストールした場合  
[参考サイト](https://centos.pkgs.org/7/centos-sclo-rh-x86_64/rh-python36-mod_wsgi-4.5.17-2.el7.x86_64.rpm.html)  

以下のコマンド実行でOKです。  

```
~# yum install rh-python36-mod_wsgi　　
```


### ソースからPythonをコンパイルした場合

以後に問題が起こるとしたらここが原因になります　　

**yumでmod_wsgiをインストールするとCentOS7にデフォルトで入っているPython2系に紐付いてしまいます。**（改めて見直して気付いたのだけど、[コレ](https://flask.palletsprojects.com/en/1.1.x/deploying/mod_wsgi/)は2系前提の記事だったんだなぁ・・・）  
それによってpython3系にインストールされたFlaskやらその他のモジュールが見つからなくて`ModuleNotFoundError: No module named 'flask'`とか出てしまいます(※)。  


そのことさえ判っていれば、最初からpipでしっかりPython3系に紐付けてインストールすれば良いだけです。  

```
~# python3 -m "pip3 install mod_wsgi"
```  

先にyumでインストールしてしまっている場合、`yum remove mod_wsgi`で削除してしまってください。後からpipでインストールしても、削除しておかないと同じ結果になってしまいます。  


後はFlask自体のインストール。  
```
~# pip3 install flask
```  


_※ 私の場合、`sys.path.append('/flask/module/path')`とか記述してFlaskを読み込めるようにしたら、その後「(2系には無い) `html` モジュールが見つからん」と言われ「（3系で動いているとしか思っていなかったので）_ :confused: _...はぁ???」って状態に陥り、更にそれも解決したと思ったら、「...何故そこでSintax Error???」ってトコでエラーが出るようになり･･･
まあ、そんなこんなでさんざんハマった挙句_  _今コレを書いているというわけデス..._ :weary:

---  

## .wsgiファイルの作成　　

アプリケーションを起動させるための`.wsgi`ファイル(ここでは名前を`application.wsgi`としています)を作成します。  
ファイル名を変更した場合、後に出てくるの設定ファイルの`WSGIScriptAlias`行のファイル名を変更してください　　

ファイルに記述する内容は以下。"&lt;yourapplication&gt;"部分は作成したアプリケーション（`app`オブジェクトを含むファイルまたはパッケージ）名です。
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
（ファイル名"flaskapp"部分は任意。お好きな名前にしてください）

rh-python36-mod_wsgiをインストールした場合、最初の行 `LoadModule wsgi_module`に続くファイルパスは  
`/opt/rh/httpd24/root/usr/lib64/httpd/modules/mod_rh-python36-wsgi.so`  
に置き換えてください  

_flaskapp.conf_
```
LoadModule wsgi_module /usr/local/lib/python3.7/site-packages/mod_wsgi/server/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so

# rh-python36-mod_wsgiをインストールした場合
#LoadModule wsgi_module /opt/rh/httpd24/root/usr/lib64/httpd/modules/mod_rh-python36-wsgi.so

<VirtualHost *:80>
    ServerName example.com

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


ファイルの作成が終わったらapachの再起動させて設定を反映させます  

```
~# systemctl restart httpd
```  

**お疲れ様でした** :relieved:  

後は/var/www/flaskappデイレクトリにアプリケーションをを配置して、あなたのサーバーにアクセスすれば、アプリケーションが動いているはずです。  

ごくシンプルな構成の[サンプルを用意しましたので](https://github.com/t2-Kusumoto/flask_app_on_centos7)、動作確認用に使ってください。


```
/var/www/flaskapp/
          ├── application/
          │   ├── templates/
          │   │   ├── hello.tpl
          │   │   └── index.html
          │   ├── __init__.py
          │   └── view.py
          |
          └── application.wsgi
```  

---  

# 【参考】FlaskアプリをHTTPS対応させる  

---

先々のことを考えると、HTTPS対応も「公開にあたって、やらなきゃいけない事」と考えておいた方が良いのではないでしょうか？  

サーバーのHTTPS設定は以下のサイトなどが参考になるかと思います  （私も参考にさせていただきました。ありがとうございます 🙇）

- [ネコでもわかる！さくらのVPS講座 ～第六回「無料SSL証明書 Let’s Encryptを導入しよう」](https://knowledge.sakura.ad.jp/10534/)
- [REMSYSTEM TECHLOG: CentOS 7とApacheをインストールした環境にLet's EncryptでHTTPSを設定](https://www.rem-system.com/cent-httpd-ssl/)

## FlaskをHTTPS対応させる  

参考サイトは以下（ありがとうございます :bow:）  
[意外と簡単！FlaskをHTTPS対応する方法【Let’s encrypt】](https://blog.capilano-fw.com/?p=374)  

今回は`/var/www/flaskapp`配下に`.well-known`デイレクトリを作成  

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


先に作成した`/etc/httpd/conf.d/flaskapp.conf`に追記。内容は  

```
LoadModule wsgi_module /usr/local/lib/python3.7/site-packages/mod_wsgi/server/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so

<VirtualHost *:443>
    ServerName sakurann-oyaji.info

    # 先に作成したファイルに追加した部分
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/sakurann-oyaji.info/cert.pem
    SSLCertificateChainFile /etc/letsencrypt/live/sakurann-oyaji.info/chain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/sakurann-oyaji.info/privkey.pem
    # 以上が追加分

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

apache再起動でエラーが出なきゃOK.  

```
~# systemctl restart httpd
```
で...結局、Flaskのルーティングも含め、後は何も変更なしでOKでした。

...やたら簡単に終わってしまったのだが、これで本当にいいのだろうか？  

以上、FlaskをHTTPS対応させる方法でした。

**ここまで付き合ってくれたあなたに感謝します :bow:  
そして、本記事を参考にしてくれたあなたが作成したアプリを、いつか私が利用する日が来ることを心から願っております** :heart:

---  
### 以下、泣き言です。読まなくて良いです(苦笑)

## Flaskに関する記事は数多あれど...Web上に公開する方法が解らなきゃ、Flaskを使う意味無くない?  



Flaskに関する記事って「・・・これでlocalhost:5000にアクセスすれば、はい！"Hello World!"」って記事はいっぱい見つかる。  
ただ、本番環境で動かすってことになると案外情報が少ない（いやまぁ、理解っている人達には必要ない情報だからなんだろうが...）

Web上の記事を頼りに、なんとか公開できる状態にはなったのだけど、技術的な部分をちゃんと理解せず、テキトーやってるだけの素人のオッサンには結構きつかった・・・「**俺はこういう部分に労力を注ぎ込みたいわけじゃないんだぁー**」って叫びたかったよ、ホント :sob:  

そんなわけで、Flaskアプリケーションを実際にWeb上に公開するための手順を、**詳細は抜きにしてとにかく公開することを念頭に**示してみたんです･･･が、  

**正直、これが正しい手順と言えるのか？...そこんトコロはオッチャンよく分からん。**  

まあでも、最初にも書いた通り、もしも何処かで誰かが困っているのを助けることが出来ていたり、罠にハマることなく本来の目的=アプリケーションの公開、に集中できるようになってくれていたら･･･私はとてもうれしいです。
