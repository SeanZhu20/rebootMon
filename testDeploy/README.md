# 简介
这里是测试用的部署包，需要启动一个HTTP服务
提供下载，url： http://reboot/testDeploy/package_name.tgz

# 步骤

1. 接收部署命令：
    > {"pkg_name":"package_name", "path":"deploy_path"}

1. 下载部署包到一个临时目录 “/tmp/rebootDeploy/”
    
1. 解压，md5sum -c md5list

1. stop

1. mv 线上代码部署为 xxx.bak

1. mv /tmp/rebootDeploy/package_name 到线上路径

1. start
