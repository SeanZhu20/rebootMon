# 简介
这里是测试用的部署包，需要启动一个HTTP服务
提供下载，url： http://reboot/testDeploy/package_name.tgz

# 步骤

1. 接收部署命令：
    > {"pkg_name":"package_name", "path":"deploy_path"}

1. 下载部署包到一个临时目录 “/tmp/rebootDeploy/”，变成
/tmp/rebootDeploy/package_name.tgz
    
1. 解压，md5sum -c md5.list
    1. 解压变成，/tmp/rebootDeploy/package_name/，需要检查有start, stop, status, md5.list四个文件
    1. md5sum -c md5.list检测返回值是否为0
    1. 给stop，start，status增加执行权限

1. stop
    
确保stop返回0

1. mv 线上代码部署为 xxx.bak

假设线上路径为/home/work/package_name
一般要求有如下目录：
    *. bin 程序存储目录
    *. log 日志目录
    *. script 存放各种运维脚本

    > mv /home/work/package_name{,.bak}

1. mv /tmp/rebootDeploy/package_name 到线上路径

1. start
