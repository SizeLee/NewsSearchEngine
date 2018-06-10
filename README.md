# Wiki Search Engine

# 使用方法
1. 安装python 3.6+环境
2. 安装lxml html解析器，命令为`pip install lxml`
3. 安装numpy，命令为`pip install numpy`
4. 安装Flask Web框架，命令为`pip install Flask`
5. 进入项目文件夹，运行main.py文件
6. 打开浏览器，访问http://127.0.0.1:5000/ 输入关键词开始测试

如果想抓取最新Wiki数据并构建索引，进入项目文件夹运行searchengineSetup.py，再按上面的方法测试。
当前爬虫抓取采用深度优先的方式，层数设置为3层，爬虫初始网页为wiki的machine learning词条。需要大概3小时左右。
可以在searchengineSetup.py中按照注释设定改变参数。

