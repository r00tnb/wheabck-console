## Description
    主要用于管理webshell，目前支持PHP、aspx的shell类型，支持插件扩展。后续会继续支持其他shell类型
    
## Usage
> Start
``git clone https://github.com/r00tnb/wheabck-console.git``
``cd wheabck-console``
``python3 ./wheabck.py``
> Example
使用use命令来设置当前需要使用的webshell连接客户端
``use php/simple_on_word # 使用php 一句话木马连接客户端``
        
使用show命令查看当前客户端的参数选项
``show``
        
使用set命令设置选项值
``set target http://xxxx.com/1.php``
``set password c``
        
选项配置完毕后使用exploit命令创建一个session
``exploit``
        
键入 help 获取当前session可执行的命令
``help``
        
可以使用如下方式获取某个命令的帮助信息
``help cmd``
``cmd -h``
        
如果从已经保存的连接中创建session，使用如下命令
``exploit -c 1``
