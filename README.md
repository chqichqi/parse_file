# 新文件解析工具
 
## 概述

    目的：
        通过使用该工具可以快速解析文件，并验证文件是否满足新文件协议的规定；
    功能：
        1）可以在解析文件时，对处算法分析ECG、PPG数据后生成的算法结果文件进行统计，以初步验证算法分析的是否准确等；
        2）可以帮助测试人员修改文件数据（例如：文件采集时间、userId以及设备编号等），再将已经存在房颤或节律异常
    的数据上传到服务器进行分析，最后通过与已知结果进行比对，从而进一步验证算法的正确性等；这样重复利用已知数据，
    从而达到提高测试效率。
    实现语言：
        基于python tinkter进行GUI界面的编写。

 
## 特性


- 安装说明：
- -    1) 配置文件：systemInfo.ini;
- -    2）解密所需的DLL文件，包括：DataEncryptorDll.dll与XJK_Aes_Encryptor.h，需放在dll文件夹下;
- -    3）项目需要python版本为3.9;
- -    4）项目需要的其他依赖，包括：numpy、openpyxl等;

- 使用说明：运行项目时一定要将配置文件及DLL文件夹放在exe的同级目录等;
-  贡献指南：若程序报错，可以通过日志文件来查找对应的错误;
-  许可证: 该项目放在github上，可供任何人员使用，即不需要任何许可证;
-  版本历史: 当前最新版本为：V1.0.0.2;
- 致谢: 感谢所有为该项目做出贡献的人员：无。
- 作者：陈强
-  联系方式: 49983655@qq.com

